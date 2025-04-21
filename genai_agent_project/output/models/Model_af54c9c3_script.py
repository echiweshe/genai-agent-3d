# Fallback model script for: a rose flower in a vase
# Style: realistic
# Name: Model_af54c9c3

import bpy
import math
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple mesh model
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Model_af54c9c3"

# Add a material
mat = bpy.data.materials.new(name="Model_af54c9c3_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get('Principled BSDF')
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.2, 1.0)  # Red-ish color
    bsdf.inputs['Metallic'].default_value = 0.2
    bsdf.inputs['Roughness'].default_value = 0.3
sphere.data.materials.append(mat)

# Apply some modifiers
bpy.ops.object.modifier_add(type='SUBSURF')
sphere.modifiers["Subdivision"].levels = 2

bpy.ops.object.modifier_add(type='DISPLACE')
texture = bpy.data.textures.new("Model_af54c9c3_Texture", type='NOISE')
sphere.modifiers["Displace"].texture = texture
sphere.modifiers["Displace"].strength = 0.2

# Add a simple armature
bpy.ops.object.armature_add(location=(0, 0, 0))
armature = bpy.context.active_object
armature.name = "Model_af54c9c3_Armature"

# Parent the sphere to the armature
sphere.select_set(True)
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.object.parent_set(type='ARMATURE')

# Add a camera to render the model
bpy.ops.object.camera_add(location=(0, -5, 0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 5))
light = bpy.context.active_object
light.data.energy = 2.0

# Set render settings for preview
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Output for status reporting
output = {
    "status": "success",
    "message": "Model 'Model_af54c9c3' created successfully",
    "objects_created": ["Model_af54c9c3", "Model_af54c9c3_Armature", "Camera", "Sun"],
    "model_description": "A red sphere with subdivision and displacement modifiers, rigged with a simple armature"
}

print("Generated model: Model_af54c9c3")
