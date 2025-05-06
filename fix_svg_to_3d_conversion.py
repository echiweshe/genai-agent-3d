"""
Fix script for SVG to 3D conversion

This script improves the SVG to 3D conversion by implementing a simpler, more robust
Blender script for converting SVG files to 3D models.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define file paths
project_dir = os.path.abspath(os.path.dirname(__file__))
svg_to_3d_module_path = os.path.join(project_dir, "genai_agent_project", "genai_agent", "svg_to_video", "svg_to_3d")
svg_to_3d_py_path = os.path.join(svg_to_3d_module_path, "svg_to_3d.py")

# Backup original files
def backup_files():
    """Create backups of original files."""
    logger.info("Creating backups of original files...")
    
    if os.path.exists(svg_to_3d_py_path):
        backup_path = f"{svg_to_3d_py_path}.bak"
        shutil.copy2(svg_to_3d_py_path, backup_path)
        logger.info(f"Backed up {svg_to_3d_py_path} to {backup_path}")
    
    logger.info("Backups created successfully")

# Improved SVG to 3D conversion script
improved_svg_to_3d_script = """﻿\"""
SVG to 3D conversion functions.

This module provides the core functionality to convert SVG files to 3D models.
\"""

import os
import logging
import subprocess
import tempfile
import shutil
import sys
from pathlib import Path

try:
    import mathutils
except ImportError:
    # If mathutils is not available, try to use the stub module
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    try:
        import mathutils
    except ImportError:
        pass
    finally:
        if script_dir in sys.path:
            sys.path.remove(script_dir)

# Configure logging
logger = logging.getLogger(__name__)

def get_blender_path():
    \"""Get the path to the Blender executable.\"""
    # Try to get the path from environment variable
    import os
    blender_path = os.environ.get("BLENDER_PATH")
    
    if blender_path and os.path.exists(blender_path):
        return blender_path
    
    # Default paths to check
    default_paths = [
        r"C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        r"C:\\Program Files\\Blender Foundation\\Blender 4.1\\blender.exe",
        r"C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
        r"C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
        r"C:\\Program Files\\Blender Foundation\\Blender 3.5\\blender.exe",
        r"C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
        r"/usr/bin/blender",
        r"/Applications/Blender.app/Contents/MacOS/Blender"
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    logger.error("Blender executable not found. Please set BLENDER_PATH environment variable.")
    return None

def convert_svg_to_3d(svg_path, output_file=None, extrude_height=10.0, scale_factor=1.0, **kwargs):
    \"""
    Convert an SVG file to a 3D model using a simpler, more reliable approach.
    
    Args:
        svg_path (str): Path to the input SVG file
        output_file (str, optional): Path to save the output 3D model
        extrude_height (float, optional): Height of extrusion in Blender units
        scale_factor (float, optional): Scale factor for the model
        **kwargs: Additional parameters for the conversion
    
    Returns:
        str: Path to the output 3D model, or None if conversion failed
    \"""
    logger.info(f"Converting SVG to 3D: {svg_path}")
    
    # Handle output file path
    if output_file is None:
        # Generate output file name based on input file
        svg_file_name = os.path.basename(svg_path)
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "output", "models")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{os.path.splitext(svg_file_name)[0]}.obj")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Get Blender executable path
    blender_path = kwargs.get('blender_path') or get_blender_path()
    if not blender_path:
        logger.error("Blender path not found. Cannot convert SVG to 3D.")
        return None
    
    # Validate SVG file
    if not os.path.exists(svg_path):
        logger.error(f"SVG file not found: {svg_path}")
        return None
    
    # Create a simplified Python script for Blender to execute
    script_content = f'''
import bpy
import os
import sys
import traceback

# Function to log messages
def log(message):
    print(f"SVG_TO_3D: {message}")

# Clean the scene
log("Cleaning scene...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import SVG
log("Importing SVG file: {svg_path}")
try:
    # Ensure we're in Object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    # Import SVG
    bpy.ops.import_curve.svg(filepath=r"{svg_path}")
    log("SVG import successful")
    
    # Check if any objects were imported
    curves = [obj for obj in bpy.context.scene.objects if obj.type == 'CURVE']
    if not curves:
        log("No curve objects imported from SVG")
        sys.exit(1)
    
    # Select all curve objects and join them if multiple
    for obj in curves:
        obj.select_set(True)
    
    # Set active object
    if curves:
        bpy.context.view_layer.objects.active = curves[0]
    
    # Join curves if there are multiple
    if len(curves) > 1:
        log(f"Joining {{len(curves)}} curves...")
        bpy.ops.object.join()
    
    # Get the active object (joined curves)
    obj = bpy.context.active_object
    
    # Set curve properties for extrusion
    log("Setting curve properties for extrusion...")
    if hasattr(obj, 'data') and obj.data:
        obj.data.dimensions = '2D'
        obj.data.fill_mode = 'BOTH'
        obj.data.bevel_depth = 0
        obj.data.extrude = {extrude_height}
        log(f"Extrusion height set to {extrude_height}")
    
    # Apply scale
    obj.scale = ({scale_factor}, {scale_factor}, {scale_factor})
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    log(f"Applied scale factor: {scale_factor}")
    
    # Center the model
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    log("Centered model at origin")
    
    # Convert curves to mesh for export
    log("Converting curves to mesh...")
    bpy.ops.object.convert(target='MESH')
    
    # Export as OBJ
    log(f"Exporting as OBJ: {output_file}")
    output_dir = os.path.dirname(r"{output_file}")
    os.makedirs(output_dir, exist_ok=True)
    
    bpy.ops.export_scene.obj(
        filepath=r"{output_file}",
        check_existing=False,
        use_selection=True,
        use_materials=True,
        use_triangles=True,
        axis_forward='-Z',
        axis_up='Y'
    )
    
    log(f"Export successful: {output_file}")
    
except Exception as e:
    log(f"Error in Blender script: {{str(e)}}")
    traceback.print_exc()
    sys.exit(1)
'''
    
    # Create temporary script file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
        temp_script.write(script_content)
        temp_script_path = temp_script.name
    
    try:
        # Run Blender with the script
        cmd = [
            blender_path,
            '--background',
            '--python', temp_script_path
        ]
        
        logger.info(f"Running Blender command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        # Log detailed output
        for line in stdout.splitlines():
            if "SVG_TO_3D:" in line:
                logger.info(line)
            elif "Error" in line or "ERROR" in line:
                logger.error(line)
        
        if process.returncode != 0:
            logger.error(f"Blender process failed with code {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        # Check if output file was created
        if os.path.exists(output_file):
            logger.info(f"SVG to 3D conversion successful: {output_file}")
            
            # Copy to SVG to Video models directory for compatibility
            svg_to_video_models_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
                "output", "svg_to_video", "models"
            )
            os.makedirs(svg_to_video_models_dir, exist_ok=True)
            svg_to_video_output = os.path.join(svg_to_video_models_dir, os.path.basename(output_file))
            shutil.copy2(output_file, svg_to_video_output)
            logger.info(f"Copied model to SVG to Video directory: {svg_to_video_output}")
            
            return output_file
        else:
            logger.error(f"Output file not created: {output_file}")
            return None
    
    except Exception as e:
        logger.error(f"Error running Blender process: {str(e)}")
        return None
    
    finally:
        # Clean up temporary script
        try:
            os.unlink(temp_script_path)
        except:
            pass

def get_supported_formats():
    \"""Get a list of supported output formats for SVG to 3D conversion.\"""
    return ['obj', 'stl', 'fbx', 'glb', 'gltf', 'x3d']

def get_conversion_options():
    \"""Get the available options for SVG to 3D conversion.\"""
    return {
        'extrude_height': {
            'type': 'float',
            'default': 10.0,
            'description': 'Height of extrusion in Blender units'
        },
        'scale_factor': {
            'type': 'float',
            'default': 1.0,
            'description': 'Scale factor for the model'
        },
        'format': {
            'type': 'enum',
            'values': get_supported_formats(),
            'default': 'obj',
            'description': 'Output format'
        }
    }

if __name__ == "__main__":
    # Simple test for the module
    import sys
    if len(sys.argv) > 1:
        svg_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = convert_svg_to_3d(svg_path, output_path)
        print(f"Conversion result: {result}")
    else:
        print("Usage: python svg_to_3d.py input.svg [output.obj]")
"""

# Update the SVG to 3D module
def update_svg_to_3d_module():
    """Update the SVG to 3D module with improved implementation."""
    logger.info("Updating SVG to 3D module with improved implementation...")
    
    with open(svg_to_3d_py_path, 'w') as f:
        f.write(improved_svg_to_3d_script)
    
    logger.info(f"Updated {svg_to_3d_py_path} with improved implementation")

# Main function
def main():
    """Main function to fix SVG to 3D conversion."""
    logger.info("Starting SVG to 3D conversion fix script...")
    
    # Create backups
    backup_files()
    
    # Update SVG to 3D module
    update_svg_to_3d_module()
    
    # Create required directories
    os.makedirs(os.path.join(project_dir, "output", "models"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "output", "svg_to_video", "models"), exist_ok=True)
    
    logger.info("SVG to 3D conversion fix completed successfully!")
    logger.info("Please restart the backend service to apply changes.")

if __name__ == "__main__":
    main()
