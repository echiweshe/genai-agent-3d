#!/usr/bin/env python
"""
GenAI Agent 3D - Install Dependencies Script

This script installs the required dependencies for the LLM integration.
"""

import os
import sys
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")

print("=" * 80)
print("GenAI Agent 3D - Installing Dependencies".center(80))
print("=" * 80)
print()

# Check if running inside a virtual environment
in_venv = hasattr(sys, "real_prefix") or (
    hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
)

if not in_venv:
    print("Attempting to activate virtual environment...")
    
    # Check for venv in project directory
    venv_python = None
    venv_pip = None
    
    if os.path.exists(os.path.join(project_dir, "venv")):
        if sys.platform == "win32":
            venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
            venv_pip = os.path.join(project_dir, "venv", "Scripts", "pip.exe")
        else:
            venv_python = os.path.join(project_dir, "venv", "bin", "python")
            venv_pip = os.path.join(project_dir, "venv", "bin", "pip")
    
    if venv_python and os.path.exists(venv_python):
        print(f"Using virtual environment at: {os.path.join(project_dir, 'venv')}")
        python_cmd = venv_python
        pip_cmd = venv_pip
    else:
        print("No virtual environment found. Using system Python.")
        python_cmd = sys.executable
        pip_cmd = "pip"
else:
    print("Already running in a virtual environment.")
    python_cmd = sys.executable
    pip_cmd = "pip"

# Install dependencies
print("\nInstalling dependencies...")
requirements_file = os.path.join(project_dir, "requirements.txt")

try:
    subprocess.run(
        [pip_cmd, "install", "-r", requirements_file],
        check=True
    )
    print("✅ Successfully installed dependencies")
except subprocess.CalledProcessError as e:
    print(f"❌ Error installing dependencies: {e}")
    
    # Try to install httpx directly
    print("\nAttempting to install httpx directly...")
    try:
        subprocess.run(
            [pip_cmd, "install", "httpx"],
            check=True
        )
        print("✅ Successfully installed httpx")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing httpx: {e}")
        print("\nPlease install the required dependencies manually:")
        print("1. Activate the virtual environment")
        print("2. Run: pip install httpx pydantic fastapi redis pyyaml requests uvicorn")
        sys.exit(1)

print("\nDependencies installation complete!")
print("\nNext steps:")
print("1. Run the update script: python 09_update_agent_llm.py")
print("2. Start the application: python genai_agent_project/manage_services.py restart all")
print("3. Access the web interface at: http://localhost:3000")
