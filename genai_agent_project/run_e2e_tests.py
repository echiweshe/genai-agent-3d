#!/usr/bin/env python
"""
Run end-to-end tests with proper setup for the GenAI Agent 3D project.

This script:
1. Starts the backend server if not already running
2. Starts the frontend dev server if not already running
3. Runs the Playwright tests
4. Optionally keeps the servers running after tests complete

Usage:
    python run_e2e_tests.py [--keep-servers]
"""
import os
import sys
import time
import argparse
import signal
import subprocess
import platform
import socket
from urllib.request import urlopen
from urllib.error import URLError
import atexit

# Globals to track our servers
backend_process = None
frontend_process = None
started_servers = []

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def url_is_responding(url, timeout=1):
    """Check if a URL is responding"""
    try:
        urlopen(url, timeout=timeout)
        return True
    except URLError:
        return False

def start_backend_server():
    """Start the backend server if not already running"""
    global backend_process
    print("Checking if backend server is running...")
    
    # Check if backend is already running on port 8000
    if is_port_in_use(8000):
        print("Backend server is already running on port 8000.")
        return None
    
    print("Starting backend server...")
    
    # Navigate to the backend directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "web", "backend")
    
    if not os.path.exists(backend_dir):
        print(f"Error: Backend directory not found at {backend_dir}")
        sys.exit(1)
    
    # Start the backend server
    cmd = [sys.executable, "run_server.py", "--test-mode"]
    
    if platform.system() == "Windows":
        # Use CREATE_NEW_PROCESS_GROUP flag on Windows
        backend_process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        backend_process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            preexec_fn=os.setsid
        )
    
    # Wait for backend to start
    print("Waiting for backend server to start...")
    max_attempts = 30
    for attempt in range(max_attempts):
        if is_port_in_use(8000):
            print("Backend server started successfully.")
            started_servers.append("backend")
            return backend_process
        
        time.sleep(1)
        print(f"Waiting for backend server to start ({attempt+1}/{max_attempts})...")
    
    print("Error: Backend server failed to start in time.")
    if backend_process:
        backend_process.terminate()
    return None

def start_frontend_server():
    """Start the frontend server if not already running"""
    global frontend_process
    print("Checking if frontend server is running...")
    
    # Check if frontend is already running on port 3000
    if is_port_in_use(3000) or url_is_responding("http://localhost:3000"):
        print("Frontend server is already running on port 3000.")
        return None
    
    print("Starting frontend server...")
    
    # Navigate to the frontend directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_dir, "web", "frontend")
    
    if not os.path.exists(frontend_dir):
        print(f"Error: Frontend directory not found at {frontend_dir}")
        sys.exit(1)
    
    # Start the frontend server
    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    
    if platform.system() == "Windows":
        # Use CREATE_NEW_PROCESS_GROUP flag on Windows
        frontend_process = subprocess.Popen(
            [npm_cmd, "start"],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        frontend_process = subprocess.Popen(
            [npm_cmd, "start"],
            cwd=frontend_dir,
            preexec_fn=os.setsid
        )
    
    # Wait for frontend to start
    print("Waiting for frontend server to start...")
    max_attempts = 60  # Frontend can take longer to start
    for attempt in range(max_attempts):
        if url_is_responding("http://localhost:3000"):
            print("Frontend server started successfully.")
            started_servers.append("frontend")
            return frontend_process
        
        time.sleep(1)
        print(f"Waiting for frontend server to start ({attempt+1}/{max_attempts})...")
    
    print("Error: Frontend server failed to start in time.")
    if frontend_process:
        frontend_process.terminate()
    return None

def run_e2e_tests():
    """Run the end-to-end tests"""
    print("\n" + "="*80)
    print("=" + " RUNNING END-TO-END TESTS ".center(78, "="))
    print("="*80)
    
    # Navigate to the e2e directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    e2e_dir = os.path.join(project_dir, "web", "e2e")
    
    if not os.path.exists(e2e_dir):
        print(f"Error: E2E directory not found at {e2e_dir}")
        return False
    
    # Set up Playwright if needed
    npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
    
    # Make sure we have the right packages
    if not os.path.exists(os.path.join(e2e_dir, "node_modules", "@playwright")):
        print("Setting up Playwright environment...")
        npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
        
        subprocess.run([npm_cmd, "init", "-y"], cwd=e2e_dir, check=False)
        subprocess.run([npm_cmd, "install", "--save-dev", "@playwright/test"], cwd=e2e_dir, check=False)
        subprocess.run([npx_cmd, "playwright", "install"], cwd=e2e_dir, check=False)
    
    # Run the tests with a single browser to speed things up
    print("Running Playwright tests with Chromium only...")
    cmd = [npx_cmd, "playwright", "test", "--project=chromium"]
    
    process = subprocess.run(cmd, cwd=e2e_dir)
    return process.returncode == 0

def cleanup_servers():
    """Cleanup servers when the script exits"""
    global backend_process, frontend_process, started_servers
    
    if "backend" in started_servers and backend_process:
        print("Stopping backend server...")
        if platform.system() == "Windows":
            os.kill(backend_process.pid, signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
    
    if "frontend" in started_servers and frontend_process:
        print("Stopping frontend server...")
        if platform.system() == "Windows":
            os.kill(frontend_process.pid, signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(frontend_process.pid), signal.SIGTERM)

def main():
    parser = argparse.ArgumentParser(description="Run E2E tests with proper setup")
    parser.add_argument("--keep-servers", action="store_true", help="Keep servers running after tests")
    args = parser.parse_args()
    
    # Register cleanup handler if not keeping servers
    if not args.keep_servers:
        atexit.register(cleanup_servers)
    
    # Start the servers if needed
    backend_ok = start_backend_server() is not None or is_port_in_use(8000)
    frontend_ok = start_frontend_server() is not None or url_is_responding("http://localhost:3000")
    
    if not backend_ok or not frontend_ok:
        print("Error: Failed to start servers. Cannot run E2E tests.")
        sys.exit(1)
    
    # Let servers settle
    print("Waiting 5 seconds for servers to fully initialize...")
    time.sleep(5)
    
    # Run the tests
    tests_ok = run_e2e_tests()
    
    # Keep servers running if requested
    if args.keep_servers:
        print("\nKeeping servers running as requested. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping servers...")
            cleanup_servers()
    
    # Exit with appropriate code
    sys.exit(0 if tests_ok else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        # The atexit handler will take care of cleanup
        sys.exit(130)
