"""
Script to open a 3D model in Blender.
This script is used by the SVG to Video pipeline to open generated 3D models in Blender.
"""
import os
import sys
import subprocess
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_blender_path():
    """Get the path to the Blender executable."""
    # Try to get the path from environment variable
    blender_path = os.environ.get("BLENDER_PATH")
    
    if blender_path and os.path.exists(blender_path):
        return blender_path
    
    # Default paths to check
    default_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        r"/usr/bin/blender",
        r"/Applications/Blender.app/Contents/MacOS/Blender"
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    logger.error("Blender executable not found. Please set BLENDER_PATH environment variable.")
    return None

def open_model_in_blender(model_path, new_instance=True):
    """
    Open a 3D model in Blender.
    
    Args:
        model_path (str): Path to the 3D model file
        new_instance (bool): Whether to open a new instance of Blender
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return False
    
    blender_path = get_blender_path()
    if not blender_path:
        logger.error("Blender path not found.")
        return False
    
    model_path = os.path.abspath(model_path)
    
    # Check the file extension
    _, ext = os.path.splitext(model_path)
    ext = ext.lower()
    
    supported_formats = ['.obj', '.fbx', '.stl', '.glb', '.gltf', '.x3d', '.blend']
    if ext not in supported_formats:
        logger.error(f"Unsupported model format: {ext}. Supported formats: {', '.join(supported_formats)}")
        return False
    
    # Create a temporary script to import the model in Blender
    if ext != '.blend':  # If it's not a Blender file, we need to import it
        script_content = f"""
import bpy
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the model
model_path = r"{model_path}"
if model_path.lower().endswith('.obj'):
    bpy.ops.import_scene.obj(filepath=model_path)
elif model_path.lower().endswith('.fbx'):
    bpy.ops.import_scene.fbx(filepath=model_path)
elif model_path.lower().endswith('.stl'):
    bpy.ops.import_mesh.stl(filepath=model_path)
elif model_path.lower().endswith('.glb') or model_path.lower().endswith('.gltf'):
    bpy.ops.import_scene.gltf(filepath=model_path)
elif model_path.lower().endswith('.x3d'):
    bpy.ops.import_scene.x3d(filepath=model_path)

# Select all imported objects
bpy.ops.object.select_all(action='SELECT')

# Zoom view to selected objects
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        override = bpy.context.copy()
        override['area'] = area
        bpy.ops.view3d.view_selected(override)
        break
        
print(f"Model imported: {model_path}")
"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
            temp_script.write(script_content)
            temp_script_path = temp_script.name
        
        # Command to run Blender with the script
        cmd = [
            blender_path,
            '--python', temp_script_path,
        ]
        
        # If not opening a new instance, add the appropriate flag
        if not new_instance:
            cmd.append('--background')
    else:
        # For .blend files, simply open them directly
        cmd = [blender_path, model_path]
    
    logger.info(f"Running Blender command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(cmd)
        logger.info(f"Blender process started with PID: {process.pid}")
        return True
    except Exception as e:
        logger.error(f"Error running Blender process: {str(e)}")
        return False

def main():
    """Main function to open a model in Blender from command line."""
    parser = argparse.ArgumentParser(description='Open a 3D model in Blender')
    parser.add_argument('model_path', help='Path to the 3D model file')
    parser.add_argument('--new-instance', action='store_true', help='Open in a new Blender instance')
    
    args = parser.parse_args()
    
    success = open_model_in_blender(args.model_path, args.new_instance)
    if success:
        logger.info("Model opened successfully in Blender")
    else:
        logger.error("Failed to open model in Blender")
        sys.exit(1)

if __name__ == "__main__":
    main()
