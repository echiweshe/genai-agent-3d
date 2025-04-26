#!/usr/bin/env python3
"""
Manage API Keys for GenAI Agent 3D

This script allows you to manage API keys for various services used by the GenAI Agent 3D project.
It updates both the .env files and the config.yaml file with the provided API keys.
"""

import os
import re
import yaml
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    return backup_path

def update_env_files(api_keys):
    """Update API keys in the .env files"""
    env_files = [
        ".env",
        "genai_agent_project/.env"
    ]
    
    for env_file in env_files:
        if not os.path.exists(env_file):
            print(f"⚠️ Could not find {env_file}")
            continue
        
        # Create backup
        backup_file(env_file)
        
        # Read the current content
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update each API key in the content
        for key_name, key_value in api_keys.items():
            if key_value:  # Only update if a value was provided
                env_var_name = f"{key_name}_API_KEY"
                
                # Check if the variable already exists in the file
                pattern = re.compile(f'^{env_var_name}=.*$', re.MULTILINE)
                match = pattern.search(content)
                
                if match:
                    # Update existing entry
                    content = pattern.sub(f'{env_var_name}={key_value}', content)
                else:
                    # Add new entry
                    content += f'\n{env_var_name}={key_value}\n'
        
        # Write the updated content
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated API keys in {env_file}")
    
    return True

def update_config_yaml(api_keys):
    """Update API keys in the config.yaml file"""
    config_file = "genai_agent_project/config.yaml"
    
    if not os.path.exists(config_file):
        print(f"⚠️ Could not find {config_file}")
        return False
    
    # Create backup
    backup_file(config_file)
    
    # Read the current config
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Update LLM API key
    if "ANTHROPIC" in api_keys and api_keys["ANTHROPIC"]:
        if 'llm' not in config:
            config['llm'] = {}
        config['llm']['api_key'] = api_keys["ANTHROPIC"]
    
    # Update OpenAI API key if needed
    if "OPENAI" in api_keys and api_keys["OPENAI"]:
        # Check if there are any tools that use OpenAI
        for tool_name, tool_config in config.get('tools', {}).items():
            if 'config' in tool_config and 'api_key' in tool_config['config']:
                # If this is a tool that likely uses OpenAI (like blender_gpt)
                if 'model' in tool_config['config'] and tool_config['config'].get('model', '').startswith('gpt-'):
                    tool_config['config']['api_key'] = api_keys["OPENAI"]
    
    # Update other API keys in integrations
    for integration_name, integration_config in config.get('integrations', {}).items():
        if 'api_key' in integration_config:
            # Match the integration to the appropriate API key
            if integration_name.lower() == "blender_gpt" and "OPENAI" in api_keys and api_keys["OPENAI"]:
                integration_config['api_key'] = api_keys["OPENAI"]
    
    # Write the updated config
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print(f"✅ Updated API keys in {config_file}")
    return True

def get_api_key_input(key_name, current_value=None):
    """Get API key input from the user"""
    if current_value:
        prompt = f"Enter {key_name} API key (or press Enter to keep current value): "
    else:
        prompt = f"Enter {key_name} API key (or press Enter to skip): "
    
    key_value = input(prompt).strip()
    if not key_value and current_value:
        return current_value
    return key_value

def get_current_api_keys():
    """Get current API keys from the .env file"""
    env_file = ".env"
    current_keys = {
        "ANTHROPIC": "",
        "OPENAI": "",
        "HUGGINGFACE": "",
        "STABILITY": ""
    }
    
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for key_name in current_keys.keys():
            pattern = re.compile(f'^{key_name}_API_KEY=(.*)$', re.MULTILINE)
            match = pattern.search(content)
            if match:
                current_keys[key_name] = match.group(1)
    
    return current_keys

def main():
    """Main function"""
    print("="*80)
    print("               Manage API Keys for GenAI Agent 3D               ")
    print("="*80)
    
    # Get current API keys
    current_keys = get_current_api_keys()
    
    print("\nThis script will update API keys in the .env files and config.yaml.")
    print("Press Enter to skip any key you don't want to update.\n")
    
    # Get API keys from user
    api_keys = {
        "ANTHROPIC": get_api_key_input("Anthropic", current_keys["ANTHROPIC"]),
        "OPENAI": get_api_key_input("OpenAI", current_keys["OPENAI"]),
        "HUGGINGFACE": get_api_key_input("HuggingFace", current_keys["HUGGINGFACE"]),
        "STABILITY": get_api_key_input("Stability AI", current_keys["STABILITY"])
    }
    
    # Update files
    env_success = update_env_files(api_keys)
    config_success = update_config_yaml(api_keys)
    
    if env_success and config_success:
        print("\n✅ API keys have been updated successfully!")
        
        # Ask if user wants to restart services
        restart = input("\nDo you want to restart all services now? (y/n): ")
        if restart.lower() == 'y':
            print("\nRestarting services...")
            os.system('cd genai_agent_project && python manage_services.py restart all')
            print("Services restarted!")
        else:
            print("\nSkipping service restart")
            print("To restart services manually:")
            print("cd genai_agent_project")
            print("python manage_services.py restart all")
    else:
        print("\n⚠️ Some updates could not be completed.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
