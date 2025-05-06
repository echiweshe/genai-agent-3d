"""
Video rendering module for the SVG to Video pipeline.

This module provides functionality to render animated 3D models to video
using Blender.
"""

import os
import sys
import logging
import tempfile
import subprocess
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class VideoRenderer:
    """
    Class for rendering animated 3D models to video.
    
    This class provides methods to render videos from animated 3D models
    using Blender.
    """
    
    def __init__(self, blender_path=None):
        """
        Initialize the VideoRenderer.
        
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
            logger.warning("Blender executable not found. Rendering functionality will be limited.")
    
    def render_video(self, model_path, output_path=None, quality="medium", duration=10.0, fps=30, resolution=(1920, 1080), **kwargs):
        """
        Render an animated 3D model to video using Blender.
        
        Args:
            model_path (str): Path to the input animated 3D model file
            output_path (str, optional): Path to save the output video file
            quality (str, optional): Rendering quality
                Options: "low", "medium", "high"
            duration (float, optional): Duration of the video in seconds
            fps (int, optional): Frames per second
            resolution (tuple, optional): Video resolution (width, height)
            **kwargs: Additional rendering parameters
                - samples (int): Number of render samples
                - output_format (str): Output format ("MP4", "AVI", "GIF")
                - codec (str): Video codec
                - color_management (dict): Color management settings
                - background_color (tuple): RGB background color (0.0-1.0)
        
        Returns:
            str: Path to the rendered video file, or None if rendering failed
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
            videos_dir = os.path.join(os.path.dirname(os.path.dirname(model_dir)), "videos")
            
            # Ensure videos directory exists
            os.makedirs(videos_dir, exist_ok=True)
            
            # Create output path
            output_path = os.path.join(
                videos_dir,
                f"{os.path.splitext(model_name)[0]}_video.mp4"
            )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if Blender is available
        if not self.blender_path:
            logger.error("Blender not available. Cannot render video.")
            return None
        
        # Get quality presets
        samples, denoise = self._get_quality_preset(quality)
        
        # Override with kwargs if provided
        samples = kwargs.get('samples', samples)
        
        # Get output format settings
        output_format = kwargs.get('output_format', 'MP4')
        codec = kwargs.get('codec', 'H264')
        
        # Generate rendering script
        render_script = self._get_render_script(
            model_path, 
            output_path, 
            samples=samples,
            denoise=denoise,
            fps=fps,
            duration=duration,
            resolution=resolution,
            output_format=output_format,
            codec=codec,
            **kwargs
        )
        
        if not render_script:
            logger.error("Failed to generate rendering script")
            return None
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
            temp_script.write(render_script)
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
                logger.info(f"Video rendering successful: {output_path}")
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
    
    def _get_quality_preset(self, quality):
        """
        Get render quality presets based on quality level.
        
        Args:
            quality (str): Quality level ("low", "medium", "high")
        
        Returns:
            tuple: (samples, denoise) settings
        """
        if quality.lower() == "low":
            return 32, True
        elif quality.lower() == "high":
            return 256, False
        else:  # Medium quality (default)
            return 128, True
    
    def _get_render_script(self, model_path, output_path, samples, denoise, fps, duration, resolution, output_format, codec, **kwargs):
        """
        Generate a Blender Python script for rendering.
        
        Args:
            model_path (str): Path to the input animated 3D model file
            output_path (str): Path to save the output video file
            samples (int): Number of render samples
            denoise (bool): Whether to use denoising
            fps (int): Frames per second
            duration (float): Duration of the video in seconds
            resolution (tuple): Video resolution (width, height)
            output_format (str): Output format ("MP4", "AVI", "GIF")
            codec (str): Video codec
            **kwargs: Additional rendering parameters
        
        Returns:
            str: Blender Python script content for rendering
        """
        # Get additional parameters with defaults
        background_color = kwargs.get('background_color', (0.9, 0.9, 0.95, 1.0))
        file_format = self._get_file_format(output_format)
        total_frames = int(duration * fps)
        
        # Build script
        script = f'''
import bpy
import os
import math
import sys

print("Starting video rendering script...")

# Open the model file
model_path = r"{model_path}"

# Check if model file exists
if not os.path.exists(model_path):
    print(f"Error: Model file not found: {{model_path}}")
    sys.exit(1)

# Load the model file
# If it's a Blend file, just load it
print(f"Loading model file: {{model_path}}")
if model_path.lower().endswith('.blend'):
    try:
        bpy.ops.wm.open_mainfile(filepath=model_path)
    except Exception as e:
        print(f"Error loading .blend file: {{str(e)}}")
        # Try appending from the file instead
        try:
            with bpy.data.libraries.load(model_path) as (data_from, data_to):
                data_to.objects = data_from.objects
                data_to.materials = data_from.materials
                data_to.scenes = data_from.scenes
            
            # Link objects to scene
            for obj in data_to.objects:
                if obj is not None and obj.name not in bpy.context.scene.objects:
                    bpy.context.collection.objects.link(obj)
        except Exception as e2:
            print(f"Error appending from .blend file: {{str(e2)}}")
            sys.exit(1)
else:
    # For other file formats, import the model
    print(f"Importing model from {{model_path}}")
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
    else:
        print(f"Unsupported file format: {{ext}}")
        sys.exit(1)

print("Model loaded successfully.")

# Set up render settings
print("Setting up render settings...")
scene = bpy.context.scene
render = scene.render

# Set resolution
render.resolution_x = {resolution[0]}
render.resolution_y = {resolution[1]}
render.resolution_percentage = 100

# Set frame rate
scene.render.fps = {fps}

# Set frame range
scene.frame_start = 1
scene.frame_end = {total_frames}

# Set up rendering engine and quality
scene.render.engine = 'CYCLES'
scene.cycles.samples = {samples}
scene.cycles.use_denoising = {str(denoise).lower()}
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium Contrast'

# Set up world background
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs[0].default_value = {background_color}  # RGBA background color
    bg_node.inputs[1].default_value = 1.0  # Strength

# Set up output format
render.image_settings.file_format = '{file_format}'
if '{file_format}' == 'FFMPEG':
    render.ffmpeg.format = '{output_format}'
    render.ffmpeg.codec = '{codec}'
    render.ffmpeg.constant_rate_factor = 'MEDIUM'  # Medium quality/size balance
    render.ffmpeg.ffmpeg_preset = 'GOOD'
    render.ffmpeg.audio_codec = 'AAC'

# Set output path
render.filepath = r"{output_path}"

# Check if camera exists, if not create one
if 'Camera' not in bpy.context.scene.objects:
    print("Camera not found, creating one...")
    bpy.ops.object.camera_add(location=(0, -10, 5), rotation=(math.radians(30), 0, 0))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

# Check if lights exist, if not create them
lights = [obj for obj in bpy.context.scene.objects if obj.type == 'LIGHT']
if not lights:
    print("No lights found, creating lights...")
    # Create key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    # Create fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    fill = bpy.context.active_object
    fill.data.energy = 3.0
    
    # Create rim light
    bpy.ops.object.light_add(type='POINT', location=(0, 5, 5))
    rim = bpy.context.active_object
    rim.data.energy = 1.5

# Render animation
print(f"Rendering animation to {{render.filepath}}...")
bpy.ops.render.render(animation=True)

print("Rendering complete.")
'''
        
        return script
    
    def _get_file_format(self, output_format):
        """
        Get Blender file format string from output format.
        
        Args:
            output_format (str): Output format ("MP4", "AVI", "GIF")
        
        Returns:
            str: Blender file format string
        """
        format_map = {
            'MP4': 'FFMPEG',
            'AVI': 'FFMPEG',
            'GIF': 'AVI_JPEG',  # GIF via AVI as intermediate
            'PNG': 'PNG',
            'JPEG': 'JPEG',
            'TIFF': 'TIFF'
        }
        
        return format_map.get(output_format.upper(), 'FFMPEG')
