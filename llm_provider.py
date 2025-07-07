"""
LLM Provider module for MCP Server
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import openai
from anthropic import AsyncAnthropic
from config import LLMConfig

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from chat messages"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = openai.AsyncOpenAI(api_key=config.api_key)
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using OpenAI"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await self.chat(messages, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from chat messages"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = AsyncAnthropic(api_key=config.api_key)
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using Anthropic"""
        try:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                system=system_prompt or "You are a helpful AI assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from chat messages"""
        # Convert OpenAI format to Anthropic format
        system_prompt = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                user_messages.append(msg["content"])
            elif msg["role"] == "assistant":
                # For simplicity, we'll just use the last user message
                # In a full implementation, you'd want to handle conversation history
                pass
        
        if not user_messages:
            raise ValueError("No user messages found")
        
        return await self.generate(user_messages[-1], system_prompt, **kwargs)

def create_llm_provider(config: LLMConfig) -> LLMProvider:
    """Factory function to create LLM provider based on configuration"""
    if config.provider.lower() == "openai":
        return OpenAIProvider(config)
    elif config.provider.lower() == "anthropic":
        return AnthropicProvider(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}") 