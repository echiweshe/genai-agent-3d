"""
SVG to 3D Converter Component

This module handles the conversion of SVG diagrams to 3D models using Blender.
It provides functionality to extract SVG elements and convert them to 3D objects.
"""

import os
import asyncio
import logging
import tempfile
import subprocess
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class SVGTo3DConverter:
    """Convert SVG diagrams to 3D models using Blender."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SVG to 3D Converter.
        
        Args:
            config: Configuration dictionary with settings like blender_path, script_dir, etc.
        """
        self.config = config or {}
        self.blender_path = self.config.get("blender_path", "blender")
        self.script_dir = self.config.get("script_dir", "scripts")
        self.script_path = os.path.join(self.script_dir, "svg_to_3d_blender.py")
    
    async def convert(self, svg_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert an SVG file to a 3D Blender scene.
        
        Args:
            svg_path: Path to the input SVG file
            output_path: Path to save the output Blender file (optional)
            
        Returns:
            Path to the output Blender file
            
        Raises:
            FileNotFoundError: If the SVG file doesn't exist
            RuntimeError: If the conversion process fails
        """
        # Validate input
        if not os.path.exists(svg_path):
            raise FileNotFoundError(f"SVG file not found: {svg_path}")
        
        # Create output path if not provided
        if not output_path:
            fd, output_path = tempfile.mkstemp(suffix=".blend")
            os.close(fd)
        
        # Ensure script file exists
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Blender script not found: {self.script_path}")
        
        # Construct the Blender command
        cmd = [
            self.blender_path,
            "--background",
            "--python", self.script_path,
            "--",
            svg_path,
            output_path
        ]
        
        logger.info(f"Running Blender command: {' '.join(cmd)}")
        
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
            logger.error(f"SVG to 3D conversion failed: {error_msg}")
            raise RuntimeError(f"SVG to 3D conversion failed: {error_msg}")
        
        # Verify the output file exists
        if not os.path.exists(output_path):
            raise RuntimeError(f"Output file was not created: {output_path}")
        
        logger.info(f"SVG converted to 3D model: {output_path}")
        return output_path
    
    async def convert_from_content(self, svg_content: str, output_path: Optional[str] = None) -> str:
        """
        Convert SVG content directly to a 3D Blender scene.
        
        Args:
            svg_content: SVG content as a string
            output_path: Path to save the output Blender file (optional)
            
        Returns:
            Path to the output Blender file
        """
        # Create a temporary SVG file
        fd, temp_svg_path = tempfile.mkstemp(suffix=".svg")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(svg_content)
            
            # Convert the temporary SVG file
            return await self.convert(temp_svg_path, output_path)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_svg_path):
                os.unlink(temp_svg_path)
