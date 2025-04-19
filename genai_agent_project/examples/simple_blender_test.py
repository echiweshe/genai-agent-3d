"""
Simple Blender test script to verify Blender Python integration.
This script creates a basic cube and sphere in a new scene.
"""
import bpy
import sys
import os

def main():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create a cube
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"
    
    # Create a material for the cube
    mat_cube = bpy.data.materials.new(name="CubeMaterial")
    mat_cube.diffuse_color = (1.0, 0.0, 0.0, 1.0)  # Red
    cube.data.materials.append(mat_cube)
    
    # Create a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 3, 0))
    sphere = bpy.context.active_object
    sphere.name = "TestSphere"
    
    # Create a material for the sphere
    mat_sphere = bpy.data.materials.new(name="SphereMaterial")
    mat_sphere.diffuse_color = (0.0, 0.0, 1.0, 1.0)  # Blue
    sphere.data.materials.append(mat_sphere)
    
    # Create a camera and point it at our objects
    bpy.ops.object.camera_add(location=(10, -10, 10))
    camera = bpy.context.active_object
    camera.name = "TestCamera"
    
    # Point camera at the cube
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = cube
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    # Create a light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    light = bpy.context.active_object
    light.name = "TestLight"
    
    # Set the camera as active
    bpy.context.scene.camera = camera
    
    # Print success message with Python version info
    print("\n" + "="*80)
    print("BLENDER TEST SCRIPT EXECUTED SUCCESSFULLY")
    print(f"Python version: {sys.version}")
    print(f"Blender version: {bpy.app.version_string}")
    print("Created objects:")
    print(f"  - {cube.name}")
    print(f"  - {sphere.name}")
    print(f"  - {camera.name}")
    print(f"  - {light.name}")
    print("="*80 + "\n")
    
    # Save the file to the examples directory
    blend_file_path = os.path.join(os.path.dirname(__file__), "test_output.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
    print(f"Saved blend file to: {blend_file_path}")

if __name__ == "__main__":
    main()
