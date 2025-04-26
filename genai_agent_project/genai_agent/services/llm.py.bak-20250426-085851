"""
LLM Service - Handles integration with various Language Models
"""

import os
import json
import logging
import httpx
import asyncio
from typing import Dict, Any, List, Optional
from ..config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with language models"""
    
    def __init__(self):
        """Initialize LLM service"""
        self.settings = get_settings()
        self.config = self.settings.llm
        self.initialized = False
        self.providers = {}
        
        logger.info(f"🔍 LLM config: type={self.config.get('type', 'local')}, provider={self.config.get('provider', 'ollama')}, model={self.config.get('model', 'llama3.2:latest')}")
        logger.info(f"LLM Service initialized with {self.config.get('provider', 'ollama')} ({self.config.get('type', 'local')})")
        
    async def initialize(self):
        """Initialize connections to LLM providers"""
        if self.initialized:
            return
        
        try:
            # Get available providers
            await self._discover_providers()
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            raise
    
    async def _discover_providers(self):
        """Discover available LLM providers"""
        # Initialize basic provider info
        self.providers = {
            "ollama": {
                "name": "Ollama",
                "is_local": True,
                "base_url": "http://127.0.0.1:11434",
                "models": []
            }
        }
        
        # Get available Ollama models
        try:
            if "ollama" in self.providers:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.providers['ollama']['base_url']}/api/tags")
                    if response.status_code == 200:
                        data = response.json()
                        if "models" in data:
                            self.providers["ollama"]["models"] = [
                                {"id": model["name"], "name": model["name"]}
                                for model in data["models"]
                            ]
                        else:
                            # Handle 0.5.0+ Ollama API response
                            self.providers["ollama"]["models"] = [
                                {"id": model["name"], "name": model["name"]}
                                for model in data.get("models", [])
                            ]
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {str(e)}")
            # Add default models as fallback
            self.providers["ollama"]["models"] = [
                {"id": "llama3.2:latest", "name": "Llama 3.2"},
                {"id": "llama3:latest", "name": "Llama 3"},
                {"id": "llama2:latest", "name": "Llama 2"}
            ]
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """Get list of available LLM providers and models"""
        providers_list = []
        
        for provider_id, provider_info in self.providers.items():
            providers_list.append({
                "name": provider_info["name"],
                "is_local": provider_info["is_local"],
                "models": provider_info["models"]
            })
        
        return providers_list
    
    async def generate(
        self, 
        prompt: str, 
        provider: Optional[str] = None,
        model: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate text from a prompt using the specified LLM"""
        if not self.initialized:
            await self.initialize()
        
        # Use parameters from request or fallback to defaults
        provider = provider or self.config.get("provider", "ollama")
        model = model or self.config.get("model", "llama3.2:latest")
        parameters = parameters or {}
        
        # Set default parameters if not provided
        if "temperature" not in parameters:
            parameters["temperature"] = 0.7
        if "max_tokens" not in parameters:
            parameters["max_tokens"] = 2048
        
        # Generate based on provider
        if provider.lower() == "ollama":
            return await self._generate_ollama(prompt, model, parameters)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _generate_ollama(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Generate text using Ollama API"""
        base_url = self.providers["ollama"]["base_url"]
        
        # Map our generic parameters to Ollama specific ones
        ollama_params = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": parameters.get("temperature", 0.7),
                "num_predict": parameters.get("max_tokens", 2048)
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/api/generate",
                    json=ollama_params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            raise
