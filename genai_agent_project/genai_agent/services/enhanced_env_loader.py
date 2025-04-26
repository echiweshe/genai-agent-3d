"""
Enhanced Environment Loader for GenAI Agent 3D

This module provides enhanced capabilities for loading environment variables
and configuration values, particularly for API keys and LLM settings.
"""

import os
import logging
import yaml
import dotenv
from typing import Any, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv.load_dotenv()

def get_api_key_for_provider(provider: str) -> Optional[str]:
    """
    Get the appropriate API key for the specified provider.
    
    Args:
        provider: The LLM provider (e.g., 'anthropic', 'openai', 'ollama')
        
    Returns:
        str: The API key if found, None otherwise
    """
    # Map providers to environment variable names
    provider_env_map = {
        'anthropic': 'ANTHROPIC_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'stability': 'STABILITY_API_KEY',
        'huggingface': 'HUGGINGFACE_API_KEY',
        'google': 'GOOGLE_API_KEY',
    }
    
    # Local providers don't need API keys
    if provider.lower() in ['ollama', 'local']:
        return None
    
    # Get the appropriate environment variable name
    env_var = provider_env_map.get(provider.lower())
    if not env_var:
        logger.warning(f"Unknown provider: {provider}. No API key mapping available.")
        return None
    
    # Get the API key from environment
    api_key = os.environ.get(env_var)
    if not api_key:
        logger.warning(f"API key for {provider} not found in environment variable {env_var}")
    
    return api_key

def get_llm_config_from_env() -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    This is used as a fallback if config.yaml doesn't have values.
    
    Returns:
        Dict[str, Any]: LLM configuration dictionary
    """
    return {
        'provider': os.environ.get('LLM_PROVIDER', 'ollama'),
        'model': os.environ.get('LLM_MODEL', 'llama3'),
        'type': os.environ.get('LLM_TYPE', 'local'),
        'timeout': int(os.environ.get('LLM_TIMEOUT', 300)),
        'generation_timeout': int(os.environ.get('LLM_GENERATION_TIMEOUT', 900)),
    }

def update_config_with_env_keys(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the configuration dictionary with API keys from environment variables.
    
    Args:
        config: The configuration dictionary loaded from config.yaml
        
    Returns:
        Dict[str, Any]: Updated configuration dictionary
    """
    # Make a copy to avoid modifying the original
    updated_config = config.copy()
    
    # Update LLM API key based on the provider
    if 'llm' in updated_config:
        provider = updated_config['llm'].get('provider', 'ollama')
        api_key = get_api_key_for_provider(provider)
        
        if api_key:
            updated_config['llm']['api_key'] = api_key
        
        # Also update other provider-specific settings if needed
        if provider.lower() == 'ollama':
            updated_config['llm']['type'] = 'local'
        elif provider.lower() in ['anthropic', 'openai']:
            updated_config['llm']['type'] = 'cloud'
    
    # Update tool API keys if needed
    if 'tools' in updated_config:
        for tool_name, tool_config in updated_config['tools'].items():
            if 'config' in tool_config and 'api_key' in tool_config['config']:
                # Determine which API key to use based on the tool
                if 'model' in tool_config['config']:
                    model = tool_config['config']['model']
                    
                    if model.startswith('gpt-'):
                        # OpenAI tool
                        tool_config['config']['api_key'] = os.environ.get('OPENAI_API_KEY')
    
    return updated_config

def load_config_with_env() -> Dict[str, Any]:
    """
    Load configuration from config.yaml and update with environment variables.
    
    Returns:
        Dict[str, Any]: The full configuration dictionary
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
    
    try:
        # Load config.yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update with API keys from environment
        config = update_config_with_env_keys(config)
        
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        # Return basic configuration from environment
        return {'llm': get_llm_config_from_env()}
