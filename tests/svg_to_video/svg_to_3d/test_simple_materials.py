"""
Simple test to verify materials and colors are working
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

def create_simple_svg():
    """Create a simple SVG with basic shapes and colors"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Red rectangle -->
    <rect x="50" y="50" width="100" height="80" fill="#ff0000" />
    
    <!-- Green circle -->
    <circle cx="250" cy="90" r="50" fill="#00ff00" />
    
    <!-- Blue ellipse -->
    <ellipse cx="450" cy="90" rx="60" ry="40" fill="#0000ff" />
    
    <!-- Yellow polygon (triangle) -->
    <polygon points="100,250 50,350 150,350" fill="#ffff00" />
    
    <!-- Magenta line -->
    <line x1="200" y1="250" x2="300" y2="350" stroke="#ff00ff" stroke-width="10" />
    
    <!-- Cyan polyline -->
    <polyline points="350,250 400,300 450,250 500,300" stroke="#00ffff" stroke-width="8" fill="none" />
</svg>"""
    
    # Save the test SVG
    test_svg_path = os.path.join(os.path.dirname(__file__), 'simple_materials_test.svg')
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

def test_materials():
    """Test materials and colors"""
    try:
        log("=" * 50)
        log("Simple Materials Test")
        log("=" * 50)
        
        # Clear scene
        log("Clearing scene...")
        clear_scene()
        
        # Create test SVG
        log("Creating simple test SVG...")
        svg_file = create_simple_svg()
        
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
            extrude_depth=0.2,  # More extrusion for better visibility
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
                        space.shading.use_scene_world = True
        
        # List all objects and materials
        log("\nCreated objects and materials:")
        for obj in bpy.data.objects:
            if obj.type in ['MESH', 'CURVE', 'FONT']:
                log(f"  - {obj.name} (Type: {obj.type})")
                if hasattr(obj.data, 'materials'):
                    for i, mat in enumerate(obj.data.materials):
                        if mat:
                            log(f"    Material {i}: {mat.name}")
                            if mat.use_nodes and 'Principled BSDF' in mat.node_tree.nodes:
                                principled = mat.node_tree.nodes['Principled BSDF']
                                base_color = principled.inputs['Base Color'].default_value
                                log(f"      Base Color: ({base_color[0]:.2f}, {base_color[1]:.2f}, {base_color[2]:.2f})")
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), 'simple_materials_output.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        log(f"\nSaved to: {output_file}")
        
        # Frame all objects
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = {'area': area, 'region': area.regions[-1]}
                bpy.ops.view3d.view_all(override)
                break
        
        log("\nTest completed successfully!")
        return True
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_materials()
