"""
SVG to 3D Blender Script

This script is executed by Blender to convert an SVG file to a 3D model.
It includes enhanced conversion capabilities for professional quality results.
"""

import sys
import os
import bpy
import json
import traceback

# Add the parent directory to sys.path to allow importing modules
script_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import the SVG to 3D conversion modules
try:
    from genai_agent.svg_to_video.svg_to_3d.enhanced_converter import get_svg_converter
    from genai_agent.svg_to_video.svg_to_3d.svg_utils import log, clean_scene
except ImportError as e:
    print(f"Error importing modules: {e}")
    # Fallback to direct import if relative import fails
    try:
        sys.path.append(os.path.join(script_dir, '..', 'genai_agent', 'svg_to_video'))
        from svg_to_3d.enhanced_converter import get_svg_converter
        from svg_to_3d.svg_utils import log, clean_scene
    except ImportError:
        print("Could not import required modules")
        sys.exit(1)

def convert_svg_to_3d(svg_path, blend_output_path, options=None):
    """
    Convert SVG file to 3D model and save as Blender file
    
    Args:
        svg_path: Path to SVG file
        blend_output_path: Path to save Blender file
        options: Dictionary of conversion options:
            - extrude_depth: Depth of extrusion (default: 0.1)
            - scale_factor: Scale factor for conversion (default: 0.01)
            - use_enhanced: Whether to use enhanced conversion (default: True)
            - style_preset: Visual style preset ('technical', 'organic', 'glossy', etc.)
            - debug: Enable debug output
    
    Returns:
        Boolean indicating success
    """
    try:
        log(f"Starting SVG to 3D conversion: {svg_path} -> {blend_output_path}")
        
        # Initialize options
        if options is None:
            options = {}
        
        # Get conversion options
        extrude_depth = float(options.get('extrude_depth', 0.1))
        scale_factor = float(options.get('scale_factor', 0.01))
        use_enhanced = bool(options.get('use_enhanced', True))
        style_preset = str(options.get('style_preset', 'technical'))
        debug = bool(options.get('debug', False))
        
        log(f"Conversion options: extrude_depth={extrude_depth}, scale_factor={scale_factor}, " +
            f"use_enhanced={use_enhanced}, style_preset={style_preset}, debug={debug}")
        
        # Get appropriate converter
        converter = get_svg_converter(
            svg_path, 
            extrude_depth=extrude_depth,
            scale_factor=scale_factor,
            use_enhanced=use_enhanced,
            style_preset=style_preset,
            debug=debug
        )
        
        # Clean the scene and convert SVG
        clean_scene()
        
        # Perform conversion
        success = converter.convert()
        
        if success:
            # Save Blender file
            log(f"Saving Blender file: {blend_output_path}")
            bpy.ops.wm.save_as_mainfile(filepath=blend_output_path)
            log("Conversion completed successfully")
            return True
        else:
            log("Conversion failed")
            return False
    except Exception as e:
        log(f"Error converting SVG to 3D: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function called when script is run directly"""
    try:
        # Check command line arguments
        if len(sys.argv) < 5:
            # Regular Blender arguments are: blender, -b, -P, <script.py>
            if len(sys.argv) < 2 or sys.argv[1] != "--":
                log("Usage: blender -b -P svg_to_3d_blender.py -- <svg_path> <blend_output_path> [options_json]")
                return 1
            
            # With -- separator, arguments are: <script.py>, --, <svg_path>, <blend_output_path>, [options_json]
            if len(sys.argv) < 4:
                log("Usage: blender -b -P svg_to_3d_blender.py -- <svg_path> <blend_output_path> [options_json]")
                return 1
            
            # Get arguments after --
            args = sys.argv[sys.argv.index("--") + 1:]
            svg_path = args[0]
            blend_output_path = args[1]
            options_json = args[2] if len(args) > 2 else "{}"
        else:
            # Get arguments
            svg_path = sys.argv[4]
            blend_output_path = sys.argv[5]
            options_json = sys.argv[6] if len(sys.argv) > 6 else "{}"
        
        # Parse options JSON
        try:
            options = json.loads(options_json)
        except json.JSONDecodeError:
            log(f"Warning: Could not parse options JSON: {options_json}")
            options = {}
        
        # Convert SVG to 3D
        success = convert_svg_to_3d(svg_path, blend_output_path, options)
        
        # Exit with appropriate code
        return 0 if success else 1
    except Exception as e:
        log(f"Error in main function: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
