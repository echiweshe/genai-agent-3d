#!/usr/bin/env python3
"""
Cross-platform test runner for SVG to 3D converter

This script automatically finds Blender and runs the tests.
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
from pathlib import Path

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
                    os.path.join(pf, "Blender Foundation", "Blender"),
                    os.path.join(pf, "Blender Foundation", "Blender 3.6"),
                    os.path.join(pf, "Blender Foundation", "Blender 4.0"),
                    os.path.join(pf, "Blender Foundation", "Blender 4.1"),
                ])
        
        # Add potential Steam paths
        steam_path = os.path.expandvars(r"%ProgramFiles(x86)%\Steam\steamapps\common\Blender")
        if os.path.exists(steam_path):
            blender_paths.append(steam_path)
            
    elif system == "Darwin":  # macOS
        blender_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/Applications/Blender 3.6.app/Contents/MacOS/Blender",
            "/Applications/Blender 4.0.app/Contents/MacOS/Blender",
            os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender"),
        ]
    else:  # Linux
        blender_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            os.path.expanduser("~/blender/blender"),
            "/opt/blender/blender",
        ]
    
    # Check for blender in PATH
    blender_in_path = shutil.which("blender")
    if blender_in_path:
        return blender_in_path
    
    # Check common locations
    for path in blender_paths:
        if system == "Windows":
            # On Windows, look for blender.exe in the directory
            blender_exe = os.path.join(path, "blender.exe")
            if os.path.exists(blender_exe):
                return blender_exe
        else:
            # On Unix systems, check if the file exists and is executable
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
    
    return None

def run_blender_script(blender_path, script_path, args=None, background=True):
    """Run a Python script with Blender"""
    cmd = [blender_path]
    
    if background:
        cmd.append("--background")
    
    cmd.extend(["--python", script_path])
    
    if args:
        cmd.append("--")
        cmd.extend(args)
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running Blender script: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run SVG to 3D converter tests")
    parser.add_argument("--test", choices=["basic", "debug", "batch", "visual"], 
                       default="basic", help="Which test to run")
    parser.add_argument("--blender", help="Path to Blender executable")
    parser.add_argument("--no-background", action="store_true", 
                       help="Run Blender with GUI (for visual tests)")
    
    args = parser.parse_args()
    
    # Find Blender
    blender_path = args.blender or find_blender()
    
    if not blender_path:
        print("ERROR: Could not find Blender installation")
        print("Please install Blender or specify the path with --blender")
        sys.exit(1)
    
    print(f"Using Blender: {blender_path}")
    
    # Determine which test to run
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    test_scripts = {
        "basic": os.path.join(script_dir, "test_converter.py"),
        "debug": os.path.join(script_dir, "debug_converter.py"),
        "batch": os.path.join(script_dir, "batch_test.py"),
        "visual": os.path.join(script_dir, "visual_test.py"),
    }
    
    test_script = test_scripts[args.test]
    
    # Run the test
    background = not args.no_background and args.test != "visual"
    success = run_blender_script(blender_path, test_script, background=background)
    
    if success:
        print(f"\n{args.test.upper()} TEST COMPLETED SUCCESSFULLY")
    else:
        print(f"\n{args.test.upper()} TEST FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
