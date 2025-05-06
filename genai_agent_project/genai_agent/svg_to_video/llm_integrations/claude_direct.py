"""
Claude Direct Integration for SVG Generation

This module provides a direct integration with the Anthropic Claude API
for generating SVG diagrams from text descriptions without LangChain dependency.
"""

import os
import requests
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ClaudeDirectSVGGenerator:
    """A class for generating SVG diagrams directly through Claude API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude Direct SVG Generator.
        
        Args:
            api_key: Anthropic API key. If not provided, will attempt to load from environment.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided and not found in environment")
        
        logger.info(f"Initialized Claude Direct SVG Generator with API key: {self.api_key[:8]}...")
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        # Use Claude 3.5 Sonnet for better SVG generation
        self.model = "claude-3-5-sonnet-20240620"  # Use Claude 3.5 Sonnet for high-quality SVGs
        
        # Verify API key is set
        if not self.api_key or len(self.api_key) < 10:
            logger.error("Invalid or missing Anthropic API key")
            raise ValueError("Invalid Anthropic API key. Please check your configuration.")
        
    def set_model(self, model_name: str) -> None:
        """
        Set the Claude model to use.
        
        Args:
            model_name: The model name (e.g., 'claude-3-opus-20240229', 'claude-3-sonnet-20240229')
        """
        self.model = model_name
        logger.info(f"Model set to: {model_name}")
    
    def generate_svg(self, concept: str, style: Optional[str] = None, temperature: float = 0.2) -> str:
        """
        Generate an SVG diagram from a text description.
        
        Args:
            concept: The concept to visualize as an SVG
            style: Optional style guideline for the SVG
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            The generated SVG as a string
        
        Raises:
            ValueError: If SVG generation fails or no valid SVG is returned
        """
        # Create the prompt with specific instructions
        prompt = self._create_svg_prompt(concept, style)
        
        # Call the Claude API
        response = self._call_claude_api(prompt, temperature)
        
        # Extract the SVG from the response
        # This will raise ValueError if no valid SVG is found
        svg = self._extract_svg(response)
        
        # Additional validation to ensure we have valid SVG
        if not svg or not svg.strip().startswith("<svg"):
            logger.error(f"Invalid SVG content returned: {svg[:100]}...")
            raise ValueError("Invalid SVG content returned from Claude API")
        
        return svg
    
    async def generate_svg_async(self, concept: str, style: Optional[str] = None, temperature: float = 0.2) -> str:
        """
        Generate an SVG diagram asynchronously.
        
        Args:
            concept: The concept to visualize as an SVG
            style: Optional style guideline for the SVG
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            The generated SVG as a string
        """
        # In real async implementation, we would use aiohttp here
        # For now, we'll just call the synchronous version
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.generate_svg(concept, style, temperature)
        )
    
    def _create_svg_prompt(self, concept: str, style: Optional[str] = None) -> str:
        """
        Create a more detailed prompt for Claude to generate better SVGs.
        
        Args:
            concept: The concept to visualize
            style: Optional style guideline
            
        Returns:
            A prompt string for Claude
        """
        # Determine specific diagram type based on style
        diagram_specific_instructions = ""
        if style and "flowchart" in style.lower():
            diagram_specific_instructions = """
- Create a professional-looking flowchart with proper flow direction (top-to-bottom or left-to-right)
- Use rectangles for processes, diamonds for decisions, oval/rounded rectangles for start/end
- Use consistent shape sizes and spacing for a clean appearance
- Connect shapes with arrows showing the process flow
- Use arrowheads to clearly indicate direction
- Add clear, concise labels to all components
- Group related elements visually
- Use a consistent color scheme with good contrast
- Include a title at the top of the diagram
            """
        elif style and "sequence" in style.lower():
            diagram_specific_instructions = """
- Create a sequence diagram with actor symbols at the top
- Use solid lines for synchronous calls, dashed for returns or async
- Include activation boxes to show when each actor is active
- Make the time flow from top to bottom
- Label all messages clearly with action verbs
- Use different colors for different actors/systems
- Include timestamps or sequence numbers if relevant
- Show clear relationships between components
            """
        elif style and "network" in style.lower():
            diagram_specific_instructions = """
- Create a comprehensive network diagram showing connected devices/components
- Use standard network icons or appropriate symbols for different device types
- Show proper network topology (star, mesh, bus, etc.)
- Indicate connection types with different line styles
- Label components with names, IP addresses, or identifiers
- Group components by network segment or function
- Use a logical layout that minimizes line crossings
- Include a legend for symbol types if necessary
            """
        elif style and "class" in style.lower() or "uml" in style.lower():
            diagram_specific_instructions = """
- Create a proper UML class diagram with class boxes
- Divide class boxes into three sections: name, attributes, methods
- Show relationships with proper UML notation (inheritance, composition, etc.)
- Use different arrow types for different relationships
- Include visibility modifiers (+, -, #) for attributes and methods
- Add multiplicity indicators where appropriate
- Group related classes visually
- Use a clean, professional layout
            """
        elif style and "entity" in style.lower() or "er" in style.lower():
            diagram_specific_instructions = """
- Create an entity-relationship diagram with entity boxes
- Show relationships between entities with proper notation
- Include cardinality/multiplicity (1-to-many, many-to-many, etc.)
- Add primary keys and foreign keys
- Use different colors or styles for different entity types
- Label all relationships clearly
- Arrange entities to minimize crossing lines
- Include attributes in each entity
            """
        elif style and "mindmap" in style.lower():
            diagram_specific_instructions = """
- Create a hierarchical mind map with a central concept
- Branch out related ideas in a radial pattern
- Use colors to distinguish different branches or levels
- Keep text concise and clear
- Use consistent shapes for items of the same hierarchy level
- Vary size to indicate importance or hierarchy
- Connect related concepts across branches if needed
- Create a visually balanced layout
            """
        
        base_prompt = f"""
I need you to create a detailed, professional-quality SVG diagram to visualize this concept:

{concept}

Requirements:
1. Generate ONLY valid SVG code - no explanations, markdown, or other content
2. Use viewBox="0 0 800 600" for dimensions
3. Create a sophisticated, visually appealing diagram that would look professional in a presentation
4. Use a subtle, professional color palette with good contrast
5. Include appropriate gradients, shadows, or effects for visual interest
6. Make all text readable and properly positioned
7. Use consistent styling for similar elements
8. Include clear labels for all important components
9. Use appropriate line weights and styles
10. Ensure the diagram has a logical layout and flow
11. Group related elements with <g> tags when appropriate
12. Use defs/symbols for repeated elements
13. Place elements at whole-pixel coordinates to avoid blurring
14. Add a title element and description for accessibility

{diagram_specific_instructions}

Your response should contain ONLY the raw SVG code without any additional text, code blocks, or explanations.
Make this a high-quality diagram that could be used in a professional presentation or documentation.
"""
        
        if style and not diagram_specific_instructions:
            base_prompt += f"\nAdditional style guidelines: {style}"
        
        logger.debug(f"Created detailed SVG prompt: {base_prompt[:200]}...")
        return base_prompt
    
    def _call_claude_api(self, prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Call the Claude API with the given prompt.
        
        Args:
            prompt: The prompt for Claude
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            The Claude API response as a dictionary
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 4000,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            logger.info(f"Calling Claude API with model: {self.model}")
            logger.info(f"Using API key: {self.api_key[:8]}...")
            start_time = time.time()
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            end_time = time.time()
            logger.info(f"Claude API call completed in {end_time - start_time:.2f} seconds")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Claude API: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise ValueError(f"Failed to generate SVG: {str(e)}")
    
    def _extract_svg(self, response: Dict[str, Any]) -> str:
        """
        Extract the SVG content from the Claude API response.
        
        Args:
            response: The Claude API response
            
        Returns:
            The extracted SVG content
        """
        try:
            # Get the content from the response
            content = response.get("content", [])
            if not content:
                raise ValueError("Empty response from Claude API")
            
            # Extract text from the content
            text = ""
            for item in content:
                if item.get("type") == "text":
                    text += item.get("text", "")
            
            logger.debug(f"Extracted text from Claude: {text[:100]}...")
            
            # Try to extract SVG using regex
            svg_match = re.search(r'<svg[^>]*>[\s\S]*<\/svg>', text)
            if svg_match:
                svg_content = svg_match.group(0)
                logger.info(f"Successfully extracted SVG: {len(svg_content)} chars")
                return svg_content
            
            # If no SVG pattern found, check if the text itself is an SVG
            if text.strip().startswith("<svg") and text.strip().endswith("</svg>"):
                logger.info(f"Found SVG in raw text response: {len(text.strip())} chars")
                return text.strip()
            
            # No fallback SVG - just raise error if no SVG content found
            logger.error("No SVG content found in Claude response.")
            logger.error(f"Response content (truncated): {text[:500]}...")
            raise ValueError("No SVG content found in Claude API response")
            
        except Exception as e:
            logger.error(f"Error extracting SVG: {e}")
            raise ValueError(f"Failed to extract SVG from response: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get a list of available Claude models for SVG generation.
        
        Returns:
            A list of dictionaries containing model information
        """
        return [
            {"id": "claude-3-5-sonnet-20240620", "name": "Claude-3.5 Sonnet", "description": "Best model for SVG diagrams with great quality and reasonable speed"},
            {"id": "claude-3-7-sonnet-20250219", "name": "Claude-3.7 Sonnet", "description": "Latest model with highest quality SVGs and reasoning capabilities"},
            {"id": "claude-3-opus-20240229", "name": "Claude-3 Opus", "description": "Highest quality SVGs with detailed elements"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude-3 Sonnet", "description": "Good balance of quality and speed"},
            {"id": "claude-3-haiku-20240307", "name": "Claude-3 Haiku", "description": "Fastest generation with simpler designs"}
        ]

# Singleton instance
_instance = None

def get_claude_direct() -> ClaudeDirectSVGGenerator:
    """
    Get the singleton instance of the Claude Direct SVG Generator.
    
    Returns:
        Claude Direct SVG Generator instance
    """
    global _instance
    if _instance is None:
        try:
            _instance = ClaudeDirectSVGGenerator()
        except ValueError as e:
            logger.error(f"Failed to create Claude Direct instance: {e}")
            return None
    return _instance
