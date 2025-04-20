#!/usr/bin/env python
"""
Blender Script Executor
This utility reliably executes Blender scripts regardless of their internal structure.
It works by creating a wrapper that properly loads and executes the script content
within Blender's environment.
"""
import os
import sys
import argparse
import subprocess
import tempfile

def create_blender_wrapper(script_path):
    """Create a wrapper script that properly executes a Blender script"""
    # Get absolute path to the script
    abs_script_path = os.path.abspath(script_path)
    
    # Create a temporary wrapper script
    wrapper_content = f"""
import bpy
import sys
import os

# Ensure the script directory is in the path
script_dir = os.path.dirname(r"{abs_script_path}")
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Load and execute the script content
try:
    print(f"\\n{'='*80}")
    print(f"EXECUTING SCRIPT: {abs_script_path}")
    print(f"{'='*80}\\n")
    
    with open(r"{abs_script_path}", 'r') as f:
        script_content = f.read()
    
    # Execute the script in Blender's environment
    exec(script_content)
    
    print(f"\\n{'='*80}")
    print(f"SCRIPT EXECUTION COMPLETED SUCCESSFULLY")
    print(f"{'='*80}\\n")
except Exception as e:
    print(f"\\n{'='*80}")
    print(f"ERROR EXECUTING SCRIPT: {{e}}")
    print(f"{'='*80}\\n")
    raise
"""
    
    # Write wrapper to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(wrapper_content)
        wrapper_path = f.name
    
    return wrapper_path

def find_blender_executable():
    """Find the Blender executable"""
    if sys.platform == "win32":
        # Look for Blender in common Windows locations
        common_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender\blender.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return "blender"  # Hope it's in the PATH
    elif sys.platform == "darwin":  # macOS
        common_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/Applications/Blender/Blender.app/Contents/MacOS/Blender"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return "blender"  # Hope it's in the PATH
    else:  # Linux
        return "blender"  # Use system Blender

def run_blender_script(script_path, blender_path=None, background=True, ui_mode=False):
    """
    Run a Blender script using a wrapper
    
    Args:
        script_path: Path to the script to execute
        blender_path: Path to Blender executable (optional)
        background: Whether to run in background mode (no UI)
        ui_mode: Whether to show the Blender UI (overrides background)
    
    Returns:
        Exit code from Blender
    """
    # Find Blender executable if not specified
    if not blender_path:
        blender_path = find_blender_executable()
    
    # Create wrapper script
    wrapper_path = create_blender_wrapper(script_path)
    
    try:
        # Build Blender command
        cmd = [blender_path]
        if not ui_mode:
            cmd.append("--background")
        cmd.extend(["--python", wrapper_path])
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Run the process and stream output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Stream the output
        for line in process.stdout:
            print(line, end='')
        
        # Wait for completion
        process.wait()
        
        if process.returncode == 0:
            print(f"\nBlender script executed successfully!")
        else:
            print(f"\nBlender script failed with exit code: {process.returncode}")
        
        return process.returncode
    
    finally:
        # Clean up the temporary wrapper
        if os.path.exists(wrapper_path):
            try:
                os.remove(wrapper_path)
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description="Execute Blender scripts reliably")
    parser.add_argument("script", help="Path to the Blender script to execute")
    parser.add_argument("--blender", help="Path to Blender executable (optional)")
    parser.add_argument("--ui", action="store_true", help="Show Blender UI")
    
    args = parser.parse_args()
    
    # Validate script path
    if not os.path.exists(args.script):
        print(f"Error: Script not found: {args.script}")
        return 1
    
    # Execute the script
    exit_code = run_blender_script(
        args.script, 
        args.blender, 
        background=not args.ui,
        ui_mode=args.ui
    )
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
