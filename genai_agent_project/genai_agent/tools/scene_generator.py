"""
Scene Generator Tool for creating 3D scenes from descriptions
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.llm import LLMService
from genai_agent.services.scene_manager import SceneManager

logger = logging.getLogger(__name__)

class SceneGeneratorTool(Tool):
    """
    Tool for generating 3D scenes from descriptions
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the Scene Generator Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
        """
        super().__init__(
            name="scene_generator",
            description="Generates 3D scenes from text descriptions"
        )
        
        self.redis_bus = redis_bus
        self.config = config or {}
        
        # We'll need to get these services from the service registry
        self.llm_service = None
        self.scene_manager = None
        
        logger.info("Scene Generator Tool initialized")
    
    async def _ensure_services(self):
        """Ensure required services are available"""
        if self.llm_service is None:
            # Register for LLM service availability
            await self.redis_bus.subscribe('service:llm_service:available', self._handle_llm_service_available)
        
        if self.scene_manager is None:
            # Register for Scene Manager service availability
            await self.redis_bus.subscribe('service:scene_manager:available', self._handle_scene_manager_available)

    async def _handle_llm_service_available(self, message: Dict[str, Any]):
        """Handle LLM service availability"""
        service_id = message.get('service_id')
        # Request service instance via RPC
        response = await self.redis_bus.call_rpc('service:get', {'service_id': service_id})
        if 'error' not in response:
            self.llm_service = response.get('service')
    
    async def _handle_scene_manager_available(self, message: Dict[str, Any]):
        """Handle Scene Manager service availability"""
        service_id = message.get('service_id')
        # Request service instance via RPC
        response = await self.redis_bus.call_rpc('service:get', {'service_id': service_id})
        if 'error' not in response:
            self.scene_manager = response.get('service')
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a 3D scene from a description
        
        Args:
            parameters: Scene parameters
                - description: Scene description
                - style: Scene style (realistic, cartoon, etc.)
                - name: Scene name
                
        Returns:
            Generated scene information
        """
        await self._ensure_services()
        
        # Get parameters
        description = parameters.get('description', '')
        style = parameters.get('style', 'basic')
        name = parameters.get('name', f"Scene {uuid.uuid4().hex[:8]}")
        
        if not description:
            return {
                'status': 'error',
                'error': "Scene description is required"
            }
        
        try:
            # Generate scene using LLM
            scene_data = await self._generate_scene_data(description, style, name)
            
            # Create scene in Scene Manager
            scene_id = await self.scene_manager.create_scene(scene_data)
            
            return {
                'status': 'success',
                'scene_id': scene_id,
                'scene_name': scene_data.get('name'),
                'object_count': len(scene_data.get('objects', [])),
                'message': f"Generated scene '{scene_data.get('name')}' with {len(scene_data.get('objects', []))} objects"
            }
        except Exception as e:
            logger.error(f"Error generating scene: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _generate_scene_data(self, description: str, style: str, name: str) -> Dict[str, Any]:
        """
        Generate scene data from description
        
        Args:
            description: Scene description
            style: Scene style
            name: Scene name
            
        Returns:
            Scene data
        """
        # Create prompt for LLM
        prompt = self._create_scene_generation_prompt(description, style, name)
        
        # Get scene data from LLM
        if self.llm_service:
            # Use LLM service
            response = await self.llm_service.generate(prompt, parameters={'temperature': 0.7})
        else:
            # Fallback for development/testing
            logger.warning("LLM service not available, using fallback scene data")
            response = self._get_fallback_scene_data(description, style, name)
        
        # Parse JSON response
        try:
            scene_data = json.loads(response)
            return scene_data
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    scene_data = json.loads(json_match.group(1))
                    return scene_data
                except json.JSONDecodeError:
                    pass
            
            # If still can't parse, use fallback
            logger.warning("Failed to parse LLM response as JSON, using fallback scene data")
            return self._get_fallback_scene_data(description, style, name)
    
    def _create_scene_generation_prompt(self, description: str, style: str, name: str) -> str:
        """
        Create scene generation prompt
        
        Args:
            description: Scene description
            style: Scene style
            name: Scene name
            
        Returns:
            LLM prompt
        """
        return f"""Generate a 3D scene based on the following description and style.

Description: {description}
Style: {style}
Name: {name}

Create a JSON structure that defines the scene with objects. Each object should have:
- type (cube, sphere, plane, etc.)
- name
- position [x, y, z]
- rotation [x, y, z] in radians
- scale [x, y, z]
- properties (materials, etc.)

Output the JSON in this format:
```json
{{
  "name": "Scene Name",
  "description": "Detailed scene description",
  "objects": [
    {{
      "id": "unique-id-1",
      "type": "cube",
      "name": "Object Name",
      "position": [0, 0, 0],
      "rotation": [0, 0, 0],
      "scale": [1, 1, 1],
      "properties": {{
        "material": {{
          "name": "Material Name",
          "color": [r, g, b, a]
        }}
      }}
    }}
  ]
}}
```

Generate a complete scene with appropriate objects, camera, and lighting.
"""
    
    def _get_fallback_scene_data(self, description: str, style: str, name: str) -> Dict[str, Any]:
        """
        Get fallback scene data
        
        Args:
            description: Scene description
            style: Scene style
            name: Scene name
            
        Returns:
            Fallback scene data
        """
        return {
            "name": name,
            "description": f"A {style} scene with {description}",
            "objects": [
                {
                    "id": str(uuid.uuid4()),
                    "type": "cube",
                    "name": "Red Cube",
                    "position": [0, 0, 1],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1],
                    "properties": {
                        "material": {
                            "name": "Red",
                            "color": [1, 0, 0, 1]
                        }
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "plane",
                    "name": "Blue Plane",
                    "position": [0, 0, 0],
                    "rotation": [0, 0, 0],
                    "scale": [10, 10, 1],
                    "properties": {
                        "material": {
                            "name": "Blue",
                            "color": [0, 0, 1, 1]
                        },
                        "size": 10
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "camera",
                    "name": "Main Camera",
                    "position": [5, -5, 5],
                    "rotation": [0.955, 0, 0.785],
                    "scale": [1, 1, 1],
                    "properties": {}
                },
                {
                    "id": str(uuid.uuid4()),
                    "type": "light",
                    "name": "Sun Light",
                    "position": [0, 0, 10],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1],
                    "properties": {
                        "light_type": "SUN",
                        "energy": 1.0
                    }
                }
            ]
        }
