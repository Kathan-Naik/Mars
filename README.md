
<img width="1920" height="1080" alt="flow" src="https://github.com/user-attachments/assets/3ab34414-0a62-46f7-9f26-c5dfd6c442b4" />

# MARS: Multi-Agent Research Bot — Architecture Summary

## 1. Core System
**MARS (Multi-Agent Research System)** is the central orchestrator that manages user queries and research workflows.  
It decides whether to:
- Answer using existing reports, or
- Trigger a new deep research process.

---

## 2. Data & Tooling Layer

### TradingView Charts Tool
- Provides market and price chart data used during analysis.

### Reports Repository
- Stores all previously generated research reports.

### Report Listing & Fetcher Tool
- Allows MARS to:
  - Discover existing reports
  - Answer user followup queries without rerunning research

### Deep Research Tool
- Enables planning and execution of multi-agent deep research workflows.

---

## 3. Specialized Research Agents

When deep research is triggered, the following agents operate (mostly in parallel):

### Financial Agent (~4 min)
- Analyzes company financials and regulatory filings
- Connects to local storage for structured data

### News Agent (~6 min)
- Researches three subtopics in depth
- Collects and synthesizes relevant news

### Sentiment Agent (~3 min)
- Analyzes public and market sentiment

### Market Agent (~2 min)
- Evaluates market conditions and macro trends

---

## 4. Synthesis & Report Generation

### Insights Agent (~5 min)
- Aggregates outputs from all research agents
- Extracts and highlights deep, high-value insights
- Produces a **New Research Report**

---

## 5. Storage & Reuse
- Newly generated reports are saved back to the **Reports Repository**
- Future queries can be answered instantly using stored knowledge

---

## 6. Key Architectural Principles
- Modular, specialized agents
- Parallel execution for speed
- Cost-efficient reuse of existing reports
- Easily extensible and scalable design

# MARS Repository — Files Overview

## Overview
The tools and modules in this repository work together to gather data about a company, perform deep multi-agent research, and generate a comprehensive research report.  
The system is designed around a conversational entry point, agent-based intelligence, and reusable data/report tooling.

---

## Core Application Files

### `server.py`
- **Conversational agent entry point**
- Handles user interaction (API / chat interface) using FastAPI!
- Orchestrates tool calls and agent execution defined in `agents.py`

---

### `agents.py`
- **Holds all research agents**
- Built using **GPT Researcher**
- Defines and manages:
  - Financial Agent
  - News Agent
  - Sentiment Agent
  - Market Agent
  - Insights Agent
- Responsible for running deep research and returning structured outputs for reporting

---

## Data Collection & Processing Tools

### `fetch.py`
- Downloads **10-K filings** for a given company
- Saves filings locally for reuse
- Acts as the primary data ingestion layer for financial analysis

---

### `tools.py`
- Contains shared **helper utilities** used across the system
- Includes:
  - TradingView chart generation
  - Common data-processing helpers
- Used by agents, report generation, and server logic

---

## Reporting Layer

### `report.py`
- Generates the final **HTML research report**
- Uses data gathered by:
  - `fetch.py`
  - Outputs from agents in `agents.py`
- Formats insights, charts, and analysis into a structured report

---

## Repository Design Summary
- **`server.py`** → Conversation & orchestration  
- **`agents.py`** → Intelligence & deep research  
- **`fetch.py`** → Data ingestion (10-K filings)  
- **`tools.py`** → Shared utilities & charting  
- **`report.py`** → Report generation & presentation  

This separation ensures modularity, scalability, and efficient reuse of data and research outputs.

