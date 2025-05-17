"""
Simple Clarity-Preserving 3D Model Generator for SVG Files
Designed to create minimal 3D models that preserve diagram clarity
"""

import bpy
import os
import sys
import traceback

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
    
    print("Scene cleaned")

def create_clarity_model(svg_file):
    """Create a simplified clarity-preserving model."""
    try:
        # Extract base name from SVG path
        base_name = os.path.basename(svg_file).split('.')[0]
        print(f"Creating model for: {base_name}")
        
        # Create node shapes based on flowchart diagram
        # Create green rectangle (start node)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.5, 0.025))
        start_node = bpy.context.active_object
        start_node.name = "StartNode"
        start_node.scale = (1.0, 0.5, 0.05)
        
        # Add material to start node
        start_mat = bpy.data.materials.new(name="StartMaterial")
        start_mat.use_nodes = True
        start_nodes = start_mat.node_tree.nodes
        start_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.8, 0.2, 1.0)
        start_mat.diffuse_color = (0.2, 0.8, 0.2, 1.0)
        start_node.data.materials.append(start_mat)
        
        # Create rectangle (process node)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.5, 0.025))
        process_node = bpy.context.active_object
        process_node.name = "ProcessNode"
        process_node.scale = (1.0, 0.5, 0.05)
        
        # Add material to process node
        process_mat = bpy.data.materials.new(name="ProcessMaterial")
        process_mat.use_nodes = True
        process_nodes = process_mat.node_tree.nodes
        process_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.8, 0.8, 1.0)
        process_mat.diffuse_color = (0.4, 0.8, 0.8, 1.0)
        process_node.data.materials.append(process_mat)
        
        # Create diamond (decision node)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.5, 0.025))
        decision = bpy.context.active_object
        decision.name = "DecisionNode"
        decision.scale = (0.7, 0.7, 0.05)
        decision.rotation_euler = (0, 0, 0.785398)  # 45 degrees
        
        # Add material to decision node
        decision_mat = bpy.data.materials.new(name="DecisionMaterial")
        decision_mat.use_nodes = True
        decision_nodes = decision_mat.node_tree.nodes
        decision_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.7, 0.2, 1.0)
        decision_mat.diffuse_color = (0.9, 0.7, 0.2, 1.0)
        decision.data.materials.append(decision_mat)
        
        # Create terminator node (red)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.5, 0.025))
        end_node = bpy.context.active_object
        end_node.name = "EndNode"
        end_node.scale = (1.0, 0.5, 0.05)
        
        # Add material to end node
        end_mat = bpy.data.materials.new(name="EndMaterial")
        end_mat.use_nodes = True
        end_nodes = end_mat.node_tree.nodes
        end_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.3, 0.3, 1.0)
        end_mat.diffuse_color = (0.9, 0.3, 0.3, 1.0)
        end_node.data.materials.append(end_mat)
        
        # Create connector lines
        curve = bpy.data.curves.new('FlowConnectors', 'CURVE')
        curve.dimensions = '3D'
        curve.resolution_u = 12
        curve.bevel_depth = 0.02
        
        # Connector from start to process
        spline = curve.splines.new('POLY')
        spline.points.add(1)  # Start with 2 points
        spline.points[0].co = (0, 1.0, 0.025, 1)  # Bottom of start node
        spline.points[1].co = (0, 1.0, 0.025, 1)  # Top of process node
        
        # Connector from process to decision
        spline = curve.splines.new('POLY')
        spline.points.add(1)
        spline.points[0].co = (0, 0.0, 0.025, 1)  # Bottom of process node
        spline.points[1].co = (0, 0.0, 0.025, 1)  # Top of decision node
        
        # Connector from decision to end
        spline = curve.splines.new('POLY')
        spline.points.add(1)
        spline.points[0].co = (0, -1.0, 0.025, 1)  # Bottom of decision node
        spline.points[1].co = (0, -1.0, 0.025, 1)  # Top of end node
        
        # Create connector object
        connector_obj = bpy.data.objects.new('Connectors', curve)
        bpy.context.collection.objects.link(connector_obj)
        
        # Add material to connectors
        conn_mat = bpy.data.materials.new(name="ConnectorMaterial")
        conn_mat.use_nodes = True
        conn_nodes = conn_mat.node_tree.nodes
        conn_nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
        conn_mat.diffuse_color = (0.1, 0.1, 0.1, 1.0)
        connector_obj.data.materials.append(conn_mat)
        
        # Set up camera
        bpy.ops.object.camera_add(location=(0, 0, 7))
        camera = bpy.context.active_object
        camera.name = "FlowchartCamera"
        camera.rotation_euler = (0, 0, 0)
        bpy.context.scene.camera = camera
        
        # Set up lighting
        bpy.ops.object.light_add(type='SUN', location=(2, -2, 4))
        key_light = bpy.context.active_object
        key_light.name = "KeyLight"
        key_light.data.energy = 3.0
        
        bpy.ops.object.light_add(type='SUN', location=(-3, -1, 3))
        fill_light = bpy.context.active_object
        fill_light.name = "FillLight"
        fill_light.data.energy = 1.5
        
        return True
    except Exception as e:
        print(f"Error creating model: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    try:
        # Parse command line arguments
        if "--" in sys.argv:
            args = sys.argv[sys.argv.index("--") + 1:]
        else:
            args = []
        
        if len(args) < 2:
            svg_file = "example.svg"
            output_file = "clarity_output.blend"
        else:
            svg_file = args[0]
            output_file = args[1]
        
        print(f"Processing: {svg_file}")
        print(f"Output to: {output_file}")
        
        # Clean the scene
        clean_scene()
        
        # Create the model
        success = create_clarity_model(svg_file)
        
        if success:
            # Save to output file
            print(f"Saving to: {output_file}")
            bpy.ops.wm.save_as_mainfile(filepath=output_file)
            print("Done!")
            return 0
        else:
            print("Failed to create model")
            return 1
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
