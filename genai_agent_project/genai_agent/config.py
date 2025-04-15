"""
Configuration utilities
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

def find_config_file(config_path=None):
    """
    Find configuration file, searching in multiple locations if needed
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Path to configuration file
        
    Raises:
        FileNotFoundError: If config file not found in any location
    """
    # If path provided, try it first
    if config_path:
        path = Path(config_path)
        if path.exists():
            return path
    
    # Try common locations
    possible_locations = [
        'config.yaml',  # Current directory
        os.path.join(os.path.dirname(__file__), '..', 'config.yaml'),  # Parent directory
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml'),  # Project root
    ]
    
    for location in possible_locations:
        path = Path(location)
        if path.exists():
            return path
    
    # If provided path doesn't exist, raise error
    if config_path:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    else:
        raise FileNotFoundError("Config file not found in any of the expected locations")

def load_config(config_path=None):
    """
    Load configuration from file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file not found
    """
    path = find_config_file(config_path)
    
    with open(path, 'r') as f:
        return yaml.safe_load(f)
