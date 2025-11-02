"""
Expert Investor MCP Server using FastMCP with stdio transport
This version uses stdio transport to avoid HTTP compatibility issues
"""
from typing import Annotated
import os
import requests
from functional.analyzer import ReportAnalysisUtils
from functional.charting import ReportChartUtils, MplFinanceUtils
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool
from textwrap import dedent
from utils import decorate_all_methods

# Create FastMCP server
server = FastMCP(
    "Expert_Investor",
    port=8001,
    instructions=dedent(
        """
        Role: Expert Investor
        Department: Finance
        Primary Responsibility: Generation of Customized Financial Analysis Reports

        Role Description:
        As an Expert Investor within the finance domain, your expertise is harnessed to develop bespoke Financial Analysis Reports that cater to specific client requirements. This role demands a deep dive into financial statements and market data to unearth insights regarding a company's financial performance and stability. Engaging directly with clients to gather essential information and continuously refining the report with their feedback ensures the final product precisely meets their needs and expectations.

        Key Objectives:

        Analytical Precision: Employ meticulous analytical prowess to interpret financial data, identifying underlying trends and anomalies.
        Effective Communication: Simplify and effectively convey complex financial narratives, making them accessible and actionable to non-specialist audiences.
        Client Focus: Dynamically tailor reports in response to client feedback, ensuring the final analysis aligns with their strategic objectives.
        Adherence to Excellence: Maintain the highest standards of quality and integrity in report generation, following established benchmarks for analytical rigor.

        Performance Indicators:
        The efficacy of the Financial Analysis Report is measured by its utility in providing clear, actionable insights. This encompasses aiding corporate decision-making, pinpointing areas for operational enhancement, and offering a lucid evaluation of the company's financial health. Success is ultimately reflected in the report's contribution to informed investment decisions and strategic planning.

        Reply TERMINATE when everything is settled.
        """
    ),
)

# Copy all the tools from the original expert_investor.py
@server.tool()
def get_sec_report_tool(
        ticker_symbol: Annotated[str, "ticker symbol"],
        fyear: Annotated[
            str,
            "year of the 10-K report, should be 'yyyy' or 'latest'. Default to 'latest'",
        ] = "latest",
    ) -> str:
    # Import inside function to avoid circular imports
    from data_source.fmp_utils import FMPUtils
    return FMPUtils.get_sec_report(ticker_symbol, fyear)

@server.tool()
def build_annual_report_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    save_path: Annotated[str, "path to save the annual report pdf"],
    operating_results: Annotated[
        str,
        "a paragraph of text: the company's income summarization from its financial report",
    ],
    market_position: Annotated[
        str,
        "a paragraph of text: the company's current situation and end market (geography), major customers (blue chip or not), market share from its financial report, avoid similar sentences also generated in the business overview section, classify it into either of the two",
    ],
    business_overview: Annotated[
        str,
        "a paragraph of text: the company's description and business highlights from its financial report",
    ],
    risk_assessment: Annotated[
        str,
        "a paragraph of text: the company's risk assessment from its financial report",
    ],
    competitors_analysis: Annotated[
        str,
        "a paragraph of text: the company's competitors analysis from its financial report and competitors' financial report",
    ],
    share_performance_image_path: Annotated[
        str, "path to the share performance image"
    ],
    pe_eps_performance_image_path: Annotated[
        str, "path to the PE and EPS performance image"
    ],
    filing_date: Annotated[str, "filing date of the analyzed financial report"],
) -> str:
    from functional.reportlab import ReportLabUtils
    return ReportLabUtils.build_annual_report(
        ticker_symbol,
        save_path,
        operating_results,
        market_position,
        business_overview,
        risk_assessment,
        competitors_analysis,
        share_performance_image_path,
        pe_eps_performance_image_path,
        filing_date
    )

@server.tool()
def analyze_company_description_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Analyze company description with 10-K report data"""
    return ReportAnalysisUtils.analyze_company_description(ticker_symbol, fyear, save_path)

@server.tool()
def analyze_income_stmt_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Analyze income statement with 10-K report data"""
    return ReportAnalysisUtils.analyze_income_stmt(ticker_symbol, fyear, save_path)

@server.tool()
def income_summarization_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    income_stmt_analysis: Annotated[str, "in-depth income statement analysis"],
    segment_analysis: Annotated[str, "in-depth segment analysis"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Summarize income statement and segment analysis"""
    return ReportAnalysisUtils.income_summarization(ticker_symbol, fyear, income_stmt_analysis, segment_analysis, save_path)

@server.tool()
def analyze_balance_sheet_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Analyze balance sheet with 10-K report data"""
    return ReportAnalysisUtils.analyze_balance_sheet(ticker_symbol, fyear, save_path)

@server.tool()
def analyze_cash_flow_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Analyze cash flow statement with 10-K report data"""
    return ReportAnalysisUtils.analyze_cash_flow(ticker_symbol, fyear, save_path)

@server.tool()
def analyze_segment_stmt_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Analyze segment statement with 10-K report data"""
    return ReportAnalysisUtils.analyze_segment_stmt(ticker_symbol, fyear, save_path)

@server.tool()
def analyze_business_highlights_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Analyze business highlights with 10-K report data"""
    return ReportAnalysisUtils.analyze_business_highlights(ticker_symbol, fyear, save_path)

@server.tool()
def get_risk_assessment_tool(
    ticker_symbol: Annotated[str, "ticker symbol"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    save_path: Annotated[str, "txt file path, to which the returned instruction & resources are written."]
) -> str:
    """Get risk assessment from 10-K report"""
    return ReportAnalysisUtils.get_risk_assessment(ticker_symbol, fyear, save_path)

@server.tool()
def get_share_performance_tool(
    ticker_symbol: Annotated[str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"],
    filing_date: Annotated[str, "filing date in 'YYYY-MM-DD' format"],
    save_path: Annotated[str, "File path where the plot should be saved"],
) -> str:
    """Plot the stock performance of a company compared to the S&P 500 over the past year."""
    return ReportChartUtils.get_share_performance(ticker_symbol, filing_date, save_path)

@server.tool()
def get_pe_eps_performance_tool(
    ticker_symbol: Annotated[str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"],
    filing_date: Annotated[str, "filing date in 'YYYY-MM-DD' format"],
    years: Annotated[int, "number of years to search from, default to 4"] = 4,
    save_path: Annotated[str, "File path where the plot should be saved"] = None,
) -> str:
    """Plot the PE ratio and EPS performance of a company over the past n years."""
    return ReportChartUtils.get_pe_eps_performance(ticker_symbol, filing_date, years, save_path)

@server.tool()
def plot_stock_price_chart_tool(
    ticker_symbol: Annotated[str, "Ticker symbol of the stock (e.g., 'AAPL' for Apple)"],
    start_date: Annotated[str, "Start date of the historical data in 'YYYY-MM-DD' format"],
    end_date: Annotated[str, "End date of the historical data in 'YYYY-MM-DD' format"],
    save_path: Annotated[str, "File path where the plot should be saved"],
    verbose: Annotated[str, "Whether to print stock data to console. Default to False."] = False,
    type: Annotated[str, "Type of the plot, should be one of 'candle','ohlc','line','renko','pnf','hollow_and_filled'. Default to 'candle'"] = "candle",
    style: Annotated[str, "Style of the plot, should be one of 'default','classic','charles','yahoo','nightclouds','sas','blueskies','mike'. Default to 'default'."] = "default",
    mav: Annotated[int, "Moving average window(s) to plot on the chart. Default to None."] = None,
    show_nontrading: Annotated[bool, "Whether to show non-trading days on the chart. Default to False."] = False,
) -> str:
    """Plot a stock price chart using mplfinance for the specified stock and time period."""
    return MplFinanceUtils.plot_stock_price_chart(
        ticker_symbol, start_date, end_date, save_path, verbose, type, style, mav, show_nontrading
    )

@server.tool()
def check_text_length_tool(
    text_file_path: Annotated[str, "path to the text file to check the length"],
) -> str:
    """Check the length of the text"""
    from functional import TextUtils
    return TextUtils.check_text_length(get_file_resource(text_file_path))

@server.resource("report://files")
def get_available_files() -> str:
    """Get a list of available files"""
    files = []
    report_path = os.path.join(os.getcwd(), "report")
    for file in os.listdir(report_path):
        file_path = os.path.join(report_path, file)
        if os.path.isfile(file_path):
            if os.path.exists(file_path):
                files.append(file)
    return files

@server.resource("report://{file}")
def get_file_resource(file: Annotated[str, "filename of the file to get"]) -> str:
    """Get a file resource"""
    file_name = file.lower()
    file_path = os.path.join(os.getcwd(), "report", file_name)

    if not os.path.exists(file_path):
        return f"File {file} not found"
    
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file {file}: {e}"

@server.prompt()
def generate_expert_investor_prompt(
    ticker_symbol: Annotated[str, "ticker symbol"],
    competitors: Annotated[str, "ticker symbols of competitors of the company"],
    company: Annotated[str, "company name"],
    fyear: Annotated[str, "fiscal year of the 10-K report"],
    work_dir: Annotated[str, "directory to save the annual report pdf"],
) -> str:
    """Generate an expert investor prompt"""
    return dedent(
        f"""
        With the tools you've been provided, write an annual report based on {ticker_symbol}'s and {competitors}'s {fyear} 10-K report, and format it into a PDF.

        Please follow these instructions carefully:

        1. **Explain your working plan** before you begin any analysis.
        2. **Use tools one by one** for clarity, especially when requesting instructions or data.
        3. **Perform all file operations** within the directory "{work_dir}".
        4. **Display any generated image** in the chat as soon as it is created.
        5. **Competitors analysis:**
           - Strictly follow my prompt.
           - Use only data from the financial metrics table.
           - Do not repeat or reuse similar sentences from other sections; delete any such sentences.
           - Classify each statement into the appropriate section.
           - The final sentence must discuss how {company}'s performance over these years and across these metrics might justify or contradict its current market valuation (as reflected in the EV/EBITDA ratio).
        6. **Paragraph length requirements:**
           - Each paragraph on the first page (business overview, market position, and operating results) should be between 150 and 160 words.
           - Each paragraph on the second page (risk assessment and competitors analysis) should be between 500 and 600 words.
           - Before passing the file path to the tool that builds the annual report, you should check the text length of the file content and if it exceeds the maximum length, you should summarize the file content, save the summary to a new file, and pass the new file path to the tool.
           - Do not generate the PDF until all these requirements are explicitly fulfilled.
        7. **Prompt length requirements:**
           - Clear the past chat history in the prompt when you finish the annual report for one ticker symbol and start a new one.
        """
    )

if __name__ == "__main__":
    from utils import register_keys_from_json
    register_keys_from_json("./config_api_keys")

    # Run the server with stdio transport
    server.run(transport="stdio") # add a newline
