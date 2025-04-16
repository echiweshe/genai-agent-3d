"""
LLM Service for interacting with language models
"""

import logging
import aiohttp
import json
import os
import sys
import requests
import subprocess
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service for interacting with language models (local or API-based)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM Service
        
        Args:
            config: LLM configuration parameters
        """
        self.type = config.get('type', 'local')
        self.provider = config.get('provider', 'ollama')
        self.model = config.get('model', 'llama3')
        self.api_key = config.get('api_key')
        self.api_url = self._get_api_url()
        
        # Fallback models to try if the primary model is not available
        self.fallback_models = [
            "llama3.2:latest",
            "deepseek-coder-v2:latest",
            "deepseek-coder:latest"
        ]
        
        logger.info(f"LLM Service initialized with {self.provider} ({self.type})")
        
        # Check if Ollama is available
        if self.provider == 'ollama' and not self.check_ollama_available():
            logger.warning("Ollama server is not running. Some features may not work.")
            logger.info("You can start Ollama by running: python run.py ollama start")
    
    def _get_api_url(self) -> str:
        """Get the API URL based on provider"""
        if self.type == 'local':
            if self.provider == 'ollama':
                return 'http://localhost:11434/api/generate'
            # Add other local providers here
        else:
            if self.provider == 'openai':
                return 'https://api.openai.com/v1/chat/completions'
            elif self.provider == 'anthropic':
                return 'https://api.anthropic.com/v1/messages'
            # Add other API providers here
        
        # Default
        return 'http://localhost:11434/api/generate'
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available in Ollama"""
        if not self.check_ollama_available():
            return False
            
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(m.get('name') == model_name for m in models)
            return False
        except Exception:
            return False
    
    async def _list_available_models(self) -> List[str]:
        """List available models"""
        if self.provider != 'ollama':
            return []
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:11434/api/tags') as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('models', [])
                        return [model.get('name') for model in models if model.get('name')]
                    return []
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    async def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None, 
                      parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate text from the language model
        
        Args:
            prompt: The prompt to send to the model
            context: Optional context information
            parameters: Optional generation parameters
            
        Returns:
            Generated text from the model
        """
        logger.info(f"Generating text with {self.provider} model: {self.model}")
        
        # Check if Ollama is running and try to start it if not
        if self.provider == 'ollama' and not self.check_ollama_available():
            self._try_start_ollama()
        
        # Prepare request
        if self.type == 'local':
            return await self._generate_local(prompt, context, parameters)
        else:
            return await self._generate_api(prompt, context, parameters)
    
    async def _generate_local(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                             parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate text using local model"""
        # Default parameters
        params = {
            'temperature': 0.7,
            'max_tokens': 2048,
            'top_p': 0.95,
        }
        
        # Update with custom parameters
        if parameters:
            params.update(parameters)
        
        # Prepare prompt with context
        full_prompt = self._prepare_prompt(prompt, context)
        
        # Different formats based on provider
        if self.provider == 'ollama':
            # Ollama request format
            request_data = {
                'model': self.model,
                'prompt': full_prompt,
                'stream': False,  # Don't stream the response
                **params
            }
            api_url = self.api_url
        else:
            # Generic format for other local providers
            request_data = {
                'model': self.model,
                'prompt': full_prompt,
                **params
            }
            api_url = self.api_url
        
        try:
            logger.debug(f"Sending request to {api_url} with model {self.model}")
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(api_url, json=request_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Extract response based on provider
                        if self.provider == 'ollama':
                            return response_data.get('response', '')
                        else:
                            return response_data.get('response', '')
                    else:
                        error_text = await response.text()
                        logger.error(f"Error from local model: {error_text}")
                        
                        # Check for model not found error
                        if 'model not found' in error_text.lower():
                            logger.warning(f"Model '{self.model}' not found. Attempting to list available models.")
                            available_models = await self._list_available_models()
                            
                            if available_models:
                                logger.info(f"Available models: {', '.join(available_models)}")
                                
                                # Try to find a model that matches from our fallback list
                                for fallback_model in self.fallback_models:
                                    if fallback_model in available_models:
                                        logger.info(f"Trying fallback model: {fallback_model}")
                                        
                                        # Update the model name for future requests
                                        self.model = fallback_model
                                        
                                        # Try again with the new model
                                        request_data['model'] = fallback_model
                                        try:
                                            async with session.post(api_url, json=request_data) as retry_response:
                                                if retry_response.status == 200:
                                                    retry_data = await retry_response.json()
                                                    return retry_data.get('response', '')
                                                else:
                                                    error_text = await retry_response.text()
                                                    logger.warning(f"Fallback model {fallback_model} also failed: {error_text}")
                                        except Exception as e:
                                            logger.warning(f"Error with fallback model {fallback_model}: {str(e)}")
                            
                        # Return error message
                        return f"Error: {response.status} - {error_text}"
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error calling local model: {error_msg}")
            
            # Fallback for development
            logger.warning("Using simulated LLM response for development")
            if 'task' in prompt.lower() and 'plan' in prompt.lower():
                # Simulate a task planning response
                return '[{"tool_name": "scene_generator", "parameters": {"description": "A simple scene with a red cube on a blue plane", "style": "basic"}, "description": "Generate a 3D scene with a red cube on a blue plane"}]'
            return "Simulated LLM response for development"
    
    def _try_start_ollama(self) -> bool:
        """Try to start Ollama server"""
        logger.info("Attempting to start Ollama server...")
        
        try:
            # Path to Ollama helper script
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ollama_script = os.path.join(script_dir, "tools", "ollama_helper.py")
            
            if os.path.exists(ollama_script):
                subprocess.run([sys.executable, ollama_script, "start"], 
                              capture_output=True, timeout=10)
                
                # Check if it started successfully
                if self.check_ollama_available():
                    logger.info("Successfully started Ollama server")
                    return True
        except Exception as e:
            logger.error(f"Error trying to start Ollama: {str(e)}")
        
        logger.warning("Failed to start Ollama server")
        return False
    
    async def _generate_api(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                           parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate text using API-based model"""
        # Default parameters
        params = {
            'temperature': 0.7,
            'max_tokens': 2048,
            'top_p': 0.95,
        }
        
        # Update with custom parameters
        if parameters:
            params.update(parameters)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
        }
        
        if self.api_key:
            if self.provider == 'openai':
                headers['Authorization'] = f"Bearer {self.api_key}"
            elif self.provider == 'anthropic':
                headers['x-api-key'] = self.api_key
        
        # Prepare prompt with context
        full_prompt = self._prepare_prompt(prompt, context)
        
        # Prepare request data based on provider
        if self.provider == 'openai':
            request_data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': full_prompt}],
                'temperature': params.get('temperature'),
                'max_tokens': params.get('max_tokens'),
                'top_p': params.get('top_p'),
            }
        elif self.provider == 'anthropic':
            request_data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': full_prompt}],
                'temperature': params.get('temperature'),
                'max_tokens': params.get('max_tokens'),
            }
        else:
            # Default format
            request_data = {
                'model': self.model,
                'prompt': full_prompt,
                **params
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=request_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Extract text based on provider
                        if self.provider == 'openai':
                            return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                        elif self.provider == 'anthropic':
                            return response_data.get('content', [{}])[0].get('text', '')
                        else:
                            return response_data.get('response', '')
                    else:
                        error_text = await response.text()
                        logger.error(f"Error from API: {error_text}")
                        return f"Error: {response.status} - {error_text}"
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            return f"Error: {str(e)}"
    
    def _prepare_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Prepare prompt with context"""
        if context is None:
            return prompt
        
        if self.provider == 'ollama' and 'deepseek-coder' in self.model:
            # Special formatting for deepseek-coder model
            base_prompt = """You are a 3D modeling assistant specialized in Blender Python scripting.
            
Focus on generating precise, efficient, and well-structured Python code for Blender.
When providing solutions:
- Use clean, optimized code
- Add detailed comments
- Follow Blender Python API best practices
- Ensure the code is ready to run in Blender without modifications

"""
            return base_prompt + prompt
        
        # Add context to prompt
        if 'scene' in context:
            scene_desc = json.dumps(context['scene'], indent=2)
            prompt = f"Scene information:\n{scene_desc}\n\n{prompt}"
        
        if 'history' in context:
            history_str = "\n".join([f"- {item}" for item in context['history']])
            prompt = f"Previous actions:\n{history_str}\n\n{prompt}"
        
        return prompt
    
    async def classify_task(self, instruction: str) -> Dict[str, Any]:
        """
        Classify a user instruction into a structured task
        
        Args:
            instruction: User instruction
            
        Returns:
            Structured task information
        """
        prompt = f"""Analyze the following instruction and convert it into a structured task for a 3D scene generation agent.

Instruction: {instruction}

Output a JSON object with the following structure:
{{
  "task_type": "scene_generation" | "model_creation" | "animation" | "modification" | "analysis",
  "description": "Brief description of what needs to be done",
  "parameters": {{
    // Task-specific parameters
  }}
}}

JSON Response:"""
        
        response = await self.generate(prompt, parameters={'temperature': 0.2})
        
        # Check for error response
        if isinstance(response, str) and response.startswith("Error:"):
            logger.warning(f"LLM error during task classification: {response}")
            return {
                "task_type": "scene_generation",
                "description": instruction,
                "parameters": {}
            }
        
        try:
            # Try to parse the response as JSON
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # If the response is not valid JSON, try to extract JSON from it
            import re
            
            # Look for JSON pattern
            json_match = re.search(r'({[\s\S]*})', response)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    return result
                except json.JSONDecodeError:
                    pass
            
            # Return a fallback result
            logger.warning(f"Failed to parse LLM response as JSON: {response}")
            return {
                "task_type": "scene_generation",
                "description": instruction,
                "parameters": {}
            }
    
    async def plan_task_execution(self, task: Dict[str, Any], available_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Plan the execution of a task using available tools
        
        Args:
            task: Task information
            available_tools: List of available tools
            
        Returns:
            List of steps to execute
        """
        # Prepare tool information
        tools_info = json.dumps([
            {
                "name": tool["name"],
                "description": tool["description"]
            }
            for tool in available_tools
        ], indent=2)
        
        # Prepare task information
        task_info = json.dumps(task, indent=2)
        
        # Create prompt
        prompt = f"""Given the following task and available tools, create a step-by-step execution plan.

Task: {task_info}

Available Tools: {tools_info}

Output a JSON array of steps, where each step has the following structure:
{{
  "tool_name": "name of the tool to use",
  "parameters": {{
    // Tool-specific parameters
  }},
  "description": "Description of what this step does"
}}

Ensure each step can be executed by one of the available tools. If the task cannot be completed with the available tools, explain why in the output.

JSON Response:"""
        
        response = await self.generate(prompt, parameters={'temperature': 0.2})
        
        # Check for error response
        if isinstance(response, str) and response.startswith("Error:"):
            logger.warning(f"LLM error during planning: {response}")
            return [{
                "tool_name": "scene_generator",
                "parameters": {
                    "description": task.get("description", "Create a simple 3D scene"),
                    "style": "basic"
                },
                "description": f"Generate a scene based on the description: {task.get('description', 'Create a simple 3D scene')}"
            }]
        
        try:
            # Try to parse the response as JSON
            result = json.loads(response)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'steps' in result:
                return result['steps']
            else:
                return [result]
        except json.JSONDecodeError:
            # If the response is not valid JSON, try to extract JSON from it
            import re
            
            # Look for JSON array pattern
            json_match = re.search(r'(\[[\s\S]*\])', response)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    return result
                except json.JSONDecodeError:
                    pass
            
            # Return a fallback result
            logger.warning(f"Failed to parse LLM response as JSON: {response}")
            return [{
                "tool_name": "scene_generator",
                "parameters": {
                    "description": task.get("description", "Create a simple 3D scene")
                },
                "description": f"Generate a scene based on the description: {task.get('description', 'Create a simple 3D scene')}"
            }]
