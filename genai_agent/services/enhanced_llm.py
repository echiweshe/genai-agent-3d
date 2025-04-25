"""
Enhanced LLM Service for dynamically selecting and interacting with language models
"""

import logging
import aiohttp
import json
import os
import sys
import asyncio
import time
import subprocess
import threading
from typing import Dict, Any, List, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor
import uuid

logger = logging.getLogger(__name__)

# Load environment variables for API keys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("dotenv not installed, using environment variables as is")

class LLMProviderConfig:
    """Configuration for an LLM provider"""
    
    def __init__(self, name: str, api_key_env: str, url: str, models: List[Dict[str, Any]]):
        self.name = name
        self.api_key = os.environ.get(api_key_env, "")
        self.url = url
        self.models = models
        self.is_local = name.lower() == "ollama"
        
    def get_model_params(self, model_id: str) -> Dict[str, Any]:
        """Get parameters for a specific model"""
        for model in self.models:
            if model["id"] == model_id:
                return model
        return {}

# Provider configurations
PROVIDERS = [
    LLMProviderConfig(
        name="Ollama",
        api_key_env="OLLAMA_API_KEY",  # Not typically needed but included for consistency
        url="http://localhost:11434/api/generate",
        models=[
            {
                "id": "llama3:latest",
                "name": "Llama3",
                "context_length": 8192,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "request_format": "ollama"
            },
            {
                "id": "llama3.2:latest",
                "name": "Llama3.2",
                "context_length": 8192,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "request_format": "ollama"
            },
            {
                "id": "deepseek-coder:latest",
                "name": "DeepSeek Coder",
                "context_length": 8192,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "request_format": "ollama"
            }
        ],
    ),
    LLMProviderConfig(
        name="OpenAI",
        api_key_env="OPENAI_API_KEY",
        url="https://api.openai.com/v1/chat/completions",
        models=[
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "context_length": 128000,
                "input_cost": 0.00005,  # $0.05 per 1K tokens
                "output_cost": 0.00015,  # $0.15 per 1K tokens
                "request_format": "openai"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "context_length": 8192,
                "input_cost": 0.00003,
                "output_cost": 0.00006,
                "request_format": "openai"
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "context_length": 16385,
                "input_cost": 0.000001,
                "output_cost": 0.000002,
                "request_format": "openai"
            }
        ],
    ),
    LLMProviderConfig(
        name="Anthropic",
        api_key_env="ANTHROPIC_API_KEY",
        url="https://api.anthropic.com/v1/messages",
        models=[
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "context_length": 200000,
                "input_cost": 0.00003,  # $0.03 per 1K tokens
                "output_cost": 0.00015,  # $0.15 per 1K tokens
                "request_format": "anthropic"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "context_length": 200000,
                "input_cost": 0.000003,  # $0.003 per 1K tokens
                "output_cost": 0.000015,  # $0.015 per 1K tokens
                "request_format": "anthropic"
            },
            {
                "id": "claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "context_length": 200000,
                "input_cost": 0.000003,  # $0.003 per 1K tokens
                "output_cost": 0.000015,  # $0.015 per 1K tokens
                "request_format": "anthropic"
            }
        ],
    ),
    LLMProviderConfig(
        name="Hunyuan3D",
        api_key_env="HUNYUAN3D_API_KEY", 
        url="http://localhost:3001/api/generate",  # Would need to be updated based on your Hunyuan3D service
        models=[
            {
                "id": "hunyuan3d",
                "name": "Hunyuan 3D",
                "context_length": 8192,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "request_format": "hunyuan"  # Custom format
            }
        ]
    )
]

class RequestQueue:
    """Thread-safe queue for LLM requests with concurrency control"""
    
    def __init__(self, max_concurrent=5, max_queue_size=100):
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self.active_requests = 0
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.lock = asyncio.Lock()
        self.request_events = {}  # Track completion events by request ID
    
    async def add_request(self, provider: str, model: str, request_data: Dict[str, Any], timeout: int = 120) -> Tuple[str, asyncio.Event]:
        """Add a request to the queue and return a request ID and event to wait on"""
        request_id = str(uuid.uuid4())
        completion_event = asyncio.Event()
        self.request_events[request_id] = {
            "event": completion_event,
            "result": None,
            "error": None,
            "timestamp": time.time(),
            "timeout": timeout
        }
        
        # Add to queue
        await self.queue.put({
            "id": request_id,
            "provider": provider,
            "model": model,
            "data": request_data,
            "timestamp": time.time()
        })
        
        return request_id, completion_event
    
    async def process_request(self, request: Dict[str, Any]) -> None:
        """Process a single request (to be implemented by LLMService)"""
        # Placeholder - will be set by LLMService
        pass
    
    async def start_processing(self):
        """Start processing requests from the queue"""
        while True:
            # Check for and clean up timed out requests
            await self._cleanup_timed_out_requests()
            
            # Get the next request from the queue
            request = await self.queue.get()
            
            # Wait until we're below the concurrency limit
            async with self.lock:
                while self.active_requests >= self.max_concurrent:
                    # Release the lock while waiting
                    await asyncio.sleep(0.1)
                    async with self.lock:
                        pass  # Re-acquire lock to check again
                
                # Increment active requests
                self.active_requests += 1
            
            # Process the request in a separate task
            asyncio.create_task(self._process_request_wrapper(request))
    
    async def _process_request_wrapper(self, request: Dict[str, Any]):
        """Wrapper to handle request processing and errors"""
        request_id = request["id"]
        
        try:
            # Call the process_request method implemented by LLMService
            result = await self.process_request(request)
            
            # Store the result and set the completion event
            if request_id in self.request_events:
                self.request_events[request_id]["result"] = result
                self.request_events[request_id]["event"].set()
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {str(e)}")
            
            # Store the error and set the completion event
            if request_id in self.request_events:
                self.request_events[request_id]["error"] = str(e)
                self.request_events[request_id]["event"].set()
        finally:
            # Decrement active requests
            async with self.lock:
                self.active_requests -= 1
    
    async def _cleanup_timed_out_requests(self):
        """Clean up timed out requests"""
        current_time = time.time()
        to_remove = []
        
        for request_id, request_info in self.request_events.items():
            if not request_info["event"].is_set() and (current_time - request_info["timestamp"]) > request_info["timeout"]:
                # Request has timed out
                request_info["error"] = "Request timed out"
                request_info["event"].set()
                to_remove.append(request_id)
        
        # Remove timed out requests
        for request_id in to_remove:
            self.request_events.pop(request_id, None)

class EnhancedLLMService:
    """
    Enhanced service for interacting with multiple language models
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the LLM Service
        
        Args:
            config: Optional LLM configuration parameters
        """
        self.config = config or {}
        
        # Default settings
        self.default_provider = self.config.get("default_provider", "Ollama")
        self.default_model = self.config.get("default_model", "llama3:latest")
        
        # Request queue
        self.request_queue = RequestQueue(
            max_concurrent=self.config.get("max_concurrent", 5),
            max_queue_size=self.config.get("max_queue_size", 100)
        )
        
        # Set the process_request method
        self.request_queue.process_request = self._process_request
        
        # Providers and models
        self.providers = {p.name: p for p in PROVIDERS}
        
        # Start processing in the background
        self.processing_task = asyncio.create_task(self.request_queue.start_processing())
        
        # Default generation parameters
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.95,
        }
        
        logger.info(f"Enhanced LLM Service initialized")
        
        # Check if Ollama is available
        if not self.check_ollama_available():
            logger.warning("Ollama server is not running. Local models will not be available.")
            logger.info("You can start Ollama by running: python manage_services.py start ollama")
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            return response.status_code == 200
        except Exception:
            logger.info("Ollama server is not running.")
            return False
    
    async def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request from the queue
        
        Args:
            request: Request data including provider, model, and request data
            
        Returns:
            Response data
        """
        provider_name = request["provider"]
        model_id = request["model"]
        request_data = request["data"]
        
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        # Get model parameters
        model_params = provider.get_model_params(model_id)
        if not model_params:
            raise ValueError(f"Unknown model: {model_id} for provider {provider_name}")
        
        # Handle different provider formats
        request_format = model_params.get("request_format", "generic")
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Add API key if available
        if provider.api_key:
            if provider_name == "OpenAI":
                headers['Authorization'] = f"Bearer {provider.api_key}"
            elif provider_name == "Anthropic":
                headers['x-api-key'] = provider.api_key
                headers['anthropic-version'] = '2023-06-01'
            else:
                # Generic API key header
                headers['Authorization'] = f"Bearer {provider.api_key}"
        
        # Format the request based on provider requirements
        if request_format == "ollama":
            formatted_request = {
                "model": model_id,
                "prompt": request_data.get("prompt", ""),
                "stream": False,
                **request_data.get("parameters", {})
            }
        elif request_format == "openai":
            formatted_request = {
                "model": model_id,
                "messages": [{"role": "user", "content": request_data.get("prompt", "")}],
                **request_data.get("parameters", {})
            }
        elif request_format == "anthropic":
            formatted_request = {
                "model": model_id,
                "messages": [{"role": "user", "content": request_data.get("prompt", "")}],
                "max_tokens": request_data.get("parameters", {}).get("max_tokens", 2048),
                "temperature": request_data.get("parameters", {}).get("temperature", 0.7),
            }
        elif request_format == "hunyuan":
            # Format for Hunyuan 3D
            formatted_request = {
                "prompt": request_data.get("prompt", ""),
                "parameters": request_data.get("parameters", {})
            }
        else:
            # Generic format
            formatted_request = request_data
        
        # Send the request
        try:
            timeout = aiohttp.ClientTimeout(total=request_data.get("timeout", 120))
            connector = aiohttp.TCPConnector(limit=10, force_close=True)
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                logger.debug(f"Sending request to {provider.url} with model {model_id}")
                
                try:
                    async with session.post(provider.url, headers=headers, json=formatted_request) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            
                            # Extract text based on provider
                            if provider_name == "OpenAI":
                                result = {
                                    "text": response_data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                                    "raw_response": response_data,
                                    "usage": response_data.get("usage", {})
                                }
                            elif provider_name == "Anthropic":
                                result = {
                                    "text": response_data.get("content", [{}])[0].get("text", ""),
                                    "raw_response": response_data,
                                    "usage": {
                                        "input_tokens": response_data.get("usage", {}).get("input_tokens", 0),
                                        "output_tokens": response_data.get("usage", {}).get("output_tokens", 0)
                                    }
                                }
                            elif provider_name == "Ollama":
                                result = {
                                    "text": response_data.get("response", ""),
                                    "raw_response": response_data,
                                }
                            elif provider_name == "Hunyuan3D":
                                result = {
                                    "text": response_data.get("text", ""),
                                    "raw_response": response_data,
                                }
                            else:
                                result = {
                                    "text": str(response_data),
                                    "raw_response": response_data,
                                }
                            
                            logger.debug(f"Request to {provider_name}/{model_id} successful")
                            return result
                        else:
                            error_text = await response.text()
                            logger.error(f"HTTP {response.status} Error from {provider_name}: {error_text}")
                            
                            # Detailed error response
                            return {
                                "error": f"HTTP {response.status} Error from {provider_name}",
                                "details": error_text,
                                "provider": provider_name,
                                "model": model_id
                            }
                
                except asyncio.TimeoutError:
                    logger.error(f"Request to {provider_name}/{model_id} timed out")
                    return {"error": f"Request to {provider_name}/{model_id} timed out"}
                
                except Exception as e:
                    logger.error(f"Exception during request to {provider_name}/{model_id}: {str(e)}")
                    return {"error": f"Exception: {str(e)}"}
        
        except Exception as e:
            logger.error(f"Error setting up request to {provider_name}/{model_id}: {str(e)}")
            return {"error": f"Error setting up request: {str(e)}"}
    
    async def generate(self, prompt: str, 
                       provider: str = None, 
                       model: str = None, 
                       context: Optional[Dict[str, Any]] = None,
                       parameters: Optional[Dict[str, Any]] = None,
                       timeout: int = 120) -> Dict[str, Any]:
        """
        Generate text from the specified language model
        
        Args:
            prompt: The prompt to send to the model
            provider: Provider name (e.g., "OpenAI", "Anthropic", "Ollama")
            model: Model ID (e.g., "gpt-4", "claude-3-opus", "llama3:latest")
            context: Optional context information
            parameters: Optional generation parameters
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with the generated text and additional information
        """
        # Use default provider and model if not specified
        provider = provider or self.default_provider
        
        # If provider exists, but no model specified, use the first model for that provider
        if not model:
            if provider in self.providers and self.providers[provider].models:
                model = self.providers[provider].models[0]["id"]
            else:
                model = self.default_model
        
        # Prepare parameters with defaults
        params = self.default_params.copy()
        if parameters:
            params.update(parameters)
        
        # Prepare prompt with context
        full_prompt = self._prepare_prompt(prompt, provider, model, context)
        
        # Add request to queue
        request_data = {
            "prompt": full_prompt,
            "parameters": params,
            "timeout": timeout
        }
        
        request_id, completion_event = await self.request_queue.add_request(
            provider=provider,
            model=model,
            request_data=request_data,
            timeout=timeout
        )
        
        # Wait for the request to complete
        try:
            await asyncio.wait_for(completion_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return {"error": f"Request timed out after {timeout}s"}
        
        # Get the result
        request_info = self.request_queue.request_events.get(request_id, {})
        result = request_info.get("result", {})
        error = request_info.get("error")
        
        if error:
            return {"error": error}
        
        # Clean up
        self.request_queue.request_events.pop(request_id, None)
        
        return result
    
    def _prepare_prompt(self, prompt: str, provider: str, model: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Prepare prompt with context"""
        if context is None:
            return prompt
        
        # Format context for different models
        provider_lower = provider.lower()
        model_lower = model.lower()
        
        # Special formatting based on model
        if provider_lower == "ollama" and "deepseek-coder" in model_lower:
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
        
        elif provider_lower == "anthropic":
            # Claude-specific formatting
            formatted_context = ""
            
            if 'scene' in context:
                scene_desc = json.dumps(context['scene'], indent=2)
                formatted_context += f"Scene information:\n{scene_desc}\n\n"
            
            if 'history' in context:
                history_str = "\n".join([f"- {item}" for item in context['history']])
                formatted_context += f"Previous actions:\n{history_str}\n\n"
            
            return formatted_context + prompt
        
        else:
            # Generic formatting
            if 'scene' in context:
                scene_desc = json.dumps(context['scene'], indent=2)
                prompt = f"Scene information:\n{scene_desc}\n\n{prompt}"
            
            if 'history' in context:
                history_str = "\n".join([f"- {item}" for item in context['history']])
                prompt = f"Previous actions:\n{history_str}\n\n{prompt}"
            
            return prompt
    
    async def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available LLM providers and their models
        
        Returns:
            List of provider information
        """
        result = []
        
        for provider_name, provider in self.providers.items():
            # Skip providers without API keys (except Ollama)
            if not provider.is_local and not provider.api_key:
                continue
            
            # Skip Ollama if it's not running
            if provider.is_local and not self.check_ollama_available():
                continue
            
            # Get available models for this provider
            models = []
            for model in provider.models:
                models.append({
                    "id": model["id"],
                    "name": model["name"],
                    "context_length": model["context_length"],
                    "input_cost": model["input_cost"],
                    "output_cost": model["output_cost"]
                })
            
            result.append({
                "name": provider_name,
                "is_local": provider.is_local,
                "models": models
            })
        
        return result
    
    async def estimate_cost(self, prompt: str, provider: str, model: str) -> Dict[str, Any]:
        """
        Estimate the cost of a request
        
        Args:
            prompt: The prompt to send to the model
            provider: Provider name
            model: Model ID
            
        Returns:
            Dictionary with cost estimate
        """
        # Simple token estimation (very rough)
        token_count = len(prompt.split())
        
        # Get provider and model information
        provider_obj = self.providers.get(provider)
        if not provider_obj:
            return {"error": f"Unknown provider: {provider}"}
        
        # Get model parameters
        model_params = provider_obj.get_model_params(model)
        if not model_params:
            return {"error": f"Unknown model: {model} for provider {provider}"}
        
        # Estimate input and output costs
        input_cost = token_count * model_params.get("input_cost", 0)
        
        # Assume output is roughly the same size as input for estimation
        output_tokens = token_count
        output_cost = output_tokens * model_params.get("output_cost", 0)
        
        total_cost = input_cost + output_cost
        
        return {
            "input_tokens": token_count,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "currency": "USD"
        }
    
    async def classify_task(self, instruction: str, provider: str = None, model: str = None) -> Dict[str, Any]:
        """
        Classify a user instruction into a structured task
        
        Args:
            instruction: User instruction
            provider: Optional provider to use
            model: Optional model to use
            
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
        
        response = await self.generate(
            prompt, 
            provider=provider, 
            model=model, 
            parameters={'temperature': 0.2}
        )
        
        # Check for error response
        if "error" in response:
            logger.warning(f"LLM error during task classification: {response['error']}")
            return {
                "task_type": "scene_generation",
                "description": instruction,
                "parameters": {}
            }
        
        # Try to parse the response as JSON
        text = response.get("text", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # If the response is not valid JSON, try to extract JSON from it
            import re
            
            # Look for JSON pattern
            json_match = re.search(r'({[\s\S]*})', text)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Return a fallback result
            logger.warning(f"Failed to parse LLM response as JSON: {text}")
            return {
                "task_type": "scene_generation",
                "description": instruction,
                "parameters": {}
            }
    
    async def plan_task_execution(self, 
                                 task: Dict[str, Any], 
                                 available_tools: List[Dict[str, Any]],
                                 provider: str = None, 
                                 model: str = None) -> List[Dict[str, Any]]:
        """
        Plan the execution of a task using available tools
        
        Args:
            task: Task information
            available_tools: List of available tools
            provider: Optional provider to use
            model: Optional model to use
            
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
        
        response = await self.generate(
            prompt, 
            provider=provider, 
            model=model, 
            parameters={'temperature': 0.2}
        )
        
        # Check for error response
        if "error" in response:
            logger.warning(f"LLM error during planning: {response['error']}")
            return [{
                "tool_name": "scene_generator",
                "parameters": {
                    "description": task.get("description", "Create a simple 3D scene"),
                    "style": "basic"
                },
                "description": f"Generate a scene based on the description: {task.get('description', 'Create a simple 3D scene')}"
            }]
        
        # Try to parse the response as JSON
        text = response.get("text", "")
        try:
            result = json.loads(text)
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
            json_match = re.search(r'(\[[\s\S]*\])', text)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    return result
                except json.JSONDecodeError:
                    pass
            
            # Return a fallback result
            logger.warning(f"Failed to parse LLM response as JSON: {text}")
            return [{
                "tool_name": "scene_generator",
                "parameters": {
                    "description": task.get("description", "Create a simple 3D scene")
                },
                "description": f"Generate a scene based on the description: {task.get('description', 'Create a simple 3D scene')}"
            }]