#!/usr/bin/env python
"""
Restart services after LLM fixes
"""

import os
import sys
import subprocess
import time

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")

print("=" * 80)
print("GenAI Agent 3D - Restart Services".center(80))
print("=" * 80)
print()

# Check if running inside a virtual environment
in_venv = hasattr(sys, "real_prefix") or (
    hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
)

# Path to Python and manage script
venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
manage_script = os.path.join(project_dir, "manage_services.py")

python_cmd = venv_python if os.path.exists(venv_python) else sys.executable

# Restart the services
print("Restarting all services...")

try:
    # Stop all services first
    subprocess.run(
        [python_cmd, manage_script, "stop", "all"],
        check=True
    )
    print("Services stopped")
    
    # Small delay
    time.sleep(2)
    
    # Start all services
    subprocess.run(
        [python_cmd, manage_script, "start", "all"],
        check=True
    )
    print("Services started")
    
    print("\n✅ Services restarted successfully!")
    print("\nYou can access the web interface at: http://localhost:3000")
    
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error restarting services: {e}")
    print("\nYou can try to manually restart services with:")
    print(f"cd {project_dir}")
    print(f"{'venv\\Scripts\\activate' if sys.platform == 'win32' else 'source venv/bin/activate'}")
    print("python manage_services.py restart all")
