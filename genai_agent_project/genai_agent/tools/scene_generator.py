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
        # Log the response for debugging
        log_response = response
        if len(log_response) > 500:
            log_response = log_response[:500] + "..."
        logger.debug(f"Attempting to extract JSON from: {log_response}")
        
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
                # Clean up common issues before parsing
                json_str = re.sub(r'//.*?(?:\n|$)', '', json_str, flags=re.MULTILINE)  # Remove // comments
                json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)  # Remove /* */ comments
                scene_data = json.loads(json_str)
                logger.info("Successfully parsed JSON from code block")
                return scene_data
        except (json.JSONDecodeError, AttributeError):
            logger.debug("JSON code block extraction failed")
        
        # Method 3: Find JSON-like structure with regex - look for largest valid JSON object
        try:
            # Find all potential JSON objects in the response
            potential_jsons = []
            bracket_pattern = re.compile(r'\{([^{}]|\{[^{}]*\})*\}')
            for match in bracket_pattern.finditer(response):
                potential_json = match.group(0)
                try:
                    # Remove comments and other invalid JSON syntax
                    cleaned = re.sub(r'//.*?(?:\n|$)', '', potential_json, flags=re.MULTILINE)  # Remove // comments
                    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)  # Remove /* */ comments
                    cleaned = re.sub(r',\s*\}', '}', cleaned)  # Remove trailing commas
                    # Replace single quotes with double quotes for keys and string values
                    cleaned = re.sub(r"'([^']*)'\s*:", r'"\1":', cleaned)  # Replace 'key': with "key":
                    cleaned = re.sub(r":\s*'([^']*)'([,\}])", r':"\1"\2', cleaned)  # Replace :'value' with :"value"
                    
                    # Attempt to parse
                    parsed = json.loads(cleaned)
                    # Store if valid
                    potential_jsons.append((cleaned, len(cleaned)))
                except json.JSONDecodeError:
                    continue
            
            # If we found any valid JSON objects, return the largest one
            if potential_jsons:
                # Sort by size (largest first)
                potential_jsons.sort(key=lambda x: x[1], reverse=True)
                largest_json_str, _ = potential_jsons[0]
                scene_data = json.loads(largest_json_str)
                logger.info("Successfully parsed JSON using advanced regex extraction")
                return scene_data
        except Exception as e:
            logger.debug(f"Advanced JSON structure extraction failed: {str(e)}")
            logger.debug(traceback.format_exc())
        
        # Method 4: Find JSON-like structure with simple brace matching
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
                            json_str = re.sub(r'//.*?(?:\n|$)', '', json_str, flags=re.MULTILINE)  # Remove // comments
                            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)  # Remove /* */ comments
                            json_str = re.sub(r',\s*\}', '}', json_str)  # Remove trailing commas
                            # Replace single quotes with double quotes for keys and string values
                            json_str = re.sub(r"'([^']*)'\s*:", r'"\1":', json_str)  # Replace 'key': with "key":
                            json_str = re.sub(r":\s*'([^']*)'([,\}])", r':"\1"\2', json_str)  # Replace :'value' with :"value"
                            
                            scene_data = json.loads(json_str)
                            logger.info("Successfully parsed JSON using brace matching")
                            return scene_data
        except (json.JSONDecodeError, AttributeError, IndexError):
            logger.debug("Simple brace matching extraction failed")
        
        # If all methods fail, return None
        logger.warning("All JSON extraction methods failed")
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
        return f"""Your task is to output ONLY a valid JSON object to define a 3D scene. No explanations or comments, just the JSON.

Description: {description}
Style: {style}
Name: {name}

The JSON object must have this structure:
{{
  "name": "{name}",
  "description": "{description}",
  "objects": [
    {{
      "id": "uuid-here",
      "type": "cube",  // Use types like: cube, sphere, plane, camera, light
      "name": "Object Name",
      "position": [0, 0, 0],
      "rotation": [0, 0, 0],
      "scale": [1, 1, 1],
      "properties": {{
        "material": {{
          "name": "Material Name",
          "color": [1, 0, 0, 1]  // RGBA values between 0 and 1
        }}
      }}
    }}
  ]
}}

Include:
- A camera (position at distance to view the scene)
- At least one light source
- 2-3 objects related to the scene description

IMPORTANT: Your response must be ONLY valid JSON with NO comments or explanations. Don't include backticks (```) or 'json' text.
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
