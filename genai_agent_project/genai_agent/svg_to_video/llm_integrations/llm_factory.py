"""
LLM Factory for SVG Generation

This module provides a simplified factory pattern for creating and managing LLM integrations.
"""

import os
import logging
import asyncio
import json
import aiohttp
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class LLMFactory:
    """
    Factory class for managing LLM integrations for SVG generation.
    """
    
    def __init__(self):
        """
        Initialize the LLM factory.
        """
        self.providers = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize the factory and discover available providers."""
        if self.initialized:
            return
        
        # Add a mock Claude Direct provider for demonstration
        self.providers["claude-direct"] = {
            "id": "claude-direct",
            "name": "Claude Direct",
            "description": "Direct integration with Anthropic's Claude API",
            "available": True,
            "integration_type": "direct"
        }
        
        # Add a mock OpenAI provider for demonstration
        self.providers["openai"] = {
            "id": "openai",
            "name": "OpenAI",
            "description": "Integration with OpenAI's API",
            "available": True,
            "integration_type": "direct"
        }
        
        # Mark as initialized
        self.initialized = True
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
        # Ensure factory is initialized
        if not self.initialized:
            await self.initialize()
        
        # Check if provider exists
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
        
        # For demo purposes, generate a simple SVG
        if style == "flowchart":
            # Generate a simple flowchart SVG
            svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect x="50" y="50" width="150" height="80" rx="10" ry="10" fill="#90caf9" stroke="#1976d2" stroke-width="2"/>
  <text x="125" y="95" text-anchor="middle" font-family="Arial" font-size="16" fill="#000">Start</text>
  
  <rect x="325" y="200" width="150" height="80" rx="10" ry="10" fill="#a5d6a7" stroke="#388e3c" stroke-width="2"/>
  <text x="400" y="245" text-anchor="middle" font-family="Arial" font-size="16" fill="#000">Process</text>
  
  <rect x="600" y="350" width="150" height="80" rx="10" ry="10" fill="#ef9a9a" stroke="#c62828" stroke-width="2"/>
  <text x="675" y="395" text-anchor="middle" font-family="Arial" font-size="16" fill="#000">End</text>
  
  <path d="M125 130 L125 180 L325 180 L325 200" fill="none" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  <path d="M400 280 L400 330 L600 330 L600 350" fill="none" stroke="#000" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#000"/>
    </marker>
  </defs>
</svg>"""
        elif style == "network":
            # Generate a simple network diagram SVG
            svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <circle cx="400" cy="300" r="50" fill="#ffcc80" stroke="#ef6c00" stroke-width="2"/>
  <text x="400" y="305" text-anchor="middle" font-family="Arial" font-size="16" fill="#000">Server</text>
  
  <circle cx="200" cy="150" r="40" fill="#b39ddb" stroke="#512da8" stroke-width="2"/>
  <text x="200" y="155" text-anchor="middle" font-family="Arial" font-size="14" fill="#000">Client 1</text>
  
  <circle cx="200" cy="450" r="40" fill="#b39ddb" stroke="#512da8" stroke-width="2"/>
  <text x="200" y="455" text-anchor="middle" font-family="Arial" font-size="14" fill="#000">Client 2</text>
  
  <circle cx="600" cy="150" r="40" fill="#b39ddb" stroke="#512da8" stroke-width="2"/>
  <text x="600" y="155" text-anchor="middle" font-family="Arial" font-size="14" fill="#000">Client 3</text>
  
  <circle cx="600" cy="450" r="40" fill="#b39ddb" stroke="#512da8" stroke-width="2"/>
  <text x="600" y="455" text-anchor="middle" font-family="Arial" font-size="14" fill="#000">Client 4</text>
  
  <line x1="230" y1="180" x2="370" y2="270" stroke="#000" stroke-width="2"/>
  <line x1="230" y1="420" x2="370" y2="330" stroke="#000" stroke-width="2"/>
  <line x1="570" y1="180" x2="430" y2="270" stroke="#000" stroke-width="2"/>
  <line x1="570" y1="420" x2="430" y2="330" stroke="#000" stroke-width="2"/>
</svg>"""
        else:
            # Generate a generic diagram
            svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect x="100" y="100" width="600" height="400" fill="#f5f5f5" stroke="#9e9e9e" stroke-width="2"/>
  <text x="400" y="300" text-anchor="middle" font-family="Arial" font-size="24" fill="#000">Example Diagram</text>
  <text x="400" y="350" text-anchor="middle" font-family="Arial" font-size="16" fill="#757575">Generated by SVG to Video Pipeline</text>
</svg>"""
        
        # Simulate generation delay
        await asyncio.sleep(2)
        
        return svg_content

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
        _instance = LLMFactory()
    return _instance
