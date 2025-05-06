"""
SVG to 3D Converter Scene Module

This module contains methods for setting up the Blender scene,
including camera, lighting, and rendering settings.
"""

import bpy
import os
import math
from mathutils import Vector
from .svg_utils import log


def setup_camera_and_lighting(self):
    """Set up camera and lighting for the 3D scene."""
    try:
        log("Setting up camera and lighting...")
        
        # Remove existing cameras and lights
        for obj in bpy.data.objects:
            if obj.type in ['CAMERA', 'LIGHT']:
                bpy.data.objects.remove(obj, do_unlink=True)
        
        # Create a new camera
        camera_data = bpy.data.cameras.new("SVGCamera")
        camera = bpy.data.objects.new("SVGCamera", camera_data)
        bpy.context.collection.objects.link(camera)
        
        # Set camera as active camera
        bpy.context.scene.camera = camera
        
        # Position the camera to view the entire scene
        # Calculate a good distance based on scene dimensions
        max_dim = max(self.width, self.height) * self.scale_factor
        camera.location = (0, 0, max_dim * 2.5)  # Position above the scene
        camera.rotation_euler = (0, 0, 0)        # Point down
        
        # Set orthographic camera for 2D-like view
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = max_dim * 1.2  # Set ortho scale to fit scene
        
        # Add three-point lighting for better 3D rendering
        # Key light (main light)
        key_light_data = bpy.data.lights.new("KeyLight", type='SUN')
        key_light_data.energy = 2.0
        key_light = bpy.data.objects.new("KeyLight", key_light_data)
        bpy.context.collection.objects.link(key_light)
        key_light.location = (max_dim, -max_dim, max_dim * 2)
        key_light.rotation_euler = (math.radians(45), math.radians(0), math.radians(45))
        
        # Fill light (softer light from opposite side)
        fill_light_data = bpy.data.lights.new("FillLight", type='SUN')
        fill_light_data.energy = 1.0
        fill_light = bpy.data.objects.new("FillLight", fill_light_data)
        bpy.context.collection.objects.link(fill_light)
        fill_light.location = (-max_dim, max_dim, max_dim)
        fill_light.rotation_euler = (math.radians(45), math.radians(0), math.radians(-135))
        
        # Back light (rim light from behind)
        back_light_data = bpy.data.lights.new("BackLight", type='SUN')
        back_light_data.energy = 1.5
        back_light = bpy.data.objects.new("BackLight", back_light_data)
        bpy.context.collection.objects.link(back_light)
        back_light.location = (0, 0, -max_dim)
        back_light.rotation_euler = (math.radians(-45), 0, 0)
        
        # Set up scene rendering settings
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.context.scene.render.film_transparent = True  # Transparent background
        
        log("Camera and lighting setup complete")
        return True
    except Exception as e:
        log(f"Error setting up camera and lighting: {e}")
        return False


def setup_default_view(self):
    """Set up the default view in Blender."""
    try:
        # Set up view for all 3D viewports
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.region_3d.view_perspective = 'ORTHO'  # Orthographic view
                space.region_3d.view_rotation = (1, 0, 0, 0)  # Top view
                
                # Set view to camera view
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region}
                        bpy.ops.view3d.view_camera(override)
                        break
        
        log("Default view setup complete")
        return True
    except Exception as e:
        log(f"Error setting up default view: {e}")
        return False


def setup_startup_script(self, scene_objects):
    """Create a startup script for setting up the view when file is opened."""
    try:
        # Select all objects for the setup script
        for obj in scene_objects:
            obj.select_set(True)
        
        # Create a text object for the startup script
        script_text = bpy.data.texts.new("startup_script.py")
        script_text.write("""
import bpy

# Function to setup view
def setup_view():
    # Select all objects
    bpy.ops.object.select_all(action='SELECT')
    
    # Frame selected objects
    bpy.ops.view3d.view_selected(use_all_regions=False)
    
    # Set to orthographic view
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'ORTHO'
            break

# Register the startup handler
bpy.app.handlers.load_post.append(lambda dummy: setup_view())
""")
        
        # Set startup script to run on file load
        bpy.context.scene.use_nodes = True  # Enable nodes to allow script execution
        
        log("Startup script created")
        return True
    except Exception as e:
        log(f"Error setting up startup script: {e}")
        return False
