#!/usr/bin/env python
"""
Update Config Script for GenAI Agent 3D

This script updates the config.yaml file to:
1. Use llama3 instead of deepseek-coder
2. Add JSON formatting instructions
3. Update integration paths to the correct locations
"""

import yaml
import os
import sys
from env_loader import get_env, get_config


# Define paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.dirname(PROJECT_ROOT)
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.yaml")
INTEGRATIONS_DIR = os.path.join(PARENT_DIR, "integrations")

print(f"Project root: {PROJECT_ROOT}")
print(f"Parent directory: {PARENT_DIR}")
print(f"Config file: {CONFIG_FILE}")
print(f"Integrations directory: {INTEGRATIONS_DIR}")

# Check if config file exists
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

# Create backup of original config
backup_file = f"{CONFIG_FILE}.bak"
try:
    with open(backup_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Created backup at {backup_file}")
except Exception as e:
    print(f"Warning: Could not create backup: {e}")

# 1. Update LLM configuration to use llama3
if 'llm' not in config:
    config['llm'] = {}

config['llm']['provider'] = 'ollama'
config['llm']['model'] = 'llama3'  # Change from deepseek-coder to llama3
config['llm']['type'] = 'local'

print("Updated LLM configuration to use llama3")

# 2. Add JSON formatting instructions
if 'prompt_templates' not in config['llm']:
    config['llm']['prompt_templates'] = {}

config['llm']['prompt_templates']['json_generation'] = '''
You are a JSON generation assistant. Generate only valid, well-formed JSON with no explanations.
The JSON should be properly formatted and include closing brackets.
Do not include markdown code blocks or any text outside the JSON.
'''

print("Added JSON formatting instructions")

# 3. Update integration paths
if 'integrations' not in config:
    config['integrations'] = {}

config['integrations']['blendergpt'] = {
    'path': os.path.join(INTEGRATIONS_DIR, 'blendergpt')
}
config['integrations']['hunyuan3d'] = {
    'path': os.path.join(INTEGRATIONS_DIR, 'hunyuan3d')
}
config['integrations']['trellis'] = {
    'path': os.path.join(INTEGRATIONS_DIR, 'trellis')
}

print("Updated integration paths:")
print(f"BlenderGPT: {config['integrations']['blendergpt']['path']}")
print(f"Hunyuan-3D: {config['integrations']['hunyuan3d']['path']}")
print(f"TRELLIS: {config['integrations']['trellis']['path']}")

# Save the updated config
try:
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print("Successfully saved updated config.yaml!")
except Exception as e:
    print(f"Error saving config file: {e}")
    sys.exit(1)

print("\nConfiguration update complete. You can now run tests with the updated settings.")
