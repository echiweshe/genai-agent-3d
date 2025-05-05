"""
Enhanced SVG to 3D Conversion Blender Script (v2)

A simplified version that handles basic SVG shapes with improved compatibility with Blender 4.2.
"""

import bpy
import os
import sys
import xml.etree.ElementTree as ET
import traceback
import math
import re

def log(message):
    """Print a message with a prefix."""
    print(f"[SVG2-3D] {message}")

def clean_scene():
    """Remove all objects from the scene."""
    log("Cleaning scene...")
    
    # Deselect all first
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
    """Parse SVG file and extract elements."""
    log(f"Parsing SVG: {svg_path}")
    
    try:
        # Parse SVG file
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Extract namespace if present
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        if '}' in root.tag:
            ns_str = root.tag.split('}')[0].strip('{')
            ns = {'svg': ns_str}
        
        # Get SVG dimensions
        if 'viewBox' in root.attrib:
            viewBox = root.attrib['viewBox'].split()
            width = float(viewBox[2])
            height = float(viewBox[3])
        else:
            width = float(root.attrib.get('width', '800').replace('px', ''))
            height = float(root.attrib.get('height', '600').replace('px', ''))
        
        log(f"SVG dimensions: {width} x {height}")
        
        # Process elements
        elements = []
        
        # Process rectangles
        for rect in root.findall(f".//{{{ns['svg']}}}rect"):
            elements.append({
                'type': 'rect',
                'x': float(rect.attrib.get('x', 0)),
                'y': float(rect.attrib.get('y', 0)),
                'width': float(rect.attrib.get('width', 0)),
                'height': float(rect.attrib.get('height', 0)),
                'rx': float(rect.attrib.get('rx', 0)),
                'ry': float(rect.attrib.get('ry', 0)),
                'fill': rect.attrib.get('fill', '#CCCCCC'),
                'opacity': float(rect.attrib.get('opacity', 1.0))
            })
        
        # Process circles
        for circle in root.findall(f".//{{{ns['svg']}}}circle"):
            elements.append({
                'type': 'circle',
                'cx': float(circle.attrib.get('cx', 0)),
                'cy': float(circle.attrib.get('cy', 0)),
                'r': float(circle.attrib.get('r', 0)),
                'fill': circle.attrib.get('fill', '#CCCCCC'),
                'opacity': float(circle.attrib.get('opacity', 1.0))
            })
        
        # Process ellipses
        for ellipse in root.findall(f".//{{{ns['svg']}}}ellipse"):
            elements.append({
                'type': 'ellipse',
                'cx': float(ellipse.attrib.get('cx', 0)),
                'cy': float(ellipse.attrib.get('cy', 0)),
                'rx': float(ellipse.attrib.get('rx', 0)),
                'ry': float(ellipse.attrib.get('ry', 0)),
                'fill': ellipse.attrib.get('fill', '#CCCCCC'),
                'opacity': float(ellipse.attrib.get('opacity', 1.0))
            })
        
        # Process lines
        for line in root.findall(f".//{{{ns['svg']}}}line"):
            elements.append({
                'type': 'line',
                'x1': float(line.attrib.get('x1', 0)),
                'y1': float(line.attrib.get('y1', 0)),
                'x2': float(line.attrib.get('x2', 0)),
                'y2': float(line.attrib.get('y2', 0)),
                'stroke': line.attrib.get('stroke', '#000000'),
                'stroke-width': float(line.attrib.get('stroke-width', 1)),
                'opacity': float(line.attrib.get('opacity', 1.0))
            })
        
        # Process text elements
        for text in root.findall(f".//{{{ns['svg']}}}text"):
            elements.append({
                'type': 'text',
                'x': float(text.attrib.get('x', 0)),
                'y': float(text.attrib.get('y', 0)),
                'text': text.text or "",
                'fill': text.attrib.get('fill', '#000000'),
                'font-size': float(text.attrib.get('font-size', 12)),
                'opacity': float(text.attrib.get('opacity', 1.0))
            })
        
        log(f"Found {len(elements)} elements")
        return elements, width, height
    
    except Exception as e:
        log(f"Error parsing SVG: {e}")
        traceback.print_exc()
        return [], 800, 600

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

def create_material(name, color_hex, opacity=1.0):
    """Create a material with the given color."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Get the principled BSDF node
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    
    # Set base color and opacity
    if bsdf and color_hex:
        rgb = hex_to_rgb(color_hex)
        bsdf.inputs['Base Color'].default_value = rgb
        
        if opacity < 1.0:
            mat.blend_method = 'BLEND'
            bsdf.inputs['Alpha'].default_value = opacity
    
    return mat

def create_rectangle(element, width, height, extrude_depth=0.1, scale_factor=0.01):
    """Create a 3D rectangle."""
    # Get rectangle properties
    x = (element['x'] - width/2) * scale_factor
    y = (height/2 - element['y']) * scale_factor
    w = element['width'] * scale_factor
    h = element['height'] * scale_factor
    
    # Create cube
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(x + w/2, y - h/2, extrude_depth/2)
    )
    obj = bpy.context.active_object
    obj.scale = (w, h, extrude_depth)
    
    # Set object name
    obj.name = f"Rectangle_{len(bpy.data.objects)}"
    
    # Create and assign material
    color = element.get('fill', '#CCCCCC')
    opacity = element.get('opacity', 1.0)
    
    mat = create_material(f"Material_{len(bpy.data.materials)}", color, opacity)
    obj.data.materials.append(mat)
    
    return obj

def create_circle(element, width, height, extrude_depth=0.1, scale_factor=0.01):
    """Create a 3D circle."""
    # Get circle properties
    cx = (element['cx'] - width/2) * scale_factor
    cy = (height/2 - element['cy']) * scale_factor
    r = element['r'] * scale_factor
    
    # Create cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=r,
        depth=extrude_depth,
        location=(cx, cy, extrude_depth/2)
    )
    obj = bpy.context.active_object
    
    # Set object name
    obj.name = f"Circle_{len(bpy.data.objects)}"
    
    # Create and assign material
    color = element.get('fill', '#CCCCCC')
    opacity = element.get('opacity', 1.0)
    
    mat = create_material(f"Material_{len(bpy.data.materials)}", color, opacity)
    obj.data.materials.append(mat)
    
    return obj

def create_ellipse(element, width, height, extrude_depth=0.1, scale_factor=0.01):
    """Create a 3D ellipse."""
    # Get ellipse properties
    cx = (element['cx'] - width/2) * scale_factor
    cy = (height/2 - element['cy']) * scale_factor
    rx = element['rx'] * scale_factor
    ry = element['ry'] * scale_factor
    
    # Create cylinder and scale
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=1.0,
        depth=extrude_depth,
        location=(cx, cy, extrude_depth/2)
    )
    obj = bpy.context.active_object
    obj.scale.x = rx
    obj.scale.y = ry
    
    # Set object name
    obj.name = f"Ellipse_{len(bpy.data.objects)}"
    
    # Create and assign material
    color = element.get('fill', '#CCCCCC')
    opacity = element.get('opacity', 1.0)
    
    mat = create_material(f"Material_{len(bpy.data.materials)}", color, opacity)
    obj.data.materials.append(mat)
    
    return obj

def create_line(element, width, height, extrude_depth=0.1, scale_factor=0.01):
    """Create a 3D line."""
    # Get line properties
    x1 = (element['x1'] - width/2) * scale_factor
    y1 = (height/2 - element['y1']) * scale_factor
    x2 = (element['x2'] - width/2) * scale_factor
    y2 = (height/2 - element['y2']) * scale_factor
    
    # Calculate center and direction
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    # Calculate line length
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    
    if length < 0.0001:
        log(f"Line too short to create")
        return None
    
    # Get line thickness
    stroke_width = element.get('stroke-width', 1) * scale_factor
    
    # Create cylinder for line
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=stroke_width / 2,
        depth=length,
        location=(center_x, center_y, 0)
    )
    obj = bpy.context.active_object
    
    # Rotate to align with line direction
    direction = math.atan2(dy, dx)
    obj.rotation_euler = (math.pi/2, 0, direction)
    
    # Set object name
    obj.name = f"Line_{len(bpy.data.objects)}"
    
    # Create and assign material
    color = element.get('stroke', '#000000')
    opacity = element.get('opacity', 1.0)
    
    mat = create_material(f"Material_{len(bpy.data.materials)}", color, opacity)
    obj.data.materials.append(mat)
    
    return obj

def create_text(element, width, height, extrude_depth=0.1, scale_factor=0.01):
    """Create 3D text."""
    # Get text properties
    x = (element['x'] - width/2) * scale_factor
    y = (height/2 - element['y']) * scale_factor
    text_content = element['text']
    
    if not text_content:
        log(f"Text element has no content")
        return None
    
    # Create text object
    bpy.ops.object.text_add(location=(x, y, 0))
    obj = bpy.context.active_object
    
    # Set text content and properties
    obj.data.body = text_content
    
    # Get font size
    font_size = element.get('font-size', 12) * scale_factor
    obj.data.size = font_size
    
    # Set extrusion
    obj.data.extrude = extrude_depth / 2
    
    # Set object name
    obj.name = f"Text_{len(bpy.data.objects)}"
    
    # Create and assign material
    color = element.get('fill', '#000000')
    opacity = element.get('opacity', 1.0)
    
    mat = create_material(f"Material_{len(bpy.data.materials)}", color, opacity)
    obj.data.materials.append(mat)
    
    return obj

def setup_camera_and_lighting():
    """Set up a camera and lighting for the scene."""
    log("Setting up camera and lighting")
    
    # Add camera
    bpy.ops.object.camera_add(location=(0, -5, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(45), 0, 0)
    
    # Make this the active camera
    bpy.context.scene.camera = camera
    
    # Add a sun light
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    # Add fill light
    bpy.ops.object.light_add(type='AREA', location=(-3, 3, 3))
    area = bpy.context.active_object
    area.data.energy = 1.5
    area.scale = (5, 5, 1)
    
    log("Camera and lighting setup complete")

def create_object(element, width, height, extrude_depth=0.1, scale_factor=0.01):
    """Create a 3D object based on the element type."""
    if element['type'] == 'rect':
        return create_rectangle(element, width, height, extrude_depth, scale_factor)
    elif element['type'] == 'circle':
        return create_circle(element, width, height, extrude_depth, scale_factor)
    elif element['type'] == 'ellipse':
        return create_ellipse(element, width, height, extrude_depth, scale_factor)
    elif element['type'] == 'line':
        return create_line(element, width, height, extrude_depth, scale_factor)
    elif element['type'] == 'text':
        return create_text(element, width, height, extrude_depth, scale_factor)
    else:
        log(f"Unsupported element type: {element['type']}")
        return None

def convert_svg_to_3d(svg_path, output_path, extrude_depth=0.1, scale_factor=0.01):
    """Convert an SVG file to a 3D Blender scene."""
    log(f"Converting SVG: {svg_path} to 3D model: {output_path}")
    
    try:
        # Clean the scene
        clean_scene()
        
        # Parse SVG
        elements, width, height = parse_svg(svg_path)
        
        if not elements:
            log("No valid elements found in SVG")
            return False
        
        log(f"Creating 3D objects for {len(elements)} elements")
        
        # Create 3D objects
        for i, element in enumerate(elements):
            log(f"Processing element {i+1}/{len(elements)}: {element['type']}")
            create_object(element, width, height, extrude_depth, scale_factor)
        
        # Set up camera and lighting
        setup_camera_and_lighting()
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save the file
        log(f"Saving Blender file to: {output_path}")
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        
        log(f"Conversion completed successfully!")
        return True
        
    except Exception as e:
        log(f"Error converting SVG to 3D: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to parse arguments and run conversion."""
    log("Starting SVG to 3D conversion")
    
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
        log("Usage: blender --background --python enhanced_svg_to_3d_v2.py -- input.svg output.blend [extrude_depth] [scale_factor]")
        sys.exit(1)

# Run main function
if __name__ == "__main__":
    main()
