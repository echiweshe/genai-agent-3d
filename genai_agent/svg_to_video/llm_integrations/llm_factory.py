"""
LLM Factory for SVG Generation

This module provides a factory pattern for creating and managing LLM integrations.
It supports multiple integration methods:
1. Direct LangChain integrations
2. Direct Claude API integration
3. Redis-based LLM service from the main project
"""

import os
import logging
import importlib.util
import asyncio
from typing import Dict, Any, List, Optional, Union

# Import integrations
from .claude_direct import get_claude_direct, ClaudeDirectSVGGenerator
from .redis_llm_service import get_redis_llm_service, RedisLLMServiceWrapper

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Try to import LangChain integration
try:
    from .langchain_integrations import get_langchain_llm_service, LangChainLLMService
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain integration not available")

class LLMFactory:
    """
    Factory class for managing LLM integrations for SVG generation.
    """
    
    def __init__(self, use_redis_service: bool = True, use_langchain: bool = True, use_direct_claude: bool = True):
        """
        Initialize the LLM factory.
        
        Args:
            use_redis_service: Whether to use the Redis-based LLM service
            use_langchain: Whether to use LangChain integrations
            use_direct_claude: Whether to use direct Claude API integration
        """
        self.providers = {}
        self.use_redis_service = use_redis_service
        self.use_langchain = use_langchain
        self.use_direct_claude = use_direct_claude
        
        # Initialize services
        self.redis_service = None
        self.langchain_service = None
        self.claude_direct = None
        
        # Initialize integrations based on settings
        self._initialize_integrations()
    
    async def initialize(self):
        """Initialize services that require async initialization."""
        if self.redis_service:
            await self.redis_service.initialize()
    
    def _initialize_integrations(self):
        """Initialize LLM integrations based on settings."""
        # Initialize Redis service
        if self.use_redis_service:
            try:
                self.redis_service = get_redis_llm_service()
                # Note: Actual provider list will be populated during async initialize
                for provider_id in ["service-claude", "service-openai", "service-ollama"]:
                    self.providers[provider_id] = {
                        "name": f"Service {provider_id.replace('service-', '').capitalize()}",
                        "description": f"Project's LLM service with {provider_id.replace('service-', '').capitalize()}",
                        "available": True,
                        "integration_type": "redis"
                    }
                logger.info("Redis LLM service integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis LLM service: {str(e)}")
        
        # Initialize LangChain integrations
        if self.use_langchain and LANGCHAIN_AVAILABLE:
            try:
                self.langchain_service = get_langchain_llm_service()
                if self.langchain_service:
                    # Get available providers
                    langchain_providers = self.langchain_service.get_available_providers()
                    for provider_id in langchain_providers:
                        self.providers[f"langchain-{provider_id}"] = {
                            "name": f"LangChain {provider_id.capitalize()}",
                            "description": f"LangChain integration with {provider_id.capitalize()}",
                            "available": True,
                            "integration_type": "langchain"
                        }
                    logger.info(f"LangChain integration initialized with providers: {langchain_providers}")
            except Exception as e:
                logger.error(f"Failed to initialize LangChain integration: {str(e)}")
        
        # Initialize direct Claude integration
        if self.use_direct_claude:
            try:
                self.claude_direct = get_claude_direct()
                if self.claude_direct:
                    # Add direct Claude provider
                    self.providers["claude-direct"] = {
                        "name": "Claude Direct",
                        "description": "Direct integration with Anthropic's Claude API",
                        "available": True,
                        "integration_type": "direct"
                    }
                    logger.info("Direct Claude integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize direct Claude integration: {str(e)}")
        
        # Log status
        logger.info(f"LLM Factory initialized with {len(self.providers)} providers")
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available LLM providers.
        
        Returns:
            A list of dictionaries containing provider information
        """
        # Create a list of provider information with ID included
        provider_list = [
            {"id": provider_id, **info}
            for provider_id, info in self.providers.items()
            if info.get("available", False)  # Only include available providers
        ]
        
        # Sort providers by name for consistent order
        provider_list.sort(key=lambda p: p.get("name", ""))
        
        return provider_list
    
    async def generate_svg(
        self, 
        provider: str, 
        concept: str, 
        style: Optional[str] = None, 
        temperature: float = 0.7
    ) -> str:
        """
        Generate an SVG diagram using the specified provider.
        
        Args:
            provider: Provider ID to use
            concept: The concept to visualize
            style: Optional style guidelines
            temperature: Temperature for generation
            
        Returns:
            The generated SVG content
            
        Raises:
            ValueError: If the provider is not available
        """
        provider_info = self.providers.get(provider)
        if not provider_info:
            available_providers = list(self.providers.keys())
            if not available_providers:
                raise ValueError("No LLM providers available")
            # Default to first available provider
            provider = available_providers[0]
            provider_info = self.providers[provider]
            logger.warning(f"Provider {provider} not found, using {provider} instead")
        
        if not provider_info.get("available", False):
            raise ValueError(f"Provider {provider} is not available")
        
        # Prepare prompt for SVG generation
        svg_prompt = f"""
Create an SVG diagram that represents the following concept:

{concept}

Requirements:
- Use standard SVG elements (rect, circle, path, text, etc.)
- Include appropriate colors and styling
- Ensure the diagram is clear and readable
- Add proper text labels
- Use viewBox="0 0 800 600" for dimensions
- Wrap the entire SVG in <svg> tags
- Do not include any explanation, just the SVG code

{f"Style guidelines: {style}" if style else ""}

SVG Diagram:
"""
        
        integration_type = provider_info.get("integration_type")
        
        try:
            # Handle different integration types
            if integration_type == "redis" and self.redis_service:
                response = await self.redis_service.generate_text(
                    prompt=svg_prompt,
                    provider=provider,
                    temperature=temperature
                )
                return response
            
            elif integration_type == "langchain" and self.langchain_service:
                # Extract the actual provider name (remove "langchain-" prefix)
                langchain_provider = provider.replace("langchain-", "")
                response = await self.langchain_service.generate_text(
                    prompt=svg_prompt,
                    provider=langchain_provider,
                    temperature=temperature
                )
                return response
            
            elif integration_type == "direct" and self.claude_direct:
                response = await self.claude_direct.generate_svg_async(
                    concept=concept,
                    style=style,
                    temperature=temperature
                )
                return response
            
            else:
                raise ValueError(f"Cannot handle provider {provider} with integration type {integration_type}")
            
        except Exception as e:
            logger.error(f"Error generating SVG with provider {provider}: {str(e)}")
            raise
    
    async def close(self):
        """Close all LLM service connections."""
        if self.redis_service:
            await self.redis_service.close()


# Singleton instance
_instance = None

def get_llm_factory() -> LLMFactory:
    """
    Get the singleton instance of the LLM factory.
    
    Returns:
        LLM factory instance
    """
    global _instance
    if _instance is None:
        _instance = LLMFactory(
            use_redis_service=True,
            use_langchain=True,
            use_direct_claude=True
        )
    return _instance
