"""
SVG Generator Component

This module handles SVG generation using LangChain with various LLM providers.
It provides functionality to prompt models like Claude, OpenAI, or Ollama to
create SVG diagrams based on text descriptions.
"""

import re
import logging
import asyncio
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

# Try to load environment variables from the master .env file
try:
    from dotenv import load_dotenv
    # Try the master .env first
    master_env_path = Path(__file__).parent.parent.parent / "genai_agent_project" / ".env"
    if master_env_path.exists():
        load_dotenv(dotenv_path=master_env_path)
        logging.info(f"Loaded environment variables from {master_env_path}")
    # Fall back to the local .env if needed
    else:
        local_env_path = Path(__file__).parent.parent.parent / ".env"
        if local_env_path.exists():
            load_dotenv(dotenv_path=local_env_path)
            logging.info(f"Loaded environment variables from {local_env_path}")
except ImportError:
    logging.warning("dotenv package not installed, skipping .env file loading")

# Assuming these imports are available in your environment
from langchain.schema import HumanMessage
from langchain.chat_models import ChatOpenAI

# Try to import ChatAnthropic, but handle it carefully
try:
    from langchain.chat_models import ChatAnthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

# Try to import ChatOllama, but don't fail if not available
try:
    from langchain.chat_models import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

# Manually fix the proxies issue for Claude API
try:
    if CLAUDE_AVAILABLE:
        import inspect
        from langchain.chat_models.anthropic import ChatAnthropic as OriginalChatAnthropic
        
        # Get the original signature
        orig_sig = inspect.signature(OriginalChatAnthropic.__init__)
        params = list(orig_sig.parameters.values())
        
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

class SVGGenerator:
    """Generate SVG diagrams using LangChain and various LLM providers."""
    
    def __init__(self):
        """Initialize the SVG Generator with available LLM providers."""
        # Initialize LLM providers
        self.providers = {}
        self._initialize_providers()
        
        # Base prompts for SVG generation
        self.svg_prompt_template = """
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
        
        SVG Diagram:
        """
    
    def _initialize_providers(self):
        """Initialize LLM providers based on available API keys."""
        try:
            # OpenAI
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key:
                try:
                    self.providers["openai"] = ChatOpenAI(
                        api_key=openai_api_key,
                        temperature=0.7
                    )
                    logger.info("Initialized OpenAI provider")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            
            # Anthropic/Claude
            if CLAUDE_AVAILABLE:
                anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
                if anthropic_api_key:
                    try:
                        # Direct initialization without proxies
                        kwargs = {
                            "temperature": 0.7
                        }
                        
                        # Try with anthropic_api_key parameter first
                        try:
                            self.providers["claude"] = ChatAnthropic(
                                anthropic_api_key=anthropic_api_key,
                                **kwargs
                            )
                            logger.info("Initialized Claude provider with anthropic_api_key")
                        except (TypeError, ValueError):
                            # If that fails, try with api_key
                            try:
                                self.providers["claude"] = ChatAnthropic(
                                    api_key=anthropic_api_key,
                                    **kwargs
                                )
                                logger.info("Initialized Claude provider with api_key")
                            except Exception as e:
                                # Last resort: custom monkey-patched direct creation
                                from anthropic import Anthropic
                                from langchain.chat_models.anthropic import ChatAnthropic
                                
                                # Direct initialization without LangChain's wrapper
                                anthropic_client = Anthropic(api_key=anthropic_api_key)
                                
                                # Create ChatAnthropic with the client
                                chat_model = ChatAnthropic(client=anthropic_client, temperature=0.7)
                                self.providers["claude"] = chat_model
                                logger.info("Initialized Claude provider with direct client")
                    except Exception as e:
                        logger.error(f"Failed to initialize Claude provider: {str(e)}")
            
            # Ollama (local models) - only try if the import succeeded
            if OLLAMA_AVAILABLE:
                try:
                    import requests
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        self.providers["ollama"] = ChatOllama(model="llama3")
                        logger.info("Initialized Ollama provider")
                except Exception as e:
                    logger.warning(f"Ollama initialization failed: {str(e)}")
                
            if not self.providers:
                logger.warning("No LLM providers initialized! Please check API keys.")
                logger.warning(f"ANTHROPIC_API_KEY: {'Set' if os.environ.get('ANTHROPIC_API_KEY') else 'Not set'}")
                logger.warning(f"OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
                
        except Exception as e:
            logger.error(f"Error initializing LLM providers: {str(e)}")
    
    async def generate_svg(self, concept: str, provider: str = "claude", max_retries: int = 2) -> str:
        """
        Generate an SVG diagram based on a concept description.
        
        Args:
            concept: Text description of the diagram to generate
            provider: LLM provider to use (claude, openai, ollama)
            max_retries: Maximum number of retry attempts
            
        Returns:
            SVG content as a string
            
        Raises:
            ValueError: If the provider is not available
            RuntimeError: If SVG generation fails after retries
        """
        if provider not in self.providers:
            available_providers = list(self.providers.keys())
            if not available_providers:
                raise ValueError("No LLM providers available. Please check API keys.")
            
            # Default to first available provider
            provider = available_providers[0]
            logger.warning(f"Requested provider not available, using {provider} instead")
        
        llm = self.providers[provider]
        prompt = self.svg_prompt_template.format(concept=concept)
        
        # Try to generate with retries
        for attempt in range(max_retries + 1):
            try:
                messages = [HumanMessage(content=prompt)]
                response = await llm.agenerate([messages])
                
                # Extract SVG content
                svg_text = response.generations[0][0].text
                
                # Validate it's proper SVG
                if "<svg" in svg_text and "</svg>" in svg_text:
                    # Extract just the SVG tags
                    svg_match = re.search(r'(<svg.*?</svg>)', svg_text, re.DOTALL)
                    if svg_match:
                        return svg_match.group(1)
                    return svg_text
                else:
                    if attempt < max_retries:
                        logger.warning(f"Invalid SVG response, retrying ({attempt+1}/{max_retries})")
                        continue
                    raise ValueError("Generated content is not valid SVG")
                
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"SVG generation error, retrying ({attempt+1}/{max_retries}): {str(e)}")
                    continue
                raise RuntimeError(f"Failed to generate SVG: {str(e)}")
        
        raise RuntimeError("Failed to generate valid SVG after multiple attempts")
    
    def save_svg(self, svg_content: str, output_path: str) -> str:
        """
        Save SVG content to a file.
        
        Args:
            svg_content: SVG content to save
            output_path: Path to save the SVG file
            
        Returns:
            Path to the saved SVG file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            logger.info(f"SVG saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving SVG to {output_path}: {str(e)}")
            raise

    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
