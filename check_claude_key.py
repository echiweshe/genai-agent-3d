#!/usr/bin/env python3
"""
Check Claude API Key Status

This script checks if the Anthropic API key is properly set up.
"""

import os
import sys
from pathlib import Path

def main():
    """Main function"""
    # Find the .env file
    project_root = Path(__file__).parent.absolute()
    env_path = project_root / "genai_agent_project" / ".env"
    
    print("=" * 80)
    print("           Claude API Key Status Check")
    print("=" * 80)
    
    # Check if .env file exists
    if not env_path.exists():
        print(f"\n❌ The .env file does not exist at: {env_path}")
        print("The Claude API key is not configured.")
        print("\nTo fix this issue, run:")
        print("  python fix_claude_api_key.py")
        return 1
    
    # Read .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Anthropic API key
    if "ANTHROPIC_API_KEY=" in content and not "# ANTHROPIC_API_KEY=" in content:
        # Extract the key value
        key_lines = [line for line in content.split('\n') if line.strip().startswith("ANTHROPIC_API_KEY=")]
        if key_lines:
            key_value = key_lines[0].strip().split('=', 1)[1]
            # Show masked key
            masked_key = "•" * (len(key_value) - 8) + key_value[-8:] if len(key_value) > 8 else "•" * len(key_value)
            
            print("\n✅ The Anthropic API key is configured!")
            print(f"Key: {masked_key}")
            
            # Basic validation
            if not key_value.startswith("sk-ant-"):
                print("\n⚠️ Warning: The key doesn't have the expected format.")
                print("It should typically start with 'sk-ant-'")
                print("The key might not work correctly.")
        else:
            print("\n❓ The Anthropic API key appears to be set, but could not be read.")
    else:
        print("\n❌ The Anthropic API key is not configured.")
        print("\nTo fix this issue, run:")
        print("  python fix_claude_api_key.py")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
