#!/usr/bin/env python
"""
Setup script for LLM services in GenAI Agent 3D.
This script creates the necessary directories and copies the implementation files to their appropriate locations.
"""

import os
import sys
import shutil
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define directories to create
directories = [
    os.path.join(script_dir, "scripts"),
    os.path.join(script_dir, "genai_agent", "services", "llm_providers"),
    os.path.join(script_dir, "logs"),
]

# Create directories
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

# Source files in the project root
root_files = {
    "enhanced_llm.py": os.path.join(script_dir, "genai_agent", "services", "enhanced_llm.py"),
    "llm_service_manager.py": os.path.join(script_dir, "genai_agent", "services", "llm_service_manager.py"),
    "llm_redis_worker.py": os.path.join(script_dir, "genai_agent", "services", "llm_redis_worker.py"),
    "run_llm_worker.py": os.path.join(script_dir, "scripts", "run_llm_worker.py"),
    "llm.env": os.path.join(script_dir, ".env"),
}

# Copy files from root to their destinations
for source_file, dest_path in root_files.items():
    source_path = os.path.join(script_dir, source_file)
    if os.path.exists(source_path):
        shutil.copy2(source_path, dest_path)
        print(f"Copied: {source_path} -> {dest_path}")
    else:
        print(f"Warning: Source file not found: {source_path}")

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
