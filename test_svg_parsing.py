"""
Test script to verify SVG parsing outside of Blender
"""

import os
import xml.etree.ElementTree as ET
import traceback

def test_svg_parsing(svg_path):
    """Test parsing SVG file"""
    print(f"Testing SVG parsing for: {svg_path}")
    
    try:
        # Check if file exists
        if not os.path.isfile(svg_path):
            print(f"Error: SVG file not found: {svg_path}")
            return False
        
        # Check file size
        file_size = os.path.getsize(svg_path)
        print(f"SVG file size: {file_size} bytes")
        
        # Read file content
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"First 100 characters: {content[:100]}...")
        
        # Parse SVG using ElementTree
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Get root tag and namespace
        print(f"Root tag: {root.tag}")
        
        # Check SVG dimensions
        width = root.attrib.get('width', 'not specified')
        height = root.attrib.get('height', 'not specified')
        viewBox = root.attrib.get('viewBox', 'not specified')
        
        print(f"SVG dimensions: {width}x{height}, viewBox: {viewBox}")
        
        # Count elements by type
        element_counts = {}
        for elem in root.findall('.//*'):
            tag = elem.tag
            # Strip namespace if present
            if '}' in tag:
                tag = tag.split('}')[1]
            
            element_counts[tag] = element_counts.get(tag, 0) + 1
        
        print("Element counts:")
        for tag, count in element_counts.items():
            print(f"  - {tag}: {count}")
        
        print("SVG parsed successfully!")
        return True
        
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Error testing SVG: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test directory setup
    test_dir = "./outputs/debug_test"
    os.makedirs(test_dir, exist_ok=True)
    
    # Test with a very simple SVG
    simple_svg_path = os.path.join(test_dir, "simple_test.svg")
    
    # Create a simple SVG
    simple_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <rect x="50" y="50" width="100" height="100" fill="red" />
</svg>"""
    
    with open(simple_svg_path, "w", encoding="utf-8") as f:
        f.write(simple_svg)
    
    print(f"Created test SVG at: {simple_svg_path}")
    
    # Test parsing
    test_svg_parsing(simple_svg_path)
    
    # Now test any SVGs in the test directory
    test_svg_dir = "./outputs/enhanced_svg_test"
    if os.path.exists(test_svg_dir):
        for file in os.listdir(test_svg_dir):
            if file.endswith(".svg"):
                svg_path = os.path.join(test_svg_dir, file)
                print("\n" + "="*50)
                print(f"Testing SVG: {file}")
                print("="*50)
                test_svg_parsing(svg_path)
