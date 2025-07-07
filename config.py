"""
Configuration module for MCP LLM Server
"""
import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """Configuration for LLM providers"""
    provider: str = Field(default="openai", description="LLM provider (openai, anthropic, etc.)")
    api_key: Optional[str] = Field(default=None, description="API key for the LLM provider")
    model: str = Field(default="gpt-4", description="Model name to use")
    temperature: float = Field(default=0.7, description="Temperature for generation")
    max_tokens: int = Field(default=1000, description="Maximum tokens to generate")
    
    class Config:
        env_prefix = "LLM_"

class MCPConfig(BaseModel):
    """Configuration for MCP server"""
    server_name: str = Field(default="llm-mcp-server", description="Name of the MCP server")
    server_version: str = Field(default="1.0.0", description="Version of the MCP server")
    description: str = Field(default="MCP server with LLM capabilities", description="Server description")
    capabilities: Dict[str, Any] = Field(default_factory=dict, description="Server capabilities")
    
    class Config:
        env_prefix = "MCP_"

class RoleConfig(BaseModel):
    """Configuration for role-based prompts"""
    system_prompt: str = Field(description="System prompt defining the role")
    user_prompt_template: str = Field(default="{user_input}", description="Template for user prompts")
    context_window: int = Field(default=4000, description="Context window size")
    
    class Config:
        env_prefix = "ROLE_"

def load_config() -> tuple[MCPConfig, LLMConfig, RoleConfig]:
    """Load configuration from environment variables"""
    
    # Load LLM config
    llm_config = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        api_key=os.getenv("LLM_API_KEY"),
        model=os.getenv("LLM_MODEL", "gpt-4"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000"))
    )
    
    # Load MCP config
    mcp_config = MCPConfig(
        server_name=os.getenv("MCP_SERVER_NAME", "llm-mcp-server"),
        server_version=os.getenv("MCP_SERVER_VERSION", "1.0.0"),
        description=os.getenv("MCP_DESCRIPTION", "MCP server with LLM capabilities"),
        capabilities={
            "tools": {
                "listTools": {},
                "callTool": {}
            }
        }
    )
    
    # Load role config
    role_config = RoleConfig(
        system_prompt=os.getenv("ROLE_SYSTEM_PROMPT", "You are a helpful AI assistant."),
        user_prompt_template=os.getenv("ROLE_USER_PROMPT_TEMPLATE", "{user_input}"),
        context_window=int(os.getenv("ROLE_CONTEXT_WINDOW", "4000"))
    )
    
    return mcp_config, llm_config, role_config 