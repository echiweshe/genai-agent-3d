#!/usr/bin/env python3
"""
Secure Configuration Setup for GenAI Agent 3D

This script helps set up configuration files with API keys in a secure way.
It creates local copies of template files and helps users add their API keys
without committing them to version control.
"""

import os
import shutil
import yaml
import re
from getpass import getpass

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"{title:^80}")
    print("="*80 + "\n")

def setup_config_yaml():
    """Set up the config.yaml file from the template"""
    template_path = "genai_agent_project/config.template.yaml"
    config_path = "genai_agent_project/config.yaml"
    
    # Check if template exists
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    # Check if config already exists
    if os.path.exists(config_path):
        overwrite = input(f"Configuration file already exists: {config_path}. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Skipping config.yaml setup.")
            return False
    
    # Copy template to config file
    shutil.copy2(template_path, config_path)
    print(f"✅ Created config file from template: {config_path}")
    
    # Ask for API keys
    print("\nEnter your API keys (press Enter to skip any you don't have):")
    anthropic_key = getpass("Anthropic API Key: ").strip()
    openai_key = getpass("OpenAI API Key: ").strip()
    
    # Update config with API keys
    if anthropic_key or openai_key:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Update with provided keys
        if anthropic_key and config.get('llm', {}).get('provider') == 'anthropic':
            config['llm']['api_key'] = anthropic_key
            print("✅ Added Anthropic API key to config.yaml")
        
        # Update tool configurations if needed
        for tool_name, tool_config in config.get('tools', {}).items():
            if 'config' in tool_config and 'api_key' in tool_config['config']:
                if openai_key and tool_config.get('config', {}).get('model', '').startswith('gpt-'):
                    tool_config['config']['api_key'] = openai_key
                    print(f"✅ Added OpenAI API key to {tool_name} tool config")
        
        # Write updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    return True

def setup_env_files():
    """Set up .env files from templates"""
    templates = [
        (".env.template", ".env"),
        (".env.template", "genai_agent_project/.env")
    ]
    
    success = True
    
    for template_path, env_path in templates:
        # Check if template exists
        if not os.path.exists(template_path):
            print(f"❌ Template file not found: {template_path}")
            success = False
            continue
        
        # Check if env file already exists
        if os.path.exists(env_path):
            overwrite = input(f"Environment file already exists: {env_path}. Overwrite? (y/n): ").lower()
            if overwrite != 'y':
                print(f"Skipping {env_path} setup.")
                continue
        
        # Create directory if needed
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        
        # Copy template to env file
        shutil.copy2(template_path, env_path)
        print(f"✅ Created environment file from template: {env_path}")
    
    # Ask for API keys
    print("\nEnter your API keys (press Enter to skip any you don't have):")
    anthropic_key = getpass("Anthropic API Key: ").strip()
    openai_key = getpass("OpenAI API Key: ").strip()
    stability_key = getpass("Stability API Key: ").strip()
    
    # Update .env files with API keys
    for _, env_path in templates:
        if os.path.exists(env_path) and (anthropic_key or openai_key or stability_key):
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace API key placeholders
            if anthropic_key:
                content = re.sub(r'ANTHROPIC_API_KEY=.*', f'ANTHROPIC_API_KEY={anthropic_key}', content)
            
            if openai_key:
                content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={openai_key}', content)
            
            if stability_key:
                content = re.sub(r'STABILITY_API_KEY=.*', f'STABILITY_API_KEY={stability_key}', content)
            
            # Write updated content
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated API keys in {env_path}")
    
    return success

def update_gitignore():
    """Make sure .gitignore contains necessary entries"""
    gitignore_path = ".gitignore"
    necessary_entries = [
        ".env",
        "genai_agent_project/.env",
        "genai_agent_project/config.yaml",
        "*.key",
        "secrets.json"
    ]
    
    # Create .gitignore if it doesn't exist
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("# Automatically generated .gitignore\n\n")
            for entry in necessary_entries:
                f.write(f"{entry}\n")
        print(f"✅ Created {gitignore_path}")
        return True
    
    # Read existing .gitignore
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check and add missing entries
    modified = False
    for entry in necessary_entries:
        pattern = re.compile(f"^{re.escape(entry)}$", re.MULTILINE)
        if not pattern.search(content):
            if not content.endswith("\n"):
                content += "\n"
            content += f"{entry}\n"
            modified = True
    
    # Write updated .gitignore if modified
    if modified:
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {gitignore_path} with necessary entries")
    else:
        print(f"✅ {gitignore_path} already contains necessary entries")
    
    return True

def main():
    """Main function"""
    print_header("GenAI Agent 3D - Secure Configuration Setup")
    
    print("This script will help you set up configuration files with your API keys.")
    print("Your API keys will be stored locally and will NOT be committed to version control.")
    print()
    print("IMPORTANT: Never commit files containing API keys to the repository!")
    
    continue_setup = input("\nContinue with setup? (y/n): ").lower()
    if continue_setup != 'y':
        print("Setup cancelled.")
        return
    
    # Set up config.yaml
    print_header("Setting up config.yaml")
    setup_config_yaml()
    
    # Set up .env files
    print_header("Setting up .env files")
    setup_env_files()
    
    # Update .gitignore
    print_header("Updating .gitignore")
    update_gitignore()
    
    print_header("Setup Complete")
    print("✅ Configuration setup completed successfully!")
    print("\nYour API keys have been added to local configuration files.")
    print("These files are now in .gitignore and will not be committed to version control.")
    print("\nNext Steps:")
    print("1. Restart all services to apply your configuration:")
    print("   python restart_services.py")
    print("2. Check system status to ensure everything is working:")
    print("   python check_status.py")
    print("\nFor more information on managing API keys, refer to API_KEYS_README.md")

if __name__ == "__main__":
    main()
