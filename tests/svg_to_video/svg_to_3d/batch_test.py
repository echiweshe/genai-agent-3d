"""
Batch test script for SVG to 3D converter

This script tests the converter with multiple SVG files to ensure robustness.
"""

import os
import sys
import bpy
import traceback
import json
from datetime import datetime

# Add the parent directories to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
if svg_to_3d_dir not in sys.path:
    sys.path.append(svg_to_3d_dir)

from svg_parser import SVGParser
from svg_converter import SVGTo3DConverter
from svg_utils import log

def create_test_svgs():
    """Create various test SVG files"""
    test_svgs = {
        'simple_shapes.svg': """<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
    <rect x="50" y="50" width="100" height="100" fill="#ff0000" />
    <circle cx="250" cy="100" r="40" fill="#00ff00" />
    <ellipse cx="150" cy="250" rx="60" ry="30" fill="#0000ff" />
</svg>""",
        
        'complex_paths.svg': """<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
    <path d="M50,50 L150,50 Q200,100 150,150 C100,200 50,150 50,100 Z" fill="#ff00ff" />
    <path d="M250,50 L350,50 L300,150 Z" fill="#00ffff" />
</svg>""",
        
        'text_elements.svg': """<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
    <text x="50" y="100" font-size="24" fill="#000000">Hello</text>
    <text x="50" y="200" font-size="36" font-family="Arial" fill="#ff0000">World</text>
</svg>""",
        
        'grouped_elements.svg': """<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(100, 100)">
        <rect x="0" y="0" width="50" height="50" fill="#ff0000" />
        <circle cx="25" cy="25" r="15" fill="#ffffff" />
    </g>
    <g transform="rotate(45 200 200)">
        <rect x="175" y="175" width="50" height="50" fill="#00ff00" />
    </g>
</svg>""",
        
        'edge_cases.svg': """<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Empty path -->
    <path d="" fill="#ff0000" />
    
    <!-- Very small circle -->
    <circle cx="100" cy="100" r="0.5" fill="#00ff00" />
    
    <!-- Polygon with 2 points -->
    <polygon points="200,200 300,200" fill="#0000ff" />
    
    <!-- Text with special characters -->
    <text x="50" y="300" font-size="20" fill="#000000">Test &amp; Debug</text>
</svg>"""
    }
    
    # Create test files
    test_dir = os.path.join(current_dir, 'test_svgs')
    os.makedirs(test_dir, exist_ok=True)
    
    for filename, content in test_svgs.items():
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return test_dir

def run_single_test(svg_file, output_dir):
    """Run a test on a single SVG file"""
    test_result = {
        'file': os.path.basename(svg_file),
        'status': 'unknown',
        'parse_success': False,
        'convert_success': False,
        'objects_created': 0,
        'error': None,
        'details': {}
    }
    
    try:
        # Clear the scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Parse SVG
        parser = SVGParser()
        svg_data = parser.parse(svg_file)
        
        if svg_data:
            test_result['parse_success'] = True
            test_result['details']['elements'] = len(svg_data['elements'])
            test_result['details']['width'] = svg_data['width']
            test_result['details']['height'] = svg_data['height']
            
            # Convert to 3D
            converter = SVGTo3DConverter()
            result = converter.convert(svg_data)
            
            if result:
                test_result['convert_success'] = True
                test_result['objects_created'] = len(bpy.data.objects)
                test_result['status'] = 'success'
                
                # Save output
                output_file = os.path.join(output_dir, 
                    os.path.splitext(os.path.basename(svg_file))[0] + '.blend')
                bpy.ops.wm.save_as_mainfile(filepath=output_file)
            else:
                test_result['status'] = 'conversion_failed'
        else:
            test_result['status'] = 'parse_failed'
            
    except Exception as e:
        test_result['status'] = 'error'
        test_result['error'] = str(e)
        print(f"Error testing {svg_file}: {e}")
        traceback.print_exc()
    
    return test_result

def run_batch_test():
    """Run batch tests on multiple SVG files"""
    print("=" * 60)
    print("SVG to 3D Converter Batch Test")
    print("=" * 60)
    
    # Create test SVGs
    test_dir = create_test_svgs()
    output_dir = os.path.join(current_dir, 'test_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of SVG files
    svg_files = [f for f in os.listdir(test_dir) if f.endswith('.svg')]
    
    print(f"\nFound {len(svg_files)} test SVG files")
    
    # Run tests
    results = []
    for i, svg_file in enumerate(svg_files):
        print(f"\nTesting {i+1}/{len(svg_files)}: {svg_file}")
        svg_path = os.path.join(test_dir, svg_file)
        result = run_single_test(svg_path, output_dir)
        results.append(result)
        print(f"Result: {result['status']}")
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(results),
        'passed': sum(1 for r in results if r['status'] == 'success'),
        'failed': sum(1 for r in results if r['status'] != 'success'),
        'results': results
    }
    
    # Save report
    report_file = os.path.join(output_dir, 'test_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("BATCH TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print("\nDetailed results:")
    for result in results:
        status_symbol = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_symbol} {result['file']}: {result['status']}")
        if result['error']:
            print(f"  Error: {result['error']}")
    
    print(f"\nReport saved to: {report_file}")
    print(f"Output files saved to: {output_dir}")

if __name__ == "__main__":
    run_batch_test()
