#!/usr/bin/env python
"""
Direct Health Endpoint Fix for GenAI Agent 3D
This script adds a health endpoint to the backend server
"""

import os
import sys

# Define the path to main.py
MAIN_PY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "backend", "main.py")

def add_health_endpoint():
    """Add a health endpoint to main.py"""
    if not os.path.exists(MAIN_PY_PATH):
        print(f"Error: Could not find main.py at {MAIN_PY_PATH}")
        return False
    
    print(f"Found main.py at {MAIN_PY_PATH}")
    
    # Create backup
    backup_path = MAIN_PY_PATH + '.health_backup'
    with open(MAIN_PY_PATH, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup at {backup_path}")
    
    # Check if health endpoint already exists
    if "@app.get('/api/health')" in content or '@app.get("/api/health")' in content:
        print("Health endpoint already exists")
        return True
    
    # Add the health endpoint
    health_endpoint = '''
@app.get("/api/health")
async def health_check():
    """Health check endpoint for service monitoring"""
    return {"status": "ok", "message": "Service is healthy"}
'''
    
    # Append to the end of the file
    with open(MAIN_PY_PATH, 'a') as f:
        f.write("\n" + health_endpoint)
    
    print("Added health endpoint to main.py")
    return True

if __name__ == "__main__":
    print("\n===== ADDING HEALTH ENDPOINT TO MAIN.PY =====\n")
    
    success = add_health_endpoint()
    
    if success:
        print("\n✅ Successfully added health endpoint to main.py")
        print("\nPlease restart your backend server using:")
        print("python manage_services.py restart backend")
    else:
        print("\n❌ Failed to add health endpoint to main.py")
        print("\nPlease try adding it manually:")
        print("\n@app.get(\"/api/health\")")
        print("async def health_check():")
        print("    \"\"\"Health check endpoint for service monitoring\"\"\"")
        print("    return {\"status\": \"ok\", \"message\": \"Service is healthy\"}")
