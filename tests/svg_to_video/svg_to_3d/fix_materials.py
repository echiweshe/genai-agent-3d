"""
Script to fix material visibility issues in the SVG to 3D converter output
"""

import bpy
import os

def fix_curve_materials():
    """Fix materials for curve objects"""
    for obj in bpy.data.objects:
        if obj.type == 'CURVE':
            # Set curve settings for better visibility
            obj.data.fill_mode = 'BOTH'
            obj.data.use_fill_caps = True
            
            # Ensure material is applied
            if obj.data.materials:
                for mat in obj.data.materials:
                    if mat:
                        # Set viewport display color
                        mat.use_nodes = True
                        if 'Principled BSDF' in mat.node_tree.nodes:
                            principled = mat.node_tree.nodes['Principled BSDF']
                            base_color = principled.inputs['Base Color'].default_value
                            mat.diffuse_color = base_color
                        
                        # Enable viewport display
                        mat.use_backface_culling = False
                        obj.show_wire = False
                        obj.show_in_front = False

def fix_mesh_materials():
    """Fix materials for mesh objects"""
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Ensure material is applied
            if obj.data.materials:
                for mat in obj.data.materials:
                    if mat:
                        mat.use_backface_culling = False
                        
                        # Set viewport shading
                        if mat.use_nodes:
                            if 'Principled BSDF' in mat.node_tree.nodes:
                                principled = mat.node_tree.nodes['Principled BSDF']
                                base_color = principled.inputs['Base Color'].default_value
                                mat.diffuse_color = base_color

def fix_viewport_settings():
    """Fix viewport settings for better material visibility"""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # Set material preview mode
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = False
                    
                    # Set color management
                    space.shading.color_type = 'MATERIAL'
                    
                    # Enable overlays
                    space.overlay.show_overlays = True
                    
                    # Set studio lighting
                    space.shading.studio_light = 'studio.exr'
                    space.shading.studiolight_rotate_z = 0
                    space.shading.studiolight_intensity = 1.0

def apply_fixes():
    """Apply all fixes"""
    print("Applying material fixes...")
    
    # Fix materials
    fix_curve_materials()
    fix_mesh_materials()
    
    # Fix viewport
    fix_viewport_settings()
    
    # Update viewport
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    
    print("Material fixes applied!")
    
    # List materials
    print("\nMaterials in scene:")
    for mat in bpy.data.materials:
        print(f"  - {mat.name}")
        if mat.use_nodes and 'Principled BSDF' in mat.node_tree.nodes:
            principled = mat.node_tree.nodes['Principled BSDF']
            base_color = principled.inputs['Base Color'].default_value
            print(f"    Base Color: {base_color}")

if __name__ == "__main__":
    apply_fixes()
