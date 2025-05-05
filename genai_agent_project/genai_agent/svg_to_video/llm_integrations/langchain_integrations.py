"""
LangChain-based LLM Integrations

This module provides direct integration with various LLM providers through LangChain.
Supports Claude, OpenAI, and Ollama models for SVG generation.
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    # Import LangChain components
    from langchain.schema import HumanMessage
    from langchain.chat_models import ChatOpenAI
    
    # Try to import ChatAnthropic
    try:
        from langchain.chat_models import ChatAnthropic
        CLAUDE_AVAILABLE = True
    except ImportError:
        CLAUDE_AVAILABLE = False
        logger.warning("Could not import ChatAnthropic. Claude integration will be unavailable.")
    
    # Try to import ChatOllama
    try:
        from langchain.chat_models import ChatOllama
        OLLAMA_AVAILABLE = True
    except ImportError:
        OLLAMA_AVAILABLE = False
        logger.warning("Could not import ChatOllama. Ollama integration will be unavailable.")
        
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available. Direct LLM integration will not work.")

# Anthropic API patch to fix issues with proxies
if LANGCHAIN_AVAILABLE and CLAUDE_AVAILABLE:
    try:
        import inspect
        from langchain.chat_models.anthropic import ChatAnthropic as OriginalChatAnthropic
        
        # Get the original signature
        orig_sig = inspect.signature(OriginalChatAnthropic.__init__)
        
        # Check if 'proxies' is in the default parameters
        has_proxies = 'proxies' in orig_sig.parameters
        
        if has_proxies:
            # Create a wrapper class that removes the proxies parameter
            class FixedChatAnthropic(OriginalChatAnthropic):
                def __init__(self, **kwargs):
                    # Remove proxies from kwargs if present
                    if 'proxies' in kwargs:
                        del kwargs['proxies']
                    super().__init__(**kwargs)
            
            # Replace the original with the fixed version
            from langchain.chat_models import anthropic
            anthropic.ChatAnthropic = FixedChatAnthropic
            ChatAnthropic = FixedChatAnthropic
            logger.info("Applied fix for proxies parameter in ChatAnthropic")
    except Exception as e:
        logger.warning(f"Failed to apply Claude API fix: {str(e)}")


class LangChainLLMService:
    """
    LangChain-based LLM service for direct integration with providers.
    """
    
    def __init__(self):
        """Initialize the LLM service with available providers."""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not available. Please install it with 'pip install langchain'")
        
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers."""
        try:
            # OpenAI
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key:
                try:
                    self.providers["openai"] = ChatOpenAI(
                        api_key=openai_api_key,
                        temperature=0.7,
                        model_name="gpt-4"
                    )
                    logger.info("Initialized OpenAI provider with GPT-4")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            
            # Anthropic/Claude
            if CLAUDE_AVAILABLE:
                anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
                if anthropic_api_key:
                    try:
                        # Try multiple approaches to create Claude integration
                        
                        # Approach 1: direct initialization with anthropic_api_key
                        try:
                            self.providers["claude"] = ChatAnthropic(
                                anthropic_api_key=anthropic_api_key,
                                temperature=0.7,
                                model="claude-3-7-sonnet-20250219"  # Use latest model
                            )
                            logger.info("Initialized Claude provider with anthropic_api_key")
                        except (TypeError, ValueError) as e:
                            logger.warning(f"Failed to initialize Claude with anthropic_api_key: {str(e)}")
                            
                            # Approach 2: try with api_key
                            try:
                                self.providers["claude"] = ChatAnthropic(
                                    api_key=anthropic_api_key,
                                    temperature=0.7,
                                    model="claude-3-7-sonnet-20250219"
                                )
                                logger.info("Initialized Claude provider with api_key")
                            except Exception as e:
                                logger.warning(f"Failed to initialize Claude with api_key: {str(e)}")
                                
                                # Approach 3: try with direct client creation
                                try:
                                    from anthropic import Anthropic
                                    
                                    # Direct initialization with Anthropic client
                                    anthropic_client = Anthropic(api_key=anthropic_api_key)
                                    
                                    # Create ChatAnthropic with the client
                                    self.providers["claude"] = ChatAnthropic(
                                        client=anthropic_client, 
                                        temperature=0.7,
                                        model="claude-3-7-sonnet-20250219"
                                    )
                                    logger.info("Initialized Claude provider with direct client")
                                except Exception as e:
                                    logger.error(f"All Claude initialization methods failed: {str(e)}")
                    except Exception as e:
                        logger.error(f"Failed to initialize Claude provider: {str(e)}")
            
            # Ollama (local models)
            if OLLAMA_AVAILABLE:
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        self.providers["ollama"] = ChatOllama(model="llama3")
                        logger.info("Initialized Ollama provider with Llama 3")
                except Exception as e:
                    logger.warning(f"Ollama initialization failed: {str(e)}")
            
            # Log status of provider initialization
            if not self.providers:
                logger.warning("No LLM providers initialized! Please check API keys.")
                logger.warning(f"ANTHROPIC_API_KEY: {'Set' if os.environ.get('ANTHROPIC_API_KEY') else 'Not set'}")
                logger.warning(f"OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
            else:
                logger.info(f"Initialized providers: {', '.join(self.providers.keys())}")
                
        except Exception as e:
            logger.error(f"Error initializing LLM providers: {str(e)}")
    
    async def generate_text(
        self, 
        prompt: str, 
        provider: str = None, 
        temperature: float = 0.7, 
        max_retries: int = 2
    ) -> str:
        """
        Generate text using the specified LLM provider.
        
        Args:
            prompt: The prompt to send to the LLM
            provider: The LLM provider to use
            temperature: Temperature for generation (0.0 to 1.0)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated text as a string
            
        Raises:
            ValueError: If no providers are available
            RuntimeError: If generation fails after retries
        """
        # Check if we have any providers
        if not self.providers:
            raise ValueError("No LLM providers available. Please check API keys.")
        
        # If provider not specified or not available, use the first available
        if not provider or provider not in self.providers:
            available_providers = list(self.providers.keys())
            provider = available_providers[0]
            logger.warning(f"Requested provider not available, using {provider} instead")
        
        llm = self.providers[provider]
        
        # Set the temperature if different from default
        if temperature != 0.7:
            if hasattr(llm, "temperature"):
                original_temperature = llm.temperature
                llm.temperature = temperature
            else:
                logger.warning(f"Provider {provider} does not support setting temperature at runtime")
        
        # Try to generate with retries
        for attempt in range(max_retries + 1):
            try:
                # Create message from prompt
                messages = [HumanMessage(content=prompt)]
                
                # Generate response
                response = await llm.agenerate([messages])
                
                # Extract and return the text content
                return response.generations[0][0].text
                
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Generation error, retrying ({attempt+1}/{max_retries}): {str(e)}")
                    await asyncio.sleep(1)  # Add a small delay before retrying
                    continue
                raise RuntimeError(f"Failed to generate text: {str(e)}")
        
        # Reset temperature if we changed it
        if temperature != 0.7 and hasattr(llm, "temperature"):
            llm.temperature = original_temperature
    
    def get_available_providers(self) -> List[str]:
        """
        Get a list of available providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a provider is available.
        
        Args:
            provider: Provider name to check
            
        Returns:
            True if available, False otherwise
        """
        return provider in self.providers


# Singleton instance for easy access
_instance = None

def get_langchain_llm_service() -> LangChainLLMService:
    """
    Get the singleton instance of the LangChain LLM service.
    
    Returns:
        LangChain LLM service instance
    """
    global _instance
    if _instance is None:
        try:
            _instance = LangChainLLMService()
        except ImportError:
            logger.error("Failed to create LangChain LLM service due to missing dependencies")
            return None
    return _instance
