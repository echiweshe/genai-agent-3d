"""
Final test for transparency and stroke issues
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
    """Create a test SVG focusing on the three specific issues"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="600" height="200" xmlns="http://www.w3.org/2000/svg">
    <!-- Test the three specific cases that were not working -->
    
    <!-- Magenta circle with 50% opacity (Issue #1) -->
    <circle cx="100" cy="100" r="50" fill="#ff00ff" opacity="0.5" />
    <text x="100" y="180" text-anchor="middle" font-size="16" fill="#000000">50% Opacity</text>
    
    <!-- Cyan circle with black stroke (Issue #2) -->
    <circle cx="300" cy="100" r="50" fill="#00ffff" stroke="#000000" stroke-width="8" />
    <text x="300" y="180" text-anchor="middle" font-size="16" fill="#000000">Black Stroke</text>
    
    <!-- Red stroke only, no fill (Issue #3) -->
    <circle cx="500" cy="100" r="50" fill="none" stroke="#ff0000" stroke-width="8" />
    <text x="500" y="180" text-anchor="middle" font-size="16" fill="#000000">Stroke Only</text>
</svg>"""
    
    test_svg_path = os.path.join(os.path.dirname(__file__), 'final_fix_test.svg')
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

def test_final_fix():
    """Test the final fixes for transparency and strokes"""
    try:
        log("=" * 50)
        log("Final Fix Test - Transparency and Strokes")
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
        
        # List all created materials and objects
        log("\nCreated Materials:")
        for mat in bpy.data.materials:
            if mat.name.startswith('SVG_'):
                blend_mode = mat.blend_method
                alpha = "Unknown"
                if mat.node_tree:
                    for node in mat.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            alpha = node.inputs['Alpha'].default_value
                            break
                log(f"  - {mat.name} (Blend: {blend_mode}, Alpha: {alpha})")
        
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
        output_file = os.path.join(os.path.dirname(__file__), 'final_fix_output.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        log(f"\nSaved to: {output_file}")
        
        log("\nTest completed!")
        return True
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_final_fix()
