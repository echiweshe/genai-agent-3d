import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set up scene
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.render.film_transparent = True

# Create diagram components
def create_cube_node(name, location, color, size=1.0):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    node = bpy.context.active_object
    node.name = name
    
    # Create material
    mat = bpy.data.materials.new(name=f"{name}_material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    
    # Assign material
    if node.data.materials:
        node.data.materials[0] = mat
    else:
        node.data.materials.append(mat)
    
    return node

def create_arrow(start, end, thickness=0.1, head_size=0.2, name="Arrow"):
    # Calculate direction vector
    direction = [end[i] - start[i] for i in range(3)]
    length = math.sqrt(sum(x*x for x in direction))
    direction = [d/length for d in direction]
    
    # Create cylinder for arrow body
    bpy.ops.mesh.primitive_cylinder_add(
        radius=thickness/2,
        depth=length * 0.9,  # Slightly shorter to make room for arrow head
        location=[start[i] + direction[i]*length*0.45 for i in range(3)]
    )
    
    # Point cylinder along direction
    import mathutils
    from mathutils import Vector
    
    arrow_body = bpy.context.active_object
    arrow_body.name = f"{name}_body"
    
    # Calculate rotation to align with direction
    up = Vector((0, 0, 1))
    axis = up.cross(Vector(direction))
    angle = up.angle(Vector(direction))
    
    arrow_body.rotation_euler = mathutils.Quaternion(axis, angle).to_euler()
    
    # Create cone for arrow head
    bpy.ops.mesh.primitive_cone_add(
        radius1=head_size,
        radius2=0,
        depth=head_size*2,
        location=[start[i] + direction[i]*length*0.95 for i in range(3)]
    )
    
    arrow_head = bpy.context.active_object
    arrow_head.name = f"{name}_head"
    arrow_head.rotation_euler = mathutils.Quaternion(axis, angle).to_euler()
    
    # Create material
    mat = bpy.data.materials.new(name=f"{name}_material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
    
    # Assign material to both parts
    for obj in [arrow_body, arrow_head]:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    
    # Group the objects
    bpy.ops.object.select_all(action='DESELECT')
    arrow_body.select_set(True)
    arrow_head.select_set(True)
    bpy.context.view_layer.objects.active = arrow_body
    bpy.ops.object.join()
    
    return arrow_body

# Create diagram
input_node = create_cube_node("Input", (-3, 0, 0), (0.2, 0.6, 0.9, 1.0))
process_node = create_cube_node("Process", (0, 0, 0), (0.9, 0.6, 0.2, 1.0))
output_node = create_cube_node("Output", (3, 0, 0), (0.2, 0.9, 0.4, 1.0))

# Create connections
arrow1 = create_arrow((-2, 0, 0), (-1, 0, 0), name="Arrow1")
arrow2 = create_arrow((1, 0, 0), (2, 0, 0), name="Arrow2")

# Add text labels
def add_text(text, location, size=0.5):
    bpy.ops.object.text_add(location=location)
    text_obj = bpy.context.active_object
    text_obj.data.body = text
    text_obj.data.size = size
    
    # Align to camera
    text_obj.rotation_euler = (math.radians(90), 0, 0)
    
    # Create material
    mat = bpy.data.materials.new(name=f"{text}_material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    
    # Assign material
    if text_obj.data.materials:
        text_obj.data.materials[0] = mat
    else:
        text_obj.data.materials.append(mat)
    
    return text_obj

add_text("Input", (-3, 0, 0.6))
add_text("Process", (0, 0, 0.6))
add_text("Output", (3, 0, 0.6))

# Set up camera
bpy.ops.object.camera_add(location=(0, -10, 2), rotation=(math.radians(80), 0, 0))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# Set up lighting
bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
sun = bpy.context.active_object
sun.data.energy = 2.0

# Configure render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Set output path
output_file = "//diagram_output.png"
bpy.context.scene.render.filepath = output_file

print("\nBasic diagram created successfully!")
