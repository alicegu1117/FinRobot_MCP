# MCP Server with LLM Capabilities

A Model Context Protocol (MCP) server that provides LLM capabilities with configurable role-based prompts. This server can be integrated with any MCP-compatible client to add AI-powered text generation and conversation capabilities.

## Features

- **Multi-LLM Support**: Supports OpenAI and Anthropic providers
- **Role-Based Configuration**: Configure the AI's role and behavior through system prompts
- **Conversation History**: Maintains conversation context for chat interactions
- **Dynamic Role Updates**: Update the AI's role on-the-fly
- **MCP Standard Compliance**: Full compliance with MCP protocol

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd FinRobot_MCP
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env_example.txt .env
# Edit .env with your configuration
```

## Configuration

### Environment Variables

Copy `env_example.txt` to `.env` and configure the following variables:

#### LLM Configuration
- `LLM_PROVIDER`: LLM provider (`openai` or `anthropic`)
- `LLM_API_KEY`: Your API key for the chosen provider
- `LLM_MODEL`: Model name (e.g., `gpt-4`, `claude-3-sonnet`)
- `LLM_TEMPERATURE`: Generation temperature (0.0-1.0)
- `LLM_MAX_TOKENS`: Maximum tokens to generate

#### MCP Server Configuration
- `MCP_SERVER_NAME`: Name of the MCP server
- `MCP_SERVER_VERSION`: Server version
- `MCP_DESCRIPTION`: Server description

#### Role Configuration
- `ROLE_SYSTEM_PROMPT`: System prompt defining the AI's role
- `ROLE_USER_PROMPT_TEMPLATE`: Template for formatting user inputs
- `ROLE_CONTEXT_WINDOW`: Context window size

### Example Role Configurations

#### Financial Advisor
```
ROLE_SYSTEM_PROMPT=You are an expert financial advisor with 20 years of experience. You provide sound financial advice, analyze market trends, and help clients make informed investment decisions. Always consider risk tolerance and financial goals in your recommendations.
```

#### Code Assistant
```
ROLE_SYSTEM_PROMPT=You are a senior software engineer and coding expert. You write clean, efficient, and well-documented code. You can work with multiple programming languages and frameworks. Always explain your reasoning and suggest best practices.
```

#### Creative Writer
```
ROLE_SYSTEM_PROMPT=You are a creative writer and storyteller. You craft engaging narratives, develop compelling characters, and create vivid descriptions. You can write in various genres and styles, always maintaining creativity and originality.
```

## Usage

### Running the Server

```bash
python mcp_server.py
```

The server will start and listen for MCP client connections via stdio.

### Available Tools

The server provides three main tools:

#### 1. `generate_text`
Generate text using the configured LLM with role-based prompts.

**Parameters:**
- `prompt` (required): The user prompt to generate text from
- `temperature` (optional): Temperature for generation (0.0-1.0)
- `max_tokens` (optional): Maximum tokens to generate

#### 2. `chat`
Have a conversation with the LLM using role-based prompts.

**Parameters:**
- `message` (required): The user message
- `reset_conversation` (optional): Reset conversation history

#### 3. `update_role`
Update the system prompt/role configuration.

**Parameters:**
- `system_prompt` (required): New system prompt defining the role
- `user_prompt_template` (optional): Template for user prompts

### Example MCP Client Usage

```python
# Example of how an MCP client might use this server
import asyncio
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client

async def example_usage():
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools.tools])
            
            # Generate text
            result = await session.call_tool("generate_text", {
                "prompt": "Explain quantum computing in simple terms"
            })
            print("Generated text:", result.content[0].text)
            
            # Start a chat
            result = await session.call_tool("chat", {
                "message": "Hello! Can you help me with a coding problem?"
            })
            print("Chat response:", result.content[0].text)
            
            # Update role
            result = await session.call_tool("update_role", {
                "system_prompt": "You are now a cybersecurity expert."
            })
            print("Role update:", result.content[0].text)

# Run the example
asyncio.run(example_usage())
```

## Integration with MCP Clients

This server can be integrated with any MCP-compatible client, including:

- **Claude Desktop**: Add the server to your MCP configuration
- **Custom MCP Clients**: Use the standard MCP protocol
- **Development Tools**: Integrate with IDEs and development environments

### Claude Desktop Integration

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "llm-server": {
      "command": "python",
      "args": ["/path/to/your/mcp_server.py"],
      "env": {
        "LLM_PROVIDER": "openai",
        "LLM_API_KEY": "your-api-key",
        "LLM_MODEL": "gpt-4",
        "ROLE_SYSTEM_PROMPT": "You are a helpful AI assistant."
      }
    }
  }
}
```

## Architecture

The server is built with a modular architecture:

- **`config.py`**: Configuration management using Pydantic
- **`llm_provider.py`**: Abstract LLM provider interface with OpenAI and Anthropic implementations
- **`mcp_server.py`**: Main MCP server implementation
- **Role Management**: Dynamic role configuration through system prompts

## Error Handling

The server includes comprehensive error handling:

- API errors from LLM providers
- Invalid tool calls
- Configuration errors
- Network connectivity issues

All errors are returned as structured error responses to the MCP client.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the documentation
2. Review the example configurations
3. Open an issue on GitHub

## Roadmap

- [ ] Support for more LLM providers (Google, Azure, etc.)
- [ ] Streaming responses
- [ ] File upload/download capabilities
- [ ] Advanced conversation management
- [ ] Plugin system for custom tools
- [ ] Web interface for configuration 