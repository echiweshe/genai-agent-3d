"""
Video Renderer Blender Script

This script is executed by Blender to render an animated 3D scene to video.
It configures the rendering settings and outputs the final video.

Usage:
    blender --background --python video_renderer.py -- input.blend output.mp4 [quality] [resolution] [fps]
"""

import bpy
import os
import sys

def setup_render_settings(quality='medium', resolution='1280x720', fps=30):
    """Configure render settings based on the provided parameters."""
    scene = bpy.context.scene
    
    # Parse resolution
    try:
        width, height = resolution.split('x')
        width, height = int(width), int(height)
    except (ValueError, AttributeError):
        print(f"Invalid resolution format: {resolution}, using default: 1280x720")
        width, height = 1280, 720
    
    # Set resolution
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    
    # Set frame rate
    scene.render.fps = fps
    
    # Set output format
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    
    # Set quality based on preset
    if quality == 'high':
        scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        scene.render.use_motion_blur = True
        scene.eevee.use_bloom = True
        scene.eevee.use_ssr = True
        scene.eevee.use_gtao = True
        scene.eevee.taa_render_samples = 64
        print("Using high quality render settings")
    elif quality == 'medium':
        scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
        scene.render.use_motion_blur = False
        scene.eevee.use_bloom = True
        scene.eevee.use_ssr = False
        scene.eevee.use_gtao = True
        scene.eevee.taa_render_samples = 32
        print("Using medium quality render settings")
    else:  # low
        scene.render.ffmpeg.constant_rate_factor = 'LOW'
        scene.render.use_motion_blur = False
        scene.eevee.use_bloom = False
        scene.eevee.use_ssr = False
        scene.eevee.use_gtao = False
        scene.eevee.taa_render_samples = 16
        print("Using low quality render settings")
    
    # Set render engine to EEVEE for faster rendering
    scene.render.engine = 'BLENDER_EEVEE'

def render_animation(output_path, frame_start=None, frame_end=None):
    """Render the animation to video."""
    scene = bpy.context.scene
    
    # Set frame range if specified
    if frame_start is not None:
        scene.frame_start = frame_start
    if frame_end is not None:
        scene.frame_end = frame_end
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Set output path
    scene.render.filepath = output_path
    
    print(f"Rendering animation from frame {scene.frame_start} to {scene.frame_end}")
    print(f"Output path: {output_path}")
    
    # Render animation
    bpy.ops.render.render(animation=True)
    
    print(f"Rendering completed: {output_path}")
    return output_path

# For command-line execution from Blender
if __name__ == "__main__":
    # Get args after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    if len(argv) >= 2:
        blend_file = argv[0]
        output_path = argv[1]
        
        # Load the blend file
        bpy.ops.wm.open_mainfile(filepath=blend_file)
        
        # Parse optional parameters
        quality = 'medium'
        if len(argv) >= 3:
            quality = argv[2]
        
        resolution = '1280x720'
        if len(argv) >= 4:
            resolution = argv[3]
        
        fps = 30
        if len(argv) >= 5:
            try:
                fps = int(argv[4])
            except ValueError:
                print(f"Invalid fps: {argv[4]}, using default: 30")
        
        # Set up render settings
        setup_render_settings(quality, resolution, fps)
        
        # Render the animation
        render_animation(output_path)
    else:
        print("Usage: blender --background --python video_renderer.py -- input.blend output.mp4 [quality] [resolution] [fps]")
        sys.exit(1)
