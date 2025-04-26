#!/usr/bin/env python
"""
Fix for LLMService initialization error

This script directly fixes the 'LLMService.__init__() takes 1 positional argument but 2 were given'
error by updating the GenAIAgent class to initialize the LLMService without passing a config parameter.
"""

import os
import sys
import shutil
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
agent_path = os.path.join(project_dir, "genai_agent", "agent.py")

print("=" * 80)
print("GenAI Agent 3D - LLMService Initialization Fix".center(80))
print("=" * 80)
print()

if not os.path.exists(agent_path):
    print(f"❌ Could not find agent.py at {agent_path}")
    sys.exit(1)

# Create a backup
backup_path = f"{agent_path}.bak"
shutil.copy2(agent_path, backup_path)
print(f"✅ Created backup at {backup_path}")

# Read the current content
with open(agent_path, 'r') as f:
    content = f.read()

# Find the LLMService initialization line
if "self.llm_service = LLMService(llm_config)" in content:
    # Replace with correct initialization
    content = content.replace(
        "self.llm_service = LLMService(llm_config)",
        "self.llm_service = LLMService()"
    )
    print("✅ Fixed LLMService initialization")
else:
    print("❌ Could not find LLMService initialization pattern")
    print("Manual inspection required")

# Write the updated content back to the file
with open(agent_path, 'w') as f:
    f.write(content)

print("\n✅ Applied fix to agent.py")
print("\nThis fix addresses the 'LLMService.__init__() takes 1 positional argument but 2 were given' error")
print("by initializing the LLMService without passing a configuration parameter.")

# Ask if user wants to restart services
restart = input("\nDo you want to restart all services now? (y/n): ")
if restart.lower() == 'y':
    print("\nRestarting services...")
    
    # Path to manage_services.py
    manage_script = os.path.join(project_dir, "manage_services.py")
    
    try:
        # Use system Python to avoid venv issues
        subprocess.run([sys.executable, manage_script, "restart", "all"], 
                      cwd=project_dir, check=True)
        
        print("\n✅ Services restarted successfully")
        print("\nYou can access the web interface at: http://localhost:3000")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error restarting services: {e}")
        print("\nYou can try to manually restart services with:")
        print(f"cd {project_dir}")
        if sys.platform == "win32":
            print("venv\\Scripts\\activate")
        else:
            print("source venv/bin/activate")
        print("python manage_services.py restart all")
else:
    print("\nSkipping service restart")
    print("\nTo restart services manually:")
    print(f"cd {project_dir}")
    if sys.platform == "win32":
        print("venv\\Scripts\\activate")
    else:
        print("source venv/bin/activate")
    print("python manage_services.py restart all")

print("\nDone! The LLMService initialization issue should now be fixed.")
