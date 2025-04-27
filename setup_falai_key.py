#!/usr/bin/env python3
"""
Setup fal.ai API Key for Hunyuan3D

This script helps you set up the fal.ai API key for Hunyuan3D integration.
"""

import os
import sys
from pathlib import Path
from getpass import getpass

def main():
    """Main function"""
    print("=" * 80)
    print("           Setup fal.ai API Key for Hunyuan3D")
    print("=" * 80)
    print("\nThis script will help you set up your fal.ai API key for Hunyuan3D integration.")
    
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
    
    # Check if key is already set
    if "HUNYUAN3D_API_KEY=" in content and not "HUNYUAN3D_API_KEY=" == content.split("HUNYUAN3D_API_KEY=")[1].split("\n")[0]:
        print("fal.ai API key for Hunyuan3D is already set.")
        replace_key = input("Would you like to replace it? (y/n): ").lower() == 'y'
        if not replace_key:
            print("Keeping existing API key.")
            return 0
    
    # Instructions for getting an API key
    print("\nTo get a fal.ai API key:")
    print("1. Go to https://fal.ai/dashboard/keys")
    print("2. Create an account or log in if you haven't already")
    print("3. Click on 'Create new key'")
    print("4. Copy the generated key")
    
    # Get the API key
    api_key = getpass("\nEnter your fal.ai API key (input is hidden): ")
    
    if not api_key:
        print("No API key provided. Exiting.")
        return 1
    
    # Update the .env file
    if "HUNYUAN3D_API_KEY=" in content:
        # Replace existing key
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("HUNYUAN3D_API_KEY="):
                lines[i] = f"HUNYUAN3D_API_KEY={api_key}"
                break
        
        updated_content = '\n'.join(lines)
    else:
        # Add new key
        if not content.endswith('\n'):
            content += '\n'
        updated_content = content + f"HUNYUAN3D_API_KEY={api_key}\n"
    
    # Write updated content
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("\n✅ fal.ai API key for Hunyuan3D has been set successfully!")
    print(f"The key is stored in: {env_path}")
    
    # Ask to restart services
    restart = input("\nWould you like to restart services to apply the changes? (y/n): ").lower() == 'y'
    if restart:
        try:
            import subprocess
            print("\nRestarting services...")
            subprocess.run([sys.executable, "genai_agent_project/manage_services.py", "restart", "all"], check=True)
            print("✅ Services restarted successfully!")
        except Exception as e:
            print(f"❌ Failed to restart services: {str(e)}")
            print("Please restart services manually using:")
            print("python genai_agent_project/manage_services.py restart all")
    else:
        print("\nRemember to restart services to apply the changes:")
        print("python genai_agent_project/manage_services.py restart all")
    
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
