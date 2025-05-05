"""
SVG to Video Pipeline Package

This package provides a modular pipeline for converting text descriptions to videos
via SVG diagrams and 3D models.
"""

import logging
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Try to import SVGGenerator which doesn't depend on Blender
from .svg_generator.svg_generator import SVGGenerator

# Try to import the full pipeline, but handle import errors gracefully
try:
    from .pipeline_integrated import SVGToVideoPipeline
except ImportError as e:
    logger.warning(f"Could not import SVGToVideoPipeline: {e}")
    logger.warning("Only SVG generation will be available (without 3D conversion or video rendering)")
    
    # Define a placeholder SVGToVideoPipeline for IDE completion
    class SVGToVideoPipeline:
        """Placeholder SVGToVideoPipeline class for when imports fail."""
        
        def __init__(self, *args, **kwargs):
            raise ImportError("SVGToVideoPipeline could not be imported. Please check the error logs.")

__all__ = ['SVGGenerator', 'SVGToVideoPipeline']
