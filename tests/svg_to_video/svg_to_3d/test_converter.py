"""
Test script for the SVG to 3D converter

This script tests the modularized SVG to 3D converter with various SVG files.
"""

import os
import sys
import bpy
import traceback

# Add the parent directories to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
sys.path.append(svg_to_3d_dir)

from svg_parser import SVGParser
from svg_converter import SVGTo3DConverter
from svg_utils import log

def create_test_svg():
    """Create a simple test SVG file"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Simple shapes for testing -->
    
    <!-- Rectangle -->
    <rect x="50" y="50" width="100" height="60" fill="#ff0000" rx="10" />
    
    <!-- Circle -->
    <circle cx="250" cy="100" r="40" fill="#00ff00" />
    
    <!-- Ellipse -->
    <ellipse cx="150" cy="200" rx="50" ry="30" fill="#0000ff" />
    
    <!-- Line -->
    <line x1="50" y1="300" x2="150" y2="350" stroke="#ff00ff" stroke-width="5" />
    
    <!-- Polyline -->
    <polyline points="200,300 250,320 300,300 350,320" stroke="#ffff00" stroke-width="3" fill="none" />
    
    <!-- Polygon -->
    <polygon points="100,250 150,230 200,250 150,270" fill="#00ffff" />
    
    <!-- Text -->
    <text x="250" y="250" font-size="24" fill="#000000">Test</text>
    
    <!-- Simple path -->
    <path d="M300,200 L350,200 L325,250 Z" fill="#ff8800" />
</svg>"""
    
    # Save the test SVG
    test_svg_path = os.path.join(os.path.dirname(__file__), 'test_input.svg')
    with open(test_svg_path, 'w', encoding='utf-8') as f:
        f.write(test_svg_content)
    
    return test_svg_path

def clear_scene():
    """Clear the Blender scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Clear meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    
    # Clear curves
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve)

def test_svg_converter():
    """Test the SVG to 3D converter"""
    try:
        # Clear the scene first
        log("Clearing scene...")
        clear_scene()
        
        # Create test SVG
        log("Creating test SVG file...")
        svg_file = create_test_svg()
        
        # Parse SVG
        log("Parsing SVG file...")
        parser = SVGParser()
        svg_data = parser.parse(svg_file)
        
        if not svg_data:
            log("ERROR: Failed to parse SVG file")
            return False
        
        log(f"Parsed SVG data:")
        log(f"  Width: {svg_data['width']}")
        log(f"  Height: {svg_data['height']}")
        log(f"  Element count: {len(svg_data['elements'])}")
        
        # Convert to 3D
        log("Converting to 3D...")
        converter = SVGTo3DConverter()
        result = converter.convert(svg_data)
        
        if not result:
            log("ERROR: Failed to convert SVG to 3D")
            return False
        
        # Verify objects were created
        obj_count = len(bpy.data.objects)
        log(f"Objects created: {obj_count}")
        
        # List created objects
        for obj in bpy.data.objects:
            log(f"  - {obj.name} (Type: {obj.type})")
        
        # Save blend file
        output_file = os.path.join(os.path.dirname(__file__), 'test_output.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        log(f"Scene saved to: {output_file}")
        
        return True
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    log("=" * 50)
    log("SVG to 3D Converter Test")
    log("=" * 50)
    
    try:
        success = test_svg_converter()
        
        if success:
            log("\nTEST PASSED: SVG conversion completed successfully!")
        else:
            log("\nTEST FAILED: SVG conversion encountered errors")
            
    except Exception as e:
        log(f"\nTEST FAILED with exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
