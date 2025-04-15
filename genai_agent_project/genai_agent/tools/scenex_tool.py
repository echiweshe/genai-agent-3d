"""
SceneX Tool for advanced scene generation and animation
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.blender_script import BlenderScriptTool

logger = logging.getLogger(__name__)

class SceneXTool(Tool):
    """
    Tool for advanced scene generation and animation using SceneX
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the SceneX Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
        """
        super().__init__(
            name="scenex",
            description="Creates advanced 3D scenes and animations using coordinate-based placement"
        )
        
        self.redis_bus = redis_bus
        self.config = config
        self.blender_tool = None  # Will be initialized on first use
        
        logger.info("SceneX Tool initialized")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a scene or animation using SceneX
        
        Args:
            parameters: SceneX parameters
                - description: Scene description
                - objects: List of objects to include
                - camera: Camera parameters
                - animation: Animation parameters
                
        Returns:
            Scene generation result
        """
        # Get parameters
        description = parameters.get('description', '')
        objects = parameters.get('objects', [])
        camera = parameters.get('camera', {})
        animation = parameters.get('animation', {})
        
        if not description:
            raise ValueError("Description parameter is required")
        
        # Initialize Blender tool if needed
        if self.blender_tool is None:
            from genai_agent.tools.blender_script import BlenderScriptTool
            self.blender_tool = BlenderScriptTool(self.redis_bus, self.config)
        
        # Generate SceneX script
        scenex_script = self._generate_scenex_script(description, objects, camera, animation)
        
        # Execute script in Blender
        return await self.blender_tool.execute({
            'script': scenex_script,
            'format': 'json'
        })
    
    def _generate_scenex_script(self, description: str, objects: List[Dict[str, Any]], 
                               camera: Dict[str, Any], animation: Dict[str, Any]) -> str:
        """
        Generate SceneX Python script
        
        Args:
            description: Scene description
            objects: List of objects to include
            camera: Camera parameters
            animation: Animation parameters
            
        Returns:
            SceneX Python script
        """
        # This is a simplified example that mimics SceneX functionality
        # In a real implementation, this would use your existing SceneX code
        
        # Setup script header
        script = f"""
# SceneX script generated for: {description}

import bpy
import math
import os
from mathutils import Vector

# SceneX utility functions
class SceneX:
    @staticmethod
    def create_coordinate_system():
        # Create empty object to represent coordinate system
        bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
        coords = bpy.context.active_object
        coords.name = "CoordinateSystem"
        return coords
    
    @staticmethod
    def place_object(obj_type, name, location, rotation=(0, 0, 0), scale=(1, 1, 1)):
        # Create object based on type
        if obj_type == "cube":
            bpy.ops.mesh.primitive_cube_add(location=location)
        elif obj_type == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(location=location)
        elif obj_type == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(location=location)
        elif obj_type == "plane":
            bpy.ops.mesh.primitive_plane_add(location=location)
        else:
            bpy.ops.mesh.primitive_cube_add(location=location)
        
        # Set object properties
        obj = bpy.context.active_object
        obj.name = name
        obj.rotation_euler = (math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2]))
        obj.scale = scale
        
        return obj
    
    @staticmethod
    def setup_camera(location, target=None, lens=35):
        # Create camera
        bpy.ops.object.camera_add(location=location)
        camera = bpy.context.active_object
        camera.data.lens = lens
        
        # Point camera at target if specified
        if target:
            constraint = camera.constraints.new(type='TRACK_TO')
            constraint.target = target
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
        
        # Set as active camera
        bpy.context.scene.camera = camera
        
        return camera
    
    @staticmethod
    def create_animation(obj, keyframes):
        # Set keyframes for object
        for frame, location in keyframes.items():
            frame_num = int(frame)
            bpy.context.scene.frame_set(frame_num)
            obj.location = location
            obj.keyframe_insert(data_path="location", frame=frame_num)

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create SceneX coordinate system
coords = SceneX.create_coordinate_system()

# Scene setup
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.film_transparent = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Create objects
objects = []
"""
        
        # Add objects
        for i, obj in enumerate(objects):
            obj_type = obj.get('type', 'cube')
            obj_name = obj.get('name', f"Object_{i}")
            obj_location = obj.get('location', (0, 0, 0))
            obj_rotation = obj.get('rotation', (0, 0, 0))
            obj_scale = obj.get('scale', (1, 1, 1))
            
            script += f"""
# Create {obj_name}
obj_{i} = SceneX.place_object(
    obj_type="{obj_type}",
    name="{obj_name}",
    location={obj_location},
    rotation={obj_rotation},
    scale={obj_scale}
)
objects.append(obj_{i})
"""
        
        # Setup camera
        cam_location = camera.get('location', (0, -10, 2))
        cam_target = camera.get('target', 'CoordinateSystem')
        cam_lens = camera.get('lens', 35)
        
        script += f"""
# Setup camera
target = bpy.data.objects.get("{cam_target}")
camera = SceneX.setup_camera(
    location={cam_location},
    target=target,
    lens={cam_lens}
)
"""
        
        # Add animation if specified
        if animation:
            script += """
# Animation setup
scene.frame_start = 1
"""
            frame_end = animation.get('frame_end', 250)
            script += f"scene.frame_end = {frame_end}\n"
            
            # Add keyframes for objects
            for anim_obj in animation.get('objects', []):
                obj_idx = anim_obj.get('object_index', 0)
                keyframes = anim_obj.get('keyframes', {})
                
                script += f"""
# Animate object {obj_idx}
SceneX.create_animation(
    obj=objects[{obj_idx}],
    keyframes={keyframes}
)
"""
        
        # Add output information
        script += """
# Store result
output = {
    "status": "success",
    "objects": [obj.name for obj in objects],
    "camera": camera.name,
    "coordinate_system": coords.name
}
"""
        return script
