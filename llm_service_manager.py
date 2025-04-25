"""
LLM Service Manager for managing LLM services and routing requests
"""

import asyncio
import logging
import os
import json
from typing import Dict, Any, List, Optional, Union
import aioredis
import time
import uuid

logger = logging.getLogger(__name__)

class LLMServiceManager:
    """
    Manager for LLM services with Redis message bus integration
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize the LLM Service Manager
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self.requests = {}  # Track ongoing requests
        self.callbacks = {}  # Callbacks for request completion
        self.request_timeout = 120  # Default timeout in seconds
        self.running = False
        self.initialized = False
        
        # Initialize logging
        logger.info(f"LLM Service Manager initializing with Redis at {redis_url}")
    
    async def initialize(self):
        """Initialize the service manager"""
        if self.initialized:
            return
        
        logger.info("Initializing LLM Service Manager")
        
        try:
            # Connect to Redis
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Set up PubSub
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("llm:responses")
            
            self.initialized = True
            logger.info("LLM Service Manager initialized successfully")
            
            # Start message processing
            self.running = True
            asyncio.create_task(self._process_messages())
            asyncio.create_task(self._check_timeouts())
            
        except Exception as e:
            logger.error(f"Error initializing LLM Service Manager: {str(e)}")
            raise
    
    async def _process_messages(self):
        """Process messages from the PubSub channel"""
        if not self.initialized:
            logger.error("Cannot process messages: Service manager not initialized")
            return
        
        logger.info("Starting to process LLM service messages")
        
        try:
            while self.running:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if not message:
                    await asyncio.sleep(0.01)  # Small delay to prevent CPU spin
                    continue
                
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        request_id = data.get("request_id")
                        
                        if request_id in self.requests:
                            # Process response
                            if request_id in self.callbacks:
                                callback_fn = self.callbacks[request_id]
                                try:
                                    await callback_fn(data)
                                except Exception as e:
                                    logger.error(f"Error in callback for request {request_id}: {str(e)}")
                            
                            # Clean up
                            self.requests.pop(request_id, None)
                            self.callbacks.pop(request_id, None)
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in message processing loop: {str(e)}")
            self.running = False
    
    async def _check_timeouts(self):
        """Check for timeout requests"""
        if not self.initialized:
            return
        
        logger.info("Starting timeout checker for LLM service requests")
        
        try:
            while self.running:
                current_time = time.time()
                timed_out_requests = []
                
                # Check for timed out requests
                for request_id, request_info in self.requests.items():
                    if (current_time - request_info["timestamp"]) > request_info["timeout"]:
                        timed_out_requests.append(request_id)
                
                # Process timed out requests
                for request_id in timed_out_requests:
                    request_info = self.requests.pop(request_id, None)
                    
                    if request_id in self.callbacks:
                        callback_fn = self.callbacks.pop(request_id)
                        try:
                            await callback_fn({
                                "request_id": request_id,
                                "error": "Request timed out",
                                "status": "error"
                            })
                        except Exception as e:
                            logger.error(f"Error in timeout callback for request {request_id}: {str(e)}")
                
                # Sleep for a bit
                await asyncio.sleep(1.0)
        
        except Exception as e:
            logger.error(f"Error in timeout checker: {str(e)}")
            self.running = False
    
    async def request(self, 
                     prompt: str, 
                     provider: str = None, 
                     model: str = None, 
                     parameters: Optional[Dict[str, Any]] = None, 
                     timeout: int = None) -> Dict[str, Any]:
        """
        Send a request to an LLM service
        
        Args:
            prompt: The prompt to send
            provider: The provider to use (e.g., "openai", "anthropic", "ollama")
            model: The model to use
            parameters: Generation parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response from the LLM service
        """
        if not self.initialized:
            await self.initialize()
        
        request_id = str(uuid.uuid4())
        timeout = timeout or self.request_timeout
        
        # Create request data
        request_data = {
            "request_id": request_id,
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "parameters": parameters or {},
            "timestamp": time.time()
        }
        
        # Store request info for timeout checking
        self.requests[request_id] = {
            "timestamp": time.time(),
            "timeout": timeout
        }
        
        # Create a future for the response
        future = asyncio.Future()
        
        # Set callback
        self.callbacks[request_id] = lambda data: self._handle_response(future, data)
        
        # Send request
        channel = f"llm:requests"
        await self.redis.publish(channel, json.dumps(request_data))
        
        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Request {request_id} timed out after {timeout}s")
            
            # Clean up
            self.requests.pop(request_id, None)
            self.callbacks.pop(request_id, None)
            
            return {
                "error": f"Request timed out after {timeout}s",
                "request_id": request_id,
                "status": "error"
            }
    
    async def _handle_response(self, future: asyncio.Future, data: Dict[str, Any]):
        """Handle a response from an LLM service"""
        if not future.done():
            future.set_result(data)
    
    async def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available LLM providers
        
        Returns:
            List of available providers and their models
        """
        if not self.initialized:
            await self.initialize()
        
        # Create request data
        request_id = str(uuid.uuid4())
        request_data = {
            "request_id": request_id,
            "action": "get_providers",
            "timestamp": time.time()
        }
        
        # Store request info
        self.requests[request_id] = {
            "timestamp": time.time(),
            "timeout": 30  # Shorter timeout for service discovery
        }
        
        # Create a future for the response
        future = asyncio.Future()
        
        # Set callback
        self.callbacks[request_id] = lambda data: self._handle_response(future, data)
        
        # Send request
        channel = f"llm:control"
        await self.redis.publish(channel, json.dumps(request_data))
        
        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=30)
            return response.get("providers", [])
        except asyncio.TimeoutError:
            logger.warning(f"Provider discovery request {request_id} timed out")
            
            # Clean up
            self.requests.pop(request_id, None)
            self.callbacks.pop(request_id, None)
            
            return []
    
    async def classify_task(self, instruction: str, provider: str = None, model: str = None) -> Dict[str, Any]:
        """
        Classify a user instruction into a structured task
        
        Args:
            instruction: User instruction text
            provider: Optional provider to use
            model: Optional model to use
            
        Returns:
            Structured task information
        """
        # Create prompt for task classification
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
        
        # Send request
        response = await self.request(
            prompt=prompt, 
            provider=provider, 
            model=model, 
            parameters={"temperature": 0.2}
        )
        
        if "error" in response:
            logger.warning(f"Error during task classification: {response['error']}")
            return {
                "task_type": "scene_generation",
                "description": instruction,
                "parameters": {}
            }
        
        # Parse the response
        text = response.get("text", "")
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from text
            import re
            json_match = re.search(r'({[\s\S]*})', text)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    return result
                except json.JSONDecodeError:
                    pass
            
            # Return fallback
            logger.warning(f"Failed to parse response as JSON: {text}")
            return {
                "task_type": "scene_generation",
                "description": instruction,
                "parameters": {}
            }
    
    async def close(self):
        """Close the service manager"""
        logger.info("Shutting down LLM Service Manager")
        
        self.running = False
        
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis:
            await self.redis.close()
        
        self.initialized = False
        logger.info("LLM Service Manager shut down")
