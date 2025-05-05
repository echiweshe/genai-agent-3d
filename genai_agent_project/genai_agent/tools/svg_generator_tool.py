"""
SVG Generator Tool

This module provides a tool for generating SVG diagrams using the SVG Generator component.
"""

import os
import sys
import uuid
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import SVG Generator
try:
    from genai_agent.svg_to_video.llm_integrations.llm_factory import get_llm_factory
    SVG_GENERATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"SVG Generator not available: {e}")
    SVG_GENERATOR_AVAILABLE = False

class SVGGeneratorTool:
    """Tool for generating SVG diagrams."""
    
    def __init__(self):
        """Initialize the SVG Generator Tool."""
        self.name = "svg_generator"
        self.description = "Generate SVG diagrams from natural language descriptions using LLMs"
        
        # Initialize LLM factory if available
        if SVG_GENERATOR_AVAILABLE:
            self.llm_factory = get_llm_factory()
            self.initialized = False
        else:
            self.llm_factory = None
            self.initialized = False
        
        # Define output directories
        self.output_dir = os.path.join(project_root, "output")
        self.svg_dir = os.path.join(self.output_dir, "svg")
        self.diagrams_dir = os.path.join(self.output_dir, "diagrams")
        
        # Ensure output directories exist
        os.makedirs(self.svg_dir, exist_ok=True)
        os.makedirs(self.diagrams_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize the LLM factory."""
        if SVG_GENERATOR_AVAILABLE and not self.initialized:
            try:
                await self.llm_factory.initialize()
                self.initialized = True
                return True
            except Exception as e:
                logger.error(f"Error initializing LLM factory: {e}")
                return False
        return self.initialized
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the SVG Generator tool.
        
        Args:
            parameters: A dictionary containing:
                - description: Text description of the diagram
                - diagram_type: Type of diagram (flowchart, network, etc.)
                - provider: LLM provider to use (optional)
                - name: Name for the diagram (optional)
        
        Returns:
            A dictionary containing the results of the operation.
        """
        if not SVG_GENERATOR_AVAILABLE:
            return {
                "status": "error",
                "error": "SVG Generator is not available. Check server logs for details."
            }
        
        try:
            # Initialize if not already initialized
            if not self.initialized:
                await self.initialize()
            
            # Extract parameters
            description = parameters.get("description")
            if not description:
                return {"status": "error", "error": "Description is required"}
            
            diagram_type = parameters.get("diagram_type", "flowchart")
            provider = parameters.get("provider")
            name = parameters.get("name")
            
            # Get available providers
            providers = self.llm_factory.get_providers()
            provider_ids = [p["id"] for p in providers]
            
            # If provider not specified or not available, use first available
            if not provider or provider not in provider_ids:
                if "claude-direct" in provider_ids:
                    provider = "claude-direct"
                elif provider_ids:
                    provider = provider_ids[0]
                else:
                    return {
                        "status": "error",
                        "error": "No LLM providers available for SVG generation."
                    }
            
            # Generate a unique ID and filename
            diagram_id = str(uuid.uuid4())
            
            # Generate a name if not provided
            if not name:
                name = f"Diagram-{diagram_id[:8]}"
            
            # Create filename
            filename = f"{name.replace(' ', '_')}.svg"
            
            # Define output paths - save to both svg and diagrams directories
            svg_path = os.path.join(self.svg_dir, filename)
            diagram_path = os.path.join(self.diagrams_dir, filename)
            
            # Generate SVG
            logger.info(f"Generating SVG with provider: {provider}, diagram type: {diagram_type}")
            svg_content = await self.llm_factory.generate_svg(
                provider=provider,
                concept=description,
                style=diagram_type,
                temperature=0.4
            )
            
            # Save SVG to both locations
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            with open(diagram_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            # Compute relative paths
            svg_rel_path = os.path.relpath(svg_path, self.output_dir)
            diagram_rel_path = os.path.relpath(diagram_path, self.output_dir)
            
            # Return success response
            return {
                "status": "success",
                "message": "SVG diagram generated successfully",
                "diagram_id": diagram_id,
                "name": name,
                "file_path": diagram_rel_path,
                "svg_path": svg_rel_path,
                "code": svg_content,
                "provider": provider,
                "diagram_type": diagram_type,
                "description": description
            }
        
        except Exception as e:
            logger.error(f"Error executing SVG Generator tool: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to generate SVG: {str(e)}"
            }
