"""
Minimal SVG to 3D Converter for Blender 4.2

This is a stripped-down version of the converter with maximum compatibility
for Blender 4.2. It focuses on basic rectangle and circle conversion only.

Usage:
    blender --background --python minimal_svg_to_3d.py -- input.svg output.blend
"""

import bpy
import os
import sys
import xml.etree.ElementTree as ET
import traceback

def log(message):
    """Print a message with a prefix."""
    print(f"[MINIMAL] {message}")

def clean_scene():
    """Remove all objects from the scene."""
    log("Cleaning scene...")
    
    # Deselect all first (Blender 2.8+ compatibility)
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select and delete all objects
    for obj in bpy.data.objects:
        obj.select_set(True)
    
    # Delete selected objects
    if bpy.context.selected_objects:
        bpy.ops.object.delete()
    
    # Clean materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    log("Scene cleaned")

def parse_svg(svg_path):
    """Parse SVG file and extract basic elements."""
    log(f"Parsing SVG: {svg_path}")
    
    # Parse SVG file
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Get SVG dimensions
    if 'viewBox' in root.attrib:
        viewBox = root.attrib['viewBox'].split()
        width = float(viewBox[2])
        height = float(viewBox[3])
    else:
        width = float(root.attrib.get('width', '800').replace('px', ''))
        height = float(root.attrib.get('height', '600').replace('px', ''))
    
    log(f"SVG dimensions: {width}x{height}")
    
    # Extract basic elements
    elements = []
    
    # Find all rectangles
    for rect in root.findall('.//{http://www.w3.org/2000/svg}rect'):
        x = float(rect.attrib.get('x', 0))
        y = float(rect.attrib.get('y', 0))
        w = float(rect.attrib.get('width', 0))
        h = float(rect.attrib.get('height', 0))
        fill = rect.attrib.get('fill', '#CCCCCC')
        
        elements.append({
            'type': 'rect',
            'x': x,
            'y': y,
            'width': w,
            'height': h,
            'fill': fill
        })
        log(f"Found rectangle at ({x}, {y}) with size {w}x{h}")
    
    # Find all circles
    for circle in root.findall('.//{http://www.w3.org/2000/svg}circle'):
        cx = float(circle.attrib.get('cx', 0))
        cy = float(circle.attrib.get('cy', 0))
        r = float(circle.attrib.get('r', 0))
        fill = circle.attrib.get('fill', '#CCCCCC')
        
        elements.append({
            'type': 'circle',
            'cx': cx,
            'cy': cy,
            'r': r,
            'fill': fill
        })
        log(f"Found circle at ({cx}, {cy}) with radius {r}")
    
    log(f"Found {len(elements)} basic elements")
    return elements, width, height

def hex_to_rgb(hex_color):
    """Convert hex color to RGB values."""
    if not hex_color or not isinstance(hex_color, str):
        return (0.8, 0.8, 0.8, 1.0)  # Default color
    
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Handle shorthand hex
    if len(hex_color) == 3:
        hex_color = ''.join([c + c for c in hex_color])
    
    # Convert to RGB
    try:
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b, 1.0)
    except (ValueError, IndexError):
        return (0.8, 0.8, 0.8, 1.0)  # Default gray

def create_material(name, color_hex):
    """Create a material with the given color."""
    log(f"Creating material: {name} with color {color_hex}")
    
    # Create new material
    mat = bpy.data.materials.new(name=name)
    
    # Enable nodes
    mat.use_nodes = True
    
    # Get the principled BSDF node
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    
    # Set base color
    if bsdf and color_hex:
        bsdf.inputs['Base Color'].default_value = hex_to_rgb(color_hex)
    
    return mat

def create_rectangle(element, width, height, depth=0.1, scale=0.01):
    """Create a 3D rectangle."""
    log(f"Creating 3D rectangle")
    
    # Get rectangle properties
    x = (element['x'] - width/2) * scale
    y = (height/2 - element['y']) * scale
    w = element['width'] * scale
    h = element['height'] * scale
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(x + w/2, y - h/2, depth/2)
    )
    
    # Get the created object
    obj = bpy.context.active_object
    
    # Scale to match rectangle dimensions
    obj.scale = (w, h, depth)
    
    # Create and assign material
    mat = create_material(f"Rect_Material_{len(bpy.data.materials)}", element['fill'])
    obj.data.materials.append(mat)
    
    # Set object name
    obj.name = f"Rectangle_{len(bpy.data.objects)}"
    
    log(f"Created rectangle: {obj.name}")
    return obj

def create_circle(element, width, height, depth=0.1, scale=0.01):
    """Create a 3D circle."""
    log(f"Creating 3D circle")
    
    # Get circle properties
    cx = (element['cx'] - width/2) * scale
    cy = (height/2 - element['cy']) * scale
    r = element['r'] * scale
    
    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=r,
        depth=depth,
        location=(cx, cy, depth/2)
    )
    
    # Get the created object
    obj = bpy.context.active_object
    
    # Create and assign material
    mat = create_material(f"Circle_Material_{len(bpy.data.materials)}", element['fill'])
    obj.data.materials.append(mat)
    
    # Set object name
    obj.name = f"Circle_{len(bpy.data.objects)}"
    
    log(f"Created circle: {obj.name}")
    return obj

def setup_camera_and_lighting():
    """Set up a simple camera and lighting."""
    log("Setting up camera and lighting")
    
    # Add camera
    bpy.ops.object.camera_add(location=(0, -5, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.0, 0, 0)
    
    # Make this the active camera
    bpy.context.scene.camera = camera
    
    # Add a sun light
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    log("Camera and lighting set up")

def convert_svg_to_3d(svg_path, output_path, extrude_depth=0.1, scale_factor=0.01):
    """Convert an SVG file to a 3D Blender scene."""
    log(f"Converting SVG: {svg_path} to 3D: {output_path}")
    
    try:
        # Clean the scene
        clean_scene()
        
        # Parse SVG
        elements, width, height = parse_svg(svg_path)
        
        # Create 3D objects
        for element in elements:
            if element['type'] == 'rect':
                create_rectangle(element, width, height, extrude_depth, scale_factor)
            elif element['type'] == 'circle':
                create_circle(element, width, height, extrude_depth, scale_factor)
        
        # Set up camera and lighting
        setup_camera_and_lighting()
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save the file
        log(f"Saving 3D model to: {output_path}")
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        
        log(f"Conversion complete!")
        return True
    
    except Exception as e:
        log(f"Error converting SVG to 3D: {e}")
        traceback.print_exc()
        return False

# Main function for command-line execution
if __name__ == "__main__":
    log("Starting minimal SVG to 3D conversion")
    
    # Get command line arguments
    argv = sys.argv
    
    # Get args after '--'
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    if len(argv) >= 2:
        svg_path = argv[0]
        output_path = argv[1]
        
        # Get optional parameters
        extrude_depth = 0.1
        scale_factor = 0.01
        
        if len(argv) >= 3:
            try:
                extrude_depth = float(argv[2])
            except ValueError:
                log(f"Invalid extrude depth: {argv[2]}, using default: 0.1")
        
        if len(argv) >= 4:
            try:
                scale_factor = float(argv[3])
            except ValueError:
                log(f"Invalid scale factor: {argv[3]}, using default: 0.01")
        
        # Convert SVG to 3D
        result = convert_svg_to_3d(svg_path, output_path, extrude_depth, scale_factor)
        
        if result:
            log("Conversion completed successfully")
            sys.exit(0)
        else:
            log("Conversion failed")
            sys.exit(1)
    else:
        log("Usage: blender --background --python minimal_svg_to_3d.py -- input.svg output.blend [extrude_depth] [scale_factor]")
        sys.exit(1)
