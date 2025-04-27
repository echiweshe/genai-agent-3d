#!/usr/bin/env python3
"""
Set Claude as Default LLM Provider

This script updates the configuration to use Claude as the default LLM provider
for the GenAI Agent 3D project.
"""

import os
import sys
import re
from pathlib import Path
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    project_root = Path(__file__).parent.absolute()
    
    # Update .env file
    env_path = project_root / "genai_agent_project" / ".env"
    if env_path.exists():
        update_env_file(env_path)
    else:
        logger.warning(f".env file not found at {env_path}")
    
    # Update config.yaml file
    config_path = project_root / "genai_agent_project" / "config.yaml"
    if config_path.exists():
        update_config_yaml(config_path)
    else:
        logger.warning(f"config.yaml file not found at {config_path}")
    
    print("\n✅ Claude is now set as the default LLM provider!")
    print(f"Updated files:")
    if env_path.exists():
        print(f"- {env_path}")
    if config_path.exists():
        print(f"- {config_path}")
    
    # Ask if the user wants to restart services
    restart = input("\nWould you like to restart the services now? (y/n): ").lower() == 'y'
    if restart:
        try:
            import subprocess
            subprocess.run([sys.executable, str(project_root / "restart_services.py")], check=True)
            print("\n✅ Services restarted successfully!")
        except Exception as e:
            print(f"\n❌ Failed to restart services: {str(e)}")
            print("Please restart services manually using restart_services.py")
    
    return 0

def update_env_file(env_path):
    """Update the .env file to use Claude as the default provider"""
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update LLM settings
        updated_content = content
        
        # Update LLM_PROVIDER
        updated_content = re.sub(
            r'LLM_PROVIDER=.*',
            'LLM_PROVIDER=anthropic',
            updated_content
        )
        
        # Update LLM_MODEL
        updated_content = re.sub(
            r'LLM_MODEL=.*',
            'LLM_MODEL=claude-3-sonnet-20240229',
            updated_content
        )
        
        # Update LLM_TYPE
        updated_content = re.sub(
            r'LLM_TYPE=.*',
            'LLM_TYPE=cloud',
            updated_content
        )
        
        # Write updated content
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"Updated .env file: {env_path}")
    except Exception as e:
        logger.error(f"Error updating .env file: {str(e)}")

def update_config_yaml(config_path):
    """Update the config.yaml file to use Claude as the default provider"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Update LLM settings in config
        if 'llm' not in config:
            config['llm'] = {}
        
        config['llm']['provider'] = 'anthropic'
        config['llm']['model'] = 'claude-3-sonnet-20240229'
        config['llm']['type'] = 'cloud'
        
        # Write updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Updated config.yaml file: {config_path}")
    except Exception as e:
        logger.error(f"Error updating config.yaml file: {str(e)}")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
