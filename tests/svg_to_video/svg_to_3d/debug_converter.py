"""
Debug script for SVG to 3D converter

This script provides detailed debugging information for each step of the conversion process.
"""

import os
import sys
import bpy
import traceback

# Add the parent directories to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
if svg_to_3d_dir not in sys.path:
    sys.path.append(svg_to_3d_dir)

from svg_parser import SVGParser
from svg_converter import SVGTo3DConverter
from svg_utils import log

def debug_element(element, level=0):
    """Print detailed information about an SVG element"""
    indent = "  " * level
    element_type = element.get('type', 'unknown')
    
    print(f"{indent}Element Type: {element_type}")
    
    # Print all attributes
    for key, value in element.items():
        if key != 'children' and key != 'type':
            if isinstance(value, dict):
                print(f"{indent}  {key}:")
                for k, v in value.items():
                    print(f"{indent}    {k}: {v}")
            else:
                print(f"{indent}  {key}: {value}")
    
    # Process children recursively
    if 'children' in element:
        print(f"{indent}  Children: {len(element['children'])}")
        for i, child in enumerate(element['children']):
            print(f"{indent}  Child {i}:")
            debug_element(child, level + 2)

def create_debug_svg():
    """Create a debug SVG with various edge cases"""
    debug_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Edge case: Rectangle with only partial rounding -->
    <rect x="50" y="50" width="100" height="60" fill="#ff0000" rx="10" />
    
    <!-- Edge case: Circle with very small radius -->
    <circle cx="200" cy="80" r="2" fill="#00ff00" />
    
    <!-- Edge case: Complex path with various commands -->
    <path d="M100,200 L150,200 C200,200 200,250 150,250 Q125,250 100,225 Z" 
          fill="#0000ff" stroke="#000000" stroke-width="2" />
    
    <!-- Edge case: Text with special characters -->
    <text x="300" y="100" font-size="20" fill="#000000">Debug & Test</text>
    
    <!-- Edge case: Group with nested transforms -->
    <g transform="translate(400, 200)">
        <g transform="rotate(30)">
            <rect x="-20" y="-20" width="40" height="40" fill="#ff00ff" />
        </g>
    </g>
    
    <!-- Edge case: Polyline with single segment -->
    <polyline points="50,300 150,350" stroke="#ff0000" stroke-width="3" />
    
    <!-- Edge case: Polygon with very few points -->
    <polygon points="300,300 350,300 325,350" fill="#00ffff" />
</svg>"""
    
    debug_svg_path = os.path.join(os.path.dirname(__file__), 'debug_test.svg')
    with open(debug_svg_path, 'w', encoding='utf-8') as f:
        f.write(debug_svg_content)
    
    return debug_svg_path

def debug_converter():
    """Run a detailed debug session of the SVG to 3D converter"""
    print("=" * 60)
    print("SVG to 3D Converter Debug Session")
    print("=" * 60)
    
    try:
        # Clear the scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Create debug SVG
        svg_file = create_debug_svg()
        print(f"\n1. Created debug SVG file: {svg_file}")
        
        # Phase 1: SVG Parsing
        print("\n2. PHASE 1: SVG PARSING")
        print("-" * 30)
        
        parser = SVGParser()
        
        # Debug: Check if parser modules are loaded correctly
        print("Parser modules status:")
        print(f"  - svg_parser_elements loaded: {hasattr(parser, 'parse_rect')}")
        print(f"  - svg_parser_paths loaded: {hasattr(parser, 'parse_path_d')}")
        
        svg_data = parser.parse(svg_file)
        
        if not svg_data:
            print("ERROR: SVG parsing failed!")
            return
        
        print(f"SVG parsed successfully!")
        print(f"  - Width: {svg_data['width']}")
        print(f"  - Height: {svg_data['height']}")
        print(f"  - Viewbox: {svg_data.get('viewbox', 'Not set')}")
        print(f"  - Number of elements: {len(svg_data['elements'])}")
        
        # Phase 2: Element Analysis
        print("\n3. PHASE 2: ELEMENT ANALYSIS")
        print("-" * 30)
        
        for i, element in enumerate(svg_data['elements']):
            print(f"\nElement {i}:")
            debug_element(element)
        
        # Phase 3: 3D Conversion
        print("\n4. PHASE 3: 3D CONVERSION")
        print("-" * 30)
        
        converter = SVGTo3DConverter()
        
        # Debug: Check if converter modules are loaded correctly
        print("Converter modules status:")
        print(f"  - svg_converter_create loaded: {hasattr(converter, 'create_3d_rect')}")
        print(f"  - svg_converter_path loaded: {hasattr(converter, 'create_3d_path')}")
        print(f"  - svg_converter_group loaded: {hasattr(converter, 'create_3d_group')}")
        print(f"  - svg_converter_scene loaded: {hasattr(converter, 'setup_scene')}")
        
        # Set debug mode
        converter.debug_mode = True
        
        result = converter.convert(svg_data)
        
        if not result:
            print("ERROR: 3D conversion failed!")
            return
        
        print("3D conversion completed successfully!")
        
        # Phase 4: Result Analysis
        print("\n5. PHASE 4: RESULT ANALYSIS")
        print("-" * 30)
        
        print(f"Objects created: {len(bpy.data.objects)}")
        print("\nObject details:")
        for obj in bpy.data.objects:
            print(f"  - {obj.name}")
            print(f"    Type: {obj.type}")
            print(f"    Location: {obj.location}")
            print(f"    Scale: {obj.scale}")
            if obj.data and hasattr(obj.data, 'materials'):
                print(f"    Materials: {len(obj.data.materials)}")
        
        print(f"\nMaterials created: {len(bpy.data.materials)}")
        for mat in bpy.data.materials:
            print(f"  - {mat.name}")
        
        print("\nDebug session completed successfully!")
        
    except Exception as e:
        print(f"\nERROR during debug session: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_converter()
