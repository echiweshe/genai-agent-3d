import bpy

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
