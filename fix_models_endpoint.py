#!/usr/bin/env python
"""
Fix Models Endpoint Mismatch
This script adds a direct route handler for the /models endpoint to fix the 404 error.
"""

import os
import sys
import glob
import shutil
from pathlib import Path

def find_main_py_files(base_dir):
    """Find all main.py files in the project"""
    main_files = []
    for root, dirs, files in os.walk(base_dir):
        if 'main.py' in files:
            main_files.append(os.path.join(root, 'main.py'))
    return main_files

def add_models_endpoint(main_py_path):
    """Add a models endpoint handler to main.py"""
    try:
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = main_py_path + '.models_backup'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                f.write(content)
            print(f"Created backup: {backup_path}")
        
        # Check if @app.get("/models") already exists
        if '@app.get("/models")' in content:
            print(f"Models endpoint already exists in {main_py_path}")
            return False
        
        # Find a good place to insert the endpoint handler
        # Look for other @app.get endpoints
        lines = content.splitlines()
        
        # Find other app.get handlers
        endpoint_lines = [i for i, line in enumerate(lines) if '@app.get("/' in line]
        
        if endpoint_lines:
            # Insert after the last endpoint
            insert_line = max(endpoint_lines) + 1
            while insert_line < len(lines) and (lines[insert_line].startswith('def ') or lines[insert_line].startswith('async def ')):
                insert_line += 1
            
            # Build the models endpoint handler
            models_handler = """
@app.get("/models")
async def get_models():
    \"\"\"Get available models - direct handler for frontend compatibility\"\"\"
    try:
        # Define output directories
        output_dir = os.path.join(parent_dir, "output")
        models_dir = os.path.join(output_dir, "models")
        
        # Ensure the directory exists
        os.makedirs(models_dir, exist_ok=True)
        
        # Look for .blend files in the models directory
        models = []
        for root, dirs, files in os.walk(models_dir):
            for file in files:
                if file.endswith('.blend') or file.endswith('.py'):
                    model_path = os.path.join(root, file)
                    rel_path = os.path.relpath(model_path, output_dir)
                    models.append({
                        "id": os.path.splitext(file)[0],
                        "name": file,
                        "path": rel_path,
                        "size": os.path.getsize(model_path),
                        "modified": os.path.getmtime(model_path)
                    })
        
        # For compatibility, return the same format as the frontend expects
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return {"status": "error", "message": str(e), "models": []}
"""
            
            # Insert the handler
            lines.insert(insert_line, models_handler)
            
            # Write the updated content
            with open(main_py_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print(f"Added models endpoint handler to {main_py_path}")
            return True
        else:
            print(f"No suitable insertion point found in {main_py_path}")
            return False
    except Exception as e:
        print(f"Error adding models endpoint to {main_py_path}: {e}")
        return False

def find_api_files(base_dir):
    """Find API service files in the frontend"""
    api_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower() == 'api.js':
                api_files.append(os.path.join(root, file))
    return api_files

def check_api_service(api_path):
    """Check and fix API service to ensure it's using the right models endpoint"""
    try:
        with open(api_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = api_path + '.models_backup'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w') as f:
                f.write(content)
            print(f"Created backup: {backup_path}")
        
        # Check if getModels is defined
        if 'export const getModels' in content:
            print(f"Found getModels in {api_path}")
            
            # Check if it's hitting the right endpoint
            if '/api/models' in content:
                # Need to fix the URL
                updated_content = content.replace('/api/models', '/models')
                with open(api_path, 'w') as f:
                    f.write(updated_content)
                print(f"Fixed models endpoint URL in {api_path}")
                return True
            elif '/models' in content:
                print(f"Models endpoint URL looks correct in {api_path}")
                return True
        else:
            print(f"getModels not found in {api_path}")
            return False
    except Exception as e:
        print(f"Error checking API service {api_path}: {e}")
        return False

def create_output_dirs():
    """Create output and models directories"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Possible paths
    output_paths = [
        os.path.join(script_dir, "output"),
        os.path.join(script_dir, "genai_agent_project", "output")
    ]
    
    for output_path in output_paths:
        try:
            os.makedirs(output_path, exist_ok=True)
            models_path = os.path.join(output_path, "models")
            os.makedirs(models_path, exist_ok=True)
            print(f"Created directory: {models_path}")
        except Exception as e:
            print(f"Error creating directory {output_path}: {e}")

def main():
    """Main function"""
    print("\n===== FIXING MODELS ENDPOINT MISMATCH =====\n")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Create output directories
    create_output_dirs()
    
    # Find and fix main.py files
    main_files = find_main_py_files(script_dir)
    if main_files:
        print(f"Found {len(main_files)} main.py files")
        for main_file in main_files:
            print(f"\nProcessing {main_file}")
            add_models_endpoint(main_file)
    else:
        print("No main.py files found")
    
    # Find and fix API service files
    api_files = find_api_files(script_dir)
    if api_files:
        print(f"\nFound {len(api_files)} API service files")
        for api_file in api_files:
            print(f"\nProcessing {api_file}")
            check_api_service(api_file)
    else:
        print("\nNo API service files found")
    
    print("\n===== FIX COMPLETE =====")
    print("Please restart your backend server for the changes to take effect.")
    print("If you still see the error, check browser console (F12) for more details.")

if __name__ == "__main__":
    main()
