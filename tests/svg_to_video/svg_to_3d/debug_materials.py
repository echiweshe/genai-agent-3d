"""
Debug script to check materials in the test output
"""

import bpy
import os
import sys

# Add the parent directories to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
svg_to_3d_dir = os.path.join(project_root, 'genai_agent', 'svg_to_video', 'svg_to_3d')
if svg_to_3d_dir not in sys.path:
    sys.path.insert(0, svg_to_3d_dir)

from svg_utils import log

def debug_materials():
    """Debug materials in the scene"""
    log("=" * 50)
    log("Material Debug Information")
    log("=" * 50)
    
    # List all materials
    log(f"Materials in scene: {len(bpy.data.materials)}")
    for mat in bpy.data.materials:
        log(f"  - {mat.name}")
        if mat.use_nodes:
            log(f"    Uses nodes: Yes")
            log(f"    Blend method: {mat.blend_method}")
            
            # Check for principled BSDF
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    log(f"    Has Principled BSDF")
                    if 'Base Color' in node.inputs:
                        color = node.inputs['Base Color'].default_value
                        log(f"    Base Color: {color}")
    
    # List all objects and their materials
    log("\nObjects and their materials:")
    for obj in bpy.data.objects:
        log(f"  - {obj.name} (Type: {obj.type})")
        if hasattr(obj.data, 'materials'):
            if len(obj.data.materials) > 0:
                for i, mat in enumerate(obj.data.materials):
                    if mat:
                        log(f"    Material {i}: {mat.name}")
                    else:
                        log(f"    Material {i}: None")
            else:
                log("    No materials assigned")
        else:
            log("    Object type doesn't support materials")

if __name__ == "__main__":
    debug_materials()
