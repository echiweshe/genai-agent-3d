"""
Scene Generator Tool for creating 3D scenes from descriptions
"""

import logging
import json
import uuid
import re
import traceback
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
            
            # For direct usage, try to create a new LLM service
            try:
                from genai_agent.services.llm import LLMService
                import yaml
                config_path = "config.yaml"
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                self.llm_service = LLMService(config.get('llm', {}))
                logger.info("Created LLM service directly")
            except Exception as e:
                logger.warning(f"Could not create LLM service directly: {str(e)}")
        
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
        try:
            # Connect required services
            await self._ensure_services()
            
            # Get parameters
            description = parameters.get('description', '')
            style = parameters.get('style', 'basic')
            name = parameters.get('name', f"Scene_{uuid.uuid4().hex[:8]}")
            
            # If no description is provided but we're in an agent context
            # use a default description for demonstration
            if not description:
                # For agent testing, use a default description
                description = "A simple scene with a mountain, trees, and a lake"
                logger.info(f"No description provided, using default: '{description}'")
            
            # Generate scene data
            scene_data = await self._generate_scene_data(description, style, name)
            
            # Create scene in Scene Manager if available
            scene_id = None
            if self.scene_manager:
                scene_id = await self.scene_manager.create_scene(scene_data)
            
            # Return scene information
            return {
                'status': 'success',
                'scene_id': scene_id,
                'scene_name': scene_data.get('name'),
                'description': description,
                'style': style,
                'object_count': len(scene_data.get('objects', [])),
                'message': f"Generated scene '{scene_data.get('name')}' with {len(scene_data.get('objects', []))} objects"
            }
        except Exception as e:
            logger.error(f"Error generating scene: {str(e)}")
            logger.error(traceback.format_exc())
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
        
        try:
            # Get scene data from LLM
            if self.llm_service:
                # Use LLM service
                logger.info(f"Generating scene for '{description}' with style '{style}'")
                response = await self.llm_service.generate(prompt, parameters={'temperature': 0.7})
                
                # Log raw response for debugging (truncated)
                log_response = response
                if len(log_response) > 500:
                    log_response = log_response[:500] + "..."
                logger.debug(f"Raw LLM response: {log_response}")
                
                # Check for error responses
                if isinstance(response, str) and response.startswith("Error:"):
                    logger.warning(f"LLM service returned an error: {response}")
                    logger.info("Using fallback scene data due to LLM error")
                    return self._get_fallback_scene_data(description, style, name)
                
                # Extract and parse JSON using multiple methods
                scene_data = self._extract_json_from_response(response)
                if scene_data:
                    return scene_data
                
                # If extraction failed, use fallback
                logger.warning("Could not extract valid JSON from LLM response, using fallback")
                return self._get_fallback_scene_data(description, style, name)
            else:
                # Fallback for development/testing
                logger.warning("LLM service not available, using fallback scene data")
                return self._get_fallback_scene_data(description, style, name)
        except Exception as e:
            logger.error(f"Error generating scene data: {str(e)}")
            logger.error(traceback.format_exc())
            return self._get_fallback_scene_data(description, style, name)
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response using multiple methods
        
        Args:
            response: LLM response text
            
        Returns:
            Extracted JSON data or None if extraction failed
        """
        # Method 1: Direct JSON parsing
        try:
            scene_data = json.loads(response)
            logger.info("Successfully parsed direct JSON response")
            return scene_data
        except json.JSONDecodeError:
            logger.debug("Direct JSON parsing failed, trying alternatives")
        
        # Method 2: Extract from code block
        try:
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                scene_data = json.loads(json_str)
                logger.info("Successfully parsed JSON from code block")
                return scene_data
        except (json.JSONDecodeError, AttributeError):
            logger.debug("JSON code block extraction failed")
        
        # Method 3: Find JSON-like structure with regex
        try:
            # Find the first { that has a matching }
            start_idx = response.find('{')
            if start_idx >= 0:
                # Find the matching closing brace
                brace_count = 0
                for i in range(start_idx, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Extract the JSON substring
                            json_str = response[start_idx:i+1]
                            
                            # Clean up common issues
                            json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)  # Remove // comments
                            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)  # Remove /* */ comments
                            
                            scene_data = json.loads(json_str)
                            logger.info("Successfully parsed JSON using brace matching")
                            return scene_data
            
            # Another approach: use regular expression
            json_match = re.search(r'(\{[\s\S]*\})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                scene_data = json.loads(json_str)
                logger.info("Successfully parsed JSON using regex extraction")
                return scene_data
        except (json.JSONDecodeError, AttributeError, IndexError):
            logger.debug("JSON structure extraction failed")
        
        # If all methods fail, return None
        return None
    
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
        return f"""You are a 3D scene generation specialist. Generate a 3D scene based on the following description and style.

Description: {description}
Style: {style}
Name: {name}

Create a JSON structure that defines the scene with objects. Each object must have:
- id (a unique identifier)
- type (cube, sphere, plane, camera, light, etc.)
- name (descriptive name)
- position [x, y, z] coordinates
- rotation [x, y, z] in radians
- scale [x, y, z] scale factors
- properties (materials, etc.)

Your response must be a valid JSON object with this exact structure:
{{
  "name": "{name}",
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

Include appropriate camera, lighting, and at least 3-4 objects in the scene. Your response must be valid JSON that can be parsed directly.
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
