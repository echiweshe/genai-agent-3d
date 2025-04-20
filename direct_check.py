#!/usr/bin/env python
"""
Direct Check for GenAI Agent 3D
This script checks all paths and configurations without relying on API endpoints.
"""

import os
import sys
import json
import glob
import shutil
from pathlib import Path

def print_header(text):
    """Print a header with decoration"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_status(message, status, indent=0):
    """Print a status message with colorful indicator"""
    indent_str = " " * indent
    status_icon = "✅" if status else "❌"
    print(f"{indent_str}{status_icon} {message}")

def check_directory(path):
    """Check if a directory exists and is accessible"""
    exists = os.path.exists(path)
    is_dir = os.path.isdir(path) if exists else False
    readable = os.access(path, os.R_OK) if exists else False
    writable = os.access(path, os.W_OK) if exists else False
    
    print_status(f"Directory: {path}", exists)
    if exists:
        print_status(f"Is directory", is_dir, indent=2)
        print_status(f"Is readable", readable, indent=2)
        print_status(f"Is writable", writable, indent=2)
        
        if is_dir:
            try:
                files = os.listdir(path)
                py_files = [f for f in files if f.endswith('.py')]
                print_status(f"Contains {len(files)} files ({len(py_files)} Python files)", True, indent=2)
                
                if py_files:
                    for py_file in py_files:
                        print_status(f"Python file: {py_file}", True, indent=4)
            except Exception as e:
                print_status(f"Error listing directory: {e}", False, indent=2)
    
    return exists and is_dir and readable

def create_example_scripts(models_dir, scenes_dir):
    """Create example Blender scripts"""
    created_files = []
    
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
        created_files.append(cube_path)
        
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
        created_files.append(sphere_path)
    
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
        created_files.append(scene_path)
    
    return created_files

def check_api_service(base_dir):
    """Check the API service configuration in the frontend"""
    print_header("Checking API Service Configuration")
    
    # Try to find the API service file
    api_paths = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower() in ['api.js', 'blenderscriptservice.js']:
                api_paths.append(os.path.join(root, file))
    
    if not api_paths:
        print_status("No API service files found", False)
        return False
    
    has_issues = False
    for api_path in api_paths:
        print_status(f"Found API file: {api_path}", True)
        
        # Check for API URL configuration
        try:
            with open(api_path, 'r') as f:
                content = f.read()
            
            if '/api' in content and 'baseURL' in content:
                print_status(f"Found potential API URL prefix issue in {os.path.basename(api_path)}", False, indent=2)
                print("    The file contains '/api' in the baseURL which might cause 404 errors.")
                has_issues = True
                
                # Create backup
                backup_path = api_path + '.backup'
                if not os.path.exists(backup_path):
                    with open(backup_path, 'w') as f:
                        f.write(content)
                    print_status(f"Created backup: {backup_path}", True, indent=4)
                
                # Fix the issue
                fixed_content = content.replace("baseURL: process.env.REACT_APP_API_URL + '/api'", "baseURL: process.env.REACT_APP_API_URL")
                fixed_content = fixed_content.replace("baseURL: 'http://localhost:8000/api'", "baseURL: 'http://localhost:8000'")
                fixed_content = fixed_content.replace("baseURL: `${process.env.REACT_APP_API_URL}/api`", "baseURL: process.env.REACT_APP_API_URL")
                
                with open(api_path, 'w') as f:
                    f.write(fixed_content)
                print_status(f"Fixed API URL prefix in {os.path.basename(api_path)}", True, indent=4)
            else:
                print_status(f"No API URL prefix issues found in {os.path.basename(api_path)}", True, indent=2)
        except Exception as e:
            print_status(f"Error checking API file {api_path}: {e}", False, indent=2)
    
    return not has_issues

def check_main_py(base_dir):
    """Check the main.py file for router configuration"""
    print_header("Checking Backend Router Configuration")
    
    # Try to find the main.py file
    main_paths = []
    for root, dirs, files in os.walk(base_dir):
        if 'main.py' in files:
            main_paths.append(os.path.join(root, 'main.py'))
    
    if not main_paths:
        print_status("No main.py file found", False)
        return False
    
    has_issues = False
    for main_path in main_paths:
        print_status(f"Found main.py: {main_path}", True)
        
        # Check for router configuration
        try:
            with open(main_path, 'r') as f:
                content = f.read()
            
            if 'app.include_router' in content and '/api' in content:
                print_status(f"Found router prefix issue in {os.path.basename(main_path)}", False, indent=2)
                print("    The file includes routers with the '/api' prefix which might cause 404 errors.")
                has_issues = True
                
                # Create backup
                backup_path = main_path + '.backup'
                if not os.path.exists(backup_path):
                    with open(backup_path, 'w') as f:
                        f.write(content)
                    print_status(f"Created backup: {backup_path}", True, indent=4)
                
                # Fix the issue
                fixed_content = content.replace("app.include_router(blender_router, prefix=\"/api\")", "app.include_router(blender_router)")
                fixed_content = fixed_content.replace("app.include_router(debug_router, prefix=\"/api\")", "app.include_router(debug_router)")
                
                with open(main_path, 'w') as f:
                    f.write(fixed_content)
                print_status(f"Fixed router prefix in {os.path.basename(main_path)}", True, indent=4)
            else:
                print_status(f"No router prefix issues found in {os.path.basename(main_path)}", True, indent=2)
        except Exception as e:
            print_status(f"Error checking main.py file {main_path}: {e}", False, indent=2)
    
    return not has_issues

def create_output_directories(base_dir):
    """Create all possible output directories with example scripts"""
    print_header("Creating Output Directories")
    
    # Possible output directory paths
    output_dir_paths = [
        os.path.join(base_dir, "output"),
        os.path.join(base_dir, "genai_agent_project", "output"),
        os.path.join(base_dir, "genai_agent_project", "web", "output")
    ]
    
    created_dirs = []
    created_files = []
    
    for output_dir in output_dir_paths:
        print(f"\nChecking output directory: {output_dir}")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            created_dirs.append(output_dir)
            print_status(f"Created/verified output directory: {output_dir}", True)
            
            # Create subdirectories
            subdirs = ["models", "scenes", "diagrams", "tools", "temp"]
            for subdir in subdirs:
                subdir_path = os.path.join(output_dir, subdir)
                os.makedirs(subdir_path, exist_ok=True)
                created_dirs.append(subdir_path)
                print_status(f"Created/verified {subdir} directory", True, indent=2)
            
            # Create example scripts
            models_dir = os.path.join(output_dir, "models")
            scenes_dir = os.path.join(output_dir, "scenes")
            new_files = create_example_scripts(models_dir, scenes_dir)
            created_files.extend(new_files)
            print_status(f"Created {len(new_files)} example scripts", True, indent=2)
        except Exception as e:
            print_status(f"Error creating output directory {output_dir}: {e}", False)
    
    return created_dirs, created_files

def check_all_paths(base_dir):
    """Check all paths and configurations"""
    print_header("Path Analysis")
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {base_dir}")
    
    # Look for project structure patterns
    project_patterns = [
        os.path.join(base_dir, "genai_agent_project"),
        os.path.join(base_dir, "web"),
        os.path.join(base_dir, "genai_agent_project", "web")
    ]
    
    found_project = False
    for pattern in project_patterns:
        if os.path.exists(pattern):
            print_status(f"Found project structure at: {pattern}", True)
            found_project = True
        else:
            print_status(f"Project structure not found at: {pattern}", False)
    
    # Look for backend and frontend directories
    backend_patterns = [
        os.path.join(base_dir, "web", "backend"),
        os.path.join(base_dir, "genai_agent_project", "web", "backend"),
        os.path.join(base_dir, "backend")
    ]
    
    frontend_patterns = [
        os.path.join(base_dir, "web", "frontend"),
        os.path.join(base_dir, "genai_agent_project", "web", "frontend"),
        os.path.join(base_dir, "frontend")
    ]
    
    found_backend = False
    for pattern in backend_patterns:
        if os.path.exists(pattern):
            print_status(f"Found backend at: {pattern}", True)
            found_backend = True
        else:
            print_status(f"Backend not found at: {pattern}", False)
    
    found_frontend = False
    for pattern in frontend_patterns:
        if os.path.exists(pattern):
            print_status(f"Found frontend at: {pattern}", True)
            found_frontend = True
        else:
            print_status(f"Frontend not found at: {pattern}", False)
    
    # Summary
    print("\nStructure Analysis Summary:")
    print_status("Project structure found", found_project)
    print_status("Backend found", found_backend)
    print_status("Frontend found", found_frontend)
    
    return found_project and found_backend and found_frontend

def main():
    """Main function"""
    print_header("GenAI Agent 3D Direct Path Check and Fix")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Check for path issues
    path_check = check_all_paths(script_dir)
    
    # Create output directories
    created_dirs, created_files = create_output_directories(script_dir)
    
    # Check and fix API service configuration
    api_fixed = check_api_service(script_dir)
    
    # Check and fix main.py
    main_fixed = check_main_py(script_dir)
    
    # Print summary
    print_header("Summary")
    print_status(f"Created {len(created_dirs)} directories", len(created_dirs) > 0)
    print_status(f"Created {len(created_files)} example scripts", len(created_files) > 0)
    print_status("API service configuration", api_fixed)
    print_status("Backend router configuration", main_fixed)
    
    print_header("Next Steps")
    print("1. Restart your backend server")
    print("2. Restart your frontend server")
    print("3. Refresh your browser")
    print("4. If issues persist, check browser console (F12) for error messages")

if __name__ == "__main__":
    main()
