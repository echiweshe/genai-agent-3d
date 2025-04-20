"""
Debug Routes for GenAI Agent 3D
This module provides debug endpoints for diagnosing issues with the application.
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from pydantic import BaseModel

# Create a router
router = APIRouter(prefix="/debug", tags=["debug"])

# Define base output directories - this should match what's in blender_execute.py
# Adjust these paths according to your project structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BASE_OUTPUT_DIR = os.path.join(BASE_DIR, "output")
REQUIRED_DIRS = [
    os.path.join(BASE_OUTPUT_DIR),
    os.path.join(BASE_OUTPUT_DIR, "models"),
    os.path.join(BASE_OUTPUT_DIR, "scenes"),
    os.path.join(BASE_OUTPUT_DIR, "diagrams"),
    os.path.join(BASE_OUTPUT_DIR, "tools"),
    os.path.join(BASE_OUTPUT_DIR, "temp")
]

# Response model for path check
class PathCheckResponse(BaseModel):
    exists: bool
    is_file: bool = False
    is_dir: bool = False
    path: str
    abs_path: str
    content: Optional[str] = None
    error: Optional[str] = None
    is_python: bool = False
    size: Optional[int] = None
    permissions: Optional[Dict[str, bool]] = None

# Script execution request model
class ScriptExecutionRequest(BaseModel):
    script_name: str

# Script execution response model
class ScriptExecutionResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None

@router.get("/paths")
async def check_directory_structure():
    """
    Check the directory structure for the application
    Returns information about required directories and available scripts
    """
    try:
        # Check required directories
        missing_dirs = []
        for dir_path in REQUIRED_DIRS:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to create directory {dir_path}: {str(e)}")
        
        # Check for scripts in each directory
        scripts = {}
        for dir_path in REQUIRED_DIRS:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                dir_name = os.path.basename(dir_path)
                script_files = []
                
                try:
                    for filename in os.listdir(dir_path):
                        if filename.endswith('.py'):
                            file_path = os.path.join(dir_path, filename)
                            script_files.append({
                                "name": filename,
                                "path": os.path.relpath(file_path, BASE_OUTPUT_DIR).replace('\\', '/'),
                                "size": os.path.getsize(file_path),
                                "modified": os.path.getmtime(file_path)
                            })
                except Exception as e:
                    scripts[dir_name] = {"error": str(e)}
                    continue
                
                scripts[dir_name] = script_files
        
        # Construct response
        return {
            "base_dir": BASE_DIR,
            "output_dir": BASE_OUTPUT_DIR,
            "required_directories": REQUIRED_DIRS,
            "missing_directories": missing_dirs,
            "scripts": scripts,
            "current_working_directory": os.getcwd()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking directory structure: {str(e)}")

@router.get("/check-path")
async def check_path(path: str = Query(..., description="Path to check relative to BASE_OUTPUT_DIR")):
    """
    Check if a specific path exists and get information about it
    """
    try:
        # Construct the absolute path
        rel_path = path.lstrip("/").replace("/", os.sep)
        abs_path = os.path.abspath(os.path.join(BASE_OUTPUT_DIR, rel_path))
        
        # Security check - ensure the path is within BASE_OUTPUT_DIR
        if not abs_path.startswith(BASE_OUTPUT_DIR):
            raise HTTPException(status_code=400, detail="Invalid path: Access outside of base directory is not allowed")
        
        result = PathCheckResponse(
            exists=os.path.exists(abs_path),
            path=path,
            abs_path=abs_path
        )
        
        if not result.exists:
            return result
        
        # Get file/directory info
        result.is_file = os.path.isfile(abs_path)
        result.is_dir = os.path.isdir(abs_path)
        result.is_python = path.endswith('.py')
        result.size = os.path.getsize(abs_path) if result.is_file else None
        
        # Get permissions
        result.permissions = {
            "read": os.access(abs_path, os.R_OK),
            "write": os.access(abs_path, os.W_OK),
            "execute": os.access(abs_path, os.X_OK)
        }
        
        # If it's a Python file, get content for inspection
        if result.is_file and result.is_python and result.size and result.size < 102400:  # Limit to 100KB
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    result.content = f.read()
            except Exception as e:
                result.error = f"Failed to read file content: {str(e)}"
        
        # If it's a directory, list contents
        if result.is_dir:
            try:
                contents = os.listdir(abs_path)
                result.content = json.dumps({
                    "items": contents,
                    "count": len(contents),
                    "files": [f for f in contents if os.path.isfile(os.path.join(abs_path, f))],
                    "directories": [d for d in contents if os.path.isdir(os.path.join(abs_path, d))]
                }, indent=2)
            except Exception as e:
                result.error = f"Failed to list directory contents: {str(e)}"
                
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking path: {str(e)}")

@router.post("/run-script", response_model=ScriptExecutionResponse)
async def run_debug_script(request: ScriptExecutionRequest, background_tasks: BackgroundTasks):
    """
    Run a debug script
    """
    # Validate script name for security
    if '..' in request.script_name or '/' in request.script_name or '\\' in request.script_name:
        raise HTTPException(status_code=400, detail="Invalid script name")
    
    # Only allow specific debug scripts
    allowed_scripts = ['debug_paths.py']
    if request.script_name not in allowed_scripts:
        raise HTTPException(status_code=400, detail=f"Script not allowed. Allowed scripts: {', '.join(allowed_scripts)}")
    
    # Construct the script path
    script_path = os.path.join(BASE_DIR, request.script_name)
    
    # Check if the script exists
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"Script not found: {request.script_name}")
    
    try:
        # Run the script and capture output
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=BASE_DIR
        )
        
        stdout, stderr = process.communicate(timeout=60)  # 60-second timeout
        
        # Check the return code
        if process.returncode != 0:
            return ScriptExecutionResponse(
                success=False,
                output=stdout,
                error=f"Script failed with exit code {process.returncode}. Error: {stderr}"
            )
        
        return ScriptExecutionResponse(
            success=True,
            output=stdout
        )
    except subprocess.TimeoutExpired:
        process.kill()
        raise HTTPException(status_code=500, detail="Script execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing script: {str(e)}")

@router.get("/fix-directory-structure")
async def fix_directory_structure():
    """
    Create all required directories and example scripts
    """
    try:
        # Create required directories
        for dir_path in REQUIRED_DIRS:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        
        # Create example scripts in models
        models_dir = os.path.join(BASE_OUTPUT_DIR, "models")
        scenes_dir = os.path.join(BASE_OUTPUT_DIR, "scenes")
        
        # Only create example scripts if the directories are empty
        if os.path.exists(models_dir) and len(os.listdir(models_dir)) == 0:
            # Example cube script
            cube_script = """import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Example_Cube"

# Create a material
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (1.0, 0.0, 0.0, 1.0)  # Red
cube.data.materials.append(mat)

print("Example cube created successfully!")
"""
            with open(os.path.join(models_dir, "example_cube.py"), "w") as f:
                f.write(cube_script)
            
            # Example sphere script
            sphere_script = """import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Example_Sphere"

# Create a material
mat = bpy.data.materials.new(name="SphereMaterial")
mat.diffuse_color = (0.0, 0.0, 1.0, 1.0)  # Blue
sphere.data.materials.append(mat)

print("Example sphere created successfully!")
"""
            with open(os.path.join(models_dir, "example_sphere.py"), "w") as f:
                f.write(sphere_script)
        
        # Create example scene script
        if os.path.exists(scenes_dir) and len(os.listdir(scenes_dir)) == 0:
            scene_script = """import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Ground"

# Create a material for the ground
mat_ground = bpy.data.materials.new(name="GroundMaterial")
mat_ground.diffuse_color = (0.2, 0.5, 0.2, 1.0)  # Green
plane.data.materials.append(mat_ground)

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "Building"

# Create a material for the cube
mat_cube = bpy.data.materials.new(name="BuildingMaterial")
mat_cube.diffuse_color = (0.8, 0.8, 0.8, 1.0)  # Gray
cube.data.materials.append(mat_cube)

# Create a camera
bpy.ops.object.camera_add(location=(10, -10, 10))
camera = bpy.context.active_object
camera.name = "SceneCamera"

# Point camera at the cube
constraint = camera.constraints.new(type='TRACK_TO')
constraint.target = cube
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Create a sun
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "Sun"

# Set the camera as active
bpy.context.scene.camera = camera

print("Example scene created successfully!")
"""
            with open(os.path.join(scenes_dir, "example_scene.py"), "w") as f:
                f.write(scene_script)
        
        # Return success with directory info
        return {
            "success": True,
            "message": "Directory structure fixed and example scripts created",
            "directories": {
                dir_path: {
                    "exists": os.path.exists(dir_path),
                    "item_count": len(os.listdir(dir_path)) if os.path.exists(dir_path) else 0
                } for dir_path in REQUIRED_DIRS
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fixing directory structure: {str(e)}")
