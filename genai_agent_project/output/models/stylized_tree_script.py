# Fallback curve model script for: A stylized tree with curving branches and a broad canopy
# Style: stylized
# Name: stylized_tree

import bpy
import math
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a new curve
curve_data = bpy.data.curves.new('stylized_tree_curve', 'CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 12
curve_data.bevel_depth = 0.1
curve_data.bevel_resolution = 6

# Create the curve object
curve_obj = bpy.data.objects.new('stylized_tree', curve_data)
bpy.context.collection.objects.link(curve_obj)

# Create a spline for the curve
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(4)  # 5 points total

# Set point coordinates
points = spline.bezier_points
points[0].co = (0, 0, 0)
points[0].handle_left = (-1, 0, 0)
points[0].handle_right = (1, 0, 0)

points[1].co = (2, 2, 0)
points[1].handle_left = (1, 2, 0)
points[1].handle_right = (3, 2, 0)

points[2].co = (4, -1, 0)
points[2].handle_left = (3, -1, 0)
points[2].handle_right = (5, -1, 0)

points[3].co = (6, 1, 3)
points[3].handle_left = (5, 1, 3)
points[3].handle_right = (7, 1, 3)

points[4].co = (8, 0, 0)
points[4].handle_left = (7, 0, 0)
points[4].handle_right = (9, 0, 0)

# Add a material
mat = bpy.data.materials.new(name="stylized_tree_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.8, 0.2, 1.0)  # Green-ish color
    bsdf.inputs['Metallic'].default_value = 0.5
    bsdf.inputs['Roughness'].default_value = 0.2
curve_obj.data.materials.append(mat)

# Add a camera to render the model
bpy.ops.object.camera_add(location=(4, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(90))
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', radius=1, location=(4, -4, 8))
light = bpy.context.active_object
light.data.energy = 2.0

# Set render settings for preview
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Output for status reporting
output = {
    "status": "success",
    "message": "Model 'stylized_tree' created successfully",
    "objects_created": ["stylized_tree", "Camera", "Sun"],
    "model_description": "A curved 3D path with bevel applied and a green metallic material"
}

print("Generated curve model: stylized_tree")
