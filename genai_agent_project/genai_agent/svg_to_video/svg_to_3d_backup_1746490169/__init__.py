"""
SVG to 3D conversion module.

This module provides functionality to convert SVG files to 3D models.
"""

import asyncio
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure the mathutils module is importable
try:
    import mathutils
    logger.info("Successfully imported mathutils module")
except ImportError:
    logger.warning("Failed to import mathutils module, using stub implementation")
    # Define the path to the stub mathutils module
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mathutils_stub_path = os.path.join(script_dir, "mathutils.py")
    
    if os.path.exists(mathutils_stub_path):
        # Add the directory to sys.path temporarily
        sys.path.insert(0, script_dir)
        try:
            import mathutils
            logger.info("Successfully imported mathutils stub module")
        except ImportError as e:
            logger.error(f"Failed to import mathutils stub module: {str(e)}")
        finally:
            # Remove the directory from sys.path
            if script_dir in sys.path:
                sys.path.remove(script_dir)
    else:
        logger.error("Mathutils stub module not found")

# Import functions and classes
from .svg_to_3d import (
    convert_svg_to_3d,
    get_supported_formats,
    get_conversion_options
)

# Create SVGTo3DConverter class
class SVGTo3DConverter:
    """Class for converting SVG files to 3D models."""
    
    def __init__(self, blender_path=None, debug=False, **kwargs):
        """Initialize the converter with a Blender path."""
        self.blender_path = blender_path
        self.debug = debug
    
    async def convert_svg_to_3d(self, svg_path, output_file=None, **kwargs):
        """Convert an SVG file to a 3D model asynchronously."""
        # Run the synchronous function in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: convert_svg_to_3d(svg_path, output_file, **kwargs)
        )
    
    def get_supported_formats(self):
        """Get a list of supported output formats."""
        return get_supported_formats()
    
    def get_conversion_options(self):
        """Get available conversion options."""
        return get_conversion_options()

__all__ = [
    'convert_svg_to_3d',
    'get_supported_formats',
    'get_conversion_options',
    'SVGTo3DConverter'
]
