"""
Simple Script for Testing SVG to 3D Conversion

This is a minimal wrapper that works even if path importing fails.
"""

import sys
import os
import bpy
import json
import traceback

def log(message):
    """Simple logging function."""
    print(f"[SVG2CLARITY] {message}")

def clean_scene():
    """Clean up the Blender scene."""
    # Remove all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Remove all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Remove all textures
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)
    
    # Remove all images
    for image in bpy.data.images:
        bpy.data.images.remove(image)
    
    # Remove all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    
    # Remove all curves
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve)
    
    log("Scene cleaned")

def create_test_model():
    """Create a simple test model to verify the script runs."""
    try:
        # Create a simple cube
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        cube = bpy.context.active_object
        cube.name = "TestCube"
        
        # Create a simple material
        mat = bpy.data.materials.new(name="TestMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.2, 0.2, 1.0)
        
        # Assign material to cube
        cube.data.materials.append(mat)
        
        log("Test model created")
        return True
    except Exception as e:
        log(f"Error creating test model: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function called when script is run directly."""
    try:
        # Check command line arguments
        if "--" in sys.argv:
            args = sys.argv[sys.argv.index("--") + 1:]
        else:
            args = []
        
        if len(args) < 2:
            log("Insufficient arguments. Running minimal test mode.")
            log("Usage: blender -b -P svg_to_3d_clarity_minimal.py -- <svg_path> <blend_output_path> [options_json]")
            
            # Clean the scene
            clean_scene()
            
            # Create test model
            create_test_model()
            
            # Save test file
            test_output = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_output.blend")
            bpy.ops.wm.save_as_mainfile(filepath=test_output)
            log(f"Test file saved to: {test_output}")
            return 0
        
        svg_path = args[0]
        blend_output_path = args[1]
        options_json = args[2] if len(args) > 2 else "{}"
        
        # Parse options JSON
        try:
            options = json.loads(options_json)
        except json.JSONDecodeError:
            log(f"Warning: Could not parse options JSON: {options_json}")
            options = {}
        
        log(f"SVG path: {svg_path}")
        log(f"Output path: {blend_output_path}")
        log(f"Options: {options}")
        
        # Clean the scene
        clean_scene()
        
        # Create test model (for now)
        create_test_model()
        
        # Save the file
        log(f"Saving Blender file: {blend_output_path}")
        bpy.ops.wm.save_as_mainfile(filepath=blend_output_path)
        log("Test conversion completed successfully")
        return 0
    except Exception as e:
        log(f"Error in main function: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
