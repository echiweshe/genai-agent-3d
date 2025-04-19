#!/usr/bin/env python
"""
Start all required services for GenAI Agent 3D
This script checks dependencies, then starts Redis, Ollama, and the backend server
"""
import os
import sys
import subprocess
import platform
import time
import signal
import shutil

# Import the dependency and connectivity checking code
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_system_connectivity import (
    check_port, check_redis, check_ollama, start_redis, 
    start_ollama, start_backend_server, check_dependencies
)

def start_frontend_server():
    """Start the frontend development server"""
    print("\n\n" + "="*80)
    print(" Starting Frontend Development Server ".center(80, "="))
    print("="*80 + "\n")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_dir, "web", "frontend")
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Frontend directory not found at: {frontend_dir}")
        return False
    
    # Check if port 3000 is already in use
    if check_port("localhost", 3000):
        print("⚠️ Port 3000 is already in use. Frontend server might already be running.")
        
        if input("Would you like to open the GenAI Agent 3D in your browser? (y/n): ").lower() == 'y':
            url = "http://localhost:3000"
            # Open browser based on platform
            if platform.system() == 'Windows':
                os.system(f'start {url}')
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open {url}')
            else:  # Linux
                os.system(f'xdg-open {url}')
            
            return True
        return False
    
    # Find npm or yarn
    npm_cmd = None
    if shutil.which("npm"):
        npm_cmd = "npm"
    elif shutil.which("yarn"):
        npm_cmd = "yarn"
    else:
        print("❌ Neither npm nor yarn found. Cannot start frontend server.")
        return False
    
    # Start the frontend server
    print(f"Starting frontend server using {npm_cmd}...")
    
    if platform.system() == "Windows":
        npm_cmd = f"{npm_cmd}.cmd"  # Use .cmd extension on Windows
        process = subprocess.Popen(
            [npm_cmd, "start"],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        process = subprocess.Popen(
            [npm_cmd, "start"],
            cwd=frontend_dir,
            start_new_session=True
        )
    
    # Wait for frontend to start
    for i in range(20):  # Frontend can take longer to start
        time.sleep(1)
        print(f"Waiting for frontend server to start... ({i+1}/20)")
        if check_port("localhost", 3000):
            print("✅ Frontend server started successfully")
            
            # Open in browser
            url = "http://localhost:3000"
            print(f"Opening {url} in your browser...")
            
            # Open browser based on platform
            if platform.system() == 'Windows':
                os.system(f'start {url}')
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open {url}')
            else:  # Linux
                os.system(f'xdg-open {url}')
            
            return True
    
    print("❌ Failed to start frontend server")
    return False

def main():
    """Start all services"""
    print("\n" + "="*80)
    print(" GenAI Agent 3D - Start All Services ".center(80, "="))
    print("="*80 + "\n")
    
    # Check dependencies first
    print("Checking dependencies...")
    if not check_dependencies():
        if input("Some dependencies are missing. Continue anyway? (y/n): ").lower() != 'y':
            return 1
    
    # Check Redis
    redis_ok, _ = check_redis()
    if not redis_ok:
        print("Redis is not running. Starting it...")
        redis_ok = start_redis()
        if not redis_ok:
            print("❌ Failed to start Redis. Aborting.")
            return 1
    else:
        print("✅ Redis is already running")
    
    # Check Ollama
    ollama_ok, _ = check_ollama()
    if not ollama_ok:
        print("Ollama is not running. Starting it...")
        ollama_ok = start_ollama()
        if not ollama_ok:
            print("❌ Failed to start Ollama. Aborting.")
            return 1
    else:
        print("✅ Ollama is already running")
    
    # Start backend server
    if check_port("localhost", 8000):
        print("✅ Backend server is already running on port 8000")
        backend_ok = True
    else:
        print("Starting backend server...")
        backend_ok = start_backend_server()
        if not backend_ok:
            print("❌ Failed to start backend server. Aborting.")
            return 1
    
    # Ask if user wants to start frontend server
    if input("\nWould you like to start the frontend development server? (y/n): ").lower() == 'y':
        frontend_ok = start_frontend_server()
    else:
        print("\nSkipping frontend server startup.")
        frontend_ok = True
    
    # Final status
    print("\n" + "="*80)
    print(" Service Status Summary ".center(80, "="))
    print("="*80)
    
    print(f"\nRedis:      {'✅ RUNNING' if redis_ok else '❌ NOT RUNNING'}")
    print(f"Ollama:     {'✅ RUNNING' if ollama_ok else '❌ NOT RUNNING'}")
    print(f"Backend:    {'✅ RUNNING' if backend_ok else '❌ NOT RUNNING'}")
    print(f"Frontend:   {'✅ RUNNING or SKIPPED' if frontend_ok else '❌ NOT RUNNING'}")
    
    if redis_ok and ollama_ok and backend_ok and frontend_ok:
        print("\nAll services are running! 🎉")
        print("\nYou can access GenAI Agent 3D at: http://localhost:3000")
    else:
        print("\n⚠️ Some services are not running.")
        print("Please check the logs above for errors.")
    
    print("\n" + "="*80)
    
    return 0 if redis_ok and ollama_ok and backend_ok and frontend_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nStartup interrupted by user.")
        sys.exit(130)
