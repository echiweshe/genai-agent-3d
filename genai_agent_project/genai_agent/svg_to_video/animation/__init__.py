"""
Animation module for SVG to Video pipeline.

This module provides functionality to animate 3D models for the SVG to Video pipeline.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelAnimator:
    """Class for animating 3D models."""
    
    def __init__(self):
        """Initialize the ModelAnimator."""
        self.supported_animations = ["rotation", "translation", "scale", "deformation", "follow_path"]
    
    async def animate_model(self, model_path, output_path, animation_type="rotation", duration=5.0, **kwargs):
        """
        Animate a 3D model asynchronously.
        
        Args:
            model_path (str): Path to the input 3D model.
            output_path (str): Path to save the animated model.
            animation_type (str): Type of animation (rotation, translation, scale, etc.).
            duration (float): Duration of the animation in seconds.
            **kwargs: Additional animation parameters.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Run the synchronous function in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: animate_model(
                model_path=model_path,
                output_file=output_path,
                animation_type=animation_type,
                duration=duration,
                **kwargs
            )
        )
    
    def get_supported_animations(self):
        """Get a list of supported animation types."""
        return self.supported_animations


def animate_model(model_path, output_file, animation_type="rotation", duration=5.0, **kwargs):
    """
    Animate a 3D model.
    
    Args:
        model_path (str): Path to the input 3D model.
        output_file (str): Path to save the animated model.
        animation_type (str): Type of animation.
        duration (float): Duration of the animation in seconds.
        **kwargs: Additional animation parameters.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        logger.info(f"Animating model: {model_path}")
        logger.info(f"Animation type: {animation_type}")
        logger.info(f"Duration: {duration} seconds")
        
        # Get Blender path
        blender_path = get_blender_path()
        if not blender_path:
            logger.error("Blender path not found. Cannot animate model.")
            return False
        
        # Validate input model file
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False
        
        # Handle output file path
        if output_file is None:
            # Generate output file name based on input file
            model_file_name = os.path.basename(model_path)
            output_dir = os.path.join(os.path.dirname(os.path.dirname(model_path)), "animations")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{os.path.splitext(model_file_name)[0]}_animated.blend")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create a Python script for Blender
        script_content = create_animation_script(
            model_path=model_path,
            output_file=output_file,
            animation_type=animation_type,
            duration=duration,
            **kwargs
        )
        
        # Create temporary script file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
            temp_script.write(script_content)
            temp_script_path = temp_script.name
        
        try:
            # Run Blender with the script
            import subprocess
            cmd = [
                blender_path,
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
                return False
            
            # Check if output file was created
            if os.path.exists(output_file):
                logger.info(f"Animation successful: {output_file}")
                return output_file
            else:
                logger.error(f"Output file not created: {output_file}")
                return False
        
        except Exception as e:
            logger.error(f"Error running Blender process: {str(e)}")
            return False
        
        finally:
            # Clean up temporary script
            try:
                os.unlink(temp_script_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error animating model: {str(e)}")
        return False

def get_blender_path():
    """Get the path to the Blender executable."""
    # Try to get the path from environment variable
    import os
    blender_path = os.environ.get("BLENDER_PATH")
    
    if blender_path and os.path.exists(blender_path):
        return blender_path
    
    # Default paths to check
    default_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        r"/usr/bin/blender",
        r"/Applications/Blender.app/Contents/MacOS/Blender"
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    logger.error("Blender executable not found. Please set BLENDER_PATH environment variable.")
    return None

def create_animation_script(model_path, output_file, animation_type, duration, **kwargs):
    """Create a Python script for Blender to animate a model."""
    
    # Default parameters
    fps = kwargs.get('fps', 24)
    rotation_axis = kwargs.get('rotation_axis', 'Z')
    rotation_angle = kwargs.get('rotation_angle', 360)
    translation_distance = kwargs.get('translation_distance', 10)
    translation_axis = kwargs.get('translation_axis', 'X')
    scale_factor = kwargs.get('scale_factor', 2)
    
    # Create script content based on animation type
    if animation_type == "rotation":
        animation_setup = f"""
        # Set keyframes for rotation
        obj.rotation_euler = (0, 0, 0)
        obj.keyframe_insert(data_path="rotation_euler", frame=1)
        
        # Calculate rotation angle based on axis
        if "{rotation_axis}" == "X":
            obj.rotation_euler = ({rotation_angle} * math.pi / 180, 0, 0)
        elif "{rotation_axis}" == "Y":
            obj.rotation_euler = (0, {rotation_angle} * math.pi / 180, 0)
        else:  # Z axis is default
            obj.rotation_euler = (0, 0, {rotation_angle} * math.pi / 180)
            
        obj.keyframe_insert(data_path="rotation_euler", frame=frames)
        """
    elif animation_type == "translation":
        animation_setup = f"""
        # Set keyframes for translation
        obj.location = (0, 0, 0)
        obj.keyframe_insert(data_path="location", frame=1)
        
        # Calculate translation based on axis
        if "{translation_axis}" == "X":
            obj.location = ({translation_distance}, 0, 0)
        elif "{translation_axis}" == "Y":
            obj.location = (0, {translation_distance}, 0)
        else:  # Z axis is default
            obj.location = (0, 0, {translation_distance})
            
        obj.keyframe_insert(data_path="location", frame=frames)
        """
    elif animation_type == "scale":
        animation_setup = f"""
        # Set keyframes for scaling
        obj.scale = (1, 1, 1)
        obj.keyframe_insert(data_path="scale", frame=1)
        
        obj.scale = ({scale_factor}, {scale_factor}, {scale_factor})
        obj.keyframe_insert(data_path="scale", frame=frames)
        """
    elif animation_type == "follow_path":
        animation_setup = f"""
        # Create a path for the object to follow
        bpy.ops.curve.primitive_bezier_circle_add(radius=5, enter_editmode=False, location=(0, 0, 0))
        path = bpy.context.active_object
        path.name = "Path"
        
        # Add Follow Path constraint
        follow_path = obj.constraints.new('FOLLOW_PATH')
        follow_path.target = path
        follow_path.use_fixed_location = True
        follow_path.forward_axis = 'Y'
        
        # Animate the path
        path.data.path_duration = frames
        path.data.use_path = True
        path.data.use_path_follow = True
        
        # Add offset animation
        path.data.eval_time = 0
        path.data.keyframe_insert(data_path="eval_time", frame=1)
        
        path.data.eval_time = 100
        path.data.keyframe_insert(data_path="eval_time", frame=frames)
        """
    else:  # Default to rotation if animation type not recognized
        animation_setup = f"""
        # Set keyframes for rotation (default animation)
        obj.rotation_euler = (0, 0, 0)
        obj.keyframe_insert(data_path="rotation_euler", frame=1)
        
        obj.rotation_euler = (0, 0, 2 * math.pi)  # 360 degrees
        obj.keyframe_insert(data_path="rotation_euler", frame=frames)
        """
    
    # Complete script content
    script_content = f"""
import bpy
import os
import sys
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import 3D model
model_path = r"{model_path}"
file_ext = os.path.splitext(model_path)[1].lower()

if file_ext == ".obj":
    bpy.ops.import_scene.obj(filepath=model_path)
elif file_ext == ".stl":
    bpy.ops.import_mesh.stl(filepath=model_path)
elif file_ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=model_path)
elif file_ext == ".glb" or file_ext == ".gltf":
    bpy.ops.import_scene.gltf(filepath=model_path)
elif file_ext == ".x3d":
    bpy.ops.import_scene.x3d(filepath=model_path)
else:
    print(f"Unsupported model format: {{file_ext}}")
    sys.exit(1)

# Select all imported objects
imported_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if not imported_objects:
    print("No mesh objects imported from model")
    sys.exit(1)

# Join all objects into one if multiple objects
if len(imported_objects) > 1:
    for obj in imported_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = imported_objects[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
else:
    obj = imported_objects[0]
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

# Center the object
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
obj.location = (0, 0, 0)

# Animation settings
fps = {fps}
duration = {duration}
frames = int(fps * duration)

# Set scene parameters
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = frames
scene.render.fps = fps
scene.render.engine = 'BLENDER_EEVEE'
scene.render.film_transparent = True

# Create animation
{animation_setup}

# Set interpolation to BEZIER for smoother animation
for fc in obj.animation_data.action.fcurves:
    for kf in fc.keyframe_points:
        kf.interpolation = 'BEZIER'

# Save the file
output_file = r"{output_file}"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_file)

print(f"Animation completed and saved to: {{output_file}}")
"""
    return script_content

def get_supported_animation_types():
    """Get a list of supported animation types."""
    return ["rotation", "translation", "scale", "follow_path", "deformation"]

def get_animation_options():
    """Get the available options for animation."""
    return {
        'animation_type': {
            'type': 'enum',
            'values': get_supported_animation_types(),
            'default': 'rotation',
            'description': 'Type of animation to apply'
        },
        'duration': {
            'type': 'float',
            'default': 5.0,
            'description': 'Duration of the animation in seconds'
        },
        'fps': {
            'type': 'int',
            'default': 24,
            'description': 'Frames per second for the animation'
        },
        'rotation_axis': {
            'type': 'enum',
            'values': ['X', 'Y', 'Z'],
            'default': 'Z',
            'description': 'Axis to rotate around for rotation animation'
        },
        'rotation_angle': {
            'type': 'float',
            'default': 360.0,
            'description': 'Angle to rotate in degrees'
        },
        'translation_axis': {
            'type': 'enum',
            'values': ['X', 'Y', 'Z'],
            'default': 'X',
            'description': 'Axis to translate along for translation animation'
        },
        'translation_distance': {
            'type': 'float',
            'default': 10.0,
            'description': 'Distance to translate'
        },
        'scale_factor': {
            'type': 'float',
            'default': 2.0,
            'description': 'Factor to scale by for scale animation'
        }
    }

if __name__ == "__main__":
    # Simple test
    import sys
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = animate_model(model_path, output_path)
        print(f"Animation result: {result}")
    else:
        print("Usage: python animation.py input_model.obj [output_animation.blend]")
