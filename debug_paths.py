#!/usr/bin/env python
"""
Debug directory paths and structure for GenAI Agent 3D
This script prints out key paths and directory content for debugging purposes.
"""
import os
import sys
import json

def print_directory_tree(path, prefix="", max_depth=3, current_depth=0):
    """Print a simple directory tree"""
    if current_depth > max_depth:
        print(f"{prefix}... (max depth reached)")
        return
    
    if not os.path.exists(path):
        print(f"{prefix}{os.path.basename(path)} [DOES NOT EXIST]")
        return
    
    if os.path.isfile(path):
        print(f"{prefix}{os.path.basename(path)}")
        return
    
    print(f"{prefix}{os.path.basename(path)}/")
    
    try:
        items = os.listdir(path)
        items.sort()
        
        for i, item in enumerate(items):
            item_path = os.path.join(path, item)
            if i == len(items) - 1:
                # Last item
                print_directory_tree(item_path, prefix + "└── ", max_depth, current_depth + 1)
            else:
                # Not last item
                print_directory_tree(item_path, prefix + "├── ", max_depth, current_depth + 1)
    except Exception as e:
        print(f"{prefix}  Error: {e}")

def main():
    """Main function to print directory information"""
    print("\n======================= DEBUG PATHS =======================\n")
    
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Construct paths - corrected to have output directly under genai_agent_project
    project_dir = os.path.join(script_dir, "genai_agent_project")
    output_dir = os.path.join(project_dir, "output")
    models_dir = os.path.join(output_dir, "models")
    scenes_dir = os.path.join(output_dir, "scenes")
    
    # Print current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Print environment variables
    print("\nRELEVANT ENVIRONMENT VARIABLES:")
    for key in ["PATH", "PYTHONPATH"]:
        if key in os.environ:
            print(f"{key}: {os.environ[key]}")
    
    # Print directory existence
    print("\nDIRECTORY EXISTENCE:")
    print(f"Project directory exists: {os.path.exists(project_dir)}")
    print(f"Output directory exists: {os.path.exists(output_dir)}")
    print(f"Models directory exists: {os.path.exists(models_dir)}")
    print(f"Scenes directory exists: {os.path.exists(scenes_dir)}")
    
    # Print directory structure
    print("\nDIRECTORY STRUCTURE:")
    print_directory_tree(script_dir, max_depth=2)
    
    # Try to create directories if they don't exist
    print("\nCREATING DIRECTORIES IF NEEDED:")
    directories = [
        project_dir,
        output_dir,
        models_dir,
        scenes_dir,
        os.path.join(output_dir, "diagrams"),
        os.path.join(output_dir, "tools"),
        os.path.join(output_dir, "temp")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"Created directory: {directory}")
            except Exception as e:
                print(f"Failed to create directory {directory}: {e}")
        else:
            print(f"Directory already exists: {directory}")
    
    # Create example files if models directory is empty
    if os.path.exists(models_dir) and len(os.listdir(models_dir)) == 0:
        print("\nCreating example Blender scripts...")
        
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
            print(f"Created example script: example_cube.py")
        
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
            print(f"Created example script: example_sphere.py")
    
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
            print(f"Created example scene script: example_scene.py")
    
    # Check if output dir exists, if so print its contents
    if os.path.exists(output_dir):
        print("\nOUTPUT DIRECTORY STRUCTURE AFTER CREATION:")
        print_directory_tree(output_dir, max_depth=3)
    
    print("\n========================= END ===========================\n")

if __name__ == "__main__":
    main()
