"""
Configuration utilities
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

class Settings(BaseModel):
    """Settings model that holds all configuration data"""
    # General settings
    debug: bool = False
    
    # LLM settings
    llm: Dict[str, Any] = {}
    
    # Blender settings
    blender: Dict[str, Any] = {}
    
    # Tool settings
    tools: Dict[str, Any] = {}

# Global settings instance
_settings = None

def find_config_file(name, search_paths=None):
    """
    Find configuration file, searching in multiple locations if needed
    
    Args:
        name: Name of the configuration file (e.g., "config.yaml", "llm.yaml")
        search_paths: Optional list of paths to search
        
    Returns:
        Path to configuration file
        
    Raises:
        FileNotFoundError: If config file not found in any location
    """
    # Default search paths
    if search_paths is None:
        search_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'config'),  # Project config dir
            os.path.dirname(__file__),  # Current directory
            os.path.join(os.path.dirname(__file__), '..'),  # Parent directory
            os.path.dirname(os.path.dirname(__file__)),  # Project root
        ]
    
    # Try all locations
    for base_path in search_paths:
        path = os.path.join(base_path, name)
        if os.path.exists(path):
            return path
    
    # If not found, raise error
    raise FileNotFoundError(f"Config file '{name}' not found in any of the expected locations")

def load_config(name):
    """
    Load configuration from file
    
    Args:
        name: Name of the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file not found
    """
    try:
        path = find_config_file(name)
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Return empty dict if file not found
        return {}

def get_settings() -> Settings:
    """
    Get application settings, initializing if needed
    
    Returns:
        Settings instance with all configuration data
    """
    global _settings
    
    if _settings is None:
        # Load main config
        main_config = load_config("config.yaml")
        
        # Load LLM config
        llm_config = load_config("llm.yaml")
        
        # Merge configurations
        all_config = {
            **main_config,
            "llm": llm_config
        }
        
        # Create settings instance
        _settings = Settings(**all_config)
    
    return _settings

def update_config(section, key, value):
    """
    Update a configuration value
    
    Args:
        section: Configuration section (e.g., "llm", "blender")
        key: Configuration key
        value: New value
        
    Returns:
        Updated configuration dictionary
    """
    # Get settings
    settings = get_settings()
    
    # Get section dict
    section_dict = getattr(settings, section, {})
    if not section_dict:
        section_dict = {}
        setattr(settings, section, section_dict)
    
    # Update value
    section_dict[key] = value
    
    # Save to file if possible
    try:
        # Find appropriate config file
        config_path = find_config_file(f"{section}.yaml", None)
        
        # Load existing config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Update config
        config[key] = value
        
        # Write back to file
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    except FileNotFoundError:
        # Create new config file in default location
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, f"{section}.yaml")
        
        # Write config to file
        with open(config_path, 'w') as f:
            yaml.dump({key: value}, f, default_flow_style=False)
    
    # Invalidate cached settings
    global _settings
    _settings = None
    
    # Return updated section
    return section_dict
