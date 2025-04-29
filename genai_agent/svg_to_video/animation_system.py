"""
Animation System Component

This module handles the animation of 3D models using the SceneX framework.
It provides functionality to apply animations to 3D objects created from SVG diagrams.
"""

import os
import asyncio
import logging
import tempfile
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class AnimationSystem:
    """Apply animations to 3D objects using the SceneX framework."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Animation System.
        
        Args:
            config: Configuration dictionary with settings like blender_path, script_dir, etc.
        """
        self.config = config or {}
        self.blender_path = self.config.get("blender_path", "blender")
        self.script_dir = self.config.get("script_dir", "scripts")
        self.script_path = os.path.join(self.script_dir, "scenex_animation.py")
        
        # Animation settings
        self.animation_type = self.config.get("animation_type", "standard")
        self.animation_duration = self.config.get("animation_duration", 250)  # frames
    
    async def animate(self, model_path: str, output_path: Optional[str] = None) -> str:
        """
        Apply animations to a 3D model.
        
        Args:
            model_path: Path to the input Blender model file
            output_path: Path to save the animated Blender file (optional)
            
        Returns:
            Path to the animated Blender file
            
        Raises:
            FileNotFoundError: If the model file doesn't exist
            RuntimeError: If the animation process fails
        """
        # Validate input
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Create output path if not provided
        if not output_path:
            fd, output_path = tempfile.mkstemp(suffix=".blend")
            os.close(fd)
        
        # Ensure script file exists
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Animation script not found: {self.script_path}")
        
        # Construct the command
        cmd = [
            self.blender_path,
            "--background",
            "--python", self.script_path,
            "--",
            model_path,
            output_path,
            self.animation_type,
            str(self.animation_duration)
        ]
        
        logger.info(f"Running animation command: {' '.join(cmd)}")
        
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
            logger.error(f"Animation failed: {error_msg}")
            raise RuntimeError(f"Animation failed: {error_msg}")
        
        # Verify the output file exists
        if not os.path.exists(output_path):
            raise RuntimeError(f"Output file was not created: {output_path}")
        
        logger.info(f"3D model animated: {output_path}")
        return output_path
    
    def set_animation_type(self, animation_type: str) -> None:
        """
        Set the animation type to use.
        
        Args:
            animation_type: Type of animation (standard, flowchart, network, etc.)
        """
        self.animation_type = animation_type
    
    def set_animation_duration(self, duration: int) -> None:
        """
        Set the animation duration in frames.
        
        Args:
            duration: Duration in frames
        """
        self.animation_duration = duration
