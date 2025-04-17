# Blender script to import and extrude SVG: example_3d
import bpy
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import SVG
svg_path = "output/svg/example_3d.svg"
bpy.ops.import_curve.svg(filepath=svg_path)

# Select all curve objects
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type == 'CURVE':
        obj.select_set(True)
        
        # Set curve properties for extrusion
        obj.data.dimensions = '3D'
        obj.data.bevel_depth = 0.2
        obj.data.bevel_resolution = 4
        
        # Add material
        if len(obj.data.materials) == 0:
            mat = bpy.data.materials.new(name=f"{obj.name}_material")
            mat.diffuse_color = (0.8, 0.8, 0.8, 1.0)
            obj.data.materials.append(mat)

# Join all curve objects into one
if len(bpy.context.selected_objects) > 1:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    
    # Rename the joined object
    bpy.context.active_object.name = "example_3d"

# Add a camera for rendering
bpy.ops.object.camera_add(location=(0, 0, 10))
camera = bpy.context.active_object
camera.name = "example_3d_camera"
bpy.context.scene.camera = camera

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
light = bpy.context.active_object
light.name = "example_3d_light"
light.data.energy = 2.0

# Save the file
output_path = os.path.join("output/svg/", "example_3d.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"Completed SVG extrusion for example_3d with depth 0.2")
