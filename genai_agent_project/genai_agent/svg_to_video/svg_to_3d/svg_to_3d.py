"""
SVG to 3D conversion functions.

This module provides the core functionality to convert SVG files to 3D models.
"""

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
    """Get the path to the Blender executable."""
    # Try to get the path from environment variable
    import os
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

def convert_svg_to_3d(svg_path, output_file=None, extrude_height=10.0, scale_factor=1.0, **kwargs):
    """
    Convert an SVG file to a 3D model.
    
    Args:
        svg_path (str): Path to the input SVG file
        output_file (str, optional): Path to save the output 3D model
        extrude_height (float, optional): Height of extrusion in Blender units
        scale_factor (float, optional): Scale factor for the model
        **kwargs: Additional parameters for the conversion
            - format (str): Output format (default is 'obj')
            - thickness (float): Thickness of the extrusion
            - resolution (int): Resolution of the curve
            - bevel_depth (float): Depth of the bevel
            - bevel_resolution (int): Resolution of the bevel
            - material (str): Material to apply to the model
            - color (tuple): Color of the model in RGB format (0.0-1.0)
            - transparency (bool): Enable transparency
    
    Returns:
        str: Path to the output 3D model, or None if conversion failed
    """
    logger.info(f"Converting SVG to 3D: {svg_path}")
    
    # Get Blender executable path
    blender_path = get_blender_path()
    if not blender_path:
        logger.error("Blender path not found. Cannot convert SVG to 3D.")
        return None
    
    # Validate SVG file
    if not os.path.exists(svg_path):
        logger.error(f"SVG file not found: {svg_path}")
        return None
    
    # Handle output file path
    if output_file is None:
        # Generate output file name based on input file
        svg_file_name = os.path.basename(svg_path)
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "output", "models")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{os.path.splitext(svg_file_name)[0]}.obj")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Get format from output file extension or kwargs
    format = kwargs.get('format', os.path.splitext(output_file)[1][1:] if output_file else 'obj')
    
    # Create a temporary Python script for Blender to execute
    script_content = f'''
import bpy
import os
import sys
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import SVG
bpy.ops.import_curve.svg(filepath=r"{svg_path}")

# Select all curve objects
curves = [obj for obj in bpy.context.scene.objects if obj.type == 'CURVE']
if not curves:
    print("No curves imported from SVG")
    sys.exit(1)

for obj in curves:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Set curve properties
    if obj.type == 'CURVE':
        obj.data.dimensions = '2D'
        obj.data.resolution_u = {kwargs.get('resolution', 12)}
        obj.data.bevel_depth = {kwargs.get('bevel_depth', 0.0)}
        obj.data.bevel_resolution = {kwargs.get('bevel_resolution', 0)}
        obj.data.extrude = {extrude_height}

        # Apply material if specified
        if {bool(kwargs.get('material', False))}:
            mat_name = "{kwargs.get('material', 'SVGMaterial')}"
            if mat_name not in bpy.data.materials:
                mat = bpy.data.materials.new(name=mat_name)
                mat.use_nodes = True
            else:
                mat = bpy.data.materials[mat_name]
            
            if not obj.data.materials:
                obj.data.materials.append(mat)
            
            # Set color if specified
            if {bool(kwargs.get('color', False))}:
                color = {kwargs.get('color', (0.8, 0.8, 0.8))}
                principled = mat.node_tree.nodes.get('Principled BSDF')
                if principled:
                    principled.inputs['Base Color'].default_value = color + (1.0,)
            
            # Set transparency if specified
            if {kwargs.get('transparency', False)}:
                mat.blend_method = 'BLEND'
                principled = mat.node_tree.nodes.get('Principled BSDF')
                if principled:
                    principled.inputs['Alpha'].default_value = 0.5

# Convert to mesh
for obj in curves:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target='MESH')

# Join all objects into one
if len(bpy.context.selected_objects) > 1:
    bpy.ops.object.join()

# Scale the model
obj = bpy.context.active_object
obj.scale = ({scale_factor}, {scale_factor}, {scale_factor})
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Center the model
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
obj.location = (0, 0, 0)

# Export as specified format
output_file = r"{output_file}"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

if output_file.lower().endswith('.obj'):
    bpy.ops.export_scene.obj(filepath=output_file, use_selection=True)
elif output_file.lower().endswith('.stl'):
    bpy.ops.export_mesh.stl(filepath=output_file, use_selection=True)
elif output_file.lower().endswith('.fbx'):
    bpy.ops.export_scene.fbx(filepath=output_file, use_selection=True)
elif output_file.lower().endswith('.glb') or output_file.lower().endswith('.gltf'):
    bpy.ops.export_scene.gltf(filepath=output_file, use_selection=True)
elif output_file.lower().endswith('.x3d'):
    bpy.ops.export_scene.x3d(filepath=output_file, use_selection=True)
else:
    print(f"Unsupported output format: {{os.path.splitext(output_file)[1]}}")
    sys.exit(1)

print(f"SVG to 3D conversion complete: {{output_file}}")
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
        
        if process.returncode != 0:
            logger.error(f"Blender process failed with code {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        # Check if output file was created
        if os.path.exists(output_file):
            logger.info(f"SVG to 3D conversion successful: {output_file}")
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
    """Get a list of supported output formats for SVG to 3D conversion."""
    return ['obj', 'stl', 'fbx', 'glb', 'gltf', 'x3d']

def get_conversion_options():
    """Get the available options for SVG to 3D conversion."""
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
        },
        'resolution': {
            'type': 'int',
            'default': 12,
            'description': 'Resolution of the curve'
        },
        'bevel_depth': {
            'type': 'float',
            'default': 0.0,
            'description': 'Depth of the bevel'
        },
        'bevel_resolution': {
            'type': 'int',
            'default': 0,
            'description': 'Resolution of the bevel'
        },
        'material': {
            'type': 'string',
            'default': 'SVGMaterial',
            'description': 'Material to apply to the model'
        },
        'color': {
            'type': 'color',
            'default': (0.8, 0.8, 0.8),
            'description': 'Color of the model in RGB format (0.0-1.0)'
        },
        'transparency': {
            'type': 'bool',
            'default': False,
            'description': 'Enable transparency'
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
