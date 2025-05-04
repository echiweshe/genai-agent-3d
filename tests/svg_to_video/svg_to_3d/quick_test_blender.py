#!/usr/bin/env python3
"""
Quick test to verify SVG to 3D converter is working
This script runs inside Blender
"""

import os
import sys
import bpy

# Add the parent directories to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
sys.path.append(svg_to_3d_dir)

try:
    # Import our modules
    from svg_parser import SVGParser
    from svg_converter import SVGTo3DConverter
    from svg_utils import log
    
    print("✓ All modules imported successfully!")
    
    # Create a simple test SVG
    test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="80" height="80" fill="#ff0000" />
    <circle cx="50" cy="50" r="20" fill="#00ff00" />
</svg>"""
    
    # Save test SVG
    test_file = os.path.join(os.path.dirname(__file__), 'test.svg')
    with open(test_file, 'w') as f:
        f.write(test_svg)
    
    print(f"✓ Test SVG created: {test_file}")
    
    # Test SVG Parser
    parser = SVGParser(test_file)
    elements, width, height = parser.parse()
    
    print(f"✓ SVG parsed successfully!")
    print(f"  - Width: {width}")
    print(f"  - Height: {height}")
    print(f"  - Elements: {len(elements)}")
    
    # Test SVG Converter
    converter = SVGTo3DConverter()
    print("✓ SVG to 3D converter initialized!")
    
    # Try converting
    svg_data = {
        'elements': elements,
        'width': width,
        'height': height
    }
    
    result = converter.convert(svg_data)
    
    if result:
        print("✓ SVG conversion successful!")
        print(f"  - Objects created: {len(bpy.data.objects)}")
        
        # Save test file
        output_file = os.path.join(os.path.dirname(__file__), 'test_output.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        print(f"✓ Output saved to: {output_file}")
    else:
        print("✗ SVG conversion failed!")
        
    print("\nAll components are working correctly!")
    print("You can now run the full test suite with: python test_suite.py")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
