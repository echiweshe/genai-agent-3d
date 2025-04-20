#!/usr/bin/env python
"""
Direct Fix for GenAI Agent 3D Blender Scripts
This script creates the required directories and example scripts exactly
where your application expects to find them.
"""

import os
import sys
import json
import shutil

def create_directory(path):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Created directory: {path}")
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
    else:
        print(f"Directory already exists: {path}")
        return True

def create_example_scripts(models_dir, scenes_dir):
    """Create example Blender scripts"""
    # Example cube script
    if os.path.exists(models_dir):
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
        cube_path = os.path.join(models_dir, "example_cube.py")
        with open(cube_path, "w") as f:
            f.write(cube_script)
        print(f"Created example cube script: {cube_path}")
        
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
        sphere_path = os.path.join(models_dir, "example_sphere.py")
        with open(sphere_path, "w") as f:
            f.write(sphere_script)
        print(f"Created example sphere script: {sphere_path}")
    
    # Example scene script
    if os.path.exists(scenes_dir):
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
        scene_path = os.path.join(scenes_dir, "example_scene.py")
        with open(scene_path, "w") as f:
            f.write(scene_script)
        print(f"Created example scene script: {scene_path}")

def find_api_js_file(base_dir):
    """Find the API.js file in the project"""
    for root, dirs, files in os.walk(base_dir):
        if 'api.js' in [f.lower() for f in files]:
            for file in files:
                if file.lower() == 'api.js':
                    return os.path.join(root, file)
    return None

def update_api_js_file(api_js_path):
    """Update the API.js file to remove the /api prefix"""
    if not api_js_path or not os.path.exists(api_js_path):
        print("API.js file not found")
        return False
    
    try:
        # Read the file
        with open(api_js_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = api_js_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Check if there's a /api prefix being used
        if 'baseURL:' in content and '/api' in content:
            # Update the baseURL to remove /api prefix
            content = content.replace("baseURL: process.env.REACT_APP_API_URL + '/api'", "baseURL: process.env.REACT_APP_API_URL")
            content = content.replace("baseURL: 'http://localhost:8000/api'", "baseURL: 'http://localhost:8000'")
            content = content.replace("baseURL: `${process.env.REACT_APP_API_URL}/api`", "baseURL: process.env.REACT_APP_API_URL")
            
            # Write the updated content
            with open(api_js_path, 'w') as f:
                f.write(content)
            
            print(f"Updated API.js to remove /api prefix: {api_js_path}")
            return True
    except Exception as e:
        print(f"Error updating API.js: {e}")
    
    return False

def find_main_py_file(base_dir):
    """Find the main.py file in the project"""
    for root, dirs, files in os.walk(base_dir):
        if 'main.py' in files:
            return os.path.join(root, 'main.py')
    return None

def update_main_py_file(main_py_path):
    """Update the main.py file to remove the /api prefix from router inclusion"""
    if not main_py_path or not os.path.exists(main_py_path):
        print("main.py file not found")
        return False
    
    try:
        # Read the file
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = main_py_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Check if there's a /api prefix being used
        if 'app.include_router' in content and '/api' in content:
            # Update the router inclusion to remove /api prefix
            content = content.replace("app.include_router(blender_router, prefix=\"/api\")", "app.include_router(blender_router)")
            content = content.replace("app.include_router(debug_router, prefix=\"/api\")", "app.include_router(debug_router)")
            
            # Write the updated content
            with open(main_py_path, 'w') as f:
                f.write(content)
            
            print(f"Updated main.py to remove /api prefix: {main_py_path}")
            return True
    except Exception as e:
        print(f"Error updating main.py: {e}")
    
    return False

def create_direct_api_py(base_dir):
    """Create a direct_api.py file in the routes directory"""
    # Find the routes directory
    routes_dir = None
    for root, dirs, files in os.walk(base_dir):
        if os.path.basename(root) == 'routes':
            routes_dir = root
            break
    
    if not routes_dir:
        print("Routes directory not found")
        return False
    
    direct_api_path = os.path.join(routes_dir, 'direct_api.py')
    
    direct_api_content = """\"\"\"
Direct API Routes for GenAI Agent 3D
This module provides direct API routes for debugging and fixing issues
\"\"\"

import os
import sys
import logging
from fastapi import APIRouter, HTTPException

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a router
router = APIRouter(tags=["direct"])

# Get project directory
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
BASE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# Alternative paths to check
ALTERNATIVE_PATHS = [
    os.path.join(SCRIPT_DIR, "genai_agent_project", "output"),
    os.path.join(SCRIPT_DIR, "web", "output"),
    os.path.join(os.path.dirname(SCRIPT_DIR), "output")
]

# Find the first existing output directory
for alt_path in ALTERNATIVE_PATHS:
    if os.path.exists(alt_path):
        BASE_OUTPUT_DIR = alt_path
        break

# Make sure output directory exists
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

@router.get("/direct/test")
async def test_direct_api():
    \"\"\"Test endpoint to verify the direct API is working\"\"\"
    return {
        "status": "ok",
        "message": "Direct API is working",
        "base_output_dir": BASE_OUTPUT_DIR
    }

@router.get("/direct/list-paths")
async def list_paths():
    \"\"\"List all possible output directories\"\"\"
    paths = [BASE_OUTPUT_DIR] + ALTERNATIVE_PATHS
    
    results = []
    for path in paths:
        results.append({
            "path": path,
            "exists": os.path.exists(path),
            "is_dir": os.path.isdir(path) if os.path.exists(path) else False,
            "contents": os.listdir(path) if os.path.exists(path) and os.path.isdir(path) else None
        })
    
    return {
        "status": "ok",
        "paths": results
    }

@router.get("/direct/fix-directories")
async def fix_directories():
    \"\"\"Create required directories and example scripts\"\"\"
    # Create subdirectories
    subdirectories = [
        "models",
        "scenes",
        "diagrams",
        "tools",
        "temp"
    ]
    
    created_dirs = []
    for subdir in subdirectories:
        subdir_path = os.path.join(BASE_OUTPUT_DIR, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path, exist_ok=True)
            created_dirs.append(subdir_path)
    
    # Create example scripts
    models_dir = os.path.join(BASE_OUTPUT_DIR, "models")
    scenes_dir = os.path.join(BASE_OUTPUT_DIR, "scenes")
    
    created_files = []
    
    # Example cube script
    if os.path.exists(models_dir) and len([f for f in os.listdir(models_dir) if f.endswith('.py')]) == 0:
        cube_script = \"\"\"import bpy

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
\"\"\"
        cube_path = os.path.join(models_dir, "example_cube.py")
        with open(cube_path, "w") as f:
            f.write(cube_script)
        created_files.append(cube_path)
    
    # Example sphere script
    if os.path.exists(models_dir) and not os.path.exists(os.path.join(models_dir, "example_sphere.py")):
        sphere_script = \"\"\"import bpy

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
\"\"\"
        sphere_path = os.path.join(models_dir, "example_sphere.py")
        with open(sphere_path, "w") as f:
            f.write(sphere_script)
        created_files.append(sphere_path)
    
    # Example scene script
    if os.path.exists(scenes_dir) and len([f for f in os.listdir(scenes_dir) if f.endswith('.py')]) == 0:
        scene_script = \"\"\"import bpy

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

print("Example scene created successfully!")
\"\"\"
        scene_path = os.path.join(scenes_dir, "example_scene.py")
        with open(scene_path, "w") as f:
            f.write(scene_script)
        created_files.append(scene_path)
    
    return {
        "status": "ok",
        "base_output_dir": BASE_OUTPUT_DIR,
        "created_directories": created_dirs,
        "created_files": created_files,
        "existing_scripts": {
            "models": [f for f in os.listdir(models_dir) if f.endswith('.py')] if os.path.exists(models_dir) else [],
            "scenes": [f for f in os.listdir(scenes_dir) if f.endswith('.py')] if os.path.exists(scenes_dir) else []
        }
    }

@router.get("/blender/list-scripts/{folder:path}")
async def list_blender_scripts(folder: str = ""):
    \"\"\"List available Blender scripts in the output directory\"\"\"
    # Build the path
    logger.info(f"Listing scripts in folder: {folder}")
    
    directory = os.path.join(BASE_OUTPUT_DIR, folder)
    abs_directory = os.path.abspath(directory)
    
    logger.info(f"Directory: {directory}")
    logger.info(f"Absolute directory: {abs_directory}")
    
    # Create directory if it doesn't exist
    if not os.path.exists(abs_directory):
        try:
            os.makedirs(abs_directory, exist_ok=True)
            logger.info(f"Created directory: {abs_directory}")
        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating directory: {str(e)}")
    
    # List all Python files in the directory
    scripts = []
    try:
        items = os.listdir(abs_directory)
        
        for filename in items:
            file_path = os.path.join(abs_directory, filename)
            if os.path.isfile(file_path) and filename.endswith('.py'):
                # Get relative path from BASE_OUTPUT_DIR
                rel_path = os.path.relpath(file_path, BASE_OUTPUT_DIR)
                script_info = {
                    "name": filename,
                    "path": rel_path.replace('\\\\', '/'),  # Use forward slashes for consistency
                    "full_path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path)
                }
                scripts.append(script_info)
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading directory: {str(e)}")
    
    return {
        "directory": folder,
        "scripts": scripts
    }

@router.get("/debug/check-path")
async def check_path(path: str):
    \"\"\"Check if a specific path exists and get information about it\"\"\"
    try:
        # Try multiple possible base paths
        all_base_paths = [BASE_OUTPUT_DIR] + ALTERNATIVE_PATHS
        all_results = []
        
        for base_path in all_base_paths:
            # Construct the absolute path
            rel_path = path.lstrip("/").replace("/", os.sep)
            abs_path = os.path.abspath(os.path.join(base_path, rel_path))
            
            result = {
                "base_path": base_path,
                "abs_path": abs_path,
                "exists": os.path.exists(abs_path),
                "path": path
            }
            
            if result["exists"]:
                # Get file/directory info
                result["is_file"] = os.path.isfile(abs_path)
                result["is_dir"] = os.path.isdir(abs_path)
                result["is_python"] = path.endswith('.py')
                result["size"] = os.path.getsize(abs_path) if result["is_file"] else None
                
                # Get permissions
                result["permissions"] = {
                    "read": os.access(abs_path, os.R_OK),
                    "write": os.access(abs_path, os.W_OK),
                    "execute": os.access(abs_path, os.X_OK)
                }
                
                # If it's a Python file, get content for inspection
                if result["is_file"] and result["is_python"] and result["size"] and result["size"] < 102400:  # Limit to 100KB
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            result["content"] = f.read()
                    except Exception as e:
                        result["error"] = f"Failed to read file content: {str(e)}"
                
                # If it's a directory, list contents
                if result["is_dir"]:
                    try:
                        contents = os.listdir(abs_path)
                        result["contents"] = {
                            "items": contents,
                            "count": len(contents),
                            "files": [f for f in contents if os.path.isfile(os.path.join(abs_path, f))],
                            "directories": [d for d in contents if os.path.isdir(os.path.join(abs_path, d))]
                        }
                    except Exception as e:
                        result["error"] = f"Failed to list directory contents: {str(e)}"
            
            all_results.append(result)
        
        # Return the first existing result, or all results if none exist
        existing_results = [r for r in all_results if r["exists"]]
        if existing_results:
            return existing_results[0]
        else:
            # If no path exists, return all checked paths
            return {
                "exists": False,
                "path": path,
                "checked_paths": all_results
            }
    except Exception as e:
        logger.error(f"Error checking path: {e}")
        return {
            "status": "error",
            "message": str(e),
            "path": path
        }
"""
    
    try:
        with open(direct_api_path, 'w') as f:
            f.write(direct_api_content)
        
        print(f"Created direct_api.py: {direct_api_path}")
        return True
    except Exception as e:
        print(f"Error creating direct_api.py: {e}")
        return False

def update_main_direct_api(base_dir):
    """Update the main.py file to import and use the direct API"""
    main_py_path = find_main_py_file(base_dir)
    if not main_py_path:
        print("main.py file not found")
        return False
    
    try:
        # Read the file
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = main_py_path + '.backup2'
        with open(backup_path, 'w') as f:
            f.write(content)
        
        # Add import for direct_api
        if 'from routes.direct_api import router as direct_router' not in content:
            # Find the imports section
            if 'from routes.' in content:
                # Insert after the last import
                lines = content.splitlines()
                import_lines = [i for i, line in enumerate(lines) if 'from routes.' in line]
                if import_lines:
                    last_import_line = max(import_lines)
                    lines.insert(last_import_line + 1, 'try:')
                    lines.insert(last_import_line + 2, '    from routes.direct_api import router as direct_router')
                    lines.insert(last_import_line + 3, '    print("Direct API router loaded successfully")')
                    lines.insert(last_import_line + 4, 'except ImportError as e:')
                    lines.insert(last_import_line + 5, '    print(f"Direct API router not loaded: {e}")')
                    lines.insert(last_import_line + 6, '    direct_router = None')
                    
                    # Find where to include the router
                    include_lines = [i for i, line in enumerate(lines) if 'app.include_router' in line]
                    if include_lines:
                        last_include_line = max(include_lines)
                        lines.insert(last_include_line + 1, '')
                        lines.insert(last_include_line + 2, '# Include direct API router')
                        lines.insert(last_include_line + 3, 'if direct_router:')
                        lines.insert(last_include_line + 4, '    app.include_router(direct_router)')
                        
                        # Write the updated content
                        with open(main_py_path, 'w') as f:
                            f.write('\n'.join(lines))
                        
                        print(f"Updated main.py to include direct API router: {main_py_path}")
                        return True
        else:
            print("main.py already includes direct_api router")
            return True
    except Exception as e:
        print(f"Error updating main.py for direct API: {e}")
    
    return False

def main():
    """Main function to fix the Blender scripts issue"""
    print("\n===== DIRECT FIX FOR GENAI AGENT 3D BLENDER SCRIPTS =====\n")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Possible output directory paths
    output_dir_paths = [
        os.path.join(script_dir, "output"),
        os.path.join(script_dir, "genai_agent_project", "output"),
        os.path.join(script_dir, "genai_agent_project", "web", "output"),
        os.path.join(script_dir, "web", "output")
    ]
    
    fixed_directories = False
    fixed_api = False
    
    # Create all possible output directories with example scripts
    for output_dir in output_dir_paths:
        print(f"\nChecking output directory: {output_dir}")
        if create_directory(output_dir):
            # Create subdirectories
            models_dir = os.path.join(output_dir, "models")
            scenes_dir = os.path.join(output_dir, "scenes")
            diagrams_dir = os.path.join(output_dir, "diagrams")
            tools_dir = os.path.join(output_dir, "tools")
            temp_dir = os.path.join(output_dir, "temp")
            
            create_directory(models_dir)
            create_directory(scenes_dir)
            create_directory(diagrams_dir)
            create_directory(tools_dir)
            create_directory(temp_dir)
            
            # Create example scripts
            create_example_scripts(models_dir, scenes_dir)
            fixed_directories = True
    
    # Attempt to find and update the API.js file
    api_js_path = find_api_js_file(script_dir)
    if api_js_path:
        print(f"\nFound API.js file: {api_js_path}")
        if update_api_js_file(api_js_path):
            fixed_api = True
    
    # Attempt to find and update the main.py file
    main_py_path = find_main_py_file(script_dir)
    if main_py_path:
        print(f"\nFound main.py file: {main_py_path}")
        if update_main_py_file(main_py_path):
            fixed_api = True
    
    # Create direct_api.py
    if create_direct_api_py(script_dir):
        fixed_api = True
    
    # Update main.py to use direct_api
    if update_main_direct_api(script_dir):
        fixed_api = True
    
    print("\n===== FIX RESULTS =====")
    if fixed_directories:
        print("✅ Successfully created directories and example scripts")
    else:
        print("❌ Failed to create directories or example scripts")
    
    if fixed_api:
        print("✅ Successfully updated API configuration")
    else:
        print("❌ Failed to update API configuration")
    
    print("\n===== NEXT STEPS =====")
    print("1. Restart your backend server")
    print("2. Restart your frontend server")
    print("3. Try accessing the Blender Scripts page again")
    print("\nIf you still encounter 404 errors, use this direct API endpoint:")
    print("http://localhost:8000/direct/fix-directories")
    print("\n===== END =====\n")

if __name__ == "__main__":
    main()
