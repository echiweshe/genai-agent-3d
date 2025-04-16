"""
Blender Script Tool for executing Blender Python scripts
"""

import logging
import os
import uuid
import tempfile
import asyncio
import json
from typing import Dict, Any, Optional

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus

logger = logging.getLogger(__name__)

class BlenderScriptTool(Tool):
    """
    Tool for executing Python scripts in Blender
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the Blender Script Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
        """
        super().__init__(
            name="blender_script",
            description="Executes Python scripts in Blender"
        )
        
        self.redis_bus = redis_bus
        self.blender_path = config.get('blender_path', '/usr/bin/blender')
        self.temp_dir = tempfile.mkdtemp()
        
        logger.info(f"Blender Script Tool initialized with Blender at {self.blender_path}")
    
    def _get_default_script(self) -> str:
        """Get a default script for development/demo purposes"""
        return """
# Default demo script for Blender
import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple scene
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "DemoCube"

# Add material to cube
if "Red" not in bpy.data.materials:
    red_mat = bpy.data.materials.new(name="Red")
    red_mat.diffuse_color = (1, 0, 0, 1)
else:
    red_mat = bpy.data.materials["Red"]
    
cube.data.materials.append(red_mat)

# Create plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "DemoPlane"

# Add material to plane
if "Blue" not in bpy.data.materials:
    blue_mat = bpy.data.materials.new(name="Blue")
    blue_mat.diffuse_color = (0, 0, 1, 1)
else:
    blue_mat = bpy.data.materials["Blue"]
    
plane.data.materials.append(blue_mat)

# Create camera
bpy.ops.object.camera_add(location=(5, -5, 5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(55), 0, math.radians(45))
bpy.context.scene.camera = camera

# Add light
bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 10))

# Store result
output = {
    "status": "success",
    "message": "Default demo scene created",
    "objects_created": 4,
    "scene_description": "A simple scene with a red cube on a blue plane"
}
"""
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Blender Python script
        
        Args:
            parameters: Script parameters
                - script: Python script to execute
                - format: Output format (json, text)
                
        Returns:
            Script execution result
        """
        # Get parameters
        script = parameters.get('script', '')
        output_format = parameters.get('format', 'json')
        
        if not script:
            # For development/demo purposes - use a default script
            script = self._get_default_script()
            logger.warning("Using default script for development/demo")
        
        # Create temporary script file
        script_path = os.path.join(self.temp_dir, f"script_{uuid.uuid4().hex}.py")
        with open(script_path, "w") as f:
            f.write(self._prepare_script(script, output_format))
        
        # Execute script in Blender
        process = await asyncio.create_subprocess_exec(
            self.blender_path,
            "--background",
            "--python", script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Clean up
        os.unlink(script_path)
        
        # Check for errors
        if process.returncode != 0:
            return {
                'status': 'error',
                'error': stderr.decode()
            }
        
        # Parse output
        return self._parse_output(stdout.decode(), output_format)
    
    def _prepare_script(self, script: str, output_format: str) -> str:
        """
        Prepare script for execution
        
        Args:
            script: Python script
            output_format: Output format
            
        Returns:
            Prepared script
        """
        # Add output handling code
        if output_format == 'json':
            wrapper = """
import bpy
import json
import sys

# Setup output capturing
def capture_output():
    output = {}
    try:
{script_indented}
        output["status"] = "success"
    except Exception as e:
        output["status"] = "error"
        output["error"] = str(e)
    
    # Print output as JSON
    print("SCRIPT_OUTPUT_START")
    print(json.dumps(output))
    print("SCRIPT_OUTPUT_END")

capture_output()
"""
            indented_script = "\n".join(f"        {line}" for line in script.split("\n"))
            return wrapper.replace("{script_indented}", indented_script)
        else:
            # Simple output capture for non-JSON formats
            return script
    
    def _parse_output(self, output: str, output_format: str) -> Dict[str, Any]:
        """
        Parse script output
        
        Args:
            output: Script output
            output_format: Output format
            
        Returns:
            Parsed output
        """
        if output_format == 'json':
            # Extract JSON output between markers
            start_marker = "SCRIPT_OUTPUT_START"
            end_marker = "SCRIPT_OUTPUT_END"
            
            start_idx = output.find(start_marker)
            end_idx = output.find(end_marker)
            
            if start_idx >= 0 and end_idx >= 0:
                json_str = output[start_idx + len(start_marker):end_idx].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    return {
                        'status': 'error',
                        'error': f"JSON decode error: {str(e)}",
                        'raw_output': json_str
                    }
            else:
                return {
                    'status': 'error',
                    'error': "Could not parse output",
                    'raw_output': output
                }
        else:
            return {
                'status': 'success',
                'output': output
            }
