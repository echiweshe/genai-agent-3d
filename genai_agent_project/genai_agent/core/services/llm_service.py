"""
LLM Service Module
----------------
Provides robust access to LLM providers (Ollama, OpenAI, Anthropic)
with error handling, retries, and streaming capabilities.
"""

import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List, Generator, Union, Callable
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("LLMService")

class LLMService:
    """Service for interacting with LLM providers with robust error handling."""
    
    def __init__(self):
        """Initialize the LLM service with configuration from the service registry."""
        from genai_agent.core.services.service_initialization import get_registry
        
        self.registry = get_registry()
        self.config = self.registry.config
        
        # Default configuration
        self.default_provider = self.config.get("LLM_PROVIDER", "ollama").lower()
        self.default_model = self.config.get("LLM_MODEL", "llama3")
        self.max_retries = int(self.config.get("LLM_MAX_RETRIES", 3))
        self.retry_delay = float(self.config.get("LLM_RETRY_DELAY", 1.0))
        self.timeout = float(self.config.get("LLM_TIMEOUT", 60.0))
        
        # Provider-specific configuration
        self.api_keys = {
            "openai": self.config.get("OPENAI_API_KEY", ""),
            "anthropic": self.config.get("ANTHROPIC_API_KEY", ""),
        }
        
        # Provider endpoints
        self.endpoints = {
            "ollama": self.config.get("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate"),
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
        }
        
        logger.info(f"LLM Service initialized with provider: {self.default_provider}, model: {self.default_model}")
    
    def generate(self, 
                 prompt: str, 
                 provider: Optional[str] = None, 
                 model: Optional[str] = None,
                 max_tokens: int = 2048, 
                 temperature: float = 0.7,
                 output_file: Optional[str] = None,
                 **kwargs) -> str:
        """
        Generate text from an LLM using the specified provider.
        
        Args:
            prompt: The text prompt to send to the LLM
            provider: The LLM provider (ollama, openai, anthropic)
            model: The specific model to use
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (higher = more creative)
            output_file: If specified, save output to this file
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        provider = (provider or self.default_provider).lower()
        model = model or self.default_model
        
        # Select the appropriate method based on provider
        if provider == "ollama":
            response = self._generate_ollama(prompt, model, max_tokens, temperature, **kwargs)
        elif provider == "openai":
            response = self._generate_openai(prompt, model, max_tokens, temperature, **kwargs)
        elif provider == "anthropic":
            response = self._generate_anthropic(prompt, model, max_tokens, temperature, **kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        # Save to file if specified
        if output_file:
            self._save_to_file(response, output_file)
        
        return response
    
    def generate_stream(self, 
                       prompt: str, 
                       provider: Optional[str] = None, 
                       model: Optional[str] = None,
                       max_tokens: int = 2048, 
                       temperature: float = 0.7,
                       output_file: Optional[str] = None,
                       callback: Optional[Callable[[str], None]] = None,
                       **kwargs) -> Generator[str, None, str]:
        """
        Generate text from an LLM with streaming responses.
        
        Args:
            prompt: The text prompt to send to the LLM
            provider: The LLM provider (ollama, openai, anthropic)
            model: The specific model to use
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            output_file: If specified, save complete output to this file
            callback: Optional function to call with each chunk of text
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generator yielding chunks of text as they are generated
        """
        provider = (provider or self.default_provider).lower()
        model = model or self.default_model
        
        # Select the appropriate streaming method based on provider
        if provider == "ollama":
            stream_gen = self._stream_ollama(prompt, model, max_tokens, temperature, **kwargs)
        elif provider == "openai":
            stream_gen = self._stream_openai(prompt, model, max_tokens, temperature, **kwargs)
        elif provider == "anthropic":
            stream_gen = self._stream_anthropic(prompt, model, max_tokens, temperature, **kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        # Initialize complete text for file output
        complete_text = ""
        
        # Process stream chunks
        for chunk in stream_gen:
            complete_text += chunk
            if callback:
                callback(chunk)
            yield chunk
        
        # Save complete text to file if specified
        if output_file:
            self._save_to_file(complete_text, output_file)
        
        return complete_text
    
    def _generate_ollama(self, 
                        prompt: str, 
                        model: str, 
                        max_tokens: int, 
                        temperature: float,
                        **kwargs) -> str:
        """Generate text using Ollama."""
        endpoint = self.endpoints["ollama"]
        
        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        # Add any additional options from kwargs
        for key, value in kwargs.items():
            if key not in payload and key not in payload["options"]:
                if key.startswith("option_"):
                    # Add to options with prefix removed
                    option_key = key[7:]  # Remove "option_" prefix
                    payload["options"][option_key] = value
                else:
                    # Add to main payload
                    payload[key] = value
        
        # Send request with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json().get("response", "")
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Ollama request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Ollama request failed after {self.max_retries} attempts")
                    raise RuntimeError(f"Failed to generate text using Ollama: {str(e)}")
    
    def _stream_ollama(self, 
                      prompt: str, 
                      model: str, 
                      max_tokens: int, 
                      temperature: float,
                      **kwargs) -> Generator[str, None, None]:
        """Stream text generation using Ollama."""
        endpoint = self.endpoints["ollama"]
        
        # Prepare the request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        # Add any additional options from kwargs
        for key, value in kwargs.items():
            if key not in payload and key not in payload["options"]:
                if key.startswith("option_"):
                    # Add to options with prefix removed
                    option_key = key[7:]  # Remove "option_" prefix
                    payload["options"][option_key] = value
                else:
                    # Add to main payload
                    payload[key] = value
        
        # Send streaming request with retries
        for attempt in range(self.max_retries):
            try:
                with requests.post(
                    endpoint,
                    json=payload,
                    stream=True,
                    timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line:
                            try:
                                chunk_data = json.loads(line)
                                if "response" in chunk_data:
                                    yield chunk_data["response"]
                                
                                # Check for completion
                                if chunk_data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse Ollama streaming response: {line}")
                
                # Successfully processed the stream
                return
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Ollama streaming request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Ollama streaming request failed after {self.max_retries} attempts")
                    raise RuntimeError(f"Failed to stream text from Ollama: {str(e)}")
    
    def _generate_openai(self, 
                        prompt: str, 
                        model: str, 
                        max_tokens: int, 
                        temperature: float,
                        **kwargs) -> str:
        """Generate text using OpenAI API."""
        endpoint = self.endpoints["openai"]
        api_key = self.api_keys["openai"]
        
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Format messages
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            messages = prompt  # Assume properly formatted message list
        else:
            raise ValueError("Prompt must be a string or a list of message objects")
        
        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Send request with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                response_data = response.json()
                
                # Extract the generated text
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    return response_data["choices"][0]["message"]["content"]
                else:
                    return ""
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"OpenAI request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"OpenAI request failed after {self.max_retries} attempts")
                    raise RuntimeError(f"Failed to generate text using OpenAI: {str(e)}")
    
    def _stream_openai(self, 
                      prompt: str, 
                      model: str, 
                      max_tokens: int, 
                      temperature: float,
                      **kwargs) -> Generator[str, None, None]:
        """Stream text generation using OpenAI API."""
        endpoint = self.endpoints["openai"]
        api_key = self.api_keys["openai"]
        
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Format messages
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            messages = prompt  # Assume properly formatted message list
        else:
            raise ValueError("Prompt must be a string or a list of message objects")
        
        # Prepare the request payload
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Send streaming request with retries
        for attempt in range(self.max_retries):
            try:
                with requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line:
                            line_text = line.decode('utf-8')
                            
                            # Skip empty or initialization lines
                            if not line_text.strip() or line_text.strip() == "data: [DONE]":
                                continue
                            
                            # Parse the SSE data
                            if line_text.startswith('data: '):
                                try:
                                    json_str = line_text[6:]  # Remove "data: " prefix
                                    data = json.loads(json_str)
                                    
                                    # Extract and yield content delta
                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0]["delta"]
                                        if "content" in delta:
                                            yield delta["content"]
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse OpenAI streaming response: {line_text}")
                
                # Successfully processed the stream
                return
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"OpenAI streaming request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"OpenAI streaming request failed after {self.max_retries} attempts")
                    raise RuntimeError(f"Failed to stream text from OpenAI: {str(e)}")
    
    def _generate_anthropic(self, 
                           prompt: str, 
                           model: str, 
                           max_tokens: int, 
                           temperature: float,
                           **kwargs) -> str:
        """Generate text using Anthropic API."""
        endpoint = self.endpoints["anthropic"]
        api_key = self.api_keys["anthropic"]
        
        if not api_key:
            raise ValueError("Anthropic API key not configured")
        
        # Prepare the request payload
        if isinstance(prompt, str):
            # Simple string prompt
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        elif isinstance(prompt, list):
            # Message list format
            payload = {
                "model": model,
                "messages": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        else:
            raise ValueError("Prompt must be a string or a list of message objects")
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Send request with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                response_data = response.json()
                
                # Extract the generated text
                if "content" in response_data and len(response_data["content"]) > 0:
                    # Get text from the first content block
                    for content_block in response_data["content"]:
                        if content_block["type"] == "text":
                            return content_block["text"]
                
                return ""  # Return empty string if no text content found
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Anthropic request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Anthropic request failed after {self.max_retries} attempts")
                    raise RuntimeError(f"Failed to generate text using Anthropic: {str(e)}")
    
    def _stream_anthropic(self, 
                         prompt: str, 
                         model: str, 
                         max_tokens: int, 
                         temperature: float,
                         **kwargs) -> Generator[str, None, None]:
        """Stream text generation using Anthropic API."""
        endpoint = self.endpoints["anthropic"]
        api_key = self.api_keys["anthropic"]
        
        if not api_key:
            raise ValueError("Anthropic API key not configured")
        
        # Prepare the request payload
        if isinstance(prompt, str):
            # Simple string prompt
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }
        elif isinstance(prompt, list):
            # Message list format
            payload = {
                "model": model,
                "messages": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }
        else:
            raise ValueError("Prompt must be a string or a list of message objects")
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Send streaming request with retries
        for attempt in range(self.max_retries):
            try:
                with requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line:
                            line_text = line.decode('utf-8')
                            
                            # Skip empty lines
                            if not line_text.strip():
                                continue
                            
                            # Parse the SSE data
                            if line_text.startswith('data: '):
                                try:
                                    json_str = line_text[6:]  # Remove "data: " prefix
                                    if json_str.strip() == "[DONE]":
                                        break
                                    
                                    data = json.loads(json_str)
                                    
                                    # Extract and yield content delta
                                    if "delta" in data and "text" in data["delta"]:
                                        yield data["delta"]["text"]
                                except json.JSONDecodeError:
                                    logger.warning(f"Failed to parse Anthropic streaming response: {line_text}")
                
                # Successfully processed the stream
                return
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Anthropic streaming request failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Anthropic streaming request failed after {self.max_retries} attempts")
                    raise RuntimeError(f"Failed to stream text from Anthropic: {str(e)}")
    
    def _save_to_file(self, content: str, file_path: str) -> None:
        """Save content to a file."""
        try:
            # Resolve file path
            if not os.path.isabs(file_path):
                # Use registry's output directory if available
                output_dir = self.registry.get_output_directory()
                file_path = os.path.join(output_dir, file_path)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            logger.info(f"Saved LLM output to {file_path}")
        except Exception as e:
            logger.error(f"Error saving to file {file_path}: {str(e)}")
            raise
