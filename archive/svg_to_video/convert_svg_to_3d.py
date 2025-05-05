"""
Command-line interface for SVG to 3D converter

This is a wrapper script that can be called from the command line or integrated into the pipeline.
"""

import os
import sys
import argparse

# Add the module directory to Python path
module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'svg_to_3d')
if module_dir not in sys.path:
    sys.path.append(module_dir)

import bpy
from svg_parser import SVGParser
from svg_converter import SVGTo3DConverter
from svg_utils import log


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Convert SVG to 3D Blender file')
    parser.add_argument('input_svg', help='Input SVG file path')
    parser.add_argument('output_blend', help='Output Blender file path')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--scale', type=float, default=0.01, help='Scale factor for conversion')
    parser.add_argument('--extrude', type=float, default=0.1, help='Extrusion depth')
    
    # Parse arguments after -- separator if running from Blender
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[1:]
    
    return parser.parse_args(argv)


def main():
    """Main conversion function"""
    args = parse_args()
    
    log(f"Converting {args.input_svg} to {args.output_blend}")
    
    try:
        # Clear the scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Parse SVG
        parser = SVGParser(args.input_svg, debug=args.debug)
        elements, width, height = parser.parse()
        
        if not elements:
            log("ERROR: No elements found in SVG file")
            sys.exit(1)
        
        log(f"Parsed {len(elements)} elements from SVG")
        
        # Create converter and configure
        converter = SVGTo3DConverter()
        converter.scale_factor = args.scale
        converter.extrude_depth = args.extrude
        
        if args.debug:
            converter.debug_mode = True
        
        # Convert to 3D
        result = converter.convert({
            'elements': elements,
            'width': width,
            'height': height
        })
        
        if not result:
            log("ERROR: Failed to convert SVG to 3D")
            sys.exit(1)
        
        log(f"Conversion successful: {len(bpy.data.objects)} objects created")
        
        # Save the result
        bpy.ops.wm.save_as_mainfile(filepath=args.output_blend)
        log(f"Saved to {args.output_blend}")
        
        print(f"SUCCESS: Converted {args.input_svg} to {args.output_blend}")
        
    except Exception as e:
        log(f"ERROR: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
