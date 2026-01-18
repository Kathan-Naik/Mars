import logging
import asyncio
from gpt_researcher import GPTResearcher
from dotenv import load_dotenv
load_dotenv()

class CompanyResearcher:
    def __init__(self):
        #inputs
        self.company_name = ""
        self.industry_focus = ""
        self.geo_focus = ""
        self.time_horizon = ""

        # reports
        self.financials = ""
        self.news = ""
        self.sentiment = ""
        self.market = ""
        self.synthesis = ""

        #notes
        self.notes = "Do not use any code blocks in your responses."

    # Agent 1: Financial & Regulatory Research
    async def financial_research(self):
        query = f"""
    Aanalyze the LAST 3 YEARS of financial info for {self.company_name}.
    Summarize key metrics and trends in short.

    Sources:
    - annualreport.com
    - Quarterly results, investor presentations, regulatory filings

    Focus On:
    - Revenue trend
    - Profitability trajectory
    - Cash flow
    - Balance sheet

    Subtopic:
    - Red flags

    {self.notes}
    """
        researcher = GPTResearcher(query=query, 
                                   report_type="detailed_report",
                                #  for local databank access but too much embeddings usage
                                #  report_source="local", 
                                   max_subtopics=1)

        await researcher.conduct_research()
        report = await researcher.write_report()

        self.financials = report

        return report


    # Agent 2: News & Media Intelligence
    async def news_intelligence(self):
        query = f"""
    Analyze news/media coverage for {self.company_name} over {self.time_horizon}. And provide brief summary.

    Identify major events:
    - Product launches
    - Tech breakthroughs
    - Funding, partnerships, acquisitions
    - Controversies/risks
    - Leadership changes

    Output:
    - Focus more on recent and hight impact events
    - Chronological or thematic summary
    - Positive vs negative narratives

    {self.notes}
    """
        researcher = GPTResearcher(query=query, report_type="detailed_report", max_subtopics=3)

        await researcher.conduct_research()
        report = await researcher.write_report()

        self.news = report

        return report


    # Agent 3: Social & Public Sentiment
    async def sentiment_analysis(self):
        query = f"""
    Analyze public and social sentiment around {self.company_name}. And Summarize in few bullet points.

    Context:
    - Time horizon: {self.time_horizon}

    Sources:
    - Social media, forums, opinion pieces, public commentary

    Identify:
    - Investor perception
    - Leadership perception
    - Customer sentiment
    - Employee sentiment
    - Recurring themes

    {self.notes}
    """
        researcher = GPTResearcher(query=query, report_type="research_report", max_subtopics=1)

        await researcher.conduct_research()
        report = await researcher.write_report()

        self.sentiment = report

        return report


    # Agent 4: Market & Competitive Context
    async def market_context(self):
        query = f"""
    Analyze market and competitive context for {self.company_name}.

    Context:
    - Industry: {self.industry_focus}
    - Geography: {self.geo_focus}

    Cover:
    - Key competitors
    - Industry positioning
    - Market dynamics
    - Growth themes
    - Competitive advantages/disadvantages

    {self.notes}
    """
        researcher = GPTResearcher(query=query, report_type="outline_report", max_subtopics=0)

        await researcher.conduct_research()
        report = await researcher.write_report()

        self.market = report

        return report


    # Agent 5: Insight Synthesis
    async def insight_synthesis(self):
        query = f"""
    Use ONLY internal analysis. Give short bulleted insights.

    === Company ===
    Name: {self.company_name}
    Geography: {self.geo_focus}
    Industry: {self.industry_focus}
    Time Horizon: {self.time_horizon}

    === Financials ===
    {self.financials}

    === News ===
    {self.news}

    === Sentiment ===
    {self.sentiment}

    === Market ===
    {self.market}

    Tasks:
    - Connect insights across domains
    - Surface non-obvious observations
    - Highlight contradictions or hidden risks
    - Avoid repeating raw facts
    """
        researcher = GPTResearcher(query=query, report_type="deep", max_subtopics=1)

        await researcher.conduct_research()
        report = await researcher.write_report()

        self.synthesis = report

        return report
