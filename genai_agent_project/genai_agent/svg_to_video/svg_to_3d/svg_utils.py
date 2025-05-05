"""
Utility functions for SVG to 3D conversion.
"""

import traceback


def log(message):
    """Print a message with a prefix."""
    print(f"[SVG2-3D] {message}")


def hex_to_rgb(hex_color):
    """Convert hex color to RGB values."""
    if not hex_color or not isinstance(hex_color, str):
        return (0.8, 0.8, 0.8, 1.0)  # Default color
    
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Handle shorthand hex
    if len(hex_color) == 3:
        hex_color = ''.join([c + c for c in hex_color])
    
    # Convert to RGB
    try:
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b, 1.0)
    except (ValueError, IndexError):
        return (0.8, 0.8, 0.8, 1.0)  # Default gray


def clean_scene():
    """Remove all objects from the scene."""
    import bpy
    
    log("Cleaning scene...")
    
    # Deselect all first
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select and delete all objects
    for obj in bpy.data.objects:
        obj.select_set(True)
    
    # Delete selected objects
    if bpy.context.selected_objects:
        bpy.ops.object.delete()
    
    # Clean materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    log("Scene cleaned")
