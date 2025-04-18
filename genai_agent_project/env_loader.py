#!/usr/bin/env python
"""
Environment Variable Loader for GenAI Agent 3D

This module loads environment variables from a .env file and makes them 
available through get_env() and get_config() functions.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Store loaded config
_ENV_CONFIG = {}
_ENV_LOADED = False

def _parse_bool(value: str) -> bool:
    """Parse a string into a boolean value."""
    return value.lower() in ('true', 'yes', '1', 'y', 't')

def _parse_int(value: str) -> int:
    """Parse a string into an integer value."""
    try:
        return int(value)
    except ValueError:
        return 0

def load_env(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load environment variables from .env file
    
    Args:
        env_file: Path to .env file. If None, looks in the current directory
                 and parent directories up to the project root.
    
    Returns:
        Dictionary of environment variables
    """
    global _ENV_CONFIG, _ENV_LOADED
    
    if _ENV_LOADED:
        return _ENV_CONFIG
    
    # If env_file is not specified, search for it
    if env_file is None:
        current_dir = Path(os.path.abspath(os.path.dirname(__file__)))
        
        # Try current directory first
        env_path = current_dir / '.env'
        if os.path.exists(env_path):
            env_file = str(env_path)
        else:
            # Try parent directories
            for parent in current_dir.parents:
                env_path = parent / '.env'
                if os.path.exists(env_path):
                    env_file = str(env_path)
                    break
    
    if env_file is None or not os.path.exists(env_file):
        print(f"Warning: .env file not found")
        _ENV_LOADED = True
        return _ENV_CONFIG
    
    # Parse the .env file
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Remove quotes if present
            if value and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            
            # Store in our config dictionary
            _ENV_CONFIG[key] = value
            
            # Also set as environment variable
            os.environ[key] = value
    
    _ENV_LOADED = True
    return _ENV_CONFIG

def get_env(key: str, default: Any = None) -> Any:
    """
    Get an environment variable, with appropriate type conversion
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Value of the environment variable, or default if not found
    """
    if not _ENV_LOADED:
        load_env()
    
    # Try from our loaded config first
    value = _ENV_CONFIG.get(key)
    
    # Fall back to environment variable if not found
    if value is None:
        value = os.environ.get(key)
    
    # Return default if still not found
    if value is None:
        return default
    
    # Convert based on default type
    if default is not None:
        if isinstance(default, bool):
            return _parse_bool(value)
        elif isinstance(default, int):
            return _parse_int(value)
    
    return value

def get_config() -> Dict[str, Any]:
    """
    Get the full configuration as a structured dictionary
    
    Returns:
        Dictionary with configuration sections
    """
    if not _ENV_LOADED:
        load_env()
    
    # Structure the flat environment variables into a nested config
    config = {
        'llm': {
            'provider': get_env('LLM_PROVIDER', 'ollama'),
            'model': get_env('LLM_MODEL', 'llama3'),
            'type': get_env('LLM_TYPE', 'local'),
        },
        'integrations': {
            'blendergpt': {
                'path': os.path.normpath(os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    get_env('BLENDERGPT_PATH', 'integrations/blendergpt')
                ))
            },
            'hunyuan3d': {
                'path': os.path.normpath(os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    get_env('HUNYUAN3D_PATH', 'integrations/hunyuan3d')
                ))
            },
            'trellis': {
                'path': os.path.normpath(os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    get_env('TRELLIS_PATH', 'integrations/trellis')
                ))
            }
        },
        'redis': {
            'host': get_env('REDIS_HOST', 'localhost'),
            'port': int(get_env('REDIS_PORT', 6379)),
            'pool_size': int(get_env('REDIS_POOL_SIZE', 10)),
            'use_connection_pool': _parse_bool(get_env('REDIS_USE_CONNECTION_POOL', 'true')),
            'separate_connections': _parse_bool(get_env('REDIS_SEPARATE_CONNECTIONS', 'true')),
            'timeout': int(get_env('REDIS_TIMEOUT', 30)),
        },
        'paths': {
            'output_dir': get_env('OUTPUT_DIR', 'output'),
            'blendergpt_output_dir': get_env('BLENDERGPT_OUTPUT_DIR', 'output/blendergpt'),
            'diagrams_output_dir': get_env('DIAGRAMS_OUTPUT_DIR', 'output/diagrams'),
            'hunyuan_output_dir': get_env('HUNYUAN_OUTPUT_DIR', 'output/hunyuan'),
            'models_output_dir': get_env('MODELS_OUTPUT_DIR', 'output/models'),
            'scenes_output_dir': get_env('SCENES_OUTPUT_DIR', 'output/scenes'),
            'svg_output_dir': get_env('SVG_OUTPUT_DIR', 'output/svg'),
            'trellis_output_dir': get_env('TRELLIS_OUTPUT_DIR', 'output/trellis'),
        },
        'blender': {
            'path': get_env('BLENDER_PATH', r'C:/Program Files/Blender Foundation/Blender 4.2/blender.exe'),
        },
        'api_keys': {
            'openai': get_env('OPENAI_API_KEY', ''),
            'huggingface': get_env('HUGGINGFACE_API_KEY', ''),
        }
    }
    
    return config

# Auto-load environment variables when the module is imported
load_env()

if __name__ == "__main__":
    # Print the loaded environment variables if run directly
    config = get_config()
    import json
    print(json.dumps(config, indent=2))
