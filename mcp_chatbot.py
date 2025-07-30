import asyncio
import json
import warnings

from contextlib import AsyncExitStack

from dotenv import load_dotenv
from anthropic import Anthropic

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

import nest_asyncio
import os
import sys

# Suppress the async generator warning
warnings.filterwarnings("ignore", message=".*async generator ignored GeneratorExit.*")

nest_asyncio.apply()

load_dotenv()

class MCP_ChatBot:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        # Use OpenAI's ChatGPT 4o mini model via openai.AsyncOpenAI
        # import openai
        # self.openai_client = openai.OpenAI()
        # Tools list required for Anthropic API
        self.available_tools = []
        # Prompts list for quick display 
        self.available_prompts = []
        # Sessions dict maps tool/prompt names or resource URIs to MCP client sessions
        self.sessions = {}

    async def connect_to_stdio_server(self, server_name, server_config):
        """Connect to a stdio-based MCP server."""
        print(f"Connecting to stdio server {server_name}")
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            await self._setup_session(session, server_name)
                
        except Exception as e:
            print(f"Error connecting to stdio server {server_name}: {e}")

    async def connect_to_http_server(self, server_name, server_config):
        """Connect to an HTTP-based MCP server with streaming support."""
        print(f"Connecting to HTTP server {server_name}")
        session = None
        try:
            print(f"[DEBUG] Attempting to connect to HTTP server at {server_config['url']}", file=sys.stderr)
            read, write, get_session_id_callback = await self.exit_stack.enter_async_context(
                streamablehttp_client(server_config["url"])
            )
            print(f"[DEBUG] HTTP connection established to {server_config['url']}", file=sys.stderr)
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            print(f"[DEBUG] ClientSession created for HTTP server {server_name}", file=sys.stderr)
            await session.initialize()
            print(f"[DEBUG] Session initialized for HTTP server {server_name}", file=sys.stderr)
            await self._setup_session(session, server_name)
            print(f"[DEBUG] Session setup complete for HTTP server {server_name}", file=sys.stderr)

        except Exception as e:
            print(f"Error connecting to HTTP server {server_name}: {e}")

    async def _setup_session(self, session, server_name):
        """Setup session by discovering available tools, prompts, and resources."""
        print(f"Setting up session for {server_name}")
        try:
            # List available tools
            response = await session.list_tools()
            for tool in response.tools:
                self.sessions[tool.name] = session
                self.available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
        
            # List available prompts
            prompts_response = await session.list_prompts()
            if prompts_response and prompts_response.prompts:
                for prompt in prompts_response.prompts:
                    self.sessions[prompt.name] = session
                    self.available_prompts.append({
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": prompt.arguments
                    })
            # List available resources
            resources_response = await session.list_resources()
            if resources_response and resources_response.resources:
                for resource in resources_response.resources:
                    resource_uri = str(resource.uri)
                    self.sessions[resource_uri] = session
            # Dynamically add all files under report folder as resources
            for file in os.listdir("report"):
                self.sessions[f"report://{file}"] = session
        
        except Exception as e:
            print(f"Warning: Error setting up session {server_name}: {e}")

    async def connect_to_servers(self):
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            
            # Connect to stdio servers
            stdio_servers = data.get("mcpServers", {})
            for server_name, server_config in stdio_servers.items():
                await self.connect_to_stdio_server(server_name, server_config)
            
            # Connect to HTTP servers
            http_servers = data.get("mcpHttpServers", {})
            for server_name, server_config in http_servers.items():
                await self.connect_to_http_server(server_name, server_config)
                
        except Exception as e:
            print(f"Error loading server config: {e}")
            raise
    
    async def process_query(self, query):
        messages = [{'role':'user', 'content':query}]
        # next_token_count = self.anthropic.count_tokens(messages)
        # print(f"Token count: {prev_token_count}")
        
        while True:
            print(f"Processing query with messages: {messages}")
            try:
                response = self.anthropic.messages.create(
                    max_tokens = 4096,  # Increased token limit
                    model = 'claude-3-7-sonnet-20250219', 
                    tools = self.available_tools,
                    messages = messages
                )
                print(f"Response received with {len(response.content)} content items")
            except Exception as e:
                print(f"API Error: {e}")
                return
            # prev_token_count = next_token_count
            
            assistant_content = []
            has_tool_use = False
            
            for content in response.content:
                print(f"Processing content type: {content.type}")
                if content.type == 'text':
                    print(f"Text response: {content.text[:100]}...")  # Show first 100 chars
                    assistant_content.append(content)
                elif content.type == 'tool_use':
                    has_tool_use = True
                    assistant_content.append(content)
                    messages.append({'role':'assistant', 'content':assistant_content})
                    
                    print(f"Tool use detected: {content.name}")
                    # Get session and call tool
                    session = self.sessions.get(content.name)
                    if not session:
                        print(f"Tool '{content.name}' not found in sessions: {list(self.sessions.keys())}")
                        break
                        
                    try:
                        result = await session.call_tool(content.name, arguments=content.input)
                        print(f"Tool result received: {len(str(result.content))} chars")
                        messages.append({
                            "role": "user", 
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": result.content
                                }
                            ]
                        })
                    except Exception as e:
                        print(f"Tool call error: {e}")
                        break
                    # next_token_count += self.anthropic.count_tokens(messages)
                    # print(f"Token count: {next_token_count}")
            
            # Exit loop if no tool was used
            if not has_tool_use:
                print("No tool use detected, exiting loop")
                break

            print("Continuing with next iteration...")
            # await asyncio.sleep(10)

    async def get_resource(self, resource_uri):
        session = self.sessions.get(resource_uri)
        
        if not session:
            print(f"Resource '{resource_uri}' not found.")
            return
        
        try:
            result = await session.read_resource(uri=resource_uri)
            if result and result.contents:
                print(f"\nResource: {resource_uri}")
                print("Content:")
                print(result.contents[0].text)
            else:
                print("No content available.")
        except Exception as e:
            print(f"Error: {e}")
    
    async def list_prompts(self):
        """List all available prompts."""
        if not self.available_prompts:
            print("No prompts available.")
            return
        
        print("\nAvailable prompts:")
        for prompt in self.available_prompts:
            print(f"- {prompt['name']}: {prompt['description']}")
            if prompt['arguments']:
                print(f"  Arguments:")
                for arg in prompt['arguments']:
                    arg_name = arg.name if hasattr(arg, 'name') else arg.get('name', '')
                    print(f"    - {arg_name}")
    
    async def execute_prompt(self, prompt_name, args):
        """Execute a prompt with the given arguments."""
        print(f"Executing prompt: {prompt_name} with args: {args}")
        session = self.sessions.get(prompt_name)
        if not session:
            print(f"Prompt '{prompt_name}' not found in sessions: {list(self.sessions.keys())}")
            return
        
        try:
            print(f"Calling get_prompt for {prompt_name}...")
            result = await session.get_prompt(prompt_name, arguments=args)
            print(f"Prompt result received: {result}")
            
            if result and result.messages:
                prompt_content = result.messages[0].content
                print(f"Prompt content type: {type(prompt_content)}")
                
                # Extract text from content (handles different formats)
                if isinstance(prompt_content, str):
                    text = prompt_content
                elif hasattr(prompt_content, 'text'):
                    text = prompt_content.text
                else:
                    # Handle list of content items
                    text = " ".join(item.text if hasattr(item, 'text') else str(item) 
                                  for item in prompt_content)
                
                print(f"Extracted text length: {len(text)}")
                print(f"Text preview: {text[:200]}...")
                
                print(f"\nExecuting prompt '{prompt_name}'...")
                await self.process_query(text)
            else:
                print("No messages in prompt result")
        except Exception as e:
            print(f"Error executing prompt: {e}")
            import traceback
            traceback.print_exc()
    
    async def chat_loop(self):
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        print("Use @reports to see available reports")
        print("Use @<report> to search report in that name")
        print("Use /prompts to list available prompts")
        print("Use /prompt <name> <arg1=value1> to execute a prompt")
        print("Use /servers to list connected servers")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                if not query:
                    continue
        
                if query.lower() == 'quit':
                    break
                
                # Check for @resource syntax first
                if query.startswith('@'):
                    # Remove @ sign  
                    filename = query[1:]
                    if filename == "reports":
                        resource_uri = "report://files"
                    else:
                        resource_uri = f"report://{filename}"
                    await self.get_resource(resource_uri)
                    continue
                
                # Check for /command syntax
                if query.startswith('/'):
                    parts = query.split()
                    command = parts[0].lower()
                    
                    if command == '/prompts':
                        await self.list_prompts()
                    elif command == '/servers':
                        await self.list_servers()
                    elif command == '/prompt':
                        if len(parts) < 2:
                            print("Usage: /prompt <name> <arg1=value1> <arg2=value2>")
                            continue
                        
                        prompt_name = parts[1]
                        args = {}
                        
                        # Parse arguments
                        for arg in parts[2:]:
                            if '=' in arg:
                                key, value = arg.split('=', 1)
                                args[key] = value
                        
                        await self.execute_prompt(prompt_name, args)
                    else:
                        print(f"Unknown command: {command}")
                    continue
                
                await self.process_query(query)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def list_servers(self):
        """List all connected servers and their types."""
        if not self.sessions:
            print("No servers connected.")
            return
        
        print("\nConnected servers:")
        # Group sessions by server type (we can't easily determine this from sessions alone)
        # But we can show available tools and resources
        unique_sessions = set(self.sessions.values())
        for i, session in enumerate(unique_sessions, 1):
            print(f"Server {i}: {type(session).__name__}")
        
        print(f"\nAvailable tools: {len(self.available_tools)}")
        print(f"Available prompts: {len(self.available_prompts)}")
        print(f"Available resources: {len([k for k in self.sessions.keys() if k.startswith('report://')])}")

    async def cleanup(self):
        """Clean up all sessions and connections."""
        try:
            # Close the exit stack
            await self.exit_stack.aclose()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")


async def main():
    chatbot = MCP_ChatBot()
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
