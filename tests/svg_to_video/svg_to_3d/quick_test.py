#!/usr/bin/env python3
"""
Quick test to verify SVG to 3D converter is working
"""

import os
import sys

# Add the parent directories to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
sys.path.append(svg_to_3d_dir)

try:
    # Check if we're running inside Blender
    try:
        import bpy
        print("✓ Running inside Blender")
    except ImportError:
        print("✗ This script must be run with Blender's Python")
        print("\nTo run this test:")
        print("1. Use the test runner: python run_quick_test.py")
        print("2. Or run directly with Blender: blender --background --python quick_test_blender.py")
        sys.exit(1)
    
    from svg_parser import SVGParser
    from svg_converter import SVGTo3DConverter
    from svg_utils import log
    
    print("✓ All modules imported successfully!")
    
    # Create a simple test SVG
    test_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="80" height="80" fill="#ff0000" />
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
    
    print("\nAll components are working correctly!")
    print("You can now run the full test suite with: python test_suite.py")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
