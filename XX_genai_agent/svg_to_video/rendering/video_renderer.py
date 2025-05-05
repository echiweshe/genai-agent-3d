"""
Video Renderer for SVG to Video Pipeline

This module handles the rendering of animated 3D scenes to video files.
It configures render settings, quality presets, and output formats.
"""

import os
import asyncio
import logging
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoRenderer:
    """
    System for rendering animated 3D scenes to video files.
    Integrates with Blender for video rendering.
    """
    
    def __init__(self, debug=False, quality="medium", output_format="mp4"):
        """
        Initialize the Video Renderer.
        
        Args:
            debug: Enable debug logging
            quality: Default rendering quality (low, medium, high)
            output_format: Default output format (mp4, webm, etc.)
        """
        self.debug = debug
        self.quality = quality
        self.output_format = output_format
        
        # Get Blender path from environment
        self.blender_path = os.environ.get("BLENDER_PATH", "blender")
        
        # Rendering script paths
        self.scripts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "scripts")
        self.render_script = os.path.join(self.scripts_dir, "render_video.py")
        
        # Create scripts directory if it doesn't exist
        os.makedirs(self.scripts_dir, exist_ok=True)
        
        if self.debug:
            logger.info("Video Renderer initialized")
            logger.info(f"Blender path: {self.blender_path}")
            logger.info(f"Render script: {self.render_script}")
            logger.info(f"Default quality: {self.quality}")
            logger.info(f"Default output format: {self.output_format}")
    
    async def render_video(
        self,
        animation_path: str,
        output_path: str,
        quality: str = None,
        resolution: tuple = None,
        fps: int = 30,
        samples: int = None
    ) -> bool:
        """
        Render an animated 3D scene to video.
        
        Args:
            animation_path: Path to input animated Blender file (.blend)
            output_path: Path to save video file
            quality: Rendering quality (low, medium, high)
            resolution: Output resolution as (width, height) tuple
            fps: Frames per second
            samples: Number of render samples (overrides quality preset)
            
        Returns:
            True if rendering was successful, False otherwise
        """
        try:
            if self.debug:
                logger.info(f"Rendering video: {animation_path}")
                logger.info(f"Quality: {quality or self.quality}")
                logger.info(f"Output: {output_path}")
            
            # Use provided quality or default
            quality = quality or self.quality
            
            # Set default resolution based on quality
            if not resolution:
                if quality == "low":
                    resolution = (640, 480)
                elif quality == "medium":
                    resolution = (1280, 720)
                else:  # high
                    resolution = (1920, 1080)
            
            # Set default samples based on quality
            if not samples:
                if quality == "low":
                    samples = 32
                elif quality == "medium":
                    samples = 64
                else:  # high
                    samples = 128
            
            # Create rendering script if it doesn't exist
            await self._ensure_render_script_exists()
            
            # Build Blender command
            cmd = [
                self.blender_path,
                "--background",
                animation_path,
                "--python",
                self.render_script,
                "--",
                "--output", output_path,
                "--quality", quality,
                "--width", str(resolution[0]),
                "--height", str(resolution[1]),
                "--fps", str(fps),
                "--samples", str(samples)
            ]
            
            # Run Blender process
            if self.debug:
                logger.info(f"Running command: {' '.join(cmd)}")
            
            # Create log files
            log_dir = os.path.dirname(output_path)
            log_base = os.path.splitext(os.path.basename(output_path))[0]
            log_file = os.path.join(log_dir, f"{log_base}.render.log")
            err_file = os.path.join(log_dir, f"{log_base}.render.err")
            
            # Run process
            with open(log_file, "w") as log, open(err_file, "w") as err:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=log,
                    stderr=err
                )
                await process.wait()
            
            # Check if process was successful
            if process.returncode != 0:
                logger.error(f"Rendering failed with code {process.returncode}")
                return False
            
            # Check if output file was created
            if not os.path.exists(output_path):
                logger.error("Video file was not created")
                return False
            
            logger.info(f"Rendering completed successfully: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error in render_video: {str(e)}")
            return False
    
    async def _ensure_render_script_exists(self) -> bool:
        """
        Ensure the render script exists. Create it if it doesn't.
        
        Returns:
            True if script exists or was created, False otherwise
        """
        if os.path.exists(self.render_script):
            return True
        
        try:
            # Create scripts directory if it doesn't exist
            os.makedirs(os.path.dirname(self.render_script), exist_ok=True)
            
            # Create render script
            script_content = """
import bpy
import argparse
import sys
import os

def parse_args():
    \"\"\"Parse command line arguments.\"\"\"
    parser = argparse.ArgumentParser(description='Render video from command line')
    
    # Add the arguments
    parser.add_argument('--output', type=str, required=True, help='Output video path')
    parser.add_argument('--quality', type=str, default='medium', help='Rendering quality (low, medium, high)')
    parser.add_argument('--width', type=int, default=1280, help='Output width')
    parser.add_argument('--height', type=int, default=720, help='Output height')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second')
    parser.add_argument('--samples', type=int, default=64, help='Render samples')
    
    # Extract arguments after '--'
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    return args

def setup_render_settings(args):
    \"\"\"Configure render settings.\"\"\"
    scene = bpy.context.scene
    
    # Set render engine (Cycles for best quality)
    scene.render.engine = 'CYCLES'
    
    # Set the resolution
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    
    # Set frames per second
    scene.render.fps = args.fps
    
    # Configure output path and format
    output_format = os.path.splitext(args.output)[1].lower()
    
    if output_format == '.mp4':
        # H.264 video codec
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'  # Quality
        scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    elif output_format == '.webm':
        # WebM format
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'WEBM'
        scene.render.ffmpeg.codec = 'VP9'
        scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    else:
        # Default to MP4 if format not recognized
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
    
    # Set output path
    scene.render.filepath = args.output
    
    # Configure quality based on selected preset
    # Set render samples
    scene.cycles.samples = args.samples
    
    if args.quality == 'low':
        # Fast render settings
        scene.cycles.use_denoising = True
        scene.cycles.preview_samples = 32
        scene.cycles.device = 'CPU'
        scene.render.film_transparent = False
    elif args.quality == 'medium':
        # Balanced settings
        scene.cycles.use_denoising = True
        scene.cycles.preview_samples = 64
        # Try GPU if available, fall back to CPU
        try:
            scene.cycles.device = 'GPU'
        except:
            scene.cycles.device = 'CPU'
        scene.render.film_transparent = False
    else:  # high
        # High quality settings
        scene.cycles.use_denoising = True
        scene.cycles.preview_samples = 128
        # Try GPU if available, fall back to CPU
        try:
            scene.cycles.device = 'GPU'
        except:
            scene.cycles.device = 'CPU'
        scene.render.film_transparent = False
        # Add motion blur for smoother animation
        scene.render.use_motion_blur = True
    
    print(f"Render settings configured: {args.width}x{args.height} at {args.fps}fps, {args.quality} quality")

def render_animation():
    \"\"\"Render the animation to video.\"\"\"
    # Ensure all objects are included in render
    for obj in bpy.data.objects:
        obj.hide_render = False
    
    # Render animation
    bpy.ops.render.render(animation=True)
    
    print("Rendering complete!")

def main():
    # Parse command line arguments
    args = parse_args()
    
    print(f"Setting up render for: {args.output}")
    print(f"Quality: {args.quality}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"FPS: {args.fps}")
    print(f"Samples: {args.samples}")
    
    # Set up render settings
    setup_render_settings(args)
    
    # Render the animation
    render_animation()
    
    print(f"Video rendered to: {args.output}")

if __name__ == "__main__":
    main()
            """
            
            # Write the script to file
            with open(self.render_script, "w") as f:
                f.write(script_content)
            
            logger.info(f"Created render script at {self.render_script}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating render script: {str(e)}")
            return False
