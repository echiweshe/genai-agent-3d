"""
Redis-based LLM Service Integration

This module provides integration with the project's Redis-based LLM service.
It acts as a wrapper around the LLMServiceManager to maintain API compatibility
with other integrations.
"""

import logging
import os
import sys
import importlib.util
from typing import Optional, Dict, Any, List
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class RedisLLMServiceWrapper:
    """
    Wrapper for the project's Redis-based LLM service.
    Maintains API compatibility with other integrations.
    """
    # Define a custom timeout error to avoid conflicts
    class ServiceTimeoutError(Exception):
        """Custom timeout error for Redis LLM service."""
    
    def __init__(self):
        """Initialize the wrapper for the Redis LLM service."""
        self.llm_service = None
        self.available_providers = []
        self._initialize_llm_service()
    
    def _initialize_llm_service(self):
        """Initialize the LLM service from the main project."""
        try:
            # Try to import the LLM service manager
            from genai_agent.services.llm_service_manager import LLMServiceManager
            
            # Get the singleton instance
            self.llm_service = LLMServiceManager.get_instance()
            logger.info("Successfully imported project LLM service manager")
            
            # Set flag for initialized state
            self.initialized = True
            
            # Populate available providers (this will be updated async)
            self.available_providers = ["service-claude", "service-openai", "service-ollama"]
            
        except (ImportError, ModuleNotFoundError) as e:
            logger.error(f"Failed to import main project LLM service: {str(e)}")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Redis LLM service: {str(e)}")
            self.initialized = False
    
    async def initialize(self):
        """Initialize the service manager if not already initialized."""
        if not self.initialized or not self.llm_service:
            self._initialize_llm_service()
        
        if self.initialized and self.llm_service:
            try:
                # Initialize the service manager if it has an initialize method
                if hasattr(self.llm_service, 'initialize'):
                    await self.llm_service.initialize()
                
                # Try to get available providers
                if hasattr(self.llm_service, 'get_available_providers'):
                    providers = await self.llm_service.get_available_providers()
                    self.available_providers = [f"service-{p['id']}" for p in providers]
                    logger.info(f"Available Redis LLM providers: {self.available_providers}")
            except Exception as e:
                logger.error(f"Error during Redis LLM service initialization: {str(e)}")
    
    async def generate_text(
        self, 
        prompt: str, 
        provider: str = None, 
        temperature: float = 0.7,
        timeout: int = 120,
        **kwargs
    ) -> str:
        """
        Generate text using the Redis LLM service.
        
        Args:
            prompt: The prompt to send
            provider: Provider to use (format: "service-<provider>")
            temperature: Temperature for generation
            timeout: Request timeout in seconds
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        if not self.initialized or not self.llm_service:
            await self.initialize()
            if not self.initialized or not self.llm_service:
                raise RuntimeError("Redis LLM service is not available")
        
        # Extract the actual provider name (remove "service-" prefix)
        actual_provider = None
        if provider and provider.startswith("service-"):
            actual_provider = provider[8:]  # Remove "service-" prefix
        
        # Prepare parameters
        parameters = {
            "temperature": temperature,
            **kwargs
        }
        
        try:
            # Use the request method to send the prompt
            response = await self.llm_service.request(
                prompt=prompt,
                provider=actual_provider,
                parameters=parameters,
                timeout=timeout
            )
            
            # Check for errors
            if "error" in response:
                raise RuntimeError(f"Error from LLM service: {response['error']}")
            
            # Return the text content
            return response.get("text", "")
        
        except Exception as e:
            logger.error(f"Error generating text with Redis LLM service: {str(e)}")
            raise
    
    def get_available_providers(self) -> List[str]:
        """
        Get a list of available providers.
        
        Returns:
            List of provider names with "service-" prefix
        """
        return self.available_providers
    
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a provider is available.
        
        Args:
            provider: Provider name to check (with "service-" prefix)
            
        Returns:
            True if available, False otherwise
        """
        return provider in self.available_providers
    
    async def close(self):
        """Close the LLM service connection."""
        if self.initialized and self.llm_service and hasattr(self.llm_service, 'close'):
            await self.llm_service.close()


# Singleton instance
_instance = None

def get_redis_llm_service() -> RedisLLMServiceWrapper:
    """
    Get the singleton instance of the Redis LLM service wrapper.
    
    Returns:
        Redis LLM service wrapper instance
    """
    global _instance
    if _instance is None:
        _instance = RedisLLMServiceWrapper()
    return _instance
