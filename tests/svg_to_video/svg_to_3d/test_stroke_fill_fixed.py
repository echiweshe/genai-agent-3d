"""
Fixed test for stroke and fill material handling
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
<svg width="1000" height="800" xmlns="http://www.w3.org/2000/svg">
    <!-- Row 1: Basic fill and stroke -->
    <text x="50" y="40" font-size="24" fill="#000000">Row 1: Basic Fill and Stroke</text>
    
    <!-- Fill only (red) -->
    <rect x="50" y="50" width="150" height="100" fill="#ff0000" />
    <text x="125" y="200" text-anchor="middle" font-size="16" fill="#000000">Fill Only</text>
    
    <!-- Stroke only (green) -->
    <rect x="250" y="50" width="150" height="100" fill="none" stroke="#00ff00" stroke-width="8" />
    <text x="325" y="200" text-anchor="middle" font-size="16" fill="#000000">Stroke Only</text>
    
    <!-- Both fill and stroke -->
    <rect x="450" y="50" width="150" height="100" fill="#0000ff" stroke="#ffff00" stroke-width="8" />
    <text x="525" y="200" text-anchor="middle" font-size="16" fill="#000000">Fill + Stroke</text>
    
    <!-- Row 2: Transparency -->
    <text x="50" y="280" font-size="24" fill="#000000">Row 2: Transparency</text>
    
    <!-- Semi-transparent fill -->
    <circle cx="125" cy="350" r="60" fill="#ff00ff" fill-opacity="0.5" />
    <text x="125" y="450" text-anchor="middle" font-size="16" fill="#000000">50% Fill</text>
    
    <!-- Semi-transparent stroke -->
    <circle cx="325" cy="350" r="60" fill="none" stroke="#00ffff" stroke-width="12" stroke-opacity="0.5" />
    <text x="325" y="450" text-anchor="middle" font-size="16" fill="#000000">50% Stroke</text>
    
    <!-- Different opacities -->
    <circle cx="525" cy="350" r="60" fill="#ff8800" fill-opacity="0.7" stroke="#0088ff" stroke-width="12" stroke-opacity="0.3" />
    <text x="525" y="450" text-anchor="middle" font-size="16" fill="#000000">70% Fill / 30% Stroke</text>
    
    <!-- Row 3: Complex shapes -->
    <text x="50" y="520" font-size="24" fill="#000000">Row 3: Complex Shapes</text>
    
    <!-- Path with fill and stroke -->
    <path d="M50,600 L150,550 L150,650 Z" fill="#88ff00" stroke="#880000" stroke-width="6" />
    <text x="100" y="700" text-anchor="middle" font-size="16" fill="#000000">Triangle</text>
    
    <!-- Complex path with curves -->
    <path d="M250,600 Q300,550 350,600 T450,600" fill="none" stroke="#ff0088" stroke-width="10" stroke-linecap="round" />
    <text x="350" y="700" text-anchor="middle" font-size="16" fill="#000000">Curved Path</text>
    
    <!-- Star shape -->
    <path d="M600,600 L620,650 L680,650 L630,680 L650,730 L600,700 L550,730 L570,680 L520,650 L580,650 Z" 
          fill="#ffff00" stroke="#ff0000" stroke-width="4" />
    <text x="600" y="750" text-anchor="middle" font-size="16" fill="#000000">Star</text>
</svg>"""
    
    # Save the test SVG
    test_svg_path = os.path.join(os.path.dirname(__file__), 'stroke_fill_test_fixed.svg')
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
        log("Stroke and Fill Test (Fixed)")
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
            scale_factor=0.005,  # Smaller scale for larger canvas
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
        
        # List all objects and materials
        log("\nCreated objects and materials:")
        material_count = {'fill': 0, 'stroke': 0, 'both': 0}
        
        for obj in bpy.data.objects:
            if obj.type in ['MESH', 'CURVE', 'FONT']:
                has_fill = False
                has_stroke = False
                
                if hasattr(obj.data, 'materials'):
                    for mat in obj.data.materials:
                        if mat:
                            if 'Fill' in mat.name:
                                has_fill = True
                            if 'Stroke' in mat.name:
                                has_stroke = True
                
                if has_fill and has_stroke:
                    material_count['both'] += 1
                elif has_fill:
                    material_count['fill'] += 1
                elif has_stroke:
                    material_count['stroke'] += 1
                
                log(f"  - {obj.name} (Type: {obj.type})")
                if hasattr(obj.data, 'materials'):
                    for i, mat in enumerate(obj.data.materials):
                        if mat:
                            log(f"    Material {i}: {mat.name}")
        
        log(f"\nMaterial summary:")
        log(f"  Fill only: {material_count['fill']}")
        log(f"  Stroke only: {material_count['stroke']}")
        log(f"  Both: {material_count['both']}")
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), 'stroke_fill_output_fixed.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        log(f"\nSaved to: {output_file}")
        
        # Frame all objects
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = {'area': area, 'region': area.regions[-1]}
                bpy.ops.view3d.view_all(override)
                # Set to front view
                bpy.ops.view3d.view_axis(override, type='FRONT')
                break
        
        log("\nTest completed successfully!")
        return True
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_stroke_fill()
