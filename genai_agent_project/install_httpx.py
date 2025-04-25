#!/usr/bin/env python
"""
Quick script to install httpx and other required dependencies directly
in the current Python environment (virtual env or system)
"""

import subprocess
import sys
import os

print("Installing httpx and other required dependencies...")

try:
    # Install directly without using requirements.txt
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "httpx", "pydantic", "fastapi", "redis", "pyyaml", "requests", "uvicorn"],
        check=True
    )
    print("✅ Successfully installed dependencies")
except subprocess.CalledProcessError as e:
    print(f"❌ Error installing dependencies: {e}")
    print("\nPlease try to install manually with:")
    print("pip install httpx pydantic fastapi redis pyyaml requests uvicorn")
    sys.exit(1)

print("\nDependencies installation complete!")
print("\nYou can now start the application with:")
print("python manage_services.py restart all")
