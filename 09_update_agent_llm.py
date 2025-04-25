#!/usr/bin/env python
"""
GenAI Agent 3D - LLM Integration Update Script

This script updates the GenAI Agent 3D platform with LLM integration capabilities.
It runs all the necessary fix scripts in the correct order and handles potential errors.
"""

import os
import sys
import subprocess
import time

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 80)
print("GenAI Agent 3D - LLM Integration Update".center(80))
print("=" * 80)
print()

# Step 1: Install dependencies
print("Step 1: Installing dependencies...")
try:
    subprocess.run(
        [sys.executable, os.path.join(script_dir, "install_dependencies.py")],
        check=True
    )
    print("✅ Dependencies installed successfully")
except subprocess.CalledProcessError as e:
    print(f"❌ Error installing dependencies: {e}")
    choice = input("\nDo you want to continue anyway? (y/n): ")
    if choice.lower() != 'y':
        print("Update aborted.")
        sys.exit(1)

print()

# List of scripts to run in order
scripts = [
    "05_fix_api_routes.py",
    "06_fix_svg_processor.py",
    "07_init_llm_services.py",
    "08_final_fixes.py"
]

# Run each script in order
for script in scripts:
    script_path = os.path.join(script_dir, script)
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script}")
        continue
    
    print(f"Running: {script}")
    print("-" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True
        )
        print(f"✅ Successfully ran: {script}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script}: {e}")
        
        # Ask if user wants to continue
        choice = input("\nAn error occurred. Do you want to continue with the next script? (y/n): ")
        if choice.lower() != 'y':
            print("Update aborted.")
            sys.exit(1)
    
    print()

# Step 6: Update App.js to include LLM Test Page routes
print("Step 6: Checking and updating App.js...")
app_js_path = os.path.join(script_dir, "genai_agent_project", "web", "frontend", "src", "App.js")

if os.path.exists(app_js_path):
    with open(app_js_path, 'r') as f:
        app_content = f.read()
    
    # Check if LLMTestPage is already imported and routed
    llm_test_import = "import LLMTestPage from './components/pages/LLMTestPage'"
    llm_test_route = "<Route path=\"/llm-test\" element={<LLMTestPage"
    
    need_update = False
    
    if llm_test_import not in app_content:
        print("Adding LLMTestPage import to App.js")
        # Add import after other page imports
        app_content = app_content.replace(
            "import BlenderScriptsPage from './components/pages/BlenderScriptsPage';",
            "import BlenderScriptsPage from './components/pages/BlenderScriptsPage';\nimport LLMTestPage from './components/pages/LLMTestPage';"
        )
        need_update = True
    
    if llm_test_route not in app_content:
        print("Adding LLMTestPage route to App.js")
        # Add route with other routes
        app_content = app_content.replace(
            "<Route path=\"/settings\" element={<SettingsPage",
            "<Route path=\"/llm-test\" element={<LLMTestPage addNotification={addNotification} />} />\n              <Route path=\"/settings\" element={<SettingsPage"
        )
        need_update = True
    
    if need_update:
        with open(app_js_path, 'w') as f:
            f.write(app_content)
        print("✅ Updated App.js with LLMTestPage import and route")
    else:
        print("✅ App.js already includes LLMTestPage import and route")
else:
    print(f"❌ Could not find App.js at {app_js_path}")

# Step 7: Update AppSidebar.js to include LLM Test link
print("\nStep 7: Checking and updating AppSidebar.js...")
sidebar_js_path = os.path.join(script_dir, "genai_agent_project", "web", "frontend", "src", "components", "AppSidebar.js")

if os.path.exists(sidebar_js_path):
    with open(sidebar_js_path, 'r') as f:
        sidebar_content = f.read()
    
    # Check if LLM Test link needs to be added
    if "LLM Test" not in sidebar_content:
        print("Adding LLM Test to sidebar menu items")
        
        # Add ChatIcon import
        if "import ChatIcon" not in sidebar_content:
            sidebar_content = sidebar_content.replace(
                "import SettingsIcon from '@mui/icons-material/Settings';",
                "import SettingsIcon from '@mui/icons-material/Settings';\nimport ChatIcon from '@mui/icons-material/Chat';"
            )
        
        # Add LLM Test menu item
        sidebar_content = sidebar_content.replace(
            "{ text: 'Blender Scripts', icon: <BlenderIcon />, path: '/blender-scripts' },",
            "{ text: 'Blender Scripts', icon: <BlenderIcon />, path: '/blender-scripts' },\n    { text: 'LLM Test', icon: <ChatIcon />, path: '/llm-test' },"
        )
        
        with open(sidebar_js_path, 'w') as f:
            f.write(sidebar_content)
        print("✅ Updated AppSidebar.js with LLM Test menu item")
    else:
        print("✅ AppSidebar.js already includes LLM Test menu item")
else:
    print(f"❌ Could not find AppSidebar.js at {sidebar_js_path}")

print("\n=" * 80)
print("GenAI Agent 3D Update Complete!".center(80))
print("=" * 80)
print()

# Ask if user wants to restart services
restart = input("Do you want to restart all services now? (y/n): ")
if restart.lower() == 'y':
    print("\nRestarting services...")
    try:
        subprocess.run(
            [sys.executable, os.path.join(script_dir, "genai_agent_project", "manage_services.py"), "restart", "all"],
            check=True
        )
        print("\n✅ Services restarted successfully!")
        print("\nYou can access the web interface at: http://localhost:3000")
        print("Navigate to the 'LLM Test' page from the sidebar to test the LLM integration.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error restarting services: {e}")
        print("\nYou can manually restart services with:")
        print(f"python {os.path.join(script_dir, 'genai_agent_project', 'manage_services.py')} restart all")
else:
    print("\nSkipping service restart.")
    print("\nYou can manually restart services with:")
    print(f"python {os.path.join(script_dir, 'genai_agent_project', 'manage_services.py')} restart all")

print("\nFor more information, see the documentation in the docs/ directory.")
