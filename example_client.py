"""
Example client for the LLM MCP Server
"""
import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

class MCPClient:
    """Simple MCP client for testing the LLM server"""
    
    def __init__(self, server_script: str = "mcp_server.py"):
        self.server_script = server_script
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process"""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server"""
        if not self.process:
            raise RuntimeError("Server not started")
        
        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        return json.loads(response_line.decode().strip())
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP connection"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "example-client",
                    "version": "1.0.0"
                }
            }
        }
        return await self.send_request(request)
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        return await self.send_request(request)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        return await self.send_request(request)
    
    async def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

async def demo_financial_advisor():
    """Demonstrate the server as a financial advisor"""
    print("=== Financial Advisor Demo ===")
    
    client = MCPClient()
    await client.start_server()
    
    try:
        # Initialize
        await client.initialize()
        
        # Update role to financial advisor
        await client.call_tool("update_role", {
            "system_prompt": """You are an expert financial advisor with 20 years of experience. 
            You provide sound financial advice, analyze market trends, and help clients make informed 
            investment decisions. Always consider risk tolerance and financial goals in your recommendations. 
            Be professional, thorough, and always mention the importance of diversification."""
        })
        
        # Ask for financial advice
        response = await client.call_tool("generate_text", {
            "prompt": "I'm 30 years old and want to start investing. I have $10,000 to invest and moderate risk tolerance. What should I do?"
        })
        
        print("Financial Advice:")
        print(response.get("result", {}).get("content", [{}])[0].get("text", "No response"))
        
    finally:
        await client.stop_server()

async def demo_code_assistant():
    """Demonstrate the server as a code assistant"""
    print("\n=== Code Assistant Demo ===")
    
    client = MCPClient()
    await client.start_server()
    
    try:
        # Initialize
        await client.initialize()
        
        # Update role to code assistant
        await client.call_tool("update_role", {
            "system_prompt": """You are a senior software engineer and coding expert. 
            You write clean, efficient, and well-documented code. You can work with multiple 
            programming languages and frameworks. Always explain your reasoning and suggest best practices. 
            Include comments in your code and explain the logic behind your solutions."""
        })
        
        # Ask for coding help
        response = await client.call_tool("generate_text", {
            "prompt": "Write a Python function to find the longest common subsequence between two strings. Include detailed comments explaining the algorithm."
        })
        
        print("Code Solution:")
        print(response.get("result", {}).get("content", [{}])[0].get("text", "No response"))
        
    finally:
        await client.stop_server()

async def demo_creative_writer():
    """Demonstrate the server as a creative writer"""
    print("\n=== Creative Writer Demo ===")
    
    client = MCPClient()
    await client.start_server()
    
    try:
        # Initialize
        await client.initialize()
        
        # Update role to creative writer
        await client.call_tool("update_role", {
            "system_prompt": """You are a creative writer and storyteller. 
            You craft engaging narratives, develop compelling characters, and create vivid descriptions. 
            You can write in various genres and styles, always maintaining creativity and originality. 
            Your writing should be evocative and emotionally resonant."""
        })
        
        # Ask for creative writing
        response = await client.call_tool("generate_text", {
            "prompt": "Write a short story (about 200 words) about a mysterious package that arrives at someone's doorstep. Make it suspenseful and engaging."
        })
        
        print("Creative Story:")
        print(response.get("result", {}).get("content", [{}])[0].get("text", "No response"))
        
    finally:
        await client.stop_server()

async def demo_chat_conversation():
    """Demonstrate chat conversation with role switching"""
    print("\n=== Chat Conversation Demo ===")
    
    client = MCPClient()
    await client.start_server()
    
    try:
        # Initialize
        await client.initialize()
        
        # Start as a general assistant
        await client.call_tool("update_role", {
            "system_prompt": "You are a helpful and knowledgeable assistant. You can adapt to different roles and provide expert advice in various domains."
        })
        
        # Start conversation
        response = await client.call_tool("chat", {
            "message": "Hello! I need help with multiple things today. First, can you explain what machine learning is?"
        })
        print("Assistant:", response.get("result", {}).get("content", [{}])[0].get("text", "No response"))
        
        # Switch to coding expert
        await client.call_tool("update_role", {
            "system_prompt": "You are now a coding expert. Provide technical programming advice and code examples."
        })
        
        response = await client.call_tool("chat", {
            "message": "Now I need help with Python. How do I create a virtual environment?"
        })
        print("Coding Expert:", response.get("result", {}).get("content", [{}])[0].get("text", "No response"))
        
        # Switch to writing coach
        await client.call_tool("update_role", {
            "system_prompt": "You are now a writing coach. Help with writing techniques, style, and creative expression."
        })
        
        response = await client.call_tool("chat", {
            "message": "Finally, I'm writing a blog post about AI. Any tips for making it engaging?"
        })
        print("Writing Coach:", response.get("result", {}).get("content", [{}])[0].get("text", "No response"))
        
    finally:
        await client.stop_server()

async def main():
    """Run all demos"""
    print("LLM MCP Server Demo")
    print("=" * 50)
    
    # Run different role demonstrations
    await demo_financial_advisor()
    await demo_code_assistant()
    await demo_creative_writer()
    await demo_chat_conversation()
    
    print("\n" + "=" * 50)
    print("Demo completed!")

if __name__ == "__main__":
    asyncio.run(main()) 