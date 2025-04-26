#!/usr/bin/env python3
"""
Set Claude as Default LLM for GenAI Agent 3D

This script updates the config.yaml file to use Anthropic Claude as the default LLM provider.
It's a simple, targeted fix that doesn't modify any code files.
"""

import os
import yaml
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    return backup_path

def set_claude_default():
    """Update config.yaml to use Claude as the default LLM"""
    # Find config.yaml
    file_path = "genai_agent_project/config.yaml"
    
    if not os.path.exists(file_path):
        # Try absolute path
        file_path = os.path.join("C:", os.sep, "ZB_Share", "Labs", "src", "CluadeMCP", 
                              "genai-agent-3d", "genai_agent_project", "config.yaml")
        if not os.path.exists(file_path):
            print(f"❌ Could not find config.yaml")
            return False
    
    # Create backup
    backup_file(file_path)
    
    try:
        # Read config
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        # Update LLM settings
        if 'llm' not in config:
            config['llm'] = {}
        
        # Set Claude as default
        config['llm']['type'] = 'cloud'
        config['llm']['provider'] = 'anthropic'
        config['llm']['model'] = 'claude-3-sonnet-20240229'
        
        # Ask for API key if needed
        if 'api_key' not in config['llm']:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                print("\nNo Anthropic API key found in environment variables or config.")
                api_key = input("Enter your Anthropic API key (or leave blank to add later): ").strip()
                if api_key:
                    config['llm']['api_key'] = api_key
                    print("✅ API key added to config")
                else:
                    print("ℹ️ No API key provided. You'll need to add it later.")
        
        # Save updated config
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✅ Updated config to use Claude as default LLM")
        return True
    
    except Exception as e:
        print(f"❌ Error updating config: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("       Set Claude as Default LLM for GenAI Agent 3D        ")
    print("="*80)
    
    success = set_claude_default()
    
    if success:
        print("\n✅ Successfully set Claude as the default LLM provider!")
        print("\nNOTE: This only updates the configuration. If the codebase doesn't")
        print("support Claude yet, you'll need to run add_anthropic_support.py first.")
        
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
        print("\n❌ Failed to set Claude as default LLM provider.")
        print("Please check the error messages above and fix manually if needed.")
