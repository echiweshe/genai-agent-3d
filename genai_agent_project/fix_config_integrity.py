#!/usr/bin/env python
"""
Fix config.yaml integrity by ensuring all tool paths are consistent

This script updates config.yaml to fix inconsistent tool paths
and removes redundant entries.
"""

import os
import yaml
import sys
from pathlib import Path

def fix_config_integrity():
    """Fix integrity issues in config.yaml"""
    # Define paths
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    PARENT_DIR = os.path.dirname(PROJECT_ROOT)
    CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.yaml")
    INTEGRATIONS_DIR = os.path.join(PARENT_DIR, "integrations")
    
    # Actual integration paths
    BLENDERGPT_PATH = os.path.join(INTEGRATIONS_DIR, "blendergpt")
    HUNYUAN3D_PATH = os.path.join(INTEGRATIONS_DIR, "hunyuan3d")
    TRELLIS_PATH = os.path.join(INTEGRATIONS_DIR, "trellis")
    
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Config file: {CONFIG_FILE}")
    print(f"Integration paths:")
    print(f"  BlenderGPT: {BLENDERGPT_PATH}")
    print(f"  Hunyuan-3D: {HUNYUAN3D_PATH}")
    print(f"  TRELLIS: {TRELLIS_PATH}")
    
    # Check if config.yaml exists
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Config file not found at {CONFIG_FILE}")
        sys.exit(1)
    
    # Load the current config
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        print("Successfully loaded config.yaml")
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)
    
    # Create a backup of the original config
    try:
        backup_file = f"{CONFIG_FILE}.integrity.bak"
        with open(backup_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"Created backup at {backup_file}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    # Fix integration paths
    
    # 1. Fix blendergpt paths
    if 'integrations' not in config:
        config['integrations'] = {}
    
    # Set the primary paths
    config['integrations']['blendergpt'] = {
        'path': BLENDERGPT_PATH
    }
    config['integrations']['hunyuan3d'] = {
        'path': HUNYUAN3D_PATH
    }
    config['integrations']['trellis'] = {
        'path': TRELLIS_PATH
    }
    
    # Fix the legacy entries if they exist
    if 'blender_gpt' in config['integrations']:
        config['integrations']['blender_gpt']['blendergpt_path'] = BLENDERGPT_PATH
        config['integrations']['blender_gpt']['enabled'] = True
        print("Fixed blender_gpt legacy entry")
    
    if 'hunyuan_3d' in config['integrations']:
        config['integrations']['hunyuan_3d']['hunyuan_path'] = HUNYUAN3D_PATH
        config['integrations']['hunyuan_3d']['enabled'] = True
        print("Fixed hunyuan_3d legacy entry")
    
    # Add scenes directory to outputs
    if 'tools' not in config:
        config['tools'] = {}
    
    # Fix scene_generator tool config
    if 'scene_generator' in config['tools']:
        if 'parameters' not in config['tools']['scene_generator']:
            config['tools']['scene_generator']['parameters'] = {}
        config['tools']['scene_generator']['parameters']['output_dir'] = 'output/scenes'
    else:
        config['tools']['scene_generator'] = {
            'class': 'SceneGeneratorTool',
            'module': 'genai_agent.tools.scene_generator',
            'parameters': {
                'output_dir': 'output/scenes'
            }
        }
    
    # Make sure LLM is set to llama3
    if 'llm' not in config:
        config['llm'] = {}
    
    config['llm']['provider'] = 'ollama'
    config['llm']['model'] = 'llama3'
    config['llm']['type'] = 'local'
    
    # Add improved JSON formatting template
    if 'prompt_templates' not in config['llm']:
        config['llm']['prompt_templates'] = {}
    
    config['llm']['prompt_templates']['json_generation'] = '''
You are a JSON generation assistant. Generate only valid, well-formed JSON with no explanations.
The JSON should be properly formatted and include closing brackets.
Do not include markdown code blocks or any text outside the JSON.
'''
    
    # Fix Redis configuration for connection issues
    if 'redis' not in config:
        config['redis'] = {}
    
    config['redis']['host'] = 'localhost'
    config['redis']['port'] = 6379
    config['redis']['pool_size'] = 10
    config['redis']['use_connection_pool'] = True
    config['redis']['separate_connections'] = True
    config['redis']['timeout'] = 30
    
    # Save the updated config
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        print("Successfully saved updated config.yaml!")
    except Exception as e:
        print(f"Error saving config file: {e}")
        sys.exit(1)
    
    print("\nConfig integrity fix complete.")
    print("All integration paths are now consistent.")
    print("The scene generator is configured to save scenes to output/scenes directory.")

if __name__ == "__main__":
    fix_config_integrity()
