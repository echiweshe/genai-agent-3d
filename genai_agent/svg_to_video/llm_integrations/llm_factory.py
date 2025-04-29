"""
LLM Factory for SVG Generation

This module provides a factory pattern for creating and managing LLM integrations
for SVG generation without using LangChain.
"""

import logging
import os
from typing import Dict, Any, List, Optional

from .claude_direct import ClaudeDirectSVGGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class LLMFactory:
    """A factory class for creating and managing LLM integrations."""
    
    def __init__(self):
        """Initialize the LLM factory."""
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers based on environment variables."""
        # Check for Anthropic/Claude
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                self.providers["claude"] = {
                    "name": "Claude",
                    "description": "Anthropic's Claude API for high-quality SVG generation",
                    "available": True,
                    "models": ClaudeDirectSVGGenerator().get_available_models()
                }
                logger.info("Claude provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude provider: {e}")
                self.providers["claude"] = {
                    "name": "Claude",
                    "description": "Anthropic's Claude API for high-quality SVG generation",
                    "available": False,
                    "error": str(e)
                }
        else:
            logger.warning("ANTHROPIC_API_KEY not found, Claude provider unavailable")
            self.providers["claude"] = {
                "name": "Claude",
                "description": "Anthropic's Claude API for high-quality SVG generation",
                "available": False,
                "error": "API key not found"
            }
        
        # TODO: Add more providers as needed (OpenAI, Ollama, etc.)
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available LLM providers.
        
        Returns:
            A list of dictionaries containing provider information
        """
        return [
            {"id": provider_id, **info}
            for provider_id, info in self.providers.items()
        ]
    
    def create_generator(self, provider: str, model: Optional[str] = None) -> Any:
        """
        Create an SVG generator for the specified provider and model.
        
        Args:
            provider: The LLM provider ID
            model: Optional model ID for the provider
            
        Returns:
            An SVG generator instance
            
        Raises:
            ValueError: If the provider is not available or invalid
        """
        provider_info = self.providers.get(provider)
        if not provider_info:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not provider_info.get("available", False):
            error = provider_info.get("error", "Provider not available")
            raise ValueError(f"Provider {provider} is not available: {error}")
        
        if provider == "claude":
            generator = ClaudeDirectSVGGenerator()
            if model:
                generator.set_model(model)
            return generator
        
        # Add other providers as needed
        
        raise ValueError(f"Provider implementation not found for {provider}")
    
    def generate_svg(self, provider: str, concept: str, model: Optional[str] = None, style: Optional[str] = None) -> str:
        """
        Generate an SVG using the specified provider and model.
        
        Args:
            provider: The LLM provider ID
            concept: The concept to visualize
            model: Optional model ID for the provider
            style: Optional style guidelines
            
        Returns:
            The generated SVG as a string
        """
        generator = self.create_generator(provider, model)
        return generator.generate_svg(concept, style)


# Example usage
if __name__ == "__main__":
    factory = LLMFactory()
    
    # List available providers
    providers = factory.get_providers()
    for provider in providers:
        print(f"Provider: {provider['name']}")
        print(f"Available: {provider['available']}")
        if provider['available']:
            print("Models:")
            for model in provider.get('models', []):
                print(f"  - {model['name']}: {model['description']}")
        print()
    
    # Generate SVG if Claude is available
    if any(p['id'] == 'claude' and p['available'] for p in providers):
        concept = "A flowchart showing the process of user authentication"
        svg = factory.generate_svg("claude", concept)
        with open("claude_output.svg", "w", encoding="utf-8") as f:
            f.write(svg)
        print("SVG generated and saved to claude_output.svg")
