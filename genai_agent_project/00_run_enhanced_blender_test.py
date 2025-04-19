#!/usr/bin/env python
"""
Cross-platform script to run the enhanced Blender test with GenAI Agent integration.
Works on Windows, Linux, and macOS.
"""
import os
import sys
import subprocess
import platform
import time
import shutil
import socket
import json

def is_service_running(host, port):
    """Check if a service is running on the specified host and port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            return True
        except:
            return False

def find_blender_executable():
    """Find the Blender executable on the system"""
    system = platform.system()
    
    # Common Blender paths by platform
    if system == "Windows":
        paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
                
    elif system == "Darwin":  # macOS
        paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/Applications/Blender/Blender.app/Contents/MacOS/Blender"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
                
    elif system == "Linux":
        # Try common Linux locations
        paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/snap/bin/blender"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    
    # If not found in common locations, try 'blender' in the PATH
    blender = shutil.which("blender")
    if blender:
        return blender
        
    return None

def ensure_ollama_running():
    """Ensure Ollama is running, start it if necessary"""
    if is_service_running("localhost", 11434):
        print("✅ Ollama is already running")
        return True
        
    print("⚠️ Ollama is not running. Attempting to start it...")
    
    # Start Ollama based on the platform
    system = platform.system()
    try:
        if system == "Windows":
            # On Windows, start in a new process
            subprocess.Popen(["ollama", "serve"], 
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                             shell=True)
        else:
            # On Unix, start in the background
            subprocess.Popen(["ollama", "serve"], 
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, 
                             start_new_session=True)
            
        # Wait for Ollama to start
        for i in range(10):
            print(f"Waiting for Ollama to start... ({i+1}/10)")
            time.sleep(1)
            if is_service_running("localhost", 11434):
                print("✅ Ollama started successfully")
                return True
                
        print("❌ Failed to start Ollama")
        return False
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def ensure_redis_running():
    """Ensure Redis is running, start it if necessary"""
    if is_service_running("localhost", 6379):
        print("✅ Redis is already running")
        return True
        
    print("⚠️ Redis is not running. Attempting to start it...")
    
    # Start Redis based on the platform
    system = platform.system()
    try:
        if system == "Windows":
            # On Windows, start in a new process
            subprocess.Popen(["redis-server"], 
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                             shell=True)
        else:
            # On Unix, start in the background
            subprocess.Popen(["redis-server"],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
            
        # Wait for Redis to start
        for i in range(5):
            print(f"Waiting for Redis to start... ({i+1}/5)")
            time.sleep(1)
            if is_service_running("localhost", 6379):
                print("✅ Redis started successfully")
                return True
                
        print("❌ Failed to start Redis")
        return False
    except Exception as e:
        print(f"❌ Error starting Redis: {e}")
        return False

def run_blender_test(blender_path, script_path):
    """Run the Blender test with the specified script"""
    print(f"\nRunning Blender test with script: {script_path}")
    print(f"Using Blender executable: {blender_path}\n")
    
    try:
        # Run Blender with the script
        process = subprocess.Popen([blender_path, "--python", script_path],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)
        
        # Stream the output in real-time
        for line in process.stdout:
            print(line, end='')
            
        # Wait for process to complete
        process.wait()
        
        if process.returncode == 0:
            print("\n✅ Blender test completed successfully")
            return True
        else:
            print(f"\n❌ Blender test failed with return code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running Blender test: {e}")
        return False

def main():
    """Main function to run the enhanced Blender test"""
    print("\n" + "="*80)
    print(" Running Enhanced Blender Test with GenAI Agent Integration ".center(80, "="))
    print("="*80 + "\n")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    examples_dir = os.path.join(project_dir, "examples")
    script_path = os.path.join(examples_dir, "enhanced_blender_test.py")
    
    # Check if examples directory exists
    if not os.path.exists(examples_dir):
        print(f"❌ Examples directory not found at: {examples_dir}")
        return 1
        
    # Check if script exists
    if not os.path.exists(script_path):
        print(f"❌ Enhanced Blender test script not found at: {script_path}")
        return 1
        
    print(f"Using script: {script_path}")
    
    # Find Blender executable
    blender_path = find_blender_executable()
    if not blender_path:
        print("❌ Could not find Blender executable.")
        print("Please ensure Blender is installed and available in the system PATH")
        return 1
        
    print(f"Found Blender at: {blender_path}")
    
    # Ensure dependencies are running
    ensure_ollama_running()
    ensure_redis_running()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(examples_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Run the Blender test
    success = run_blender_test(blender_path, script_path)
    
    # Check for output files
    if success:
        print("\nChecking for output files...")
        output_files = {
            "Agent Result": os.path.join(output_dir, "agent_result.json"),
            "Blender Code": os.path.join(output_dir, "last_blender_code.py"),
            "Rendered Scene": os.path.join(output_dir, "rendered_scene.png"),
            "Blend File": os.path.join(output_dir, "generated_scene.blend")
        }
        
        for name, path in output_files.items():
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"✅ {name}: {path} ({size} bytes)")
            else:
                print(f"❌ {name} not found at: {path}")
    
    print("\nTest execution complete.")
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(130)
