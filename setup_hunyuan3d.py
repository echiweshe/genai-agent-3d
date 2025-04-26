#!/usr/bin/env python3
"""
Setup Hunyuan3D Integration for GenAI Agent 3D

This script helps set up the Hunyuan3D integration by:
1. Setting up the Hunyuan3D API key
2. Configuring integration path
3. Testing the connection
"""

import os
import sys
from pathlib import Path
import subprocess
from getpass import getpass

def setup_hunyuan3d_key():
    """Set up Hunyuan3D API key in .env file"""
    # Find the .env file
    project_root = Path(__file__).parent.absolute()
    env_path = project_root / "genai_agent_project" / ".env"
    
    if not env_path.exists():
        print(f"❌ .env file not found at: {env_path}")
        print("Please run the project setup first.")
        return False
    
    # Read the .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    # Check if key is already set
    if "HUNYUAN3D_API_KEY=" in env_content and not "HUNYUAN3D_API_KEY=" == env_content.split("HUNYUAN3D_API_KEY=")[1].split("\n")[0]:
        print("Hunyuan3D API key is already set.")
        replace_key = input("Would you like to replace it? (y/n): ").lower() == 'y'
        if not replace_key:
            print("Keeping existing API key.")
            return True
    
    # Get the API key
    print("\nHunyuan3D API Key Setup")
    print("=======================")
    print("You need to provide your Hunyuan3D API key.")
    api_key = getpass("Enter your Hunyuan3D API key (input is hidden): ")
    
    if not api_key:
        print("No API key provided. Skipping.")
        return False
    
    # Update the .env file
    if "HUNYUAN3D_API_KEY=" in env_content:
        # Replace existing key
        lines = env_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("HUNYUAN3D_API_KEY="):
                lines[i] = f"HUNYUAN3D_API_KEY={api_key}"
                break
        
        updated_content = '\n'.join(lines)
    else:
        # Add new key (should not happen with our template)
        updated_content = env_content.replace(
            "# LLM API Keys", 
            "# LLM API Keys\nHUNYUAN3D_API_KEY=" + api_key
        )
    
    # Write updated content
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Hunyuan3D API key has been set successfully!")
    return True

def setup_hunyuan3d_path():
    """Set up Hunyuan3D integration path"""
    project_root = Path(__file__).parent.absolute()
    integrations_dir = project_root / "genai_agent_project" / "integrations"
    hunyuan3d_dir = integrations_dir / "hunyuan3d"
    
    # Create integrations directory if it doesn't exist
    integrations_dir.mkdir(exist_ok=True)
    
    # Check if hunyuan3d directory exists
    if not hunyuan3d_dir.exists():
        print(f"Creating Hunyuan3D integration directory at: {hunyuan3d_dir}")
        hunyuan3d_dir.mkdir(exist_ok=True)
        
        # Create a placeholder file
        with open(hunyuan3d_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write("""# Hunyuan3D Integration

This directory contains the Hunyuan3D integration files for GenAI Agent 3D.

## Setup

1. Install the Hunyuan3D Python package:
   ```
   pip install hunyuan3d
   ```

2. Set your Hunyuan3D API key in the `.env` file:
   ```
   HUNYUAN3D_API_KEY=your_api_key_here
   ```

3. Restart the GenAI Agent 3D services
""")
        
        print("✅ Hunyuan3D integration directory created.")
    else:
        print("✅ Hunyuan3D integration directory already exists.")
    
    return True

def main():
    """Main function"""
    print("=" * 80)
    print("           Hunyuan3D Setup for GenAI Agent 3D")
    print("=" * 80)
    print("\nThis script will help you set up the Hunyuan3D integration.")
    
    # Set up API key
    print("\n[1/2] Setting up Hunyuan3D API key...")
    if not setup_hunyuan3d_key():
        print("⚠️ Skipping API key setup.")
    
    # Set up integration path
    print("\n[2/2] Setting up Hunyuan3D integration path...")
    if not setup_hunyuan3d_path():
        print("❌ Failed to set up Hunyuan3D integration path.")
        return 1
    
    # Final instructions
    print("\n✅ Hunyuan3D setup completed!")
    print("\nTo complete the setup, you need to:")
    print("1. Make sure you have the Hunyuan3D Python package installed:")
    print("   pip install hunyuan3d")
    print("2. Restart the GenAI Agent 3D services:")
    print("   python genai_agent_project/manage_services.py restart all")
    
    # Ask if the user wants to restart services
    restart = input("\nWould you like to restart services now? (y/n): ").lower() == 'y'
    if restart:
        try:
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
