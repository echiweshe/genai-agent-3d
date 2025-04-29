"""
Video Renderer Component

This module handles rendering animated 3D scenes to video files.
It provides functionality to render Blender scenes to MP4 or other video formats.
"""

import os
import asyncio
import logging
import tempfile
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class VideoRenderer:
    """Render animated 3D scenes to video."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Video Renderer.
        
        Args:
            config: Configuration dictionary with settings like blender_path, script_dir, etc.
        """
        self.config = config or {}
        self.blender_path = self.config.get("blender_path", "blender")
        self.script_dir = self.config.get("script_dir", "scripts")
        self.script_path = os.path.join(self.script_dir, "video_renderer.py")
        
        # Rendering settings
        self.quality = self.config.get("render_quality", "medium")
        self.resolution = self.config.get("resolution", (1280, 720))
        self.fps = self.config.get("fps", 30)
    
    async def render(self, blend_file: str, output_path: str) -> str:
        """
        Render an animated Blender scene to video.
        
        Args:
            blend_file: Path to the input Blender file
            output_path: Path to save the output video file
            
        Returns:
            Path to the output video file
            
        Raises:
            FileNotFoundError: If the Blender file doesn't exist
            RuntimeError: If the rendering process fails
        """
        # Validate input
        if not os.path.exists(blend_file):
            raise FileNotFoundError(f"Blend file not found: {blend_file}")
        
        # Ensure script file exists
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Renderer script not found: {self.script_path}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Construct the command
        cmd = [
            self.blender_path,
            "--background",
            "--python", self.script_path,
            "--",
            blend_file,
            output_path,
            self.quality,
            f"{self.resolution[0]}x{self.resolution[1]}",
            str(self.fps)
        ]
        
        logger.info(f"Running render command: {' '.join(cmd)}")
        
        # Execute Blender as a subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for the process to complete
        stdout, stderr = await process.communicate()
        
        # Check if the process was successful
        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"Rendering failed: {error_msg}")
            raise RuntimeError(f"Rendering failed: {error_msg}")
        
        # Verify the output file exists
        if not os.path.exists(output_path):
            raise RuntimeError(f"Output video file was not created: {output_path}")
        
        logger.info(f"Video rendering completed: {output_path}")
        return output_path
    
    def set_quality(self, quality: str) -> None:
        """
        Set the rendering quality.
        
        Args:
            quality: Rendering quality (low, medium, high)
        """
        if quality not in ["low", "medium", "high"]:
            raise ValueError(f"Invalid quality: {quality}. Must be low, medium, or high.")
        self.quality = quality
    
    def set_resolution(self, width: int, height: int) -> None:
        """
        Set the video resolution.
        
        Args:
            width: Video width in pixels
            height: Video height in pixels
        """
        self.resolution = (width, height)
    
    def set_fps(self, fps: int) -> None:
        """
        Set the frames per second.
        
        Args:
            fps: Frames per second
        """
        self.fps = fps
