"""
Test stroke and fill material handling
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

def create_stroke_fill_test_svg():
    """Create an SVG with various stroke and fill combinations"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
    <!-- Fill only -->
    <rect x="50" y="50" width="100" height="80" fill="#ff0000" />
    
    <!-- Stroke only -->
    <rect x="200" y="50" width="100" height="80" fill="none" stroke="#00ff00" stroke-width="5" />
    
    <!-- Both fill and stroke -->
    <rect x="350" y="50" width="100" height="80" fill="#0000ff" stroke="#ffff00" stroke-width="4" />
    
    <!-- Semi-transparent fill -->
    <circle cx="100" cy="200" r="40" fill="#ff00ff" fill-opacity="0.5" />
    
    <!-- Semi-transparent stroke -->
    <circle cx="250" cy="200" r="40" fill="none" stroke="#00ffff" stroke-width="4" stroke-opacity="0.5" />
    
    <!-- Both with different opacities -->
    <circle cx="400" cy="200" r="40" fill="#ff8800" fill-opacity="0.7" stroke="#0088ff" stroke-width="3" stroke-opacity="0.3" />
    
    <!-- Path with fill and stroke -->
    <path d="M50,350 L150,300 L150,400 Z" fill="#88ff00" stroke="#880000" stroke-width="3" />
    
    <!-- Complex path with curves -->
    <path d="M200,350 Q250,300 300,350 T400,350" fill="none" stroke="#ff0088" stroke-width="6" stroke-linecap="round" />
    
    <!-- Different stroke styles -->
    <line x1="500" y1="100" x2="750" y2="100" stroke="#000000" stroke-width="4" stroke-dasharray="10,5" />
    <line x1="500" y1="150" x2="750" y2="150" stroke="#000000" stroke-width="4" stroke-linecap="round" />
    <line x1="500" y1="200" x2="750" y2="200" stroke="#000000" stroke-width="4" stroke-linejoin="bevel" />
</svg>"""
    
    # Save the test SVG
    test_svg_path = os.path.join(os.path.dirname(__file__), 'stroke_fill_test.svg')
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

def test_stroke_fill():
    """Test stroke and fill handling"""
    try:
        log("=" * 50)
        log("Stroke and Fill Test")
        log("=" * 50)
        
        # Clear scene
        log("Clearing scene...")
        clear_scene()
        
        # Create test SVG
        log("Creating stroke/fill test SVG...")
        svg_file = create_stroke_fill_test_svg()
        
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
                            if 'Fill' in mat.name or 'Stroke' in mat.name:
                                log(f"      Type: {'Fill' if 'Fill' in mat.name else 'Stroke'}")
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), 'stroke_fill_output.blend')
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
    test_stroke_fill()
