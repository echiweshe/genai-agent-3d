"""
Enhanced SVG to 3D Conversion Blender Script (DEBUG VERSION)

This script is executed by Blender to convert SVG elements to 3D objects.
It includes extra debug output and error handling.

Usage:
    blender --background --python enhanced_svg_to_3d_blender_debug.py -- --svg input.svg --output output.blend [--extrude 0.1] [--scale 1.0] [--debug]
"""

import bpy
import os
import sys
import xml.etree.ElementTree as ET
import traceback
import argparse

# Ensure we can find our script
script_dir = os.path.dirname(os.path.realpath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Function to log messages
def log(message, error=False):
    if error:
        print(f"[ERROR] {message}", file=sys.stderr)
    else:
        print(f"[INFO] {message}")

# Function to clean the scene
def clean_scene():
    """Remove all objects from the scene."""
    log("Cleaning scene...")
    try:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        
        # Also remove all materials
        for material in bpy.data.materials:
            bpy.data.materials.remove(material)
    except Exception as e:
        log(f"Error cleaning scene: {e}", error=True)
        traceback.print_exc()

# Function to parse SVG file
def parse_svg(svg_path):
    """Parse SVG file and extract basic elements."""
    log(f"Parsing SVG file: {svg_path}")
    try:
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
        
        log(f"SVG dimensions: {width}x{height}")
        
        # Extract some basic elements for test purposes
        elements = []
        
        # Process rectangles
        for elem in root.findall('.//rect', ns):
            x = float(elem.attrib.get('x', 0))
            y = float(elem.attrib.get('y', 0))
            w = float(elem.attrib.get('width', 0))
            h = float(elem.attrib.get('height', 0))
            fill = elem.attrib.get('fill', '#CCCCCC')
            
            elements.append({
                'type': 'rect',
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'fill': fill
            })
        
        # Process circles
        for elem in root.findall('.//circle', ns):
            cx = float(elem.attrib.get('cx', 0))
            cy = float(elem.attrib.get('cy', 0))
            r = float(elem.attrib.get('r', 0))
            fill = elem.attrib.get('fill', '#CCCCCC')
            
            elements.append({
                'type': 'circle',
                'cx': cx,
                'cy': cy,
                'r': r,
                'fill': fill
            })
        
        log(f"Parsed {len(elements)} elements from SVG")
        return elements, width, height
        
    except Exception as e:
        log(f"Error parsing SVG file: {e}", error=True)
        traceback.print_exc()
        return [], 800, 600

# Function to convert hex color to RGB
def hex_to_rgb(hex_color):
    """Convert hex color to RGB values."""
    try:
        if not hex_color or not isinstance(hex_color, str):
            return (0.8, 0.8, 0.8, 1.0)  # Default color
            
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            # Short form (#RGB)
            hex_color = ''.join([c + c for c in hex_color])
        
        # Convert to RGB values between 0 and 1
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b, 1.0)
    except Exception as e:
        log(f"Error converting hex to RGB: {e}", error=True)
        return (0.8, 0.8, 0.8, 1.0)  # Default gray

# Function to create a material
def create_material(name, color_hex=None):
    """Create a material with the given color."""
    try:
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        
        # Get the nodes and links
        nodes = material.node_tree.nodes
        bsdf = nodes.get('Principled BSDF')
        
        if color_hex:
            rgb = hex_to_rgb(color_hex)
            bsdf.inputs['Base Color'].default_value = rgb
        
        return material
    except Exception as e:
        log(f"Error creating material: {e}", error=True)
        return None

# Function to create a 3D object
def create_3d_object(element, max_width, max_height, extrude_depth=0.1, scale_factor=0.01):
    """Create a basic 3D object from SVG element."""
    log(f"Creating 3D object for {element['type']}")
    try:
        if element['type'] == 'rect':
            # Create a cube for rectangle
            x = (element['x'] - max_width/2) * scale_factor
            y = (max_height/2 - element['y']) * scale_factor
            
            width = element['width'] * scale_factor
            height = element['height'] * scale_factor
            depth = extrude_depth
            
            log(f"Creating rectangle at ({x}, {y}) with dimensions {width}x{height}x{depth}")
            
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
            if material:
                if obj.data.materials:
                    obj.data.materials[0] = material
                else:
                    obj.data.materials.append(material)
        
        elif element['type'] == 'circle':
            # Create a cylinder for circle
            cx = (element['cx'] - max_width/2) * scale_factor
            cy = (max_height/2 - element['cy']) * scale_factor
            r = element['r'] * scale_factor
            
            log(f"Creating circle at ({cx}, {cy}) with radius {r}")
            
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=32,
                radius=r,
                depth=extrude_depth,
                location=(cx, cy, 0)
            )
            obj = bpy.context.active_object
            
            # Create material
            material_name = f"Circle_Material_{len(bpy.data.materials)}"
            material = create_material(material_name, element.get('fill'))
            
            # Assign material
            if material:
                if obj.data.materials:
                    obj.data.materials[0] = material
                else:
                    obj.data.materials.append(material)
    
    except Exception as e:
        log(f"Error creating 3D object: {e}", error=True)
        traceback.print_exc()

# Function to add a camera and lighting
def setup_camera_and_lighting():
    """Set up camera and lighting for the scene."""
    log("Setting up camera and lighting...")
    try:
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
    except Exception as e:
        log(f"Error setting up camera and lighting: {e}", error=True)
        traceback.print_exc()

# Main function to convert SVG to 3D
def convert_svg_to_3d(svg_path, output_path, extrude_depth=0.1, scale_factor=0.01):
    """Convert an SVG file to a 3D Blender scene."""
    log(f"Converting SVG: {svg_path} to 3D model: {output_path}")
    
    # Check if SVG file exists
    if not os.path.isfile(svg_path):
        log(f"SVG file not found: {svg_path}", error=True)
        return False
    
    try:
        # Clean the scene
        clean_scene()
        
        # Parse SVG
        elements, width, height = parse_svg(svg_path)
        log(f"Processing {len(elements)} elements with dimensions {width}x{height}")
        
        # Create 3D objects
        for i, element in enumerate(elements):
            log(f"Creating 3D object {i+1} of {len(elements)}: {element['type']}")
            create_3d_object(element, width, height, extrude_depth, scale_factor)
        
        # Setup camera and lighting
        setup_camera_and_lighting()
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save the file
        log(f"Saving 3D model to: {output_path}")
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        
        log(f"Successfully converted SVG to 3D model!")
        return True
    except Exception as e:
        log(f"Error converting SVG to 3D: {e}", error=True)
        traceback.print_exc()
        return False

# Function to parse command line arguments
def parse_args():
    """Parse command line arguments."""
    log("Parsing command line arguments...")
    parser = argparse.ArgumentParser(description="Convert SVG to 3D model using Blender")
    parser.add_argument("--svg", required=True, help="Path to the SVG file")
    parser.add_argument("--output", required=True, help="Path to the output Blender file")
    parser.add_argument("--extrude", type=float, default=0.1, help="Extrusion depth for 3D objects")
    parser.add_argument("--scale", type=float, default=0.01, help="Scale factor for SVG to Blender space")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    # Ensure that argv exists (Blender might not pass proper sys.argv)
    try:
        if "--" in sys.argv:
            args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
        else:
            log("No command line args found. Using defaults.", error=True)
            args = parser.parse_args([])
    except Exception as e:
        log(f"Error parsing args: {e}", error=True)
        args = parser.Namespace(svg='', output='', extrude=0.1, scale=0.01, debug=True)
    
    return args

# Main execution
if __name__ == "__main__":
    log("Starting SVG to 3D conversion script")
    try:
        # Get command line arguments
        args = parse_args()
        
        if args.svg and args.output:
            log(f"Running conversion with:")
            log(f"  SVG: {args.svg}")
            log(f"  Output: {args.output}")
            log(f"  Extrude: {args.extrude}")
            log(f"  Scale: {args.scale}")
            log(f"  Debug: {args.debug}")
            
            result = convert_svg_to_3d(
                args.svg,
                args.output,
                extrude_depth=args.extrude,
                scale_factor=args.scale
            )
            
            if result:
                log("Conversion completed successfully")
                sys.exit(0)
            else:
                log("Conversion failed", error=True)
                sys.exit(1)
        else:
            log("Missing required arguments: --svg and --output", error=True)
            sys.exit(1)
    except Exception as e:
        log(f"Unhandled exception: {e}", error=True)
        traceback.print_exc()
        sys.exit(1)
