#!/usr/bin/env python3
"""
Fix Claude API Key Issue

This script adds the Anthropic API key to the .env file and ensures it's loaded properly.
"""

import os
import sys
from pathlib import Path

def main():
    """Main function"""
    # Find the .env file
    project_root = Path(__file__).parent.absolute()
    env_path = project_root / "genai_agent_project" / ".env"
    
    # Create .env file if it doesn't exist
    if not env_path.exists():
        os.makedirs(env_path.parent, exist_ok=True)
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# GenAI Agent 3D Environment Variables\n\n")
    
    # Read current content
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if Anthropic API key is already set
    if "ANTHROPIC_API_KEY=" in content and not "# ANTHROPIC_API_KEY=" in content:
        print("Anthropic API key is already set in .env file.")
        replace_key = input("Would you like to replace it? (y/n): ").lower() == 'y'
        if not replace_key:
            print("Keeping existing API key.")
            return 0
    
    # Get the API key
    print("\nAnthropic API Key Setup")
    print("=======================")
    print("You need to provide your Anthropic API key to use Claude models.")
    print("The API key should start with 'sk-ant-'")
    
    api_key = input("Enter your Anthropic API key: ")
    if not api_key:
        print("No API key provided. Exiting.")
        return 1
    
    # Basic validation
    if not api_key.startswith("sk-ant-"):
        print("Warning: The API key doesn't seem to have the expected format.")
        print("It should typically start with 'sk-ant-'")
        continue_anyway = input("Continue anyway? (y/n): ").lower() == 'y'
        if not continue_anyway:
            print("Operation cancelled.")
            return 1
    
    # Update or add the API key
    if "ANTHROPIC_API_KEY=" in content:
        # Replace existing key
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("ANTHROPIC_API_KEY="):
                lines[i] = f"ANTHROPIC_API_KEY={api_key}"
                break
            elif line.strip().startswith("# ANTHROPIC_API_KEY="):
                lines[i] = f"ANTHROPIC_API_KEY={api_key}"
                break
        
        updated_content = '\n'.join(lines)
    else:
        # Add new key
        if not content.endswith('\n'):
            content += '\n'
        updated_content = content + f"ANTHROPIC_API_KEY={api_key}\n"
    
    # Write updated content
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("\n✅ Anthropic API key has been successfully added to .env file!")
    print(f"The key is stored in: {env_path}")
    print("\nTo apply the changes, restart the services:")
    print("python genai_agent_project/manage_services.py restart all")
    
    # Ask if the user wants to restart services
    restart = input("\nWould you like to restart services now? (y/n): ").lower() == 'y'
    if restart:
        try:
            import subprocess
            subprocess.run([sys.executable, "genai_agent_project/manage_services.py", "restart", "all"], check=True)
            print("\n✅ Services restarted successfully!")
        except Exception as e:
            print(f"\n❌ Failed to restart services: {str(e)}")
            print("Please restart services manually.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
