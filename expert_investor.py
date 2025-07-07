"""
Expert Investor MCP Server using FastMCP
This shows how the expert investor would look with FastMCP and its limitations
"""
import asyncio
import os
from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP

from config import load_config
from llm_provider import create_llm_provider

# Create FastMCP server
server = FastMCP("expert-investor-mcp")

# Load configuration
mcp_config, llm_config, role_config = load_config()
llm_provider = create_llm_provider(llm_config)

# Note: We lose the detailed enum constraints and descriptions that were in the original
@server.tool()
async def analyze_investment(
    investment_type: Literal["stocks", "bonds", "real_estate", "crypto", "commodities", "etfs", "mutual_funds"],
    amount: float,
    time_horizon: Literal["short_term", "medium_term", "long_term"],
    risk_tolerance: Literal["conservative", "moderate", "aggressive"],
    additional_context: Optional[str] = None
) -> str:
    """Analyze an investment opportunity or strategy"""
    
    prompt = f"""Analyze this investment opportunity:
    
Investment Type: {investment_type}
Amount: ${amount:,.2f}
Time Horizon: {time_horizon}
Risk Tolerance: {risk_tolerance}
Additional Context: {additional_context or "None"}

Please provide a comprehensive analysis including:
1. Risk assessment
2. Potential returns and volatility
3. Suitability for the given parameters
4. Diversification considerations
5. Alternative recommendations
6. Key factors to monitor"""
    
    response = await llm_provider.generate(
        prompt,
        system_prompt=role_config.system_prompt
    )
    
    return response

@server.tool()
async def portfolio_review(
    portfolio_holdings: str,
    total_value: float,
    goals: str,
    time_horizon: Optional[str] = "long_term"
) -> str:
    """Review and analyze an investment portfolio"""
    
    prompt = f"""Review this investment portfolio:
    
Portfolio Holdings: {portfolio_holdings}
Total Value: ${total_value:,.2f}
Goals: {goals}
Time Horizon: {time_horizon}

Please provide a comprehensive portfolio review including:
1. Asset allocation analysis
2. Diversification assessment
3. Risk evaluation
4. Alignment with stated goals
5. Recommendations for optimization
6. Rebalancing suggestions"""
    
    response = await llm_provider.generate(
        prompt,
        system_prompt=role_config.system_prompt
    )
    
    return response

@server.tool()
async def market_analysis(
    market_sector: Literal["technology", "healthcare", "finance", "energy", "consumer", "real_estate", "general"],
    analysis_type: Literal["trends", "risks", "opportunities", "outlook", "comprehensive"],
    timeframe: Optional[Literal["short_term", "medium_term", "long_term"]] = "medium_term"
) -> str:
    """Provide market analysis and economic insights"""
    
    prompt = f"""Provide {analysis_type} analysis for the {market_sector} sector:
    
Sector: {market_sector}
Analysis Type: {analysis_type}
Timeframe: {timeframe}

Please provide:
1. Current market conditions
2. Key trends and drivers
3. Risk factors
4. Investment opportunities
5. Outlook for the specified timeframe
6. Considerations for investors"""
    
    response = await llm_provider.generate(
        prompt,
        system_prompt=role_config.system_prompt
    )
    
    return response

@server.tool()
async def financial_planning(
    age: int,
    income: float,
    goals: str,
    savings: Optional[float] = 0,
    debt: Optional[float] = 0
) -> str:
    """Provide financial planning advice"""
    
    prompt = f"""Provide financial planning advice:
    
Age: {age}
Annual Income: ${income:,.2f}
Current Savings: ${savings:,.2f}
Financial Goals: {goals}
Current Debt: ${debt:,.2f}

Please provide:
1. Financial health assessment
2. Goal prioritization
3. Savings and investment recommendations
4. Debt management strategies
5. Retirement planning considerations
6. Risk management recommendations
7. Action plan and timeline"""
    
    response = await llm_provider.generate(
        prompt,
        system_prompt=role_config.system_prompt
    )
    
    return response

@server.tool()
async def investment_education(
    topic: Literal["basics", "diversification", "risk_management", "asset_allocation", "tax_efficiency", "retirement_planning"],
    complexity: Optional[Literal["beginner", "intermediate", "advanced"]] = "intermediate"
) -> str:
    """Provide educational content about investing"""
    
    prompt = f"""Provide {complexity}-level education about {topic}:
    
Topic: {topic}
Complexity Level: {complexity}

Please provide:
1. Clear explanation of the concept
2. Practical examples
3. Common mistakes to avoid
4. Best practices
5. How it fits into overall investment strategy
6. Additional resources for learning"""
    
    response = await llm_provider.generate(
        prompt,
        system_prompt=role_config.system_prompt
    )
    
    return response

if __name__ == "__main__":
    # Run the server
    server.run() 