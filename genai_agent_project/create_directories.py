#!/usr/bin/env python
"""
Create Output Directories for GenAI Agent 3D

This script creates the necessary output directories based on
environment variables defined in .env
"""

import os
import sys
from pathlib import Path

# Import our environment variable loader
try:
    from env_loader import get_env, get_config
except ImportError:
    print("Error: env_loader.py not found. Please create this file first.")
    sys.exit(1)

def create_directories():
    """Create all required output directories"""
    # Get configuration
    config = get_config()
    
    # Get the base output directory
    output_dir = config['paths']['output_dir']
    
    # List of output directories to create
    directories = [
        output_dir,
        config['paths']['blendergpt_output_dir'],
        config['paths']['diagrams_output_dir'],
        config['paths']['hunyuan_output_dir'],
        config['paths']['models_output_dir'],
        config['paths']['scenes_output_dir'],
        config['paths']['svg_output_dir'],
        config['paths']['trellis_output_dir']
    ]
    
    # Create each directory
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    return directories

def main():
    """Main function"""
    print("Creating output directories for GenAI Agent 3D...")
    
    # Create the directories
    directories = create_directories()
    
    print(f"\nSuccessfully created {len(directories)} directories.")
    print("Now scenes will be properly saved in output/scenes directory.")

if __name__ == "__main__":
    main()
