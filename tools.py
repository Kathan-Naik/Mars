from dotenv import load_dotenv
import os, json, asyncio, traceback

from agents import CompanyResearcher
from report import save_html

load_dotenv()

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def list_existing_researches():
    reports = [f for f in os.listdir(REPORT_DIR) if f.endswith(".html")]
    if not reports:
        return "No reports found."
    report_list = "\n- ".join(reports)
    return f"I found {len(reports)} report(s):\n- {report_list}\n\nWould you like me to open it, summarize it, or run a new company research? \n Note: Pass this info and links as it is to user!"

def fetch_research(args):
    """Return the HTML content of a requested report."""
    report_name = args.get("report_name")
    if not report_name:
        return "Please provide a report_name."
    
    filepath = os.path.join(REPORT_DIR, report_name)
    if not os.path.exists(filepath):
        return f"Report '{report_name}' not found."
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content

async def trigger_deep_research(args):
    research = CompanyResearcher()
    research.company_name = args["company_name"]
    research.geo_focus = args.get("geo_focus", "Global")
    research.time_horizon = args.get("time_horizon", "last 12 months")
    research.industry_focus = args.get("industry_focus")
    
    await research.financial_research()
    await research.news_intelligence()
    await research.sentiment_analysis()
    await research.market_context()
    await research.insight_synthesis()
    
    filename = f"{REPORT_DIR}/{research.company_name}.html"
    save_html(research, filename)
    
    return f"Research completed for {research.company_name}. Report saved as {filename}."

def display_tradingview_chart(args):
    """Generate TradingView chart HTML for display in chat."""
    symbol = args.get("symbol", "").upper()
    timeframe = args.get("timeframe", "1D")
    
    if not symbol:
        return "Please provide a stock symbol (e.g., AAPL, TSLA, NVDA)"
    
    if ":" not in symbol:
        symbol = f"NASDAQ:{symbol}"
    
    interval_map = {
        "1D": "D",
        "1M": "W", 
        "1Y": "M"
    }
    
    interval = interval_map.get(timeframe.upper(), "D")
    
    chart_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .chart-container {{ width: 100%; height: 500px; }}
    </style>
</head>
<body>
    <div class="chart-container">
        <div class="tradingview-widget-container" style="height:100%;width:100%">
            <div id="tradingview_chart" style="height:100%;width:100%"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true,
                "symbol": "{symbol}",
                "interval": "{interval}",
                "timezone": "Etc/UTC",
                "theme": "light",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_chart"
            }});
            </script>
        </div>
    </div>
</body>
</html>"""
    
    # Return with a special marker that GPT should include in its response
    return f"[CHART_HTML_START]{chart_html}[CHART_HTML_END]"

# Updated TOOLS array with TradingView chart tool
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_existing_researches",
            "description": "List all previously generated company research reports. You should forward this to the user as it is.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_deep_research",
            "description": "Run a full multi-agent deep research on a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Name of the company to research"
                    },
                    "geo_focus": {
                        "type": "string",
                        "description": "Geographic focus (e.g., Global, USA, Europe)"
                    },
                    "industry_focus": {
                        "type": "string",
                        "description": "Industry or sector focus"
                    },
                    "time_horizon": {
                        "type": "string",
                        "description": "Time period for analysis (e.g., last 12 months, 3-5 years)"
                    }
                },
                "required": ["company_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_research",
            "description": "Fetch the HTML content of a saved research report for summarization or Q&A",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_name": {
                        "type": "string",
                        "description": "The name of the report to fetch, e.g., Tesla.html"
                    }
                },
                "required": ["report_name"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "display_tradingview_chart",
        "description": "Display an interactive TradingView price chart in the side panel. This will show the chart immediately without returning HTML. Just acknowledge that the chart is displayed.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, TSLA, NVDA, MSFT)"
                },
                "timeframe": {
                    "type": "string",
                    "enum": ["1D", "1M", "1Y"],
                    "description": "Chart timeframe: 1D (daily), 1M (monthly), 1Y (yearly)",
                    "default": "1D"
                }
            },
            "required": ["symbol"]
        }
    }
}
]