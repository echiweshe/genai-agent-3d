"""
Script to better visualize SVG elements in Blender
"""

import bpy
import random

def add_debug_colors():
    """Add distinct colors to each object for debugging"""
    colors = [
        (1, 0, 0, 1),    # Red
        (0, 1, 0, 1),    # Green
        (0, 0, 1, 1),    # Blue
        (1, 1, 0, 1),    # Yellow
        (1, 0, 1, 1),    # Magenta
        (0, 1, 1, 1),    # Cyan
        (1, 0.5, 0, 1),  # Orange
        (0.5, 0, 1, 1),  # Purple
    ]
    
    for i, obj in enumerate(bpy.data.objects):
        if obj.type in ['MESH', 'CURVE', 'FONT']:
            # Create a new material with debug color
            mat_name = f"Debug_Material_{i}"
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            
            # Set up the material
            nodes = mat.node_tree.nodes
            principled = nodes.get('Principled BSDF')
            if principled:
                color = colors[i % len(colors)]
                principled.inputs['Base Color'].default_value = color
                principled.inputs['Roughness'].default_value = 0.5
                principled.inputs['Metallic'].default_value = 0.0
            
            # Set viewport color
            mat.diffuse_color = color
            
            # Clear existing materials and apply new one
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            
            # Set object color
            obj.color = color
            
            print(f"Applied color {color} to {obj.name}")

def setup_debug_view():
    """Set up the view for debugging"""
    # Set viewport shading
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            # Use solid view with color
            space.shading.type = 'SOLID'
            space.shading.color_type = 'OBJECT'
            space.shading.show_object_outline = True
            
            # Show object names
            space.overlay.show_text = True
            space.overlay.show_stats = True
            
            # Frame all objects
            override = {'area': area, 'region': area.regions[-1]}
            bpy.ops.view3d.view_all(override)

def add_debug_labels():
    """Add text labels to objects"""
    for obj in bpy.data.objects:
        if obj.type in ['MESH', 'CURVE', 'FONT'] and obj.type != 'FONT':
            # Create text object for label
            bpy.ops.object.text_add()
            text_obj = bpy.context.active_object
            text_obj.data.body = obj.name
            text_obj.data.size = 0.1
            
            # Position above the object
            text_obj.location = obj.location
            text_obj.location.z += 0.5
            
            # Make it always face camera
            constraint = text_obj.constraints.new('TRACK_TO')
            constraint.target = bpy.context.scene.camera
            constraint.track_axis = 'TRACK_Z'
            constraint.up_axis = 'UP_Y'

def main():
    """Main function"""
    print("Applying debug visualization...")
    
    # Apply debug colors
    add_debug_colors()
    
    # Set up debug view
    setup_debug_view()
    
    # Optional: Add labels
    # add_debug_labels()
    
    print("Debug visualization applied!")
    print("\nObjects in scene:")
    for obj in bpy.data.objects:
        if obj.type in ['MESH', 'CURVE', 'FONT']:
            print(f"  - {obj.name} at {obj.location}")

if __name__ == "__main__":
    main()
