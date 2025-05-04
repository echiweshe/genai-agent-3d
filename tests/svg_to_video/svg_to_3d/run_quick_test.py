#!/usr/bin/env python3
"""
Run quick test with Blender
This script should be run with regular Python to launch Blender with the test script
"""

import os
import sys
import subprocess
import platform

def find_blender():
    """Find Blender executable on the system"""
    system = platform.system()
    blender_paths = []
    
    if system == "Windows":
        # Common Windows paths
        program_files = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ]
        
        for pf in program_files:
            if pf:
                blender_paths.extend([
                    os.path.join(pf, "Blender Foundation", "Blender", "blender.exe"),
                    os.path.join(pf, "Blender Foundation", "Blender 3.6", "blender.exe"),
                    os.path.join(pf, "Blender Foundation", "Blender 4.0", "blender.exe"),
                    os.path.join(pf, "Blender Foundation", "Blender 4.1", "blender.exe"),
                ])
    
    # Check if blender is in PATH
    import shutil
    blender_in_path = shutil.which("blender")
    if blender_in_path:
        return blender_in_path
    
    # Check common locations
    for path in blender_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    # Find Blender
    blender_path = find_blender()
    if not blender_path:
        print("ERROR: Could not find Blender installation")
        print("Please install Blender or add it to your PATH")
        sys.exit(1)
    
    print(f"Found Blender at: {blender_path}")
    
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_script = os.path.join(current_dir, "quick_test_blender.py")
    
    # Run the test with Blender
    cmd = [blender_path, "--background", "--python", test_script]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
