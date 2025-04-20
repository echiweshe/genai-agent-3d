#!/usr/bin/env python
"""
Ensure Output Directories for GenAI Agent 3D

This script creates all necessary output directories for the GenAI Agent 3D project
to ensure that the Blender script execution feature works correctly.
"""
import os
import sys

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

def ensure_output_directories():
    """Ensure all required output directories exist"""
    print("Ensuring output directories exist...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.join(project_dir, "genai_agent_project")
    
    # Create main output directory
    output_dir = os.path.join(project_dir, "output")
    if not create_directory(output_dir):
        return False
    
    # Create subdirectories
    subdirectories = [
        "models",
        "scenes",
        "diagrams",
        "tools",
        "temp"
    ]
    
    for subdir in subdirectories:
        subdir_path = os.path.join(output_dir, subdir)
        if not create_directory(subdir_path):
            return False
    
    # Create example scripts if needed
    if len(os.listdir(os.path.join(output_dir, "models"))) == 0:
        print("Creating example scripts...")
        create_example_scripts(output_dir)
    
    print("All output directories created successfully!")
    return True

def create_example_scripts(output_dir):
    """Create example scripts for testing"""
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
    
    # Example scene script
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
    
    # Write the scripts to files
    with open(os.path.join(output_dir, "models", "example_cube.py"), "w") as f:
        f.write(cube_script)
    
    with open(os.path.join(output_dir, "models", "example_sphere.py"), "w") as f:
        f.write(sphere_script)
    
    with open(os.path.join(output_dir, "scenes", "example_scene.py"), "w") as f:
        f.write(scene_script)
    
    print("Example scripts created successfully!")

if __name__ == "__main__":
    success = ensure_output_directories()
    sys.exit(0 if success else 1)
