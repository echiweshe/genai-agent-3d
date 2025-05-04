"""
Check imports for SVG to 3D converter modules

This script verifies that all modules can be imported correctly.
"""

import sys
import os
import importlib

# Add the parent directories to Python path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
if svg_to_3d_dir not in sys.path:
    sys.path.append(svg_to_3d_dir)

def check_imports():
    """Check if all modules can be imported"""
    modules = [
        'svg_utils',
        'svg_parser',
        'svg_parser_elements',
        'svg_parser_paths',
        'svg_converter',
        'svg_converter_create',
        'svg_converter_path',
        'svg_converter_group',
        'svg_converter_scene'
    ]
    
    results = {}
    
    print("Checking module imports...")
    print("-" * 40)
    
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            results[module_name] = {
                'status': 'success',
                'functions': [item for item in dir(module) if not item.startswith('_')]
            }
            print(f"✓ {module_name}: OK")
        except Exception as e:
            results[module_name] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"✗ {module_name}: FAILED - {e}")
    
    # Check for circular imports or other issues
    print("\nDetailed module information:")
    print("-" * 40)
    
    for module_name, result in results.items():
        print(f"\n{module_name}:")
        if result['status'] == 'success':
            print(f"  Functions: {', '.join(result['functions'][:10])}")
            if len(result['functions']) > 10:
                print(f"  ... and {len(result['functions']) - 10} more")
        else:
            print(f"  Error: {result['error']}")
    
    # Test import chain
    print("\nTesting import chain...")
    print("-" * 40)
    
    try:
        from svg_parser import SVGParser
        from svg_converter import SVGTo3DConverter
        print("✓ Main classes can be imported")
        
        # Test instantiation
        parser = SVGParser()
        converter = SVGTo3DConverter()
        print("✓ Main classes can be instantiated")
        
    except Exception as e:
        print(f"✗ Import chain failed: {e}")
    
    return results

if __name__ == "__main__":
    print("SVG to 3D Converter - Import Check")
    print("=" * 40)
    check_imports()
