"""
Complete test for transparency and stroke rendering
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
    <!-- Row 1: Test cases that were not working -->
    <text x="300" y="30" text-anchor="middle" font-size="24" fill="#000000">Transparency and Stroke Test</text>
    
    <!-- Magenta circle with 50% opacity (was showing as 100%) -->
    <circle cx="100" cy="100" r="50" fill="#ff00ff" opacity="0.5" />
    <text x="100" y="170" text-anchor="middle" font-size="14" fill="#000000">50% Opacity</text>
    
    <!-- Cyan circle with black stroke (stroke was missing) -->
    <circle cx="300" cy="100" r="50" fill="#00ffff" stroke="#000000" stroke-width="8" />
    <text x="300" y="170" text-anchor="middle" font-size="14" fill="#000000">Black Stroke</text>
    
    <!-- Red circle with no fill, only stroke -->
    <circle cx="500" cy="100" r="50" fill="none" stroke="#ff0000" stroke-width="8" />
    <text x="500" y="170" text-anchor="middle" font-size="14" fill="#000000">Stroke Only</text>
    
    <!-- Row 2: More test cases -->
    <text x="300" y="230" text-anchor="middle" font-size="20" fill="#000000">Combined Effects</text>
    
    <!-- Semi-transparent fill with solid stroke -->
    <circle cx="100" cy="300" r="50" fill="#00ff00" fill-opacity="0.5" stroke="#0000ff" stroke-width="8" />
    <text x="100" y="370" text-anchor="middle" font-size="14" fill="#000000">50% Fill + Stroke</text>
    
    <!-- Solid fill with semi-transparent stroke -->
    <circle cx="300" cy="300" r="50" fill="#ff8800" stroke="#000000" stroke-width="8" stroke-opacity="0.5" />
    <text x="300" y="370" text-anchor="middle" font-size="14" fill="#000000">Fill + 50% Stroke</text>
    
    <!-- Both semi-transparent -->
    <circle cx="500" cy="300" r="50" fill="#0000ff" fill-opacity="0.7" stroke="#ff0000" stroke-width="8" stroke-opacity="0.3" />
    <text x="500" y="370" text-anchor="middle" font-size="14" fill="#000000">70% Fill + 30% Stroke</text>
</svg>"""
    
    test_svg_path = os.path.join(os.path.dirname(__file__), 'transparency_stroke_complete_test.svg')
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

def test_transparency_stroke():
    """Test transparency and strokes"""
    try:
        log("=" * 50)
        log("Complete Transparency and Stroke Test")
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
        
        # List all created materials and objects
        log("\nCreated Materials:")
        for mat in bpy.data.materials:
            if mat.name.startswith('SVG_'):
                transparency = "Transparent" if mat.blend_method == 'BLEND' else "Opaque"
                log(f"  - {mat.name} ({transparency})")
        
        log("\nCreated Objects:")
        for obj in bpy.data.objects:
            if obj.type in ['MESH', 'CURVE', 'FONT']:
                log(f"  - {obj.name} ({obj.type})")
                if hasattr(obj.data, 'materials'):
                    for i, mat in enumerate(obj.data.materials):
                        if mat:
                            log(f"    Material {i}: {mat.name}")
                if obj.modifiers:
                    for mod in obj.modifiers:
                        log(f"    Modifier: {mod.name} ({mod.type})")
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), 'transparency_stroke_complete_output.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        log(f"\nSaved to: {output_file}")
        
        # Try to frame all objects without causing the error
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                try:
                    # Use correct context override for Blender 4.x
                    with bpy.context.temp_override(area=area, region=area.regions[-1]):
                        bpy.ops.view3d.view_all()
                        bpy.ops.view3d.view_axis(type='FRONT')
                except Exception as e:
                    log(f"Warning: Could not set view (non-critical): {e}")
                break
        
        log("\nTest completed successfully!")
        return True
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_transparency_stroke()
