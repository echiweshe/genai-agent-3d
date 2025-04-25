#!/usr/bin/env python
"""
Setup script for LLM services in GenAI Agent 3D.
This script creates the necessary directories and files for the enhanced LLM services.
"""

import os
import sys
import shutil
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Define directories to create
directories = [
    os.path.join(project_root, "scripts"),
    os.path.join(project_root, "genai_agent", "services", "llm_providers"),
    os.path.join(project_root, "logs"),
]

# Create directories
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

# Copy files to their respective locations
files_to_copy = [
    # Enhanced LLM service
    {
        "source": os.path.join(project_root, "enhanced_llm.py"),
        "destination": os.path.join(project_root, "genai_agent", "services", "enhanced_llm.py")
    },
    # LLM service manager
    {
        "source": os.path.join(project_root, "llm_service_manager.py"),
        "destination": os.path.join(project_root, "genai_agent", "services", "llm_service_manager.py")
    },
    # LLM Redis worker
    {
        "source": os.path.join(project_root, "llm_redis_worker.py"),
        "destination": os.path.join(project_root, "genai_agent", "services", "llm_redis_worker.py")
    },
    # Run LLM worker script
    {
        "source": os.path.join(project_root, "run_llm_worker.py"),
        "destination": os.path.join(project_root, "scripts", "run_llm_worker.py")
    },
    # .env file
    {
        "source": os.path.join(project_root, "llm.env"),
        "destination": os.path.join(project_root, ".env")
    }
]

# Copy files if they exist
for file_info in files_to_copy:
    source = file_info["source"]
    destination = file_info["destination"]
    
    if os.path.exists(source):
        shutil.copy2(source, destination)
        print(f"Copied: {source} -> {destination}")
    else:
        print(f"Warning: Source file not found: {source}")

# Install required packages
packages = [
    "aiohttp",
    "aioredis",
    "python-dotenv",
    "psutil",
    "requests"
]

print("\nInstalling required packages...")
subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)

print("\nSetup complete!")
print("\nNext steps:")
print("1. Add your API keys to the .env file")
print("2. Start the services with: python manage_services.py start all")
print("3. Or start just the LLM services with: python manage_services.py start llm_worker")