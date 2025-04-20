#!/usr/bin/env python
"""
Add Health Endpoint to FastAPI Server
This script adds a /api/health endpoint to the main.py file
"""

import os
import sys
import re

def find_main_py_file(base_dir):
    """Find the main.py file in the project"""
    for root, dirs, files in os.walk(base_dir):
        if 'main.py' in files:
            return os.path.join(root, 'main.py')
    return None

def add_health_endpoint(main_py_path):
    """Add a health endpoint to main.py"""
    try:
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = main_py_path + '.health_backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"Created backup: {backup_path}")
        
        # Check if health endpoint already exists
        if "@app.get(\"/api/health\")" in content or "@app.get('/api/health')" in content:
            print("Health endpoint already exists")
            return False
        
        # Find a good place to insert the health endpoint
        # Look for the @app.get("/status") endpoint
        status_match = re.search(r'@app\.get\([\'"]\/status[\'"]\)[^\n]*\n[^\n]*def get_status\(\):', content)
        
        if status_match:
            # Find the end of the get_status function
            function_end = content.find('\n\n', status_match.end())
            if function_end == -1:
                function_end = len(content)
            
            # Add the health endpoint after the status endpoint
            health_endpoint = """

@app.get("/api/health")
async def health_check():
    \"\"\"Health check endpoint for service monitoring\"\"\"
    return {"status": "ok", "message": "Service is healthy"}
"""
            new_content = content[:function_end] + health_endpoint + content[function_end:]
            
            # Write the updated content
            with open(main_py_path, 'w') as f:
                f.write(new_content)
            
            print(f"Added health endpoint to {main_py_path}")
            return True
        else:
            print("Status endpoint not found")
            
            # Look for any @app.get endpoint as a fallback
            endpoint_match = re.search(r'@app\.get\([^\n]+\)[^\n]*\n', content)
            
            if endpoint_match:
                # Find the start of the function
                function_start = content.find('\n', endpoint_match.end())
                
                # Find a good place to insert the health endpoint
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if '@app.get' in line and i+1 < len(lines) and 'def ' in lines[i+1]:
                        # Add the health endpoint before this endpoint
                        health_endpoint = """@app.get("/api/health")
async def health_check():
    \"\"\"Health check endpoint for service monitoring\"\"\"
    return {"status": "ok", "message": "Service is healthy"}

"""
                        new_lines = lines[:i] + [health_endpoint] + lines[i:]
                        new_content = '\n'.join(new_lines)
                        
                        # Write the updated content
                        with open(main_py_path, 'w') as f:
                            f.write(new_content)
                        
                        print(f"Added health endpoint to {main_py_path}")
                        return True
            
            # If we couldn't find a good place, append it to the end
            health_endpoint = """

@app.get("/api/health")
async def health_check():
    \"\"\"Health check endpoint for service monitoring\"\"\"
    return {"status": "ok", "message": "Service is healthy"}
"""
            new_content = content + health_endpoint
            
            # Write the updated content
            with open(main_py_path, 'w') as f:
                f.write(new_content)
            
            print(f"Added health endpoint to the end of {main_py_path}")
            return True
    except Exception as e:
        print(f"Error adding health endpoint: {e}")
        return False

def main():
    """Main function"""
    print("\n===== ADDING HEALTH ENDPOINT TO MAIN.PY =====\n")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Find main.py
    main_py_path = find_main_py_file(script_dir)
    
    if main_py_path:
        print(f"Found main.py at {main_py_path}")
        fixed = add_health_endpoint(main_py_path)
        
        if fixed:
            print("\n✅ Successfully added health endpoint to main.py")
            print("\nPlease restart your backend server to apply the changes")
        else:
            print("\n❌ Failed to add health endpoint to main.py")
    else:
        print("❌ Could not find main.py file")
        print("Please provide the full path to main.py:")
        custom_path = input("> ")
        
        if os.path.exists(custom_path):
            fixed = add_health_endpoint(custom_path)
            
            if fixed:
                print("\n✅ Successfully added health endpoint to main.py")
                print("\nPlease restart your backend server to apply the changes")
            else:
                print("\n❌ Failed to add health endpoint to main.py")
        else:
            print(f"❌ File not found: {custom_path}")

if __name__ == "__main__":
    main()
