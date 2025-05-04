"""
Visual test script for SVG to 3D converter
Run this script from within Blender's Text Editor
"""

import os
import sys
import bpy

# Add the parent directories to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
if svg_to_3d_dir not in sys.path:
    sys.path.append(svg_to_3d_dir)

# Import our modules
from svg_parser import SVGParser
from svg_converter import SVGTo3DConverter
from svg_utils import log

def create_complex_test_svg():
    """Create a more complex test SVG file with various elements"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect x="0" y="0" width="800" height="600" fill="#f0f0f0" />
    
    <!-- Group with transform -->
    <g transform="translate(100, 100)">
        <rect x="0" y="0" width="100" height="100" fill="#ff0000" />
        <circle cx="50" cy="50" r="30" fill="#ffffff" />
    </g>
    
    <!-- Complex path with curves -->
    <path d="M200,300 C250,250 350,250 400,300 S500,350 550,300" 
          stroke="#0000ff" stroke-width="4" fill="none" />
    
    <!-- Text with styling -->
    <text x="400" y="100" font-size="48" font-family="Arial" fill="#333333" text-anchor="middle">
        SVG to 3D Test
    </text>
    
    <!-- Nested groups -->
    <g transform="translate(500, 200)">
        <g transform="rotate(45)">
            <rect x="-25" y="-25" width="50" height="50" fill="#00ff00" />
            <rect x="-15" y="-15" width="30" height="30" fill="#ffffff" />
        </g>
    </g>
    
    <!-- Polygon star -->
    <polygon points="400,400 430,480 510,480 450,530 470,610 400,560 330,610 350,530 290,480 370,480" 
             fill="#ffff00" stroke="#000000" stroke-width="2" />
    
    <!-- Rounded rectangle -->
    <rect x="50" y="450" width="150" height="80" rx="20" ry="20" 
          fill="#ff00ff" stroke="#000000" stroke-width="3" />
    
    <!-- Ellipse -->
    <ellipse cx="700" cy="500" rx="60" ry="40" 
             fill="#00ffff" stroke="#000000" stroke-width="2" />
</svg>"""
    
    # Save the test SVG
    test_svg_path = os.path.join(addon_dir, 'complex_test.svg')
    with open(test_svg_path, 'w', encoding='utf-8') as f:
        f.write(test_svg_content)
    
    return test_svg_path

def run_visual_test():
    """Run a visual test of the SVG to 3D converter"""
    try:
        # Clear the scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Clear data blocks
        for block in bpy.data.meshes:
            bpy.data.meshes.remove(block)
        for block in bpy.data.materials:
            bpy.data.materials.remove(block)
        for block in bpy.data.curves:
            bpy.data.curves.remove(block)
        
        print("Scene cleared successfully")
        
        # Create test SVG
        svg_file = create_complex_test_svg()
        print(f"Created test SVG: {svg_file}")
        
        # Parse SVG
        parser = SVGParser()
        svg_data = parser.parse(svg_file)
        
        if not svg_data:
            print("ERROR: Failed to parse SVG file")
            return
        
        print(f"Parsed SVG successfully:")
        print(f"  Width: {svg_data['width']}")
        print(f"  Height: {svg_data['height']}")
        print(f"  Element count: {len(svg_data['elements'])}")
        
        # Debug: Print element types
        element_types = {}
        for element in svg_data['elements']:
            element_type = element.get('type', 'unknown')
            element_types[element_type] = element_types.get(element_type, 0) + 1
        
        print("\nElement types found:")
        for element_type, count in element_types.items():
            print(f"  {element_type}: {count}")
        
        # Convert to 3D
        converter = SVGTo3DConverter()
        result = converter.convert(svg_data)
        
        if not result:
            print("ERROR: Failed to convert SVG to 3D")
            return
        
        print(f"\nConversion completed. Objects created: {len(bpy.data.objects)}")
        
        # List created objects
        print("\nCreated objects:")
        for obj in bpy.data.objects:
            print(f"  - {obj.name} (Type: {obj.type})")
        
        # Frame all objects in view
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = {'area': area, 'region': area.regions[-1]}
                bpy.ops.view3d.view_all(override)
                break
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"ERROR during test: {e}")
        import traceback
        traceback.print_exc()

# Run the test
if __name__ == "__main__":
    run_visual_test()
