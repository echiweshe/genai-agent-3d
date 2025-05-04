"""
Comprehensive test for all SVG elements with proper materials and visibility
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

def create_comprehensive_svg():
    """Create a comprehensive SVG with all element types"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect x="0" y="0" width="800" height="600" fill="#ffffff" />
    
    <!-- Basic Shapes Section -->
    <g id="basic-shapes">
        <!-- Rectangle with color -->
        <rect x="50" y="50" width="100" height="60" fill="#ff0000" />
        
        <!-- Rectangle with rounded corners -->
        <rect x="200" y="50" width="100" height="60" rx="15" ry="15" fill="#00ff00" />
        
        <!-- Circle -->
        <circle cx="400" cy="80" r="40" fill="#0000ff" />
        
        <!-- Ellipse -->
        <ellipse cx="550" cy="80" rx="50" ry="30" fill="#ff00ff" />
    </g>
    
    <!-- Lines and Paths Section -->
    <g id="lines-paths">
        <!-- Simple line -->
        <line x1="50" y1="200" x2="150" y2="250" stroke="#ff0000" stroke-width="5" />
        
        <!-- Polyline -->
        <polyline points="200,200 250,220 300,200 350,220" stroke="#00ff00" stroke-width="3" fill="none" />
        
        <!-- Polygon (star) -->
        <polygon points="450,200 470,250 520,250 480,280 500,330 450,300 400,330 420,280 380,250 430,250" 
                 fill="#ffff00" stroke="#000000" stroke-width="2" />
    </g>
    
    <!-- Text Section -->
    <g id="text-elements">
        <text x="50" y="400" font-size="36" fill="#000000">SVG to 3D</text>
        <text x="300" y="400" font-size="24" fill="#0000ff" font-family="Arial">Test Complete</text>
    </g>
    
    <!-- Complex Path -->
    <path d="M50,500 C100,450 150,450 200,500 S300,550 350,500 L400,500 Z" 
          fill="#ff8800" stroke="#000000" stroke-width="2" />
    
    <!-- Group with Transform -->
    <g transform="translate(600, 400) rotate(45)">
        <rect x="-30" y="-30" width="60" height="60" fill="#008800" />
        <circle cx="0" cy="0" r="20" fill="#ffffff" />
    </g>
</svg>"""
    
    # Save the test SVG
    test_svg_path = os.path.join(os.path.dirname(__file__), 'comprehensive_test.svg')
    with open(test_svg_path, 'w', encoding='utf-8') as f:
        f.write(test_svg_content)
    
    return test_svg_path

def clear_scene():
    """Clear the Blender scene completely"""
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear all data blocks
    for block_type in [bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights]:
        for block in block_type:
            block_type.remove(block)

def setup_viewport():
    """Configure viewport for better visualization"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = False
                    space.shading.studio_light = 'studio.exr'
                    space.shading.color_type = 'MATERIAL'
                    space.overlay.show_axis_x = True
                    space.overlay.show_axis_y = True
                    space.overlay.show_axis_z = True

def test_comprehensive():
    """Run comprehensive test"""
    try:
        log("=" * 50)
        log("Comprehensive SVG to 3D Test")
        log("=" * 50)
        
        # Clear scene
        log("Clearing scene...")
        clear_scene()
        
        # Create test SVG
        log("Creating comprehensive test SVG...")
        svg_file = create_comprehensive_svg()
        
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
        
        # Setup viewport
        setup_viewport()
        
        # List all objects
        log("\nCreated objects:")
        for obj in bpy.data.objects:
            log(f"  - {obj.name} (Type: {obj.type})")
            if hasattr(obj.data, 'materials') and obj.data.materials:
                for i, mat in enumerate(obj.data.materials):
                    if mat:
                        log(f"    Material {i}: {mat.name}")
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), 'comprehensive_output.blend')
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
    test_comprehensive()
