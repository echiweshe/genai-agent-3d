"""
Final comprehensive test showing all working features
"""

import os
import sys
import bpy
import traceback
import importlib
import gc

# Add the parent directories to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
if svg_to_3d_dir not in sys.path:
    sys.path.insert(0, svg_to_3d_dir)

# Force cleanup and reload of modules
def cleanup_and_reload():
    """Force cleanup and reload of modules"""
    # Remove all cached modules
    modules_to_remove = []
    for name, module in sys.modules.items():
        if 'svg_' in name and 'svg_to_3d' in str(module):
            modules_to_remove.append(name)
    
    for name in modules_to_remove:
        if name in sys.modules:
            del sys.modules[name]
    
    # Force garbage collection
    gc.collect()
    
    # Now import fresh modules
    import svg_utils
    import svg_parser_elements  
    import svg_parser_paths
    import svg_parser
    import svg_converter_materials_final
    import svg_converter_create
    import svg_converter_path
    import svg_converter_group
    import svg_converter_scene
    import svg_to_3d_converter_new
    
    print("Modules cleaned and reloaded!")

# Clean and reload
cleanup_and_reload()

# Now import our modules
from svg_parser import SVGParser
from svg_to_3d_converter_new import SVGTo3DConverter
from svg_utils import log

def create_comprehensive_test_svg():
    """Create a comprehensive test SVG with all working features"""
    test_svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg">
    <!-- Title -->
    <text x="600" y="50" font-size="36" text-anchor="middle" fill="#000000">SVG to 3D Feature Test</text>
    
    <!-- Row 1: Basic Shapes with Colors -->
    <text x="100" y="120" font-size="24" fill="#000000">Basic Shapes</text>
    
    <rect x="100" y="150" width="120" height="80" fill="#ff0000" />
    <text x="160" y="260" text-anchor="middle" font-size="16">Red Rect</text>
    
    <rect x="250" y="150" width="120" height="80" fill="#00ff00" rx="15" ry="15" />
    <text x="310" y="260" text-anchor="middle" font-size="16">Green Rounded</text>
    
    <circle cx="460" cy="190" r="40" fill="#0000ff" />
    <text x="460" y="260" text-anchor="middle" font-size="16">Blue Circle</text>
    
    <ellipse cx="610" cy="190" rx="60" ry="30" fill="#ff00ff" />
    <text x="610" y="260" text-anchor="middle" font-size="16">Magenta Ellipse</text>
    
    <!-- Row 2: Stroke and Fill Combinations -->
    <text x="100" y="320" font-size="24" fill="#000000">Stroke & Fill</text>
    
    <rect x="100" y="350" width="120" height="80" fill="none" stroke="#ff0000" stroke-width="8" />
    <text x="160" y="460" text-anchor="middle" font-size="16">Stroke Only</text>
    
    <rect x="250" y="350" width="120" height="80" fill="#00ff00" stroke="#000000" stroke-width="8" />
    <text x="310" y="460" text-anchor="middle" font-size="16">Fill + Stroke</text>
    
    <circle cx="460" cy="390" r="40" fill="#0000ff" stroke="#ffff00" stroke-width="8" />
    <text x="460" y="460" text-anchor="middle" font-size="16">Circle Both</text>
    
    <!-- Row 3: Transparency -->
    <text x="100" y="520" font-size="24" fill="#000000">Transparency</text>
    
    <rect x="100" y="550" width="120" height="80" fill="#ff0000" opacity="0.5" />
    <text x="160" y="660" text-anchor="middle" font-size="16">50% Opacity</text>
    
    <circle cx="310" cy="590" r="40" fill="#00ff00" fill-opacity="0.3" />
    <text x="310" y="660" text-anchor="middle" font-size="16">30% Fill</text>
    
    <circle cx="460" cy="590" r="40" fill="none" stroke="#0000ff" stroke-width="8" stroke-opacity="0.6" />
    <text x="460" y="660" text-anchor="middle" font-size="16">60% Stroke</text>
    
    <!-- Complex Shapes -->
    <text x="750" y="120" font-size="24" fill="#000000">Complex Shapes</text>
    
    <polygon points="800,150 850,150 875,190 850,230 800,230 775,190" fill="#ffff00" stroke="#ff0000" stroke-width="4" />
    <text x="825" y="260" text-anchor="middle" font-size="16">Hexagon</text>
    
    <path d="M950,150 L1050,150 L1000,230 Z" fill="#00ffff" stroke="#000000" stroke-width="4" />
    <text x="1000" y="260" text-anchor="middle" font-size="16">Triangle</text>
    
    <polyline points="750,350 800,400 850,350 900,400 950,350" fill="none" stroke="#ff00ff" stroke-width="6" />
    <text x="850" y="460" text-anchor="middle" font-size="16">Polyline</text>
    
    <path d="M750,550 Q800,500 850,550 T950,550" fill="none" stroke="#0088ff" stroke-width="8" stroke-linecap="round" />
    <text x="850" y="620" text-anchor="middle" font-size="16">Curved Path</text>
</svg>"""
    
    # Save the test SVG
    test_svg_path = os.path.join(os.path.dirname(__file__), 'comprehensive_test.svg')
    with open(test_svg_path, 'w', encoding='utf-8') as f:
        f.write(test_svg_content)
    
    return test_svg_path

def clear_scene():
    """Clear the Blender scene completely"""
    # Select all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear all data blocks
    for block_type in [bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights]:
        for block in block_type:
            block_type.remove(block)

def test_all_features():
    """Test all working features"""
    try:
        log("=" * 50)
        log("Comprehensive Feature Test")
        log("=" * 50)
        
        # Clear scene
        log("Clearing scene...")
        clear_scene()
        
        # Create test SVG
        log("Creating comprehensive test SVG...")
        svg_file = create_comprehensive_test_svg()
        
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
            scale_factor=0.005,
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
        
        # Set viewport to material preview
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.use_scene_lights = True
                        space.shading.use_scene_world = False
                        space.shading.studio_light = 'studio.exr'
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), 'comprehensive_output.blend')
        bpy.ops.wm.save_as_mainfile(filepath=output_file)
        log(f"\nSaved to: {output_file}")
        
        # Frame all objects
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces.active:
                    if space.type == 'VIEW_3D':
                        with bpy.context.temp_override(area=area, space_data=space):
                            bpy.ops.view3d.view_all()
                            bpy.ops.view3d.view_axis(type='FRONT')
                break
        
        log("\nTest completed successfully!")
        log("\nFeatures demonstrated:")
        log("- Basic shapes with colors (rectangles, circles, ellipses)")
        log("- Rounded rectangles")
        log("- Stroke only, fill only, and combined")
        log("- Transparency (opacity, fill-opacity, stroke-opacity)")
        log("- Complex shapes (polygons, paths, polylines)")
        log("- Text elements")
        
        return True
        
    except Exception as e:
        log(f"ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_all_features()
