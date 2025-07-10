"""
Expert Investor MCP Server using FastMCP
This shows how the expert investor would look with FastMCP and its limitations
"""
import os
import requests
from typing import Annotated
from mcp.types import Tool

from mcp.server.fastmcp import FastMCP

# Create FastMCP server
server = FastMCP("expert-investor", port=8001)

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


if __name__ == "__main__":
    from utils import register_keys_from_json
    register_keys_from_json("./config_api_keys")

    # Run the server
    server.run(transport="streamable-http") 