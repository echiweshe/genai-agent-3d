#!/usr/bin/env python
"""
SVG to 3D Conversion Script

This script demonstrates the use of the SVG to 3D converter module.
It can be called from the command line to convert an SVG file to a 3D model.
"""

import os
import sys
import argparse
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add the project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the SVG to 3D converter
try:
    from genai_agent.svg_to_video.svg_to_3d.svg_to_3d_converter_new import SVGTo3DConverter
    from genai_agent.svg_to_video.svg_to_3d.svg_utils import log
except ImportError:
    print("Error: Could not import SVG to 3D converter. Make sure the project is properly installed.")
    sys.exit(1)

async def convert_svg_to_3d(svg_path, output_path, extrude_depth=0.1, scale_factor=0.01, debug=False):
    """
    Convert an SVG file to a 3D model.
    
    Args:
        svg_path: Path to the SVG file
        output_path: Path to save the 3D model
        extrude_depth: Depth of extrusion
        scale_factor: Scale factor
        debug: Enable debug output
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        converter = SVGTo3DConverter(extrude_depth=extrude_depth, scale_factor=scale_factor, debug=debug)
        result = await converter.convert_svg_to_3d(svg_path, output_path)
        return result
    except Exception as e:
        logger.error(f"Error in SVG to 3D conversion: {e}", exc_info=True)
        return False

async def main():
    """
    Main entry point for the script.
    Parses command line arguments and runs the conversion.
    """
    parser = argparse.ArgumentParser(description='Convert an SVG file to a 3D model.')
    parser.add_argument('svg_path', help='Path to the SVG file')
    parser.add_argument('output_path', help='Path to save the 3D model')
    parser.add_argument('--extrude_depth', type=float, default=0.1, help='Depth of extrusion')
    parser.add_argument('--scale_factor', type=float, default=0.01, help='Scale factor')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Verify input file exists
    if not os.path.exists(args.svg_path):
        print(f"Error: SVG file '{args.svg_path}' does not exist.")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    log(f"Converting SVG {args.svg_path} to 3D model {args.output_path}")
    log(f"Parameters: extrude_depth={args.extrude_depth}, scale_factor={args.scale_factor}, debug={args.debug}")
    
    result = await convert_svg_to_3d(
        args.svg_path,
        args.output_path,
        args.extrude_depth,
        args.scale_factor,
        args.debug
    )
    
    if result:
        log("Conversion completed successfully.")
        return 0
    else:
        log("Conversion failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
