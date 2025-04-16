"""
Model Generator Tool for creating 3D models from descriptions
"""

import logging
import json
import uuid
import os
from typing import Dict, Any, List, Optional

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.llm import LLMService
from genai_agent.services.asset_manager import AssetManager

logger = logging.getLogger(__name__)

class ModelGeneratorTool(Tool):
    """
    Tool for generating 3D models from descriptions
    
    Uses LLM to generate scripts for procedural 3D model creation.
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the Model Generator Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
        """
        super().__init__(
            name="model_generator",
            description="Generates 3D models from text descriptions"
        )
        
        self.redis_bus = redis_bus
        self.config = config or {}
        
        # Output directory for generated models
        self.output_dir = self.config.get('output_dir', 'output/models/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # We'll need to get these services from the service registry
        self.llm_service = None
        self.asset_manager = None
        
        logger.info("Model Generator Tool initialized")
    
    async def _ensure_services(self):
        """Ensure required services are available"""
        if self.llm_service is None:
            # Register for LLM service availability
            await self.redis_bus.subscribe('service:llm_service:available', self._handle_llm_service_available)
        
        if self.asset_manager is None:
            # Register for Asset Manager service availability
            await self.redis_bus.subscribe('service:asset_manager:available', self._handle_asset_manager_available)
    
    async def _handle_llm_service_available(self, message: Dict[str, Any]):
        """Handle LLM service availability"""
        service_id = message.get('service_id')
        # Request service instance via RPC
        response = await self.redis_bus.call_rpc('service:get', {'service_id': service_id})
        if 'error' not in response:
            self.llm_service = response.get('service')
    
    async def _handle_asset_manager_available(self, message: Dict[str, Any]):
        """Handle Asset Manager service availability"""
        service_id = message.get('service_id')
        # Request service instance via RPC
        response = await self.redis_bus.call_rpc('service:get', {'service_id': service_id})
        if 'error' not in response:
            self.asset_manager = response.get('service')
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a 3D model from a description
        
        Args:
            parameters: Model parameters
                - description: Model description
                - model_type: Type of model to generate (mesh, curve, etc.)
                - style: Model style (realistic, cartoon, etc.)
                - name: Model name
                
        Returns:
            Model generation result
        """
        try:
            # Connect required services
            await self._ensure_services()
            
            # Get parameters
            description = parameters.get('description', '')
            model_type = parameters.get('model_type', 'mesh')
            style = parameters.get('style', 'basic')
            name = parameters.get('name', f"Model_{uuid.uuid4().hex[:8]}")
            
            # If no description is provided but we're in an agent context
            # use a default description for demonstration
            if not description:
                # For agent testing, use a default description
                description = "A simple geometric model with basic materials"
                logger.info(f"No description provided, using default: '{description}'")
            
            # Generate Blender script for the model
            script = await self._generate_model_script(description, model_type, style, name)
            
            # Generate model file path
            model_file_path = os.path.join(self.output_dir, f"{name}.blend")
            
            # Store script in a file for reference
            script_file_path = os.path.join(self.output_dir, f"{name}_script.py")
            with open(script_file_path, 'w') as f:
                f.write(script)
            
            # TODO: Actually execute the script with Blender to create the model
            # For now, we just return the script as proof of concept
            
            # Store the script as an asset if asset manager is available
            asset_id = None
            if self.asset_manager:
                asset_id = await self.asset_manager.store_asset(script_file_path, {
                    'name': name,
                    'description': description,
                    'model_type': model_type,
                    'style': style,
                    'type': 'model_script'
                }, 'script')
            
            return {
                'status': 'success',
                'name': name,
                'description': description,
                'model_type': model_type,
                'style': style,
                'script_path': script_file_path,
                'model_path': model_file_path,  # This would be the path if we actually created the model
                'asset_id': asset_id,
                'message': f"Generated model script for '{name}'",
                'script': script[:500] + "..." if len(script) > 500 else script  # Preview of the script
            }
        except Exception as e:
            logger.error(f"Error generating model: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _generate_model_script(self, description: str, model_type: str, style: str, name: str) -> str:
        """
        Generate Blender Python script for creating a 3D model
        
        Args:
            description: Model description
            model_type: Type of model to generate
            style: Model style
            name: Model name
            
        Returns:
            Blender Python script
        """
        # Create prompt for LLM
        prompt = self._create_model_generation_prompt(description, model_type, style, name)
        
        # Get script from LLM
        if self.llm_service:
            # Use LLM service
            response = await self.llm_service.generate(prompt, parameters={'temperature': 0.7})
        else:
            # Fallback for development/testing
            logger.warning("LLM service not available, using fallback model script")
            response = self._get_fallback_model_script(description, model_type, style, name)
        
        # Extract code from response
        import re
        script_match = re.search(r'```python\s*(.*?)\s*```', response, re.DOTALL)
        
        if script_match:
            script = script_match.group(1)
        else:
            # If no code block found, use the whole response
            script = response
        
        return script
    
    def _create_model_generation_prompt(self, description: str, model_type: str, style: str, name: str) -> str:
        """
        Create model generation prompt
        
        Args:
            description: Model description
            model_type: Type of model to generate
            style: Model style
            name: Model name
            
        Returns:
            LLM prompt
        """
        return f"""Generate a Blender Python script to create a 3D model based on the following description.

Description: {description}
Model Type: {model_type}
Style: {style}
Name: {name}

Your script should:
1. Create the model procedurally using Blender's Python API
2. Add appropriate materials and textures
3. Set up proper naming for objects and materials
4. Include comments explaining key parts of the code
5. Be ready to run in Blender without modifications

Focus on creating a clean, efficient script that produces a high-quality model.
Only return the Python code, no explanations needed.

```python
"""
    
    def _get_fallback_model_script(self, description: str, model_type: str, style: str, name: str) -> str:
        """
        Get fallback model script
        
        Args:
            description: Model description
            model_type: Type of model to generate
            style: Model style
            name: Model name
            
        Returns:
            Fallback Blender Python script
        """
        if model_type == 'mesh':
            return f"""# Fallback model script for: {description}
# Style: {style}
# Name: {name}

import bpy
import math
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple mesh model
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "{name}"

# Add a material
mat = bpy.data.materials.new(name="{name}_Material")
mat.diffuse_color = (0.8, 0.2, 0.2, 1.0)  # Red-ish color
sphere.data.materials.append(mat)

# Apply some modifiers
bpy.ops.object.modifier_add(type='SUBSURF')
sphere.modifiers["Subdivision"].levels = 2

bpy.ops.object.modifier_add(type='DISPLACE')
texture = bpy.data.textures.new("{name}_Texture", type='NOISE')
sphere.modifiers["Displace"].texture = texture
sphere.modifiers["Displace"].strength = 0.2

# Add a simple armature
bpy.ops.object.armature_add(location=(0, 0, 0))
armature = bpy.context.active_object
armature.name = "{name}_Armature"

# Parent the sphere to the armature
sphere.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.parent_set(type='ARMATURE')

# Add a camera to render the model
bpy.ops.object.camera_add(location=(0, -5, 0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 5))
light = bpy.context.active_object
light.data.energy = 2.0

# Set render settings for preview
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("Generated model: {name}")
"""
        elif model_type == 'curve':
            return f"""# Fallback curve model script for: {description}
# Style: {style}
# Name: {name}

import bpy
import math
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a new curve
curve_data = bpy.data.curves.new('{name}_curve', 'CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 12
curve_data.bevel_depth = 0.1
curve_data.bevel_resolution = 6

# Create the curve object
curve_obj = bpy.data.objects.new('{name}', curve_data)
bpy.context.collection.objects.link(curve_obj)

# Create a spline for the curve
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(4)  # 5 points total

# Set point coordinates
points = spline.bezier_points
points[0].co = (0, 0, 0)
points[0].handle_left = (-1, 0, 0)
points[0].handle_right = (1, 0, 0)

points[1].co = (2, 2, 0)
points[1].handle_left = (1, 2, 0)
points[1].handle_right = (3, 2, 0)

points[2].co = (4, -1, 0)
points[2].handle_left = (3, -1, 0)
points[2].handle_right = (5, -1, 0)

points[3].co = (6, 1, 3)
points[3].handle_left = (5, 1, 3)
points[3].handle_right = (7, 1, 3)

points[4].co = (8, 0, 0)
points[4].handle_left = (7, 0, 0)
points[4].handle_right = (9, 0, 0)

# Add a material
mat = bpy.data.materials.new(name="{name}_Material")
mat.diffuse_color = (0.2, 0.8, 0.2, 1.0)  # Green-ish color
curve_obj.data.materials.append(mat)

# Add a camera to render the model
bpy.ops.object.camera_add(location=(4, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(90))
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', radius=1, location=(4, -4, 8))
light = bpy.context.active_object
light.data.energy = 2.0

# Set render settings for preview
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("Generated curve model: {name}")
"""
        else:
            return f"""# Fallback script for unknown model type: {model_type}
# Description: {description}
# Style: {style}
# Name: {name}

import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple cube as placeholder
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "{name}"

# Add a material
mat = bpy.data.materials.new(name="{name}_Material")
mat.diffuse_color = (0.5, 0.5, 0.8, 1.0)  # Blue-ish color
cube.data.materials.append(mat)

# Add text note about the model
bpy.ops.object.text_add(location=(0, 0, 2))
text = bpy.context.active_object
text.name = "{name}_Description"
text.data.body = "Model: {name}\\nDescription: {description}\\nStyle: {style}"
text.data.size = 0.5

# Add a camera to render the model
bpy.ops.object.camera_add(location=(0, -5, 0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 5))
light = bpy.context.active_object
light.data.energy = 2.0

print("Generated placeholder model: {name}")
"""
