"""
Model animation module for the SVG to Video pipeline.

This module provides functionality to animate 3D models created from SVG diagrams.
"""

import os
import sys
import logging
import tempfile
import subprocess
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ModelAnimator:
    """
    Class for animating 3D models created from SVGs.
    
    This class provides methods to apply animations to 3D models
    using Blender.
    """
    
    def __init__(self, blender_path=None):
        """
        Initialize the ModelAnimator.
        
        Args:
            blender_path (str, optional): Path to the Blender executable.
                If not provided, it will try to get it from the environment.
        """
        # Get Blender path
        self.blender_path = blender_path
        
        if not self.blender_path:
            # Try to get from environment
            self.blender_path = os.environ.get("BLENDER_PATH")
            
            if not self.blender_path:
                # Try to find Blender in common locations
                common_paths = [
                    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                    r"/usr/bin/blender",
                    r"/Applications/Blender.app/Contents/MacOS/Blender"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        self.blender_path = path
                        break
        
        if not self.blender_path or not os.path.exists(self.blender_path):
            logger.warning("Blender executable not found. Animation functionality will be limited.")
    
    def animate_model(self, model_path, output_path=None, animation_type="simple", duration=10.0, **kwargs):
        """
        Animate a 3D model using Blender.
        
        Args:
            model_path (str): Path to the input 3D model file
            output_path (str, optional): Path to save the animated model file
            animation_type (str, optional): Type of animation to apply
                Options: "simple", "rotate", "explode", "flow", "network"
            duration (float, optional): Duration of the animation in seconds
            **kwargs: Additional animation parameters
                - fps (int): Frames per second
                - highlight_color (tuple): RGB color for highlighting (0.0-1.0)
                - camera_distance (float): Distance of camera from model
                - rotation_axis (str): Axis for rotation animation ("X", "Y", "Z")
                - rotation_speed (float): Speed of rotation animation
        
        Returns:
            str: Path to the animated model file, or None if animation failed
        """
        # Validate input
        if not model_path or not os.path.exists(model_path):
            logger.error(f"Input model file not found: {model_path}")
            return None
        
        # Handle output path
        if not output_path:
            # Generate output file name based on input file
            model_name = os.path.basename(model_path)
            model_dir = os.path.dirname(model_path)
            animations_dir = os.path.join(os.path.dirname(os.path.dirname(model_dir)), "animations")
            
            # Ensure animations directory exists
            os.makedirs(animations_dir, exist_ok=True)
            
            # Create output path
            output_path = os.path.join(
                animations_dir,
                f"{os.path.splitext(model_name)[0]}_animated.blend"
            )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if Blender is available
        if not self.blender_path:
            logger.error("Blender not available. Cannot animate model.")
            return None
        
        # Get animation script based on type
        animation_script = self._get_animation_script(
            model_path, 
            output_path, 
            animation_type, 
            duration, 
            **kwargs
        )
        
        if not animation_script:
            logger.error(f"Failed to generate animation script for type: {animation_type}")
            return None
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
            temp_script.write(animation_script)
            temp_script_path = temp_script.name
        
        try:
            # Run Blender with the script
            cmd = [
                self.blender_path,
                '--background',
                '--python', temp_script_path
            ]
            
            logger.info(f"Running Blender command: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Blender process failed with code {process.returncode}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return None
            
            # Check if output file was created
            if os.path.exists(output_path):
                logger.info(f"Model animation successful: {output_path}")
                return output_path
            else:
                logger.error(f"Output file not created: {output_path}")
                return None
        
        except Exception as e:
            logger.error(f"Error running Blender process: {str(e)}")
            return None
        
        finally:
            # Clean up temporary script
            try:
                os.unlink(temp_script_path)
            except:
                pass
    
    def _get_animation_script(self, model_path, output_path, animation_type, duration, **kwargs):
        """
        Get the appropriate animation script based on the animation type.
        
        Args:
            model_path (str): Path to the input 3D model file
            output_path (str): Path to save the animated model file
            animation_type (str): Type of animation to apply
            duration (float): Duration of the animation in seconds
            **kwargs: Additional animation parameters
        
        Returns:
            str: Blender Python script content for the animation
        """
        # Get parameters with defaults
        fps = kwargs.get('fps', 30)
        total_frames = int(duration * fps)
        highlight_color = kwargs.get('highlight_color', (0.8, 0.2, 0.2))
        camera_distance = kwargs.get('camera_distance', 10.0)
        rotation_axis = kwargs.get('rotation_axis', 'Z')
        rotation_speed = kwargs.get('rotation_speed', 1.0)
        
        # Base script template
        base_script = f'''
import bpy
import os
import math
import random
from mathutils import Vector, Matrix, Quaternion

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

# Set animation parameters
fps = {fps}
duration = {duration}
total_frames = {total_frames}

# Set render settings
bpy.context.scene.render.fps = fps
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = total_frames

# Import the model
model_path = r"{model_path}"
output_path = r"{output_path}"

# Detect file format from extension
_, ext = os.path.splitext(model_path)
ext = ext.lower()

if ext == '.obj':
    bpy.ops.import_scene.obj(filepath=model_path)
elif ext == '.fbx':
    bpy.ops.import_scene.fbx(filepath=model_path)
elif ext == '.stl':
    bpy.ops.import_mesh.stl(filepath=model_path)
elif ext == '.glb' or ext == '.gltf':
    bpy.ops.import_scene.gltf(filepath=model_path)
elif ext == '.x3d':
    bpy.ops.import_scene.x3d(filepath=model_path)
elif ext == '.blend':
    # We need to append from the blend file instead of importing
    with bpy.data.libraries.load(model_path) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    # Link objects to scene
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
else:
    print(f"Unsupported file format: {ext}")
    import sys
    sys.exit(1)

# Select all objects in the scene
bpy.ops.object.select_all(action='SELECT')

# Group objects into a collection for easier animation
collection_name = "Model"
anim_collection = bpy.data.collections.new(collection_name)
bpy.context.scene.collection.children.link(anim_collection)

for obj in bpy.context.selected_objects:
    # Unlink from current collection
    bpy.context.scene.collection.objects.unlink(obj)
    # Link to new collection
    anim_collection.objects.link(obj)

# Set up basic camera and lighting
bpy.ops.object.camera_add(location=(0, -15, 8), rotation=(math.radians(60), 0, 0))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0

bpy.ops.object.light_add(type='AREA', location=(0, -8, 8))
fill = bpy.context.active_object
fill.data.energy = 3.0

# Set up environment
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs[0].default_value = (0.9, 0.9, 0.95, 1.0)  # Light blue-gray background
    bg_node.inputs[1].default_value = 1.0  # Strength

# Get all mesh objects
mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
if not mesh_objects:
    print("No mesh objects found in the scene")
    import sys
    sys.exit(1)
'''

        # Add animation-specific script based on the type
        if animation_type == "simple":
            script = base_script + self._get_simple_animation_script(fps, total_frames, **kwargs)
        elif animation_type == "rotate":
            script = base_script + self._get_rotate_animation_script(fps, total_frames, rotation_axis, rotation_speed, **kwargs)
        elif animation_type == "explode":
            script = base_script + self._get_explode_animation_script(fps, total_frames, **kwargs)
        elif animation_type == "flow":
            script = base_script + self._get_flow_animation_script(fps, total_frames, **kwargs)
        elif animation_type == "network":
            script = base_script + self._get_network_animation_script(fps, total_frames, **kwargs)
        else:
            # Default to simple animation
            logger.warning(f"Unknown animation type: {animation_type}. Using simple animation.")
            script = base_script + self._get_simple_animation_script(fps, total_frames, **kwargs)
        
        # Add the save code to the script
        script += f'''
# Save the file
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"Animation completed and saved to {output_path}")
'''
        
        return script
    
    def _get_simple_animation_script(self, fps, total_frames, **kwargs):
        """Get script for simple animation (fade in, rotate, scale)."""
        return f'''
# Create a simple animation - fade in, rotate, and scale
print("Creating simple animation...")

# Center all objects at origin
bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objects:
    obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.location_clear()

# Get the bounds of all objects combined
min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

for obj in mesh_objects:
    for v in obj.bound_box:
        world_v = obj.matrix_world @ Vector(v)
        min_x = min(min_x, world_v.x)
        min_y = min(min_y, world_v.y)
        min_z = min(min_z, world_v.z)
        max_x = max(max_x, world_v.x)
        max_y = max(max_y, world_v.y)
        max_z = max(max_z, world_v.z)

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2
size = max(max_x - min_x, max_y - min_y, max_z - min_z)

# Position camera to see the entire model
camera.location = Vector((center_x, center_y - size * 2, center_z + size * 0.8))
camera.rotation_euler = (math.radians(60), 0, 0)

# Create an empty as the center of rotation
bpy.ops.object.empty_add(location=(center_x, center_y, center_z))
empty = bpy.context.active_object
empty.name = "AnimationCenter"

# Parent all mesh objects to the empty
for obj in mesh_objects:
    obj.select_set(True)
    empty.select_set(True)
    bpy.context.view_layer.objects.active = empty
    bpy.ops.object.parent_set(type='OBJECT')
    empty.select_set(False)
    obj.select_set(False)

# Create material for objects
for obj in mesh_objects:
    # Create new material
    mat_name = f"AnimMaterial_{obj.name}"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        # Set initial values
        principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)  # White
        principled.inputs['Metallic'].default_value = 0.5
        principled.inputs['Roughness'].default_value = 0.3
        principled.inputs['Alpha'].default_value = 0.0  # Start transparent
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Animation: Fade in
fade_in_frames = int(total_frames * 0.3)  # 30% of the animation is fade in
for obj in mesh_objects:
    mat = obj.data.materials[0]
    principled = mat.node_tree.nodes.get('Principled BSDF')
    
    # Set alpha to 0 at frame 1
    principled.inputs['Alpha'].default_value = 0
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=1)
    
    # Set alpha to 1 at end of fade in
    principled.inputs['Alpha'].default_value = 1
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=fade_in_frames)
    
    # Add easing to the fade in
    for fcurve in obj.data.materials[0].node_tree.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'EASE_IN_OUT'

# Animation: Rotate the empty
rotate_start_frame = int(total_frames * 0.2)  # Start rotation at 20% of the animation
rotate_end_frame = total_frames

# Set initial rotation
empty.rotation_euler = (0, 0, 0)
empty.keyframe_insert(data_path="rotation_euler", frame=rotate_start_frame)

# Set final rotation (one full revolution)
empty.rotation_euler = (0, 0, math.radians(360))
empty.keyframe_insert(data_path="rotation_euler", frame=rotate_end_frame)

# Add easing to the rotation
for fcurve in empty.animation_data.action.fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'EASE_IN_OUT'

# Animation: Highlight objects sequentially
if len(mesh_objects) > 1:
    highlight_duration = int(total_frames * 0.6 / len(mesh_objects))
    for i, obj in enumerate(mesh_objects):
        mat = obj.data.materials[0]
        principled = mat.node_tree.nodes.get('Principled BSDF')
        
        # Calculate highlight frames
        highlight_start = int(total_frames * 0.3) + i * highlight_duration
        highlight_mid = highlight_start + int(highlight_duration * 0.3)
        highlight_end = highlight_start + highlight_duration
        
        # Set normal color before highlight
        principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=highlight_start)
        
        # Set highlight color at middle of highlight duration
        principled.inputs['Base Color'].default_value = (1.0, 0.6, 0.2, 1.0)  # Orange highlight
        principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=highlight_mid)
        
        # Set back to normal color at end of highlight
        principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=highlight_end)
'''

    def _get_rotate_animation_script(self, fps, total_frames, rotation_axis, rotation_speed, **kwargs):
        """Get script for rotation animation."""
        return f'''
# Create a rotation animation
print("Creating rotation animation...")

# Center all objects at origin
bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objects:
    obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.location_clear()

# Get the bounds of all objects combined
min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

for obj in mesh_objects:
    for v in obj.bound_box:
        world_v = obj.matrix_world @ Vector(v)
        min_x = min(min_x, world_v.x)
        min_y = min(min_y, world_v.y)
        min_z = min(min_z, world_v.z)
        max_x = max(max_x, world_v.x)
        max_y = max(max_y, world_v.y)
        max_z = max(max_z, world_v.z)

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2
size = max(max_x - min_x, max_y - min_y, max_z - min_z)

# Position camera to see the entire model
camera.location = Vector((center_x, center_y - size * 2, center_z + size * 0.8))
camera.rotation_euler = (math.radians(60), 0, 0)

# Create an empty as the center of rotation
bpy.ops.object.empty_add(location=(center_x, center_y, center_z))
empty = bpy.context.active_object
empty.name = "RotationCenter"

# Parent all mesh objects to the empty
for obj in mesh_objects:
    obj.select_set(True)
    empty.select_set(True)
    bpy.context.view_layer.objects.active = empty
    bpy.ops.object.parent_set(type='OBJECT')
    empty.select_set(False)
    obj.select_set(False)

# Apply materials
for obj in mesh_objects:
    # Create new material
    mat_name = f"RotateMaterial_{obj.name}"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        # Set values
        principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        principled.inputs['Metallic'].default_value = 0.7
        principled.inputs['Roughness'].default_value = 0.2
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Animation: Rotate the empty
num_rotations = {rotation_speed} * (duration / 10.0)  # Scale rotation speed with duration
rotation_degrees = 360 * num_rotations

# Set initial rotation
empty.rotation_euler = (0, 0, 0)
empty.keyframe_insert(data_path="rotation_euler", frame=1)

# Set rotation axis
if "{rotation_axis}".upper() == "X":
    empty.rotation_euler = (math.radians(rotation_degrees), 0, 0)
elif "{rotation_axis}".upper() == "Y":
    empty.rotation_euler = (0, math.radians(rotation_degrees), 0)
else:  # Default to Z
    empty.rotation_euler = (0, 0, math.radians(rotation_degrees))

empty.keyframe_insert(data_path="rotation_euler", frame=total_frames)

# Add camera movement
# Start with a wider view
camera.location = Vector((center_x, center_y - size * 2.5, center_z + size))
camera.keyframe_insert(data_path="location", frame=1)

# Move to a closer view at 1/3 of the animation
closer_frame = int(total_frames / 3)
camera.location = Vector((center_x, center_y - size * 2, center_z + size * 0.7))
camera.keyframe_insert(data_path="location", frame=closer_frame)

# Move to a different angle at 2/3 of the animation
angle_frame = int(total_frames * 2 / 3)
camera.location = Vector((center_x + size, center_y - size * 1.5, center_z + size * 0.5))
camera.keyframe_insert(data_path="location", frame=angle_frame)

# Return to the starting position
camera.location = Vector((center_x, center_y - size * 2.5, center_z + size))
camera.keyframe_insert(data_path="location", frame=total_frames)

# Add easing to the camera movement
for fcurve in camera.animation_data.action.fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'BEZIER'
        kf.handle_left_type = 'AUTO'
        kf.handle_right_type = 'AUTO'
'''

    def _get_explode_animation_script(self, fps, total_frames, **kwargs):
        """Get script for explosion animation (objects move outward from center)."""
        return f'''
# Create an explosion animation
print("Creating explosion animation...")

# Center all objects at origin
bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objects:
    obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.location_clear()

# Get the bounds of all objects combined
min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

for obj in mesh_objects:
    for v in obj.bound_box:
        world_v = obj.matrix_world @ Vector(v)
        min_x = min(min_x, world_v.x)
        min_y = min(min_y, world_v.y)
        min_z = min(min_z, world_v.z)
        max_x = max(max_x, world_v.x)
        max_y = max(max_y, world_v.y)
        max_z = max(max_z, world_v.z)

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2
size = max(max_x - min_x, max_y - min_y, max_z - min_z)
center = Vector((center_x, center_y, center_z))

# Position camera to see the entire animation
camera.location = Vector((center_x, center_y - size * 3, center_z + size))
camera.rotation_euler = (math.radians(60), 0, 0)

# Apply materials
for obj in mesh_objects:
    # Create new material
    mat_name = f"ExplodeMaterial_{obj.name}"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        # Set values
        color = (random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), 1.0)
        principled.inputs['Base Color'].default_value = color
        principled.inputs['Metallic'].default_value = 0.5
        principled.inputs['Roughness'].default_value = 0.3
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Animation: Move objects outward from center
# Calculate start frame for explosion (after a brief pause)
start_frame = int(total_frames * 0.1)
mid_frame = int(total_frames * 0.5)
end_frame = total_frames

# Define the explosion strength
explosion_strength = size * 1.5

# Move objects to center at start
for obj in mesh_objects:
    # Store original location
    obj["original_location"] = obj.location.copy()
    
    # Move to center at start_frame
    obj.location = center
    obj.keyframe_insert(data_path="location", frame=start_frame)
    
    # Calculate explosion direction (random but outward)
    direction = Vector((
        random.uniform(-1, 1),
        random.uniform(-1, 1),
        random.uniform(-1, 1)
    ))
    direction.normalize()
    
    # Move outward at mid_frame
    explosion_location = center + direction * explosion_strength
    obj.location = explosion_location
    obj.keyframe_insert(data_path="location", frame=mid_frame)
    
    # Add rotation during explosion
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)
    
    # Random rotation at mid_frame
    obj.rotation_euler = (
        random.uniform(0, math.pi * 2),
        random.uniform(0, math.pi * 2),
        random.uniform(0, math.pi * 2)
    )
    obj.keyframe_insert(data_path="rotation_euler", frame=mid_frame)
    
    # Smooth the animation with Bezier curves
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'BEZIER'
            kf.handle_left_type = 'AUTO'
            kf.handle_right_type = 'AUTO'

# Camera animation: Zoom out during explosion
camera.keyframe_insert(data_path="location", frame=1)

# Zoom out at mid_frame
camera.location = Vector((center_x, center_y - size * 4, center_z + size * 1.5))
camera.keyframe_insert(data_path="location", frame=mid_frame)

# Zoom back in at end_frame
camera.location = Vector((center_x, center_y - size * 3, center_z + size))
camera.keyframe_insert(data_path="location", frame=end_frame)

# Add easing to the camera movement
for fcurve in camera.animation_data.action.fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'BEZIER'
        kf.handle_left_type = 'AUTO'
        kf.handle_right_type = 'AUTO'
'''

    def _get_flow_animation_script(self, fps, total_frames, **kwargs):
        """Get script for flow animation (suitable for flowcharts)."""
        return f'''
# Create a flow animation (suitable for flowcharts)
print("Creating flow animation...")

# Center all objects at origin
bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objects:
    obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.location_clear()

# Get the bounds of all objects combined
min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

for obj in mesh_objects:
    for v in obj.bound_box:
        world_v = obj.matrix_world @ Vector(v)
        min_x = min(min_x, world_v.x)
        min_y = min(min_y, world_v.y)
        min_z = min(min_z, world_v.z)
        max_x = max(max_x, world_v.x)
        max_y = max(max_y, world_v.y)
        max_z = max(max_z, world_v.z)

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2
size = max(max_x - min_x, max_y - min_y, max_z - min_z)
center = Vector((center_x, center_y, center_z))

# Position camera to see the entire animation
camera.location = Vector((center_x, center_y - size * 2.5, center_z + size))
camera.rotation_euler = (math.radians(60), 0, 0)

# Apply materials
for obj in mesh_objects:
    # Create new material
    mat_name = f"FlowMaterial_{obj.name}"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        # Set initial values
        principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        principled.inputs['Metallic'].default_value = 0.3
        principled.inputs['Roughness'].default_value = 0.5
        principled.inputs['Alpha'].default_value = 0.0  # Start transparent
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Sort objects based on X or Y position (typical flowchart progression)
# Use Y for top-to-bottom flowcharts, X for left-to-right
sorted_objects = sorted(mesh_objects, key=lambda obj: obj.location.y, reverse=True)

# Animation: Sequential appearance and highlighting
appear_frame_duration = int(total_frames * 0.7 / len(sorted_objects))
highlight_frame_duration = int(appear_frame_duration * 0.7)

for i, obj in enumerate(sorted_objects):
    mat = obj.data.materials[0]
    principled = mat.node_tree.nodes.get('Principled BSDF')
    
    # Calculate appearance frames
    appear_start = i * appear_frame_duration + 1
    appear_end = appear_start + int(appear_frame_duration * 0.3)
    highlight_start = appear_end
    highlight_end = highlight_start + highlight_frame_duration
    
    # Fade in animation
    principled.inputs['Alpha'].default_value = 0.0
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=appear_start)
    
    principled.inputs['Alpha'].default_value = 1.0
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=appear_end)
    
    # Highlight animation (change color)
    principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
    principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=appear_end)
    
    principled.inputs['Base Color'].default_value = (0.2, 0.6, 1.0, 1.0)  # Blue highlight
    principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=highlight_start)
    
    principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
    principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=highlight_end)
    
    # Scale animation
    obj.scale = (0.1, 0.1, 0.1)  # Start small
    obj.keyframe_insert(data_path="scale", frame=appear_start)
    
    obj.scale = (1.0, 1.0, 1.0)  # Normal scale
    obj.keyframe_insert(data_path="scale", frame=appear_end)
    
    # Add slight bounce effect
    if i < len(sorted_objects) - 1:
        next_obj = sorted_objects[i + 1]
        
        # Add a slight movement to simulate "flowing" to the next object
        flow_start = highlight_end
        flow_end = flow_start + int(appear_frame_duration * 0.3)
        
        # Calculate direction to next object
        direction = (next_obj.location - obj.location).normalized()
        
        # Save original location
        original_location = obj.location.copy()
        
        # Move slightly towards next object
        obj.location = original_location + direction * size * 0.1
        obj.keyframe_insert(data_path="location", frame=flow_end - int(appear_frame_duration * 0.15))
        
        # Move back to original location
        obj.location = original_location
        obj.keyframe_insert(data_path="location", frame=flow_end)
    
    # Add easing to all animations
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = 'AUTO'
                kf.handle_right_type = 'AUTO'

# Camera animation: Follow the flow
if len(sorted_objects) > 1:
    # Create keyframes for camera to follow important objects
    keyframe_spacing = total_frames / (min(5, len(sorted_objects)))
    
    for i in range(min(5, len(sorted_objects))):
        # Get representative object (evenly spaced through the list)
        obj_index = int(i * (len(sorted_objects) - 1) / (min(5, len(sorted_objects)) - 1)) if min(5, len(sorted_objects)) > 1 else 0
        obj = sorted_objects[obj_index]
        
        # Calculate frame
        frame = int(i * keyframe_spacing + 1)
        
        # Position camera to look at this object
        look_at = obj.location
        camera_pos = look_at + Vector((0, -size * 2, size * 0.8))
        camera.location = camera_pos
        camera.keyframe_insert(data_path="location", frame=frame)
        
        # Look-at constraint would be ideal, but for simplicity just set rotation
        direction = look_at - camera_pos
        # Simple approximation of looking at the object
        camera.rotation_euler = (math.radians(60), 0, 0)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Add easing to camera movement
    if camera.animation_data and camera.animation_data.action:
        for fcurve in camera.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = 'AUTO'
                kf.handle_right_type = 'AUTO'
'''

    def _get_network_animation_script(self, fps, total_frames, **kwargs):
        """Get script for network animation (suitable for network diagrams)."""
        return f'''
# Create a network animation (suitable for network diagrams)
print("Creating network animation...")

# Center all objects at origin
bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objects:
    obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.location_clear()

# Get the bounds of all objects combined
min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

for obj in mesh_objects:
    for v in obj.bound_box:
        world_v = obj.matrix_world @ Vector(v)
        min_x = min(min_x, world_v.x)
        min_y = min(min_y, world_v.y)
        min_z = min(min_z, world_v.z)
        max_x = max(max_x, world_v.x)
        max_y = max(max_y, world_v.y)
        max_z = max(max_z, world_v.z)

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2
center_z = (min_z + max_z) / 2
size = max(max_x - min_x, max_y - min_y, max_z - min_z)
center = Vector((center_x, center_y, center_z))

# Position camera to see the entire animation
camera.location = Vector((center_x, center_y - size * 3, center_z + size * 1.2))
camera.rotation_euler = (math.radians(60), 0, 0)

# Create an empty as the center of rotation
bpy.ops.object.empty_add(location=center)
empty = bpy.context.active_object
empty.name = "NetworkCenter"

# Find node and connection objects
# Typically, in network diagrams:
# - Nodes are larger, more square/round objects
# - Connections are longer, thinner objects (lines, arrows)
nodes = []
connections = []

for obj in mesh_objects:
    # Calculate aspect ratio to differentiate nodes from connections
    dimensions = obj.dimensions
    max_dim = max(dimensions)
    min_dim = min(dimensions)
    aspect_ratio = max_dim / min_dim if min_dim > 0 else float('inf')
    
    # If aspect ratio is high, it's likely a connection (line)
    if aspect_ratio > 3.0:
        connections.append(obj)
    else:
        nodes.append(obj)

# If we couldn't identify nodes and connections, use a heuristic
if not nodes or len(nodes) < len(mesh_objects) * 0.2:
    # Sort objects by volume
    volumes = [(obj, obj.dimensions.x * obj.dimensions.y * obj.dimensions.z) for obj in mesh_objects]
    volumes.sort(key=lambda x: x[1], reverse=True)
    
    # Take the largest 1/3 as nodes, the rest as connections
    node_count = max(1, len(mesh_objects) // 3)
    nodes = [item[0] for item in volumes[:node_count]]
    connections = [item[0] for item in volumes[node_count:]]

# Apply materials
# Nodes get one color, connections another
for obj in nodes:
    # Create new material for nodes
    mat_name = f"NodeMaterial_{obj.name}"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        # Set initial values
        principled.inputs['Base Color'].default_value = (0.2, 0.6, 0.9, 1.0)  # Blue for nodes
        principled.inputs['Metallic'].default_value = 0.5
        principled.inputs['Roughness'].default_value = 0.3
        principled.inputs['Alpha'].default_value = 0.0  # Start transparent
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

for obj in connections:
    # Create new material for connections
    mat_name = f"ConnectionMaterial_{obj.name}"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    principled = mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        # Set initial values
        principled.inputs['Base Color'].default_value = (0.9, 0.5, 0.1, 1.0)  # Orange for connections
        principled.inputs['Metallic'].default_value = 0.7
        principled.inputs['Roughness'].default_value = 0.2
        principled.inputs['Alpha'].default_value = 0.0  # Start transparent
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Animation: Network activation sequence
# 1. Nodes appear first
# 2. Connections appear, simulating data flow
# 3. Pulse effect through the network

# Fade in nodes
node_appear_duration = int(total_frames * 0.3)
node_fade_in_time = int(node_appear_duration * 0.6 / len(nodes))

for i, obj in enumerate(nodes):
    mat = obj.data.materials[0]
    principled = mat.node_tree.nodes.get('Principled BSDF')
    
    # Calculate appearance frames
    appear_start = i * node_fade_in_time + 1
    appear_end = appear_start + node_fade_in_time
    
    # Fade in animation
    principled.inputs['Alpha'].default_value = 0.0
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=appear_start)
    
    principled.inputs['Alpha'].default_value = 1.0
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=appear_end)
    
    # Scale animation
    obj.scale = (0.1, 0.1, 0.1)  # Start small
    obj.keyframe_insert(data_path="scale", frame=appear_start)
    
    obj.scale = (1.0, 1.0, 1.0)  # Normal scale
    obj.keyframe_insert(data_path="scale", frame=appear_end)

# After nodes appear, animate connections
connection_start_frame = node_appear_duration
connection_duration = int(total_frames * 0.3)
connection_fade_in_time = int(connection_duration * 0.8 / max(1, len(connections)))

for i, obj in enumerate(connections):
    mat = obj.data.materials[0]
    principled = mat.node_tree.nodes.get('Principled BSDF')
    
    # Calculate appearance frames
    appear_start = connection_start_frame + i * connection_fade_in_time
    appear_end = appear_start + connection_fade_in_time
    
    # Fade in animation
    principled.inputs['Alpha'].default_value = 0.0
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=appear_start)
    
    principled.inputs['Alpha'].default_value = 1.0
    principled.inputs['Alpha'].keyframe_insert(data_path="default_value", frame=appear_end)
    
    # Scale animation for connections (only in one dimension to simulate drawing)
    # Determine the main axis of the connection
    dimensions = obj.dimensions
    main_axis = 0  # X axis by default
    if dimensions.y > dimensions.x and dimensions.y > dimensions.z:
        main_axis = 1  # Y axis
    elif dimensions.z > dimensions.x and dimensions.z > dimensions.y:
        main_axis = 2  # Z axis
    
    # Create a custom scale vector
    scale_vector = [1.0, 1.0, 1.0]
    scale_vector[main_axis] = 0.01  # Start very thin
    
    obj.scale = tuple(scale_vector)
    obj.keyframe_insert(data_path="scale", frame=appear_start)
    
    obj.scale = (1.0, 1.0, 1.0)  # Normal scale
    obj.keyframe_insert(data_path="scale", frame=appear_end)

# Network pulse animation after all elements are visible
pulse_start_frame = connection_start_frame + connection_duration
pulse_duration = total_frames - pulse_start_frame - int(total_frames * 0.1)
pulse_count = 2  # Number of pulses to show

for pulse in range(pulse_count):
    pulse_cycle_frames = pulse_duration / pulse_count
    
    # Animate through nodes with a pulse effect
    for i, obj in enumerate(nodes):
        # Calculate time offset for each node to create wave effect
        offset = i * (pulse_cycle_frames * 0.8 / len(nodes))
        
        mat = obj.data.materials[0]
        principled = mat.node_tree.nodes.get('Principled BSDF')
        
        # Normal color
        principled.inputs['Emission'].default_value = (0, 0, 0, 1)
        principled.inputs['Emission Strength'].default_value = 0
        principled.inputs['Emission'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse * pulse_cycle_frames)
        principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse * pulse_cycle_frames)
        
        # Pulse color (glow effect)
        principled.inputs['Emission'].default_value = (0.2, 0.8, 1.0, 1)  # Bright blue
        principled.inputs['Emission Strength'].default_value = 2.0
        principled.inputs['Emission'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.2 + pulse * pulse_cycle_frames)
        principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.2 + pulse * pulse_cycle_frames)
        
        # Back to normal
        principled.inputs['Emission'].default_value = (0, 0, 0, 1)
        principled.inputs['Emission Strength'].default_value = 0
        principled.inputs['Emission'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.4 + pulse * pulse_cycle_frames)
        principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.4 + pulse * pulse_cycle_frames)

    # Animate connections with pulse effect following nodes
    for i, obj in enumerate(connections):
        # Calculate time offset for each connection
        offset = (i + len(nodes) * 0.8) * (pulse_cycle_frames * 0.8 / (len(nodes) + len(connections)))
        
        mat = obj.data.materials[0]
        principled = mat.node_tree.nodes.get('Principled BSDF')
        
        # Normal color
        principled.inputs['Emission'].default_value = (0, 0, 0, 1)
        principled.inputs['Emission Strength'].default_value = 0
        principled.inputs['Emission'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse * pulse_cycle_frames)
        principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse * pulse_cycle_frames)
        
        # Pulse color (glow effect)
        principled.inputs['Emission'].default_value = (1.0, 0.6, 0.2, 1)  # Bright orange
        principled.inputs['Emission Strength'].default_value = 2.0
        principled.inputs['Emission'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.2 + pulse * pulse_cycle_frames)
        principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.2 + pulse * pulse_cycle_frames)
        
        # Back to normal
        principled.inputs['Emission'].default_value = (0, 0, 0, 1)
        principled.inputs['Emission Strength'].default_value = 0
        principled.inputs['Emission'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.4 + pulse * pulse_cycle_frames)
        principled.inputs['Emission Strength'].keyframe_insert(data_path="default_value", frame=pulse_start_frame + offset + pulse_cycle_frames * 0.4 + pulse * pulse_cycle_frames)

# Camera animation: Slow rotation around the network
empty.keyframe_insert(data_path="rotation_euler", frame=1)

empty.rotation_euler = (0, 0, math.radians(120))
empty.keyframe_insert(data_path="rotation_euler", frame=int(total_frames * 0.33))

empty.rotation_euler = (0, 0, math.radians(240))
empty.keyframe_insert(data_path="rotation_euler", frame=int(total_frames * 0.66))

empty.rotation_euler = (0, 0, math.radians(360))
empty.keyframe_insert(data_path="rotation_euler", frame=total_frames)

# Add easing to all animations
for obj in mesh_objects + [empty, camera]:
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'BEZIER'
                kf.handle_left_type = 'AUTO'
                kf.handle_right_type = 'AUTO'
'''
