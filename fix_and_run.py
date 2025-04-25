#!/usr/bin/env python
"""
GenAI Agent 3D - Fix and Run Script
This script applies all fixes and then starts the application.
"""

import os
import sys
import subprocess
import time

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")

print("=" * 80)
print("GenAI Agent 3D - Fix and Run".center(80))
print("=" * 80)
print()

# Step 1: Fix API routes
print("Step 1: Running API route fixes...")
try:
    subprocess.run([sys.executable, os.path.join(script_dir, "05_fix_api_routes.py")], check=True)
    print("✅ API route fixes completed successfully")
except subprocess.CalledProcessError as e:
    print(f"❌ Error applying API route fixes: {e}")
    input("Press Enter to continue anyway...")

print()

# Step 2: Apply final fixes
print("Step 2: Running final fixes...")
try:
    subprocess.run([sys.executable, os.path.join(script_dir, "08_final_fixes.py")], check=True)
    print("✅ Final fixes completed successfully")
except subprocess.CalledProcessError as e:
    print(f"❌ Error applying final fixes: {e}")
    input("Press Enter to continue anyway...")

print()

# Step 3: Restart all services
print("Step 3: Restarting all services...")
try:
    venv_python = os.path.join(project_dir, "venv", "Scripts", "python")
    manage_script = os.path.join(project_dir, "manage_services.py")
    
    if os.path.exists(venv_python):
        result = subprocess.run([venv_python, manage_script, "restart", "all"], check=True)
    else:
        # Fall back to system Python if venv not found
        result = subprocess.run([sys.executable, manage_script, "restart", "all"], check=True)
    
    print("✅ Services restarted successfully")
except subprocess.CalledProcessError as e:
    print(f"❌ Error restarting services: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("GenAI Agent 3D is now running!".center(80))
print("=" * 80)
print()
print("You can access the web interface at: http://localhost:3000")
print()
print("To test the LLM integration:")
print("1. Navigate to the 'LLM Test' page from the sidebar")
print("2. Select a provider and model")
print("3. Enter a prompt and click 'Generate'")
print()
print("Press Ctrl+C to stop the application")

# Wait for user to exit
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping services...")
    try:
        if os.path.exists(venv_python):
            subprocess.run([venv_python, manage_script, "stop", "all"], check=True)
        else:
            subprocess.run([sys.executable, manage_script, "stop", "all"], check=True)
        print("✅ Services stopped successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error stopping services: {e}")
    print("Goodbye!")
