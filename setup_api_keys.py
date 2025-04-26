#!/usr/bin/env python3
"""
Setup API Keys for GenAI Agent 3D

This script helps users set up API keys for various AI providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Stability AI
- Replicate

Usage:
    python setup_api_keys.py
"""

import os
import sys
import re
import logging
from pathlib import Path
from getpass import getpass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define API key providers
PROVIDERS = {
    'openai': {
        'name': 'OpenAI',
        'env_var': 'OPENAI_API_KEY',
        'info': 'Used for GPT-4, GPT-3.5 Turbo, and DALL-E services',
        'format': r'^sk-[A-Za-z0-9]{32,}$',
        'format_help': 'Should start with "sk-" followed by a long string of characters'
    },
    'anthropic': {
        'name': 'Anthropic',
        'env_var': 'ANTHROPIC_API_KEY',
        'info': 'Used for Claude models',
        'format': r'^sk-ant-[A-Za-z0-9]{32,}$',
        'format_help': 'Should start with "sk-ant-" followed by a long string of characters'
    },
    'stability': {
        'name': 'Stability AI',
        'env_var': 'STABILITY_API_KEY',
        'info': 'Used for image generation services',
        'format': r'^sk-[A-Za-z0-9]{32,}$',
        'format_help': 'Should start with "sk-" followed by a long string of characters'
    },
    'replicate': {
        'name': 'Replicate',
        'env_var': 'REPLICATE_API_KEY',
        'info': 'Used for various AI models on Replicate platform',
        'format': r'^r8_[A-Za-z0-9]{32,}$',
        'format_help': 'Should start with "r8_" followed by a long string of characters'
    }
}

def update_env_file(env_path, key, value):
    """Update a key in the .env file"""
    # Create the file if it doesn't exist
    if not os.path.exists(env_path):
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"# GenAI Agent 3D Environment Variables\n")
    
    # Read the current content
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check if the key already exists
    key_exists = False
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            if line.split('=')[0].strip() == key:
                lines[i] = f"{key}={value}\n"
                key_exists = True
                break
    
    # If the key doesn't exist, add it
    if not key_exists:
        lines.append(f"{key}={value}\n")
    
    # Write the updated content
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def check_key_format(provider_id, key):
    """Check if the key matches the expected format"""
    provider = PROVIDERS.get(provider_id)
    if not provider or not provider.get('format'):
        return True
    
    return bool(re.match(provider['format'], key))

def setup_provider_key(provider_id, env_path):
    """Set up the API key for a specific provider"""
    provider = PROVIDERS.get(provider_id)
    if not provider:
        logger.error(f"Unknown provider: {provider_id}")
        return False
    
    print(f"\n=== {provider['name']} API Key ===")
    print(f"Info: {provider['info']}")
    
    # Check if key already exists
    env_var = provider['env_var']
    current_key = os.environ.get(env_var)
    
    if current_key:
        print(f"Current key: {'*' * (len(current_key) - 8)}{current_key[-8:]}")
        update = input("Do you want to update this key? (y/n): ").lower()
        if update != 'y':
            print(f"Keeping existing {provider['name']} API key")
            return True
    
    # Get the new key
    print(f"Enter your {provider['name']} API key:")
    if provider.get('format_help'):
        print(f"Format: {provider['format_help']}")
    
    key = getpass("API Key (input is hidden): ")
    
    if not key:
        print("No key entered. Skipping.")
        return True
    
    # Validate key format
    if not check_key_format(provider_id, key):
        print(f"Warning: The key doesn't match the expected format for {provider['name']}.")
        confirm = input("Use this key anyway? (y/n): ").lower()
        if confirm != 'y':
            print(f"Skipping {provider['name']} API key setup")
            return False
    
    # Update the .env file
    if update_env_file(env_path, env_var, key):
        print(f"{provider['name']} API key saved successfully")
        # Update environment variable for the current process
        os.environ[env_var] = key
        return True
    else:
        print(f"Failed to save {provider['name']} API key")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("           GenAI Agent 3D - API Key Setup")
    print("=" * 80)
    print("\nThis script will help you set up API keys for various AI providers.")
    print("API keys are stored in the .env file in your project directory.")
    print("Note: Your API keys are valuable secrets - never share them publicly!")
    
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Identify the .env file location
    env_path = project_root / "genai_agent_project" / ".env"
    
    # Make sure the directory exists
    env_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Show setup options
    print("\nAvailable providers:")
    for i, (provider_id, provider) in enumerate(PROVIDERS.items(), 1):
        print(f"{i}. {provider['name']} - {provider['info']}")
    print(f"{len(PROVIDERS) + 1}. All providers")
    print(f"{len(PROVIDERS) + 2}. Exit")
    
    # Get user selection
    try:
        selection = int(input("\nEnter your choice (1-6): "))
        
        if selection == len(PROVIDERS) + 2:
            print("Exiting without changes")
            return 0
        
        if selection == len(PROVIDERS) + 1:
            # Set up all providers
            for provider_id in PROVIDERS.keys():
                setup_provider_key(provider_id, env_path)
        elif 1 <= selection <= len(PROVIDERS):
            # Set up specific provider
            provider_id = list(PROVIDERS.keys())[selection - 1]
            setup_provider_key(provider_id, env_path)
        else:
            print("Invalid selection")
            return 1
        
        print("\nAPI key setup completed")
        print(f"Keys are stored in: {env_path}")
        print("\nRestart the GenAI Agent 3D application to apply changes.")
        
        return 0
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Error during API key setup: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
