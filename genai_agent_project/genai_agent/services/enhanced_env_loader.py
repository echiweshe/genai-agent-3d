"""
Enhanced Environment Variable Loader for GenAI Agent 3D

Handles loading API keys and configuration from environment variables.
"""

import os
import logging
from typing import Dict, Any, Optional
import dotenv
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv.load_dotenv(Path(__file__).parent.parent.parent / ".env")

def get_api_key_for_provider(provider: str) -> Optional[str]:
    """
    Get API key for the specified provider from environment variables
    
    Args:
        provider: Provider name (e.g., 'openai', 'anthropic')
    
    Returns:
        API key from environment variables or None if not found
    """
    provider = provider.lower()
    
    # Map providers to environment variable names
    provider_env_map = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'stability': 'STABILITY_API_KEY',
        'replicate': 'REPLICATE_API_KEY'
    ,
        'hunyuan3d': 'HUNYUAN3D_API_KEY'
    }
    
    # Get the appropriate environment variable name
    env_var_name = provider_env_map.get(provider)
    
    # Return the API key if the environment variable exists
    if env_var_name:
        api_key = os.environ.get(env_var_name)
        if api_key:
            logger.debug(f"Found API key for {provider} in environment variables")
            return api_key
        else:
            logger.debug(f"API key for {provider} not found in environment variables")
            return None
    else:
        logger.debug(f"Unknown provider: {provider}")
        return None

def get_llm_config_from_env() -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables
    
    Returns:
        Dictionary with LLM configuration from environment variables
    """
    # Get LLM configuration from environment variables
    llm_config = {
        'provider': os.environ.get('LLM_PROVIDER'),
        'model': os.environ.get('LLM_MODEL'),
        'type': os.environ.get('LLM_TYPE')
    }
    
    # Filter out None values
    return {k: v for k, v in llm_config.items() if v is not None}
