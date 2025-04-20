#!/usr/bin/env python
"""
Fix Directories for GenAI Agent 3D
This script creates all necessary output directories and example scripts
"""

import os
import sys
import json

def print_dir_info(path):
    """Print information about a directory"""
    print(f"Directory: {path}")
    print(f"  Exists: {os.path.exists(path)}")
    if os.path.exists(path):
        print(f"  Is Directory: {os.path.isdir(path)}")
        if os.path.isdir(path):
            try:
                files = os.listdir(path)
                print(f"  Contains {len(files)} items")
            except Exception as e:
                print(f"  Error listing files: {e}")

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

def main():
    """Main function to fix directories"""
    print("\n======= FIXING DIRECTORIES FOR GENAI AGENT 3D =======\n")
    
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Try multiple possible project structures to find the right one
    possible_structures = [
        # Structure 1: Direct under script directory
        {
            "output_dir": os.path.join(script_dir, "output"),
        },
        # Structure 2: Under genai_agent_project
        {
            "output_dir": os.path.join(script_dir, "genai_agent_project", "output"),
        },
        # Structure 3: Under web directory
        {
            "output_dir": os.path.join(script_dir, "web", "output"),
        },
        # Structure 4: Under genai_agent_project/web
        {
            "output_dir": os.path.join(script_dir, "genai_agent_project", "web", "output"),
        }
    ]
    
    # Create the first structure by default and try others if needed
    output_dir = possible_structures[0]["output_dir"]
    create_directory(output_dir)
    
    # Create subdirectories
    subdirs = ["models", "scenes", "diagrams", "tools", "temp"]
    created_dirs = {}
    
    for subdir in subdirs:
        subdir_path = os.path.join(output_dir, subdir)
        success = create_directory(subdir_path)
        created_dirs[subdir] = subdir_path
    
    # Check all possible structures and ensure they exist
    print("\nChecking alternative directory structures...")
    for structure in possible_structures[1:]:
        alt_output_dir = structure["output_dir"]
        if create_directory(alt_output_dir):
            # Also create subdirectories
            for subdir in subdirs:
                create_directory(os.path.join(alt_output_dir, subdir))
    
    # Create example scripts
    print("\nCreating example scripts...")
    create_example_scripts(created_dirs["models"], created_dirs["scenes"])
    
    # Create duplicate scripts in all possible locations
    for structure in possible_structures[1:]:
        alt_output_dir = structure["output_dir"]
        if os.path.exists(alt_output_dir):
            models_dir = os.path.join(alt_output_dir, "models")
            scenes_dir = os.path.join(alt_output_dir, "scenes")
            create_example_scripts(models_dir, scenes_dir)
    
    print("\n======= DIRECTORY CREATION COMPLETE =======")
    print("\nThe following directories have been created and populated with example scripts:")
    for structure in possible_structures:
        print_dir_info(structure["output_dir"])
        for subdir in subdirs:
            print_dir_info(os.path.join(structure["output_dir"], subdir))
    
    print("\nYou should now be able to see and execute the example Blender scripts in the application.")
    print("If you're still having issues, check the logs for any errors and make sure your server is running correctly.")

if __name__ == "__main__":
    main()
