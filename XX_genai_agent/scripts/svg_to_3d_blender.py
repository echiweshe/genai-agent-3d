"""
SVG to 3D Conversion Blender Script

This script is executed by Blender to convert SVG elements to 3D objects.
It parses an SVG file and creates corresponding 3D objects in Blender.

Usage:
    blender --background --python svg_to_3d_blender.py -- input.svg output.blend
"""

import bpy
import os
import sys
import xml.etree.ElementTree as ET
import mathutils

def clean_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Also remove all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

def parse_svg(svg_path):
    """Parse SVG file and extract elements."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Extract namespace if present
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Extract viewBox dimensions
    if 'viewBox' in root.attrib:
        viewBox = root.attrib['viewBox'].split()
        width = float(viewBox[2])
        height = float(viewBox[3])
    else:
        width = float(root.attrib.get('width', 800))
        height = float(root.attrib.get('height', 600))
    
    elements = []
    
    # Process all elements
    for elem in root.findall('.//*', ns):
        tag = elem.tag
        if ns:
            # Remove namespace prefix if present
            tag = tag.split('}')[-1]
            
        if tag == 'rect':
            # Process rectangle
            x = float(elem.attrib.get('x', 0))
            y = float(elem.attrib.get('y', 0))
            w = float(elem.attrib.get('width', 0))
            h = float(elem.attrib.get('height', 0))
            fill = elem.attrib.get('fill', '#CCCCCC')
            stroke = elem.attrib.get('stroke')
            stroke_width = float(elem.attrib.get('stroke-width', 1))
            
            elements.append({
                'type': 'rect',
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'fill': fill,
                'stroke': stroke,
                'stroke_width': stroke_width
            })
        
        elif tag == 'circle':
            # Process circle
            cx = float(elem.attrib.get('cx', 0))
            cy = float(elem.attrib.get('cy', 0))
            r = float(elem.attrib.get('r', 0))
            fill = elem.attrib.get('fill', '#CCCCCC')
            stroke = elem.attrib.get('stroke')
            stroke_width = float(elem.attrib.get('stroke-width', 1))
            
            elements.append({
                'type': 'circle',
                'cx': cx,
                'cy': cy,
                'r': r,
                'fill': fill,
                'stroke': stroke,
                'stroke_width': stroke_width
            })
        
        elif tag == 'ellipse':
            # Process ellipse
            cx = float(elem.attrib.get('cx', 0))
            cy = float(elem.attrib.get('cy', 0))
            rx = float(elem.attrib.get('rx', 0))
            ry = float(elem.attrib.get('ry', 0))
            fill = elem.attrib.get('fill', '#CCCCCC')
            stroke = elem.attrib.get('stroke')
            stroke_width = float(elem.attrib.get('stroke-width', 1))
            
            elements.append({
                'type': 'ellipse',
                'cx': cx,
                'cy': cy,
                'rx': rx,
                'ry': ry,
                'fill': fill,
                'stroke': stroke,
                'stroke_width': stroke_width
            })
        
        elif tag == 'line':
            # Process line
            x1 = float(elem.attrib.get('x1', 0))
            y1 = float(elem.attrib.get('y1', 0))
            x2 = float(elem.attrib.get('x2', 0))
            y2 = float(elem.attrib.get('y2', 0))
            stroke = elem.attrib.get('stroke', '#000000')
            stroke_width = float(elem.attrib.get('stroke-width', 1))
            
            elements.append({
                'type': 'line',
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'stroke': stroke,
                'stroke_width': stroke_width
            })
        
        elif tag == 'text':
            # Process text
            x = float(elem.attrib.get('x', 0))
            y = float(elem.attrib.get('y', 0))
            text_content = elem.text or ""
            fill = elem.attrib.get('fill', '#000000')
            font_size = float(elem.attrib.get('font-size', 12))
            
            elements.append({
                'type': 'text',
                'x': x,
                'y': y,
                'text': text_content,
                'fill': fill,
                'font_size': font_size
            })
        
        elif tag == 'path':
            # Process path (simplified)
            # Note: Full path parsing is complex and not implemented here
            d = elem.attrib.get('d', '')
            fill = elem.attrib.get('fill', 'none')
            stroke = elem.attrib.get('stroke', '#000000')
            stroke_width = float(elem.attrib.get('stroke-width', 1))
            
            elements.append({
                'type': 'path',
                'd': d,
                'fill': fill,
                'stroke': stroke,
                'stroke_width': stroke_width
            })
    
    return elements, width, height

def hex_to_rgb(hex_color):
    """Convert hex color to RGB values."""
    if not hex_color or not isinstance(hex_color, str):
        return (0.8, 0.8, 0.8, 1.0)  # Default color
        
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        # Short form (#RGB)
        hex_color = ''.join([c + c for c in hex_color])
    
    # Convert to RGB values between 0 and 1
    try:
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b, 1.0)
    except ValueError:
        # Return a default color if conversion fails
        return (0.8, 0.8, 0.8, 1.0)

def create_material(name, color_hex=None, is_emissive=False):
    """Create a material with the given color."""
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    
    # Get the nodes and links
    nodes = material.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')
    
    if color_hex:
        rgb = hex_to_rgb(color_hex)
        bsdf.inputs['Base Color'].default_value = rgb
        
        if is_emissive:
            bsdf.inputs['Emission'].default_value = rgb
            bsdf.inputs['Emission Strength'].default_value = 1.0
    
    return material

def create_3d_object(element, max_width, max_height):
    """Convert an SVG element to a 3D Blender object."""
    if element['type'] == 'rect':
        # Create a cube for rectangle
        x = (element['x'] - max_width/2) * 0.01  # Scale and center
        y = (max_height/2 - element['y']) * 0.01  # Scale, center, and flip Y
        
        width = element['width'] * 0.01
        height = element['height'] * 0.01
        depth = 0.1  # Fixed depth for now
        
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x + width/2, y - height/2, 0)
        )
        obj = bpy.context.active_object
        obj.scale = (width, height, depth)
        
        # Create material
        material_name = f"Rect_Material_{len(bpy.data.materials)}"
        material = create_material(material_name, element.get('fill'))
        
        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
    elif element['type'] == 'circle':
        # Create a cylinder for circle
        cx = (element['cx'] - max_width/2) * 0.01
        cy = (max_height/2 - element['cy']) * 0.01
        r = element['r'] * 0.01
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r,
            depth=0.1,
            location=(cx, cy, 0)
        )
        obj = bpy.context.active_object
        
        # Create material
        material_name = f"Circle_Material_{len(bpy.data.materials)}"
        material = create_material(material_name, element.get('fill'))
        
        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
    elif element['type'] == 'ellipse':
        # Create a cylinder for ellipse and scale it
        cx = (element['cx'] - max_width/2) * 0.01
        cy = (max_height/2 - element['cy']) * 0.01
        rx = element['rx'] * 0.01
        ry = element['ry'] * 0.01
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1,  # Will be scaled
            depth=0.1,
            location=(cx, cy, 0)
        )
        obj = bpy.context.active_object
        obj.scale = (rx, ry, 0.05)
        
        # Create material
        material_name = f"Ellipse_Material_{len(bpy.data.materials)}"
        material = create_material(material_name, element.get('fill'))
        
        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
    elif element['type'] == 'line':
        # Create a line/cylinder for connecting elements
        x1 = (element['x1'] - max_width/2) * 0.01
        y1 = (max_height/2 - element['y1']) * 0.01
        x2 = (element['x2'] - max_width/2) * 0.01
        y2 = (max_height/2 - element['y2']) * 0.01
        
        # Calculate center point
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Calculate direction vector
        direction = mathutils.Vector((x2 - x1, y2 - y1, 0))
        length = direction.length
        
        # Determine line thickness from stroke width
        thickness = element.get('stroke_width', 1) * 0.005  # Scale factor
        
        # Create cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=thickness,
            depth=length,
            location=(center_x, center_y, 0)
        )
        obj = bpy.context.active_object
        
        # Align cylinder with line direction
        if length > 0:
            direction.normalize()
            # Get the default cylinder orientation (z-axis)
            up_vector = mathutils.Vector((0, 0, 1))
            # Calculate rotation quaternion
            quaternion = up_vector.rotation_difference(
                mathutils.Vector((direction.x, direction.y, 0)).normalized()
            )
            obj.rotation_euler = quaternion.to_euler()
            # Rotate 90 degrees on local X axis to align with line
            obj.rotation_euler.x += 1.5708  # 90 degrees in radians
        
        # Create material for the line
        material_name = f"Line_Material_{len(bpy.data.materials)}"
        material = create_material(material_name, element.get('stroke'))
        
        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
    elif element['type'] == 'text':
        # Create 3D text
        x = (element['x'] - max_width/2) * 0.01
        y = (max_height/2 - element['y']) * 0.01
        
        # Create text object
        bpy.ops.object.text_add(location=(x, y, 0.05))  # Slightly raised above other elements
        text_obj = bpy.context.active_object
        text_obj.data.body = element['text']
        
        # Set text properties
        text_obj.data.size = element.get('font_size', 12) * 0.01  # Scale font size
        text_obj.data.extrude = 0.02  # Give some depth to the text
        
        # Create material
        material_name = f"Text_Material_{len(bpy.data.materials)}"
        material = create_material(material_name, element.get('fill'))
        
        # Assign material
        if text_obj.data.materials:
            text_obj.data.materials[0] = material
        else:
            text_obj.data.materials.append(material)
    
    elif element['type'] == 'path':
        # Creating a path is complex and requires path parsing
        # This is a placeholder for path handling
        pass

def setup_camera_and_lighting():
    """Set up camera and lighting for the scene."""
    # Add camera
    bpy.ops.object.camera_add(location=(0, -5, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.0, 0, 0)
    
    # Make this the active camera
    bpy.context.scene.camera = camera
    
    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    # Add ambient light
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    area = bpy.context.active_object
    area.data.energy = 3.0
    area.scale = (10, 10, 1)

def convert_svg_to_3d(svg_path, output_path):
    """Convert an SVG file to a 3D Blender scene."""
    print(f"Converting SVG: {svg_path} to 3D model: {output_path}")
    
    # Clean the scene
    clean_scene()
    
    # Parse SVG
    elements, width, height = parse_svg(svg_path)
    print(f"Parsed {len(elements)} elements from SVG with dimensions {width}x{height}")
    
    # Create 3D objects for each element
    for i, element in enumerate(elements):
        print(f"Creating 3D object for element {i+1}: {element['type']}")
        create_3d_object(element, width, height)
    
    # Setup camera and lighting
    setup_camera_and_lighting()
    
    # Save the file
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    
    print(f"Successfully converted SVG to 3D model: {output_path}")
    return output_path

# For command-line execution from Blender
if __name__ == "__main__":
    # Get args after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    if len(argv) >= 2:
        svg_path = argv[0]
        output_path = argv[1]
        convert_svg_to_3d(svg_path, output_path)
    else:
        print("Usage: blender --background --python svg_to_3d_blender.py -- input.svg output.blend")
        sys.exit(1)
