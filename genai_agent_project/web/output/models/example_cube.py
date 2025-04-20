import bpy

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
