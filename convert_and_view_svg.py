"""
SVG to 3D Conversion and Viewer

This script converts an SVG file to a 3D model and opens it in Blender.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_blender_executable():
    """Find the Blender executable path."""
    # Check environment variable first
    blender_path = os.environ.get("BLENDER_PATH")
    if blender_path and os.path.exists(blender_path):
        return blender_path
    
    # Default paths to check
    default_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        r"/usr/bin/blender",
        r"/Applications/Blender.app/Contents/MacOS/Blender"
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    return None

def convert_svg_to_3d(svg_path, debug=True):
    """
    Convert SVG to 3D model using the SVG to 3D converter.
    
    Args:
        svg_path: Path to the SVG file
        debug: Enable debug output
    
    Returns:
        Path to the output 3D model
    """
    logger.info(f"Converting SVG file: {svg_path}")
    
    try:
        # Add the project root to the Python path
        project_dir = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, project_dir)
        
        # Import the SVG to 3D converter
        from genai_agent_project.genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter
        
        # Create the converter
        converter = SVGTo3DConverter(debug=debug)
        
        # Convert the SVG to a 3D model
        output_file = converter.convert_svg_to_3d(svg_path)
        
        if output_file:
            logger.info(f"Conversion successful: {output_file}")
            return output_file
        else:
            logger.error("Conversion failed")
            return None
    
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return None

def open_in_blender(model_path):
    """
    Open a 3D model in Blender.
    
    Args:
        model_path: Path to the 3D model file
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Opening 3D model in Blender: {model_path}")
    
    try:
        # Find Blender executable
        blender_exe = find_blender_executable()
        if not blender_exe:
            logger.error("Blender executable not found")
            return False
        
        logger.info(f"Using Blender executable: {blender_exe}")
        
        # Open the model in Blender
        subprocess.Popen([blender_exe, model_path])
        
        logger.info("Opened model in Blender")
        return True
    
    except Exception as e:
        logger.error(f"Error opening model in Blender: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Convert SVG to 3D and view in Blender")
    parser.add_argument("svg_path", help="Path to the SVG file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    
    # Validate SVG file path
    svg_path = os.path.abspath(args.svg_path)
    if not os.path.exists(svg_path):
        logger.error(f"SVG file not found: {svg_path}")
        return
    
    # Convert SVG to 3D
    model_path = convert_svg_to_3d(svg_path, args.debug)
    if not model_path:
        logger.error("SVG to 3D conversion failed")
        return
    
    # Open in Blender
    open_in_blender(model_path)

if __name__ == "__main__":
    main()
