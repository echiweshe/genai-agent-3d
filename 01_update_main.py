#!/usr/bin/env python
"""
Script to update the main.py file with LLM API routes.
"""

import os
import re
import sys
import shutil

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(script_dir, "genai_agent_project", "web", "backend")
main_py_path = os.path.join(backend_dir, "main.py")

# Check if main.py exists
if not os.path.exists(main_py_path):
    print(f"Error: main.py not found at {main_py_path}")
    sys.exit(1)

# Create a backup
backup_path = main_py_path + ".bak"
shutil.copy2(main_py_path, backup_path)
print(f"Created backup: {backup_path}")

# Read the content of main.py
with open(main_py_path, "r") as f:
    content = f.read()

# Add the import for LLM routes
import_pattern = r"# Import routes[^\n]*\n"
import_statement = "from genai_agent.services.llm_api_routes import add_llm_routes\n"

# Check if the import already exists
if "from genai_agent.services.llm_api_routes import add_llm_routes" not in content:
    # Find the imports section and add our import
    matches = re.search(import_pattern, content)
    if matches:
        insert_point = matches.end()
        content = content[:insert_point] + import_statement + content[insert_point:]
        print("Added import statement for LLM API routes")
    else:
        print("Warning: Could not find appropriate place to add import statement")

# Add the call to add_llm_routes
app_creation_pattern = r"app = FastAPI\([^\)]*\)[^\n]*\n"
add_routes_pattern = r"# Add LLM routes\nadd_llm_routes\(app\)\n"

# Check if the route addition already exists
if "add_llm_routes(app)" not in content:
    # Find where the app is created and add our route addition after that
    matches = re.search(app_creation_pattern, content)
    if matches:
        insert_point = matches.end()
        content = content[:insert_point] + "\n# Add LLM routes\nadd_llm_routes(app)\n" + content[insert_point:]
        print("Added call to add_llm_routes")
    else:
        print("Warning: Could not find appropriate place to add route initialization")

# Write the updated content back to main.py
with open(main_py_path, "w") as f:
    f.write(content)

print(f"Updated {main_py_path} with LLM API routes integration")
print("\nNext steps:")
print("1. Start all services: python manage_services.py start all")
print("2. Test the LLM API at: http://localhost:8000/api/llm/providers")
