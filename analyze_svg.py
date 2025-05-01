"""
SVG Analysis Script - Examines SVG file structure for debugging conversion issues
"""

import xml.etree.ElementTree as ET
import sys
import os
import re

def parse_transform(transform_str):
    """Parse SVG transform attribute and return components."""
    if not transform_str:
        return {}
    
    result = {}
    transforms = re.findall(r'(\w+)\s*\(([^)]*)\)', transform_str)
    
    for transform_type, params_str in transforms:
        params = [float(p) for p in re.findall(r'[-+]?[0-9]*\.?[0-9]+', params_str)]
        result[transform_type] = params
    
    return result

def analyze_svg(svg_path):
    """Analyze SVG file and print structure information."""
    if not os.path.exists(svg_path):
        print(f"Error: File not found - {svg_path}")
        return
    
    print(f"Analyzing SVG file: {svg_path}")
    print("=" * 50)
    
    try:
        # Parse SVG file
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Extract namespace if present
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        if '}' in root.tag:
            ns_str = root.tag.split('}')[0].strip('{')
            ns = {'svg': ns_str}
        
        # Get SVG dimensions
        if 'viewBox' in root.attrib:
            viewBox = root.attrib['viewBox'].split()
            width = float(viewBox[2])
            height = float(viewBox[3])
            print(f"SVG viewBox: {viewBox}")
        else:
            width = float(root.attrib.get('width', '800').replace('px', ''))
            height = float(root.attrib.get('height', '600').replace('px', ''))
        
        print(f"SVG dimensions: {width} x {height}")
        
        # Count elements by type
        element_counts = {}
        
        def count_element(elem):
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}')[1]
            
            if tag not in element_counts:
                element_counts[tag] = 0
            element_counts[tag] += 1
            
            # Process children
            for child in elem:
                count_element(child)
        
        # Start counting from root
        count_element(root)
        
        print("\nElement counts:")
        for tag, count in element_counts.items():
            print(f"  - {tag}: {count}")
        
        # Examine interesting elements
        print("\nDetailed element analysis:")
        
        # Rectangles
        rects = root.findall(f".//{{{ns['svg']}}}rect")
        if rects:
            print(f"\nRectangles ({len(rects)}):")
            for i, rect in enumerate(rects[:5]):  # Show first 5
                x = rect.attrib.get('x', '0')
                y = rect.attrib.get('y', '0')
                w = rect.attrib.get('width', '0')
                h = rect.attrib.get('height', '0')
                fill = rect.attrib.get('fill', 'none')
                transform = rect.attrib.get('transform', None)
                if transform:
                    transform_info = parse_transform(transform)
                    print(f"  {i+1}. Rect: x={x}, y={y}, w={w}, h={h}, fill={fill}, transform={transform_info}")
                else:
                    print(f"  {i+1}. Rect: x={x}, y={y}, w={w}, h={h}, fill={fill}")
            if len(rects) > 5:
                print(f"  ... ({len(rects) - 5} more)")
        
        # Paths
        paths = root.findall(f".//{{{ns['svg']}}}path")
        if paths:
            print(f"\nPaths ({len(paths)}):")
            for i, path in enumerate(paths[:3]):  # Show first 3
                d = path.attrib.get('d', '')
                if len(d) > 50:
                    d = d[:47] + "..."
                fill = path.attrib.get('fill', 'none')
                stroke = path.attrib.get('stroke', 'none')
                print(f"  {i+1}. Path: d={d}, fill={fill}, stroke={stroke}")
            if len(paths) > 3:
                print(f"  ... ({len(paths) - 3} more)")
        
        # Text
        texts = root.findall(f".//{{{ns['svg']}}}text")
        if texts:
            print(f"\nText elements ({len(texts)}):")
            for i, text in enumerate(texts[:5]):  # Show first 5
                x = text.attrib.get('x', '0')
                y = text.attrib.get('y', '0')
                content = text.text or "".join(child.text or "" for child in text)
                if content and len(content) > 30:
                    content = content[:27] + "..."
                print(f"  {i+1}. Text: x={x}, y={y}, content=\"{content}\"")
            if len(texts) > 5:
                print(f"  ... ({len(texts) - 5} more)")
        
        # Groups
        groups = root.findall(f".//{{{ns['svg']}}}g")
        if groups:
            print(f"\nGroups ({len(groups)}):")
            for i, group in enumerate(groups[:3]):  # Show first 3
                group_id = group.attrib.get('id', f"group_{i}")
                transform = group.attrib.get('transform', None)
                child_count = len(list(group))
                
                if transform:
                    transform_info = parse_transform(transform)
                    print(f"  {i+1}. Group: id={group_id}, children={child_count}, transform={transform_info}")
                else:
                    print(f"  {i+1}. Group: id={group_id}, children={child_count}")
            if len(groups) > 3:
                print(f"  ... ({len(groups) - 3} more)")
        
        # Check for potential issues
        print("\nPotential issues:")
        
        # Check for elements without visual properties
        invisible_count = 0
        for elem in root.findall(".//*"):
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}')[1]
                
            if tag in ['rect', 'circle', 'ellipse', 'path', 'polygon', 'polyline']:
                fill = elem.attrib.get('fill', None)
                stroke = elem.attrib.get('stroke', None)
                
                if (fill == 'none' or not fill) and (stroke == 'none' or not stroke):
                    invisible_count += 1
        
        if invisible_count > 0:
            print(f"  - Found {invisible_count} elements with potentially invisible rendering (no fill or stroke)")
        
        # Check for elements with zero dimensions
        zero_dim_count = 0
        for rect in rects:
            w = float(rect.attrib.get('width', '0'))
            h = float(rect.attrib.get('height', '0'))
            if w <= 0 or h <= 0:
                zero_dim_count += 1
                
        if zero_dim_count > 0:
            print(f"  - Found {zero_dim_count} rectangles with zero or negative dimensions")
        
        # Check for complex transforms
        complex_transforms = 0
        for elem in root.findall(".//*[@transform]"):
            transform = elem.attrib.get('transform', '')
            if transform and ('matrix' in transform or transform.count('(') > 1):
                complex_transforms += 1
                
        if complex_transforms > 0:
            print(f"  - Found {complex_transforms} elements with complex transforms (matrix or multiple transforms)")
        
        # Final summary
        print("\nSummary:")
        print(f"  - Total elements: {sum(element_counts.values())}")
        print(f"  - Visual elements: {sum(element_counts.get(t, 0) for t in ['rect', 'circle', 'ellipse', 'path', 'polygon', 'polyline', 'text'])}")
        print(f"  - Container elements: {sum(element_counts.get(t, 0) for t in ['g', 'svg'])}")
        
        # Recommendation
        print("\nRecommendation:")
        if 'path' in element_counts and element_counts['path'] > 0:
            print("  - This SVG contains paths which require careful handling in 3D conversion")
        if complex_transforms > 0:
            print("  - Complex transforms may require special attention during conversion")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"Error analyzing SVG: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        svg_path = sys.argv[1]
        analyze_svg(svg_path)
    else:
        print("Usage: python analyze_svg.py path/to/your/file.svg")
        if input("Analyze a specific SVG file? (y/n): ").lower() == 'y':
            svg_path = input("Enter SVG file path: ")
            analyze_svg(svg_path)