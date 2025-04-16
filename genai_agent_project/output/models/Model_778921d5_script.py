# Fallback script for unknown model type: cabin
# Description: A simple geometric model with basic materials
# Style: basic
# Name: Model_778921d5

import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple cube as placeholder
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Model_778921d5"

# Add a material
mat = bpy.data.materials.new(name="Model_778921d5_Material")
mat.diffuse_color = (0.5, 0.5, 0.8, 1.0)  # Blue-ish color
cube.data.materials.append(mat)

# Add text note about the model
bpy.ops.object.text_add(location=(0, 0, 2))
text = bpy.context.active_object
text.name = "Model_778921d5_Description"
text.data.body = "Model: Model_778921d5\nDescription: A simple geometric model with basic materials\nStyle: basic"
text.data.size = 0.5

# Add a camera to render the model
bpy.ops.object.camera_add(location=(0, -5, 0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 5))
light = bpy.context.active_object
light.data.energy = 2.0

print("Generated placeholder model: Model_778921d5")
