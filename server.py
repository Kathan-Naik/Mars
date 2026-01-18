from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os, json, asyncio, traceback
from collections import defaultdict

from tools import TOOLS, list_existing_researches, fetch_research, trigger_deep_research

load_dotenv()
client = OpenAI()
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount reports directory
app.mount("/reports", StaticFiles(directory="reports"), name="reports")
app.mount("/flow", StaticFiles(directory="flow"), name="flow")

# In memory conversation storage and chart queue
conversations = {}
chart_queue = defaultdict(list)

class ChatRequest(BaseModel):
    messages: list
    session_id: str = "default"

@app.get("/")
async def serve_index():
    """Serve the main HTML interface"""
    return FileResponse("index.html")

# execution loop for tool calls
async def execute_tool(tool_name: str, args: dict, session_id: str) -> str:
    """Execute the tool and return result as string"""
    if tool_name == "list_existing_researches":
        return list_existing_researches()
    elif tool_name == "fetch_research":
        return fetch_research(args)
    elif tool_name == "trigger_deep_research":
        return await trigger_deep_research(args)
    elif tool_name == "display_tradingview_chart":
        # Queue the chart for display without returning HTML to LLM
        symbol = args.get("symbol", "").upper()
        timeframe = args.get("timeframe", "1D")
        
        if ":" not in symbol:
            symbol = f"NASDAQ:{symbol}"
        
        chart_queue[session_id].append({
            "symbol": symbol,
            "timeframe": timeframe
        })
        
        return f"Chart for {symbol} ({timeframe}) is now displayed in the side panel."
    else:
        return f"Unknown tool: {tool_name}"

# chat endpoint
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        session_id = req.session_id
        
        if session_id not in conversations:
            conversations[session_id] = []

        chart_queue[session_id] = []
        
        user_message = req.messages[-1] 
        conversations[session_id].append(user_message)
        
        messages_to_send = conversations[session_id].copy()
        
        response = client.chat.completions.create(
            model="gpt-4.1", 
            messages=messages_to_send,
            tools=TOOLS
        )

        max_iterations = 5  
        iteration = 0
        
        while iteration < max_iterations:
            message = response.choices[0].message
            assistant_text = message.content or ""
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None

            if not tool_calls:
                conversations[session_id].append({
                    "role": "assistant",
                    "content": assistant_text
                })
                
                # Get charts and then clear the queue
                charts = chart_queue.get(session_id, []).copy()
                chart_queue[session_id] = []  # Clear after getting
                
                return {
                    "response": assistant_text or "I'm not sure how to help with that.",
                    "charts": charts
                }

            conversations[session_id].append({
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in tool_calls
                ]
            })

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")
                tool_result = await execute_tool(tool_name, args, session_id)

                conversations[session_id].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=conversations[session_id],
                tools=TOOLS
            )
            
            iteration += 1

        return {"response": "Processing completed but may be incomplete. Please try again."}

    except Exception as e:
        traceback.print_exc()
        return {"error": "Backend error. Check server logs.", "details": str(e)}


@app.post("/clear")
async def clear_conversation(session_id: str = "default"):
    """Clear conversation history for a session"""
    if session_id in conversations:
        conversations[session_id] = []
        chart_queue[session_id] = []
        return {"message": f"Conversation history cleared for session: {session_id}"}
    return {"message": "No conversation found for this session"}


@app.get("/history/{session_id}")
async def get_history(session_id: str = "default"):
    """Retrieve conversation history"""
    return {"history": conversations.get(session_id, [])}