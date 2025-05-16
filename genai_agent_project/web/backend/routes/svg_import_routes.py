"""
API route for importing SVG directly to Blender using FastAPI.

This module implements a route for the 'Import SVG to Blender' option in the UI.
"""

import os
import sys
import logging
import tempfile
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body, status
from typing import Optional, Dict, Any

# Add project root to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Import for reading config
import yaml

# Load configuration from config.yaml
config_path = os.path.join(os.path.dirname(__file__), '../../../config.yaml')
try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded configuration from {config_path}")
except Exception as e:
    logger.warning(f"Error loading config from {config_path}: {str(e)}")
    config = {'paths': {}}

# Define output directories from config if available, otherwise use defaults
OUTPUT_DIR = config.get('paths', {}).get('output_dir', os.path.join(project_root, "output"))
SVG_OUTPUT_DIR = config.get('paths', {}).get('svg_output_dir', os.path.join(OUTPUT_DIR, "svg"))
DIAGRAMS_OUTPUT_DIR = config.get('paths', {}).get('diagrams_output_dir', os.path.join(OUTPUT_DIR, "diagrams"))
MODELS_OUTPUT_DIR = config.get('paths', {}).get('models_output_dir', os.path.join(OUTPUT_DIR, "models"))

# Create router
router = APIRouter(tags=["svg_import"])

@router.post("/svg-generator/import-svg-to-blender")
async def import_svg_to_blender(
    svg_path: str = Body(..., description="Path to the SVG file"),
    name: Optional[str] = Body(None, description="Name for the Blender file"),
    extrusion_depth: float = Body(0.1, description="Depth for 3D extrusion")
):
    """Import SVG directly to Blender with extrusion."""
    try:
        # Parse SVG path
        if svg_path.startswith("diagrams/") or svg_path.startswith("svg/"):
            # Path is relative to output directory
            full_svg_path = os.path.join(OUTPUT_DIR, svg_path)
        else:
            # Assume path is absolute
            full_svg_path = svg_path
        
        # Ensure SVG file exists
        if not os.path.exists(full_svg_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SVG file not found: {full_svg_path}"
            )
        
        # Generate a unique name if none provided
        if not name:
            name = f"blender_import_{os.path.basename(full_svg_path).split('.')[0]}"
            
        # Define output path for Blender file
        blend_file_path = os.path.join(MODELS_OUTPUT_DIR, f"{name}.blend")
        
        # Create MODELS_OUTPUT_DIR if it doesn't exist
        os.makedirs(MODELS_OUTPUT_DIR, exist_ok=True)
        
        # Get Blender path from config or environment
        blender_path = config.get('blender', {}).get('path')
        if not blender_path:
            blender_path = os.environ.get("BLENDER_PATH")
        
        if not blender_path:
            # Try common locations
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                r"/usr/bin/blender",
                r"/Applications/Blender.app/Contents/MacOS/Blender"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    blender_path = path
                    break
        
        if not blender_path or not os.path.exists(blender_path):
            logger.error("Blender executable not found")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Blender is not available. Check server logs for details."
            )
        
        # Create a temporary Python script to import SVG to Blender
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
            temp_script_path = temp_script.name
            temp_script.write(f"""
import bpy
import os
import sys

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import SVG
svg_path = r"{full_svg_path}"
bpy.ops.import_curve.svg(filepath=svg_path)

# Extrude all curves
for obj in bpy.context.scene.objects:
    if obj.type == 'CURVE':
        # Select object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Extrude
        obj.data.extrude = {extrusion_depth}
        obj.data.bevel_depth = 0.01  # Small bevel for rounded edges

# Set up camera and lighting for better view
# Create camera if needed
if not any(obj.type == 'CAMERA' for obj in bpy.context.scene.objects):
    bpy.ops.object.camera_add(location=(0, -10, 5), rotation=(0.5, 0, 0))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

# Create lighting if needed
if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
    # Key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.active_object
    key_light.data.energy = 2.0
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, -2, 5))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 1.0

# Center view on objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.view3d.camera_to_view_selected()

# Save file
output_path = r"{blend_file_path}"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"SVG imported and saved to: {{output_path}}")
            """)
        
        try:
            logger.info(f"Running Blender to import SVG: {full_svg_path}")
            
            # Command with UI
            cmd = [
                blender_path,
                "--python", temp_script_path
            ]
            
            # Execute command
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Log output
            logger.info(f"Blender output: {process.stdout}")
            if process.stderr:
                logger.warning(f"Blender errors: {process.stderr}")
            
            logger.info(f"SVG imported to Blender successfully: {blend_file_path}")
            
            # Return success response
            return {
                "status": "success",
                "message": "SVG imported to Blender successfully",
                "name": name,
                "blender_file_path": blend_file_path
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing Blender: {str(e)}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error executing Blender: {str(e)}"
            )
        finally:
            # Clean up the temporary script
            try:
                os.unlink(temp_script_path)
            except:
                pass
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error importing SVG to Blender: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing SVG to Blender: {str(e)}"
        )
