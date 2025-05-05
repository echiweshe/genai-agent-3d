"""
SVG Generator Component (Integrated Version)

This module handles SVG generation using the project's EnhancedLLMService.
It provides functionality to prompt LLMs via Redis to create SVG diagrams
based on text descriptions.
"""

import re
import logging
import asyncio
import os
import uuid
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

# Import the LLM service
from genai_agent.services.llm.llm_service_manager import LLMServiceManager

logger = logging.getLogger(__name__)

class SVGGenerator:
    """Generate SVG diagrams using the project's EnhancedLLMService."""
    
    def __init__(self, debug=False):
        """Initialize the SVG Generator."""
        self.debug = debug
        
        # Initialize LLM service manager
        self.llm_service = LLMServiceManager.get_instance()
        
        # Determine output directory
        self.output_dir = os.environ.get("SVG_OUTPUT_DIR", "output/svg")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Template for SVG generation
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
        
        # Initialize available providers
        self._available_providers = self._get_available_providers()
        
        if self.debug:
            logger.info(f"SVG Generator initialized with providers: {self._available_providers}")
    
    def _get_available_providers(self) -> List[str]:
        """Get list of available LLM providers from the service."""
        try:
            # Check which providers are available through the LLM service
            providers = ["claude", "openai", "ollama"]
            available_providers = []
            
            for provider in providers:
                if self.llm_service.is_provider_available(provider):
                    available_providers.append(provider)
            
            return available_providers
        except Exception as e:
            logger.error(f"Error getting available providers: {str(e)}")
            return []
    
    async def generate_svg(self, concept: str, provider: str = None, diagram_type: str = None, max_retries: int = 2) -> str:
        """
        Generate an SVG diagram based on a concept description.
        
        Args:
            concept: Text description of the diagram to generate
            provider: LLM provider to use (claude, openai, ollama)
            diagram_type: Type of diagram to generate (optional)
            max_retries: Maximum number of retry attempts
            
        Returns:
            SVG content as a string
            
        Raises:
            ValueError: If no providers are available
            RuntimeError: If SVG generation fails after retries
        """
        if not self._available_providers:
            raise ValueError("No LLM providers available. Please check LLM service configuration.")
        
        # If provider not specified or not available, use the first available
        if not provider or provider not in self._available_providers:
            provider = self._available_providers[0]
            if self.debug:
                logger.info(f"Using provider {provider}")
        
        # Enhance the prompt based on diagram type if specified
        prompt = self._get_prompt_for_diagram_type(concept, diagram_type)
        
        # Try to generate with retries
        for attempt in range(max_retries + 1):
            try:
                if self.debug:
                    logger.info(f"Generating SVG, attempt {attempt+1}/{max_retries+1}")
                
                # Use the LLM service to generate the SVG
                response = await self.llm_service.generate_text(
                    prompt=prompt,
                    model=provider,
                    temperature=0.7,
                    timeout=120  # Longer timeout for SVG generation
                )
                
                # Extract SVG content
                if response:
                    svg_content = self._extract_svg(response)
                    if svg_content:
                        return svg_content
                
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
            text: Response text
            
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
        base_prompt = self.svg_prompt_template.format(concept=concept)
        
        if not diagram_type:
            return base_prompt
        
        # Enhanced prompts for specific diagram types
        if diagram_type.lower() == "flowchart":
            return f"""
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
        
        elif diagram_type.lower() == "network":
            return f"""
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
        
        # For any other diagram type, use the base prompt
        return base_prompt
    
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
