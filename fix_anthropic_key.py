#!/usr/bin/env python3
"""
Fix Anthropic API Key Issue for GenAI Agent 3D

This script adds the Anthropic API key to the environment and fixes
the authentication issue with the Claude API.

Usage:
    python fix_anthropic_key.py [--key YOUR_API_KEY]
"""

import os
import sys
import argparse
import logging
import dotenv
from getpass import getpass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_anthropic_api_key(key, env_path):
    """Set the Anthropic API key in the .env file"""
    try:
        # Make sure directory exists
        env_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the file if it doesn't exist
        if not os.path.exists(env_path):
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write("# GenAI Agent 3D Environment Variables\n")
        
        # Read the current content
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if the key already exists
        key_exists = False
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                if line.split('=')[0].strip() == "ANTHROPIC_API_KEY":
                    lines[i] = f"ANTHROPIC_API_KEY={key}\n"
                    key_exists = True
                    break
        
        # If the key doesn't exist, add it
        if not key_exists:
            lines.append(f"ANTHROPIC_API_KEY={key}\n")
        
        # Write the updated content
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Load the updated environment variables
        dotenv.load_dotenv(env_path, override=True)
        
        logger.info(f"Anthropic API key set successfully in {env_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error setting Anthropic API key: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Fix Anthropic API Key Issue for GenAI Agent 3D")
    parser.add_argument("--key", help="Anthropic API key (if not provided, will prompt for input)")
    args = parser.parse_args()
    
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Print banner
    print("=" * 80)
    print("           Fix Anthropic API Key Issue for GenAI Agent 3D")
    print("=" * 80)
    
    # Determine .env file path
    env_path = project_root / "genai_agent_project" / ".env"
    
    # Get the API key
    api_key = args.key
    if not api_key:
        print("\nEnter your Anthropic API key (starts with 'sk-ant-'):")
        api_key = getpass("API Key (input is hidden): ")
    
    if not api_key:
        print("No API key provided. Exiting.")
        return 1
    
    # Validate the key format (basic check)
    if not api_key.startswith("sk-ant-"):
        print("Warning: The API key doesn't seem to be in the expected format (should start with 'sk-ant-').")
        confirm = input("Continue anyway? (y/n): ").lower()
        if confirm != 'y':
            print("Operation cancelled by user.")
            return 1
    
    # Set the API key
    if set_anthropic_api_key(api_key, env_path):
        print("\n✅ Success! The Anthropic API key has been set.")
        print(f"The key is stored in: {env_path}")
        print("\nNext steps:")
        print("1. Restart the GenAI Agent 3D application")
        print("2. Try using Claude in the application")
        return 0
    else:
        print("\n❌ Failed to set the Anthropic API key.")
        print("Please check the error messages above and try again.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
