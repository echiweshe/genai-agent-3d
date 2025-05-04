"""
Command-line interface for SVG to 3D converter

Usage:
    blender --background --python convert_svg.py -- <input_svg> <output_blend>
"""

import os
import sys
import bpy
import argparse

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from svg_parser import SVGParser
from svg_converter import SVGTo3DConverter
from svg_utils import log

def parse_args():
    """Parse command line arguments"""
    # Get arguments after the -- separator
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description='Convert SVG to 3D Blender file')
    parser.add_argument('input_svg', help='Input SVG file path')
    parser.add_argument('output_blend', help='Output Blender file path')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    if len(argv) < 2:
        print("Usage: blender --background --python convert_svg.py -- <input_svg> <output_blend>")
        sys.exit(1)
    
    return parser.parse_args(argv)

def main():
    """Main conversion function"""
    args = parse_args()
    
    # Set up logging
    if args.debug:
        log("Debug mode enabled")
    
    log(f"Converting {args.input_svg} to {args.output_blend}")
    
    try:
        # Clear the scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Parse SVG
        log("Parsing SVG file...")
        parser = SVGParser()
        svg_data = parser.parse(args.input_svg)
        
        if not svg_data:
            log("ERROR: Failed to parse SVG file")
            sys.exit(1)
        
        log(f"SVG parsed successfully: {len(svg_data['elements'])} elements")
        
        # Convert to 3D
        log("Converting to 3D...")
        converter = SVGTo3DConverter()
        
        if args.debug:
            converter.debug_mode = True
        
        result = converter.convert(svg_data)
        
        if not result:
            log("ERROR: Failed to convert SVG to 3D")
            sys.exit(1)
        
        log(f"Conversion successful: {len(bpy.data.objects)} objects created")
        
        # Save the result
        log(f"Saving to {args.output_blend}")
        bpy.ops.wm.save_as_mainfile(filepath=args.output_blend)
        
        log("Conversion completed successfully!")
        
    except Exception as e:
        log(f"ERROR: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
