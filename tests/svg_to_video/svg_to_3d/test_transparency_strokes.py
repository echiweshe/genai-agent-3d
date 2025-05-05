"""
Test for transparency and stroke rendering
"""

import os
import sys
import bpy
import traceback

# Add the parent directories to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
if svg_to_3d_dir not in sys.path:
    sys.path.insert(0, svg_to_3d_dir)

from svg_parser import SVGParser
from svg_to_3d_converter_new import SVGTo3DConverter
from svg_utils import log

def create_test_svg():
    """Create a test SVG focusing on transparency and strokes"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- First, test the specific cases that were not working -->
    <!-- Magenta circle with 50% opacity -->
    <circle cx="100" cy="100" r="50" fill="#ff00ff" opacity="0.5" />
    
    <!-- Cyan circle with black stroke -->
    <circle cx="300" cy="100" r="50" fill="#00ffff" stroke="#000000" stroke-width="5" />
    
    <!-- Now test other transparency and stroke combinations -->
    <!-- Stroke only (no fill) -->
    <circle cx="500" cy="100" r="50" fill="none" stroke="#ff0000" stroke-width="8" />
    
    <!-- Fill with transparent stroke -->
    <circle cx="100" cy="250" r="50" fill="#00ff00" stroke="#0000ff" stroke-width="8" stroke-opacity="0.5" />
    
    <!-- Transparent fill with solid stroke -->
    <circle cx="300" cy="250" r="50" fill="#ff8800" fill-opacity="0.5" stroke="#000000" stroke-width="6" />
    
    <!-- Both fill and stroke transparent -->
    <circle cx="500" cy="250" r="50" fill="#0000ff" fill-opacity="0.7" stroke="#ff0000" stroke-width="8" stroke-opacity="0.3" />
</svg>"""
    
    test_svg_path = os.path.join(os.path.dirname(__file__), 'transparency_strokes_test.svg')
    with open(test_svg_path, 'w', encoding='utf-8') as f:
        f.write(test_svg_content)
    
    return test_svg_path

def clear_scene():
    """Clear the Blender scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear all data blocks
    for block_type in [bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights]:
        for block in block_type:
            block_type.remove(block)

def test_transparency_strokes():
    """Test transparency and strokes"""
    try:
        log("=" * 50)
        log("Transparency and Strokes Test")
        log("=" * 50)
        
        # Clear scene
        log("Clearing scene...")
        clear_scene()
        
        # Create test SVG
        log("Creating test SVG...")
        svg_file = create_test_svg()
        
        # Parse SVG
        log("Parsing SVG...")
        parser = SVGParser(svg_file)
        elements, width, height = parser.parse()
        
        if not elements:
            log("ERROR: No elements parsed")
            return False
        
        log(f"Parsed {len(elements)} elements")
        
        # Convert to 3D
        log("Converting to 3D...")
        converter = SVGTo3DConverter(
            extrude_depth=0.1,
            scale_factor=0.01,
            debug=True
        )
        
        svg_data = {
            'elements': elements,
            'width': width,
            'height': height
        }
        
        result = converter.convert(svg_data)
        
        if not result:
            log("ERROR: Conversion failed")
            return False
        
        # Set viewport to material preview
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.use_scene_lights = True
                        space.shading.use_scene_world = False
                        space.shading.studio_light = 'studio.exr'
                        space.shading.studiolight_rotate_z = 0
                        space.shading.studiolight_intensity = 1.0
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), 'transparency_strokes_output.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        log(f"\nSaved to: {output_file}")
        
        # Frame all objects
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = {'area': area, 'region': area.regions[-1]}
                bpy.ops.view3d.view_all(override)
                bpy.ops.view3d.view_axis(override, type='FRONT')
                break
        
        log("\nTest completed successfully!")
        return True
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_transparency_strokes()
