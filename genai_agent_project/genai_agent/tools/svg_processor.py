"""
SVG Processor Tool for converting SVGs to 3D scenes
"""

import logging
import os
import json
import re
from typing import Dict, Any, List, Optional

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.blender_script import BlenderScriptTool

logger = logging.getLogger(__name__)

class SVGProcessorTool(Tool):
    """
    Tool for converting SVGs to 3D scenes
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the SVG Processor Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
        """
        super().__init__(
            name="svg_processor",
            description="Converts SVG graphics to 3D scenes"
        )
        
        self.redis_bus = redis_bus
        self.config = config
        self.blender_tool = None  # Will be initialized on first use
        
        logger.info("SVG Processor Tool initialized")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an SVG and convert to 3D
        
        Args:
            parameters: SVG parameters
                - svg_content: SVG content string
                - extrude_depth: Depth to extrude 2D shapes (default: 0.1)
                - animation: Animation parameters
                
        Returns:
            Processing result
        """
        # Get parameters
        svg_content = parameters.get('svg_content', '')
        extrude_depth = parameters.get('extrude_depth', 0.1)
        animation = parameters.get('animation', {})
        
        if not svg_content:
            raise ValueError("SVG content parameter is required")
        
        # Initialize Blender tool if needed
        if self.blender_tool is None:
            from genai_agent.tools.blender_script import BlenderScriptTool
            self.blender_tool = BlenderScriptTool(self.redis_bus, self.config)
        
        # Parse SVG content
        svg_elements = self._parse_svg(svg_content)
        
        # Generate Blender script for SVG conversion
        blender_script = self._generate_svg_conversion_script(svg_elements, extrude_depth, animation)
        
        # Execute script in Blender
        return await self.blender_tool.execute({
            'script': blender_script,
            'format': 'json'
        })
    
    def _parse_svg(self, svg_content: str) -> List[Dict[str, Any]]:
        """
        Parse SVG content into elements
        
        Args:
            svg_content: SVG content string
            
        Returns:
            List of SVG elements
        """
        # This is a simple placeholder parser
        # In a real implementation, this would use a proper SVG parser
        
        elements = []
        
        # Extract viewBox
        viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
        viewbox = viewbox_match.group(1).split() if viewbox_match else ["0", "0", "100", "100"]
        viewbox = [float(v) for v in viewbox]
        
        # Extract paths
        path_matches = re.finditer(r'<path[^>]*d="([^"]+)"[^>]*>', svg_content)
        for i, match in enumerate(path_matches):
            path_data = match.group(1)
            elements.append({
                'type': 'path',
                'id': f'path_{i}',
                'data': path_data
            })
        
        # Extract rectangles
        rect_matches = re.finditer(r'<rect[^>]*x="([^"]+)"[^>]*y="([^"]+)"[^>]*width="([^"]+)"[^>]*height="([^"]+)"[^>]*>', svg_content)
        for i, match in enumerate(rect_matches):
            elements.append({
                'type': 'rect',
                'id': f'rect_{i}',
                'x': float(match.group(1)),
                'y': float(match.group(2)),
                'width': float(match.group(3)),
                'height': float(match.group(4))
            })
        
        # Extract circles
        circle_matches = re.finditer(r'<circle[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"[^>]*r="([^"]+)"[^>]*>', svg_content)
        for i, match in enumerate(circle_matches):
            elements.append({
                'type': 'circle',
                'id': f'circle_{i}',
                'cx': float(match.group(1)),
                'cy': float(match.group(2)),
                'r': float(match.group(3))
            })
        
        # Extract SVG viewBox for scaling
        elements.append({
            'type': 'viewbox',
            'x': viewbox[0],
            'y': viewbox[1],
            'width': viewbox[2],
            'height': viewbox[3]
        })
        
        return elements
    
    def _generate_svg_conversion_script(self, svg_elements: List[Dict[str, Any]], 
                                       extrude_depth: float,
                                       animation: Dict[str, Any]) -> str:
        """
        Generate Blender script for SVG conversion
        
        Args:
            svg_elements: List of SVG elements
            extrude_depth: Depth to extrude 2D shapes
            animation: Animation parameters
            
        Returns:
            Blender Python script
        """
        # This is a simplified script generator
        # In a real implementation, this would be much more complex
        
        script = f"""
# SVG to 3D conversion script

import bpy
import math
import os
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# SVG Conversion Utilities
class SVGConverter:
    @staticmethod
    def create_rectangle(x, y, width, height, name, extrude_depth={extrude_depth}):
        # Create rectangle mesh
        verts = [
            Vector((x, y, 0)),
            Vector((x + width, y, 0)),
            Vector((x + width, y + height, 0)),
            Vector((x, y + height, 0))
        ]
        faces = [(0, 1, 2, 3)]
        
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        # Link object to scene
        bpy.context.collection.objects.link(obj)
        
        # Extrude
        if extrude_depth > 0:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate=(0, 0, extrude_depth)
            )
            bpy.ops.object.mode_set(mode='OBJECT')
        
        return obj
    
    @staticmethod
    def create_circle(cx, cy, r, name, extrude_depth={extrude_depth}):
        # Create circle mesh
        bpy.ops.mesh.primitive_circle_add(
            radius=r,
            location=(cx, cy, 0),
            vertices=32
        )
        obj = bpy.context.active_object
        obj.name = name
        
        # Fill circle
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
        
        # Extrude
        if extrude_depth > 0:
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate=(0, 0, extrude_depth)
            )
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return obj
    
    @staticmethod
    def create_path(path_data, name, extrude_depth={extrude_depth}):
        # In a real implementation, this would parse SVG path data
        # For simplicity, we'll just create a placeholder object
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.name = name
        
        # Add a custom property with the path data for reference
        obj["svg_path_data"] = path_data
        
        # Note: Real implementation would convert path to curves
        
        return obj

# Scene setup
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.film_transparent = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Get SVG viewbox for scaling
viewbox = None
for element in {svg_elements}:
    if element.get('type') == 'viewbox':
        viewbox = element
        break

# Scale factor to normalize coordinates
scale_factor = 10.0 / max(viewbox['width'], viewbox['height']) if viewbox else 0.1

# Create objects
created_objects = []
"""
        
        # Process each SVG element
        for element in svg_elements:
            if element['type'] == 'viewbox':
                continue  # Already processed
                
            elif element['type'] == 'rect':
                script += f"""
# Create rectangle: {element['id']}
x = {element['x']} * scale_factor
y = {element['y']} * scale_factor
width = {element['width']} * scale_factor
height = {element['height']} * scale_factor
obj = SVGConverter.create_rectangle(x, y, width, height, "{element['id']}", {extrude_depth})
created_objects.append(obj)
"""
            
            elif element['type'] == 'circle':
                script += f"""
# Create circle: {element['id']}
cx = {element['cx']} * scale_factor
cy = {element['cy']} * scale_factor
r = {element['r']} * scale_factor
obj = SVGConverter.create_circle(cx, cy, r, "{element['id']}", {extrude_depth})
created_objects.append(obj)
"""
            
            elif element['type'] == 'path':
                script += f"""
# Create path: {element['id']}
path_data = "{element['data']}"
obj = SVGConverter.create_path(path_data, "{element['id']}", {extrude_depth})
created_objects.append(obj)
"""
        
        # Add camera setup
        script += """
# Setup camera
bpy.ops.object.camera_add(location=(0, 0, 20))
camera = bpy.context.active_object
camera.name = "SVGCamera"
bpy.context.scene.camera = camera

# Point camera at the center of objects
constraint = camera.constraints.new(type='TRACK_TO')
empty = bpy.data.objects.new("CameraTarget", None)
bpy.context.collection.objects.link(empty)
empty.location = (0, 0, 0)
constraint.target = empty
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'
"""
        
        # Add animation if specified
        if animation:
            script += """
# Animation setup
scene.frame_start = 1
"""
            frame_end = animation.get('frame_end', 250)
            script += f"scene.frame_end = {frame_end}\n"
            
            # Add basic animation (rotation)
            script += f"""
# Create a parent object for animation
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
parent = bpy.context.active_object
parent.name = "SVGParent"

# Parent all created objects to the empty
for obj in created_objects:
    obj.parent = parent

# Add rotation animation
parent.keyframe_insert(data_path="rotation_euler", frame=1)
parent.rotation_euler = (0, 0, math.radians(360))
parent.keyframe_insert(data_path="rotation_euler", frame={frame_end})
"""
        
        # Add output information
        script += """
# Store result
output = {
    "status": "success",
    "objects_created": len(created_objects),
    "object_names": [obj.name for obj in created_objects]
}
"""
        return script
