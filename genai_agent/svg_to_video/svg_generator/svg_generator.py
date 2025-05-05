"""
SVG Generator Component (Enhanced Version)

This module handles SVG generation using multiple LLM integration methods:
1. Direct LangChain integrations with Claude, OpenAI, Ollama
2. Direct Claude API integration without LangChain
3. Redis-based LLM service from the main project

It provides functionality to prompt LLMs to create SVG diagrams
based on text descriptions.
"""

import re
import logging
import asyncio
import os
import uuid
import sys
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

# Try to load environment variables from the master .env file
try:
    from dotenv import load_dotenv
    # Try the master .env first
    master_env_path = Path(__file__).parent.parent.parent.parent / "genai_agent_project" / ".env"
    if master_env_path.exists():
        load_dotenv(dotenv_path=master_env_path)
        logging.info(f"Loaded environment variables from {master_env_path}")
    # Fall back to the local .env if needed
    else:
        local_env_path = Path(__file__).parent.parent.parent.parent / ".env"
        if local_env_path.exists():
            load_dotenv(dotenv_path=local_env_path)
            logging.info(f"Loaded environment variables from {local_env_path}")
except ImportError:
    logging.warning("dotenv package not installed, skipping .env file loading")

# Import our LLM factory
from ..llm_integrations import get_llm_factory

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class SVGGenerator:
    """Generate SVG diagrams using multiple LLM integration methods."""
    
    def __init__(self, debug=False):
        """
        Initialize the SVG Generator.
        
        Args:
            debug: Whether to enable debug logging
        """
        self.debug = debug
        
        # Get the LLM factory
        self.llm_factory = get_llm_factory()
        
        # Determine output directory
        self.output_dir = os.environ.get("SVG_OUTPUT_DIR", "output/svg")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Templates for SVG generation
        self._initialize_templates()
        
        # Initialize available providers from the factory
        self._available_providers = []
        
        if self.debug:
            logger.info("SVG Generator initialized")
    
    async def initialize(self):
        """Initialize the SVG generator and its dependencies."""
        # Initialize the LLM factory
        await self.llm_factory.initialize()
        
        # Get available providers
        providers = self.llm_factory.get_providers()
        self._available_providers = [p["id"] for p in providers]
        
        if self.debug:
            logger.info(f"SVG Generator initialized with providers: {self._available_providers}")
    
    def _initialize_templates(self):
        """Initialize prompt templates for SVG generation."""
        # Base template for SVG generation
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
        
        # Template for flowchart diagrams
        self.flowchart_template = """
        Create a flowchart diagram in SVG format that represents the following process:
        
        {concept}
        
        Requirements:
        - Use standard SVG elements (rect, circle, path, text, etc.)
        - Use rectangles for process steps, diamonds for decision points
        - Connect elements with arrows showing the flow direction
        - Include appropriate colors and styling
        - Ensure the diagram is clear and readable
        - Add proper text labels for each step
        - Use viewBox="0 0 800 600" for dimensions
        - Wrap the entire SVG in <svg> tags
        - Do not include any explanation, just the SVG code
        
        SVG Diagram:
        """
        
        # Template for network diagrams
        self.network_template = """
        Create a network diagram in SVG format that represents the following system:
        
        {concept}
        
        Requirements:
        - Use standard SVG elements (rect, circle, path, text, etc.)
        - Use circles or icons for nodes/devices
        - Use lines or paths for connections between nodes
        - Include appropriate colors and styling
        - Ensure the diagram is clear and readable
        - Add proper text labels for each component
        - Use viewBox="0 0 800 600" for dimensions
        - Wrap the entire SVG in <svg> tags
        - Do not include any explanation, just the SVG code
        
        SVG Diagram:
        """
    
    async def generate_svg(
        self, 
        concept: str, 
        provider: str = None, 
        diagram_type: str = None, 
        max_retries: int = 2,
        temperature: float = 0.4
    ) -> str:
        """
        Generate an SVG diagram based on a concept description.
        
        Args:
            concept: Text description of the diagram to generate
            provider: LLM provider to use
            diagram_type: Type of diagram to generate (flowchart, network, etc.)
            max_retries: Maximum number of retry attempts
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            SVG content as a string
            
        Raises:
            ValueError: If no providers are available
            RuntimeError: If SVG generation fails after retries
        """
        # Initialize if not already initialized
        if not self._available_providers:
            await self.initialize()
        
        if not self._available_providers:
            raise ValueError("No LLM providers available. Please check LLM service configuration.")
        
        # If provider not specified or not available, use the first available
        if not provider or provider not in self._available_providers:
            provider = self._available_providers[0]
            if self.debug:
                logger.info(f"Using provider {provider}")
        
        # Try to generate with retries
        for attempt in range(max_retries + 1):
            try:
                if self.debug:
                    logger.info(f"Generating SVG, attempt {attempt+1}/{max_retries+1}")
                
                # Use the LLM factory to generate the SVG
                svg_content = await self.llm_factory.generate_svg(
                    provider=provider,
                    concept=concept,
                    style=diagram_type,
                    temperature=temperature
                )
                
                # Extract SVG content if needed
                if svg_content:
                    processed_svg = self._extract_svg(svg_content)
                    if processed_svg:
                        return processed_svg
                
                if attempt < max_retries:
                    logger.warning(f"Invalid SVG response, retrying ({attempt+1}/{max_retries})")
                    continue
                raise ValueError("Generated content is not valid SVG")
                
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"SVG generation error, retrying ({attempt+1}/{max_retries}): {str(e)}")
                    await asyncio.sleep(1)  # Add a small delay before retrying
                    continue
                raise RuntimeError(f"Failed to generate SVG: {str(e)}")
        
        raise RuntimeError("Failed to generate valid SVG after multiple attempts")
    
    def _extract_svg(self, text: str) -> Optional[str]:
        """
        Extract SVG content from the response text.
        
        Args:
            text: Response text from LLM
            
        Returns:
            SVG content or None if not found
        """
        # Check for SVG tags
        if "<svg" in text and "</svg>" in text:
            # Extract just the SVG tags
            svg_match = re.search(r'(<svg.*?</svg>)', text, re.DOTALL)
            if svg_match:
                return svg_match.group(1)
            return text
        
        return None
    
    def _get_prompt_for_diagram_type(self, concept: str, diagram_type: str = None) -> str:
        """
        Get the appropriate prompt for the diagram type.
        
        Args:
            concept: Text description of the diagram
            diagram_type: Type of diagram (flowchart, network, sequence, etc.)
            
        Returns:
            Formatted prompt
        """
        if not diagram_type:
            return self.svg_prompt_template.format(concept=concept)
        
        # Use specialized templates for different diagram types
        diagram_type = diagram_type.lower()
        if diagram_type == "flowchart":
            return self.flowchart_template.format(concept=concept)
        elif diagram_type == "network":
            return self.network_template.format(concept=concept)
        else:
            # For any other diagram type, use the base template
            return self.svg_prompt_template.format(concept=concept)
    
    def save_svg(self, svg_content: str, filename: str = None) -> str:
        """
        Save SVG content to a file.
        
        Args:
            svg_content: SVG content to save
            filename: Optional filename to use (generates UUID if not provided)
            
        Returns:
            Path to the saved SVG file
        """
        try:
            if not filename:
                filename = f"{str(uuid.uuid4())}.svg"
            
            # Ensure filename has .svg extension
            if not filename.lower().endswith('.svg'):
                filename += '.svg'
            
            # Create full path
            output_path = os.path.join(self.output_dir, filename)
            
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write SVG content
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            logger.info(f"SVG saved to {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error saving SVG: {str(e)}")
            raise
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of provider names
        """
        return self._available_providers
    
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a specific provider is available.
        
        Args:
            provider: Provider name to check
            
        Returns:
            True if provider is available, False otherwise
        """
        return provider in self._available_providers
