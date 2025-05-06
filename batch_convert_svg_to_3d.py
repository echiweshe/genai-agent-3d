"""
Batch Convert SVG to 3D Models

This script converts multiple SVG files to 3D models in batch mode.
"""

import os
import sys
import argparse
import logging
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            logger.error(f"Conversion failed for {svg_path}")
            return None
    
    except Exception as e:
        logger.error(f"Error during conversion of {svg_path}: {str(e)}")
        return None

def find_svg_files(input_dir):
    """
    Find all SVG files in the input directory.
    
    Args:
        input_dir: Directory to search for SVG files
    
    Returns:
        List of paths to SVG files
    """
    svg_files = glob.glob(os.path.join(input_dir, "**", "*.svg"), recursive=True)
    return sorted(svg_files)

def batch_convert(input_dir, max_workers=4, debug=False):
    """
    Convert all SVG files in the input directory to 3D models.
    
    Args:
        input_dir: Directory to search for SVG files
        max_workers: Maximum number of parallel conversions
        debug: Enable debug output
    
    Returns:
        List of paths to converted 3D models
    """
    # Find SVG files
    svg_files = find_svg_files(input_dir)
    if not svg_files:
        logger.error(f"No SVG files found in {input_dir}")
        return []
    
    logger.info(f"Found {len(svg_files)} SVG files to convert")
    
    # Convert SVG files in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_svg = {executor.submit(convert_svg_to_3d, svg, debug): svg for svg in svg_files}
        for future in as_completed(future_to_svg):
            svg = future_to_svg[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error processing {svg}: {str(e)}")
    
    logger.info(f"Successfully converted {len(results)} out of {len(svg_files)} SVG files")
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Batch convert SVG files to 3D models")
    parser.add_argument("input_dir", help="Directory containing SVG files")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of parallel conversions")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()
    
    # Validate input directory
    input_dir = os.path.abspath(args.input_dir)
    if not os.path.isdir(input_dir):
        logger.error(f"Input directory not found: {input_dir}")
        return
    
    # Convert SVG files
    output_models = batch_convert(input_dir, args.max_workers, args.debug)
    
    # Print summary
    if output_models:
        logger.info("Conversion complete. Output models:")
        for model in output_models:
            logger.info(f"  {model}")
    else:
        logger.error("No models were successfully converted")

if __name__ == "__main__":
    main()
