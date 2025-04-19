#!/usr/bin/env python
"""
Fix system connectivity issues for GenAI Agent 3D
This script diagnoses and resolves backend connectivity problems.
"""
import os
import sys
import subprocess
import platform
import time
import json
import socket
import requests
from urllib.parse import urljoin
import signal

# Constants
BACKEND_URL = "http://localhost:8000"
REDIS_PORT = 6379
OLLAMA_PORT = 11434

def check_port(host, port):
    """Check if a port is open on the specified host"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except:
            return False

def check_backend_api():
    """Check if the backend API is responsive"""
    try:
        response = requests.get(urljoin(BACKEND_URL, "/api/health"), timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, {"status": "error", "message": f"API returned status code {response.status_code}"}
    except requests.RequestException as e:
        return False, {"status": "error", "message": str(e)}

def check_redis():
    """Check if Redis is running and responsive"""
    if not check_port("localhost", REDIS_PORT):
        return False, "Redis is not running on port 6379"
    
    try:
        result = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "PONG" in result.stdout:
            return True, "Redis is running and responsive"
        return False, f"Redis is running but not responsive: {result.stdout}"
    except Exception as e:
        return False, f"Error checking Redis: {str(e)}"

def check_ollama():
    """Check if Ollama is running and responsive"""
    if not check_port("localhost", OLLAMA_PORT):
        return False, "Ollama is not running on port 11434"
    
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            return True, f"Ollama is running version {response.json().get('version', 'unknown')}"
        return False, f"Ollama returned status code {response.status_code}"
    except requests.RequestException as e:
        return False, f"Error checking Ollama: {str(e)}"

def start_redis():
    """Start Redis server"""
    print("Starting Redis server...")
    if platform.system() == "Windows":
        process = subprocess.Popen(
            ["redis-server"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            shell=True
        )
    else:
        process = subprocess.Popen(
            ["redis-server"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    
    # Wait for Redis to start
    for i in range(5):
        time.sleep(1)
        if check_port("localhost", REDIS_PORT):
            print("✅ Redis server started successfully")
            return True
    
    print("❌ Failed to start Redis server")
    return False

def start_ollama():
    """Start Ollama server"""
    print("Starting Ollama server...")
    if platform.system() == "Windows":
        process = subprocess.Popen(
            ["ollama", "serve"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            shell=True
        )
    else:
        process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    
    # Wait for Ollama to start
    for i in range(10):
        time.sleep(1)
        if check_port("localhost", OLLAMA_PORT):
            print("✅ Ollama server started successfully")
            return True
    
    print("❌ Failed to start Ollama server")
    return False

def check_dependencies():
    """Check if required Python dependencies are installed"""
    print("Checking for required dependencies...")
    
    # Most critical dependencies
    required_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",  # Required for file uploads
        "redis",
        "websockets"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package} is installed")
        except ImportError:
            print(f"  ❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\nMissing dependencies found: {', '.join(missing)}")
        print("These need to be installed for the backend to work properly.")
        
        if input("Install missing dependencies now? (y/n): ").lower() == 'y':
            for package in missing:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"  ✅ Successfully installed {package}")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ Failed to install {package}: {e}")
                    return False
            print("✅ All dependencies installed successfully")
            return True
        else:
            print("Dependency installation skipped")
            return False
    
    return True

def start_backend_server():
    """Start the backend server"""
    print("Starting backend server...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "web", "backend")
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found at: {backend_dir}")
        return False
    
    # Check for dependencies first
    if not check_dependencies():
        print("⚠️ Dependency check failed. Backend may not start correctly.")
    
    # Start the backend server
    if platform.system() == "Windows":
        process = subprocess.Popen(
            [sys.executable, "run_server.py"],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        process = subprocess.Popen(
            [sys.executable, "run_server.py"],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    
    # Wait for backend to start
    for i in range(10):
        time.sleep(1)
        print(f"Waiting for backend server to start... ({i+1}/10)")
        if check_port("localhost", 8000):
            print("✅ Backend server started successfully")
            return True
    
    print("❌ Failed to start backend server")
    return False

def restart_backend_server():
    """Restart the backend server"""
    print("Restarting backend server...")
    
    # On Windows
    if platform.system() == "Windows":
        # Kill existing processes on port 8000
        try:
            result = subprocess.run(
                ["netstat", "-ano", "|", "findstr", ":8000"],
                capture_output=True,
                text=True,
                shell=True
            )
            
            for line in result.stdout.splitlines():
                if "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    try:
                        subprocess.run(["taskkill", "/F", "/PID", pid], check=False)
                        print(f"Killed process with PID: {pid}")
                    except:
                        pass
        except:
            pass
    else:
        # On Unix systems
        try:
            result = subprocess.run(
                ["lsof", "-i", ":8000", "-t"],
                capture_output=True,
                text=True
            )
            
            for pid in result.stdout.splitlines():
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"Killed process with PID: {pid}")
                except:
                    pass
        except:
            pass
    
    # Wait for port to be released
    time.sleep(2)
    
    # Start the backend server
    return start_backend_server()

def main():
    """Main function to fix system connectivity"""
    print("\n" + "="*80)
    print(" GenAI Agent 3D System Connectivity Diagnostics ".center(80, "="))
    print("="*80 + "\n")
    
    # Check Redis
    print("\n[1/3] Checking Redis status...")
    redis_ok, redis_msg = check_redis()
    print(f"Redis status: {'✅ OK' if redis_ok else '❌ ERROR'}")
    print(f"  {redis_msg}")
    
    if not redis_ok:
        if input("\nRedis is not running or not responsive. Start it? (y/n): ").lower() == 'y':
            redis_ok = start_redis()
    
    # Check Ollama
    print("\n[2/3] Checking Ollama status...")
    ollama_ok, ollama_msg = check_ollama()
    print(f"Ollama status: {'✅ OK' if ollama_ok else '❌ ERROR'}")
    print(f"  {ollama_msg}")
    
    if not ollama_ok:
        if input("\nOllama is not running or not responsive. Start it? (y/n): ").lower() == 'y':
            ollama_ok = start_ollama()
    
    # Check Backend API
    print("\n[3/3] Checking Backend API status...")
    api_ok, api_data = check_backend_api()
    print(f"Backend API status: {'✅ OK' if api_ok else '❌ ERROR'}")
    print(f"  {json.dumps(api_data, indent=2) if isinstance(api_data, dict) else api_data}")
    
    if not api_ok:
        if input("\nBackend API is not running or not responsive. Start/restart it? (y/n): ").lower() == 'y':
            api_ok = restart_backend_server()
    
    # Summary
    print("\n" + "="*80)
    print(" System Status Summary ".center(80, "="))
    print("="*80)
    
    print(f"\nRedis:      {'✅ RUNNING' if redis_ok else '❌ NOT RUNNING'}")
    print(f"Ollama:     {'✅ RUNNING' if ollama_ok else '❌ NOT RUNNING'}")
    print(f"Backend:    {'✅ RUNNING' if api_ok else '❌ NOT RUNNING'}")
    
    # Check if frontend needs reloading
    if redis_ok and ollama_ok and api_ok:
        print("\nAll systems are running! 🎉")
        print("\nPlease refresh your browser to reconnect the GenAI Agent 3D frontend.")
    else:
        print("\n⚠️ Some systems are still not running.")
        print("Please fix the issues above before using GenAI Agent 3D.")
    
    print("\n" + "="*80)
    
    # Return status
    return 0 if redis_ok and ollama_ok and api_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDiagnostics interrupted by user.")
        sys.exit(130)
