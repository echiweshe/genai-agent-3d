"""
Enhanced SVG to 3D Conversion Blender Script (Part 2)

A Blender script for converting SVG files to 3D models with:
- 3D object creation for SVG elements
- Material creation and assignment
- Support for complex shapes and paths
- Camera and lighting setup
"""

import bpy
import os
import sys
import traceback
import math
from mathutils import Vector, Matrix

# Import Part 1: SVG Parser
# SVGParser class should be defined in the same file or imported here

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

class SVGTo3DConverter:
    """Convert SVG elements to 3D Blender objects."""
    
    def __init__(self, svg_path, extrude_depth=0.1, scale_factor=0.01, debug=False):
        """
        Initialize the SVG to 3D converter.
        
        Args:
            svg_path: Path to the SVG file
            extrude_depth: Depth for 3D extrusion (default: 0.1)
            scale_factor: Scale factor for SVG to Blender space (default: 0.01)
            debug: Enable debug output
        """
        self.svg_path = svg_path
        self.extrude_depth = extrude_depth
        self.scale_factor = scale_factor
        self.debug = debug
        self.parser = SVGParser(svg_path, debug)
        self.width = 0
        self.height = 0
        self.elements = []
        self.material_cache = {}
        self.group_objects = {}
    
    def debug_log(self, message):
        """Debug logging function."""
        if self.debug:
            log(f"DEBUG: {message}")
    
    def create_material(self, name, color_hex=None, opacity=1.0, is_emissive=False):
        """
        Create a material with the given color.
        
        Args:
            name: Material name
            color_hex: Hex color string (e.g., '#FF0000')
            opacity: Opacity value (0.0 to 1.0)
            is_emissive: Whether to make the material emissive
            
        Returns:
            The created Blender material
        """
        # Check if material already exists in cache
        cache_key = f"{name}_{color_hex}_{opacity}_{is_emissive}"
        if cache_key in self.material_cache:
            return self.material_cache[cache_key]
            
        # Create new material
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
        
        # Cache the material
        self.material_cache[cache_key] = mat
        
        return mat
    
    def apply_material_to_object(self, obj, style):
        """
        Apply material to an object based on style attributes.
        
        Args:
            obj: Blender object
            style: Style dictionary with 'fill', 'stroke', etc.
        """
        # Determine color and opacity
        color = style.get('fill', '#CCCCCC')
        opacity = float(style.get('opacity', 1.0))
        
        if not color or color == 'none':
            # Use stroke color if fill is not specified
            color = style.get('stroke', '#000000')
            if not color or color == 'none':
                color = '#CCCCCC'  # Default gray
        
        # Create material name based on color
        material_name = f"Material_{color.replace('#', '')}"
        
        # Create material
        material = self.create_material(material_name, color, opacity)
        
        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
        
        return material
    
    def create_3d_rect(self, element):
        """Create a 3D rectangle from SVG rect element."""
        x = (element['x'] - self.width/2) * self.scale_factor
        y = (self.height/2 - element['y'] - element['height']) * self.scale_factor
        width = element['width'] * self.scale_factor
        height = element['height'] * self.scale_factor
        rx = element.get('rx', 0) * self.scale_factor
        ry = element.get('ry', 0) * self.scale_factor
        
        # Create mesh
        if rx > 0 or ry > 0:
            # Create rounded rectangle
            # This is a simplified approach - for proper rounded rect we'd need to use Bezier curves
            # or create a more complex mesh
            bpy.ops.mesh.primitive_circle_add(
                vertices=32,
                radius=1.0,
                location=(x + width/2, y + height/2, 0)
            )
            obj = bpy.context.active_object
            obj.scale = (width/2, height/2, 1)
            
            # Extrude for 3D
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate=(0, 0, self.extrude_depth)
            )
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            # Create standard rectangle
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(x + width/2, y + height/2, self.extrude_depth/2)
            )
            obj = bpy.context.active_object
            obj.scale = (width, height, self.extrude_depth)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Rect_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_circle(self, element):
        """Create a 3D circle from SVG circle element."""
        cx = (element['cx'] - self.width/2) * self.scale_factor
        cy = (self.height/2 - element['cy']) * self.scale_factor
        r = element['r'] * self.scale_factor
        
        # Create cylinder for circle
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=r,
            depth=self.extrude_depth,
            location=(cx, cy, self.extrude_depth/2)
        )
        obj = bpy.context.active_object
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Circle_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_ellipse(self, element):
        """Create a 3D ellipse from SVG ellipse element."""
        cx = (element['cx'] - self.width/2) * self.scale_factor
        cy = (self.height/2 - element['cy']) * self.scale_factor
        rx = element['rx'] * self.scale_factor
        ry = element['ry'] * self.scale_factor
        
        # Create cylinder and scale to make ellipse
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=1.0,
            depth=self.extrude_depth,
            location=(cx, cy, self.extrude_depth/2)
        )
        obj = bpy.context.active_object
        obj.scale = (rx, ry, 1.0)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Ellipse_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_line(self, element):
        """Create a 3D line from SVG line element."""
        x1 = (element['x1'] - self.width/2) * self.scale_factor
        y1 = (self.height/2 - element['y1']) * self.scale_factor
        x2 = (element['x2'] - self.width/2) * self.scale_factor
        y2 = (self.height/2 - element['y2']) * self.scale_factor
        
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
        stroke_width = float(element['style'].get('stroke-width', 1))
        thickness = stroke_width * self.scale_factor * 0.5  # Adjust for visual consistency
        
        # Create cylinder for line
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=thickness,
            depth=length,
            location=(center_x, center_y, self.extrude_depth/2)
        )
        obj = bpy.context.active_object
        
        # Rotate to align with line direction
        direction = math.atan2(dy, dx)
        obj.rotation_euler = (math.pi/2, 0, direction)
        
        # Apply material
        stroke_style = element['style'].copy()
        if 'stroke' in stroke_style:
            stroke_style['fill'] = stroke_style['stroke']  # Use stroke color as fill
        self.apply_material_to_object(obj, stroke_style)
        
        # Set object name
        obj.name = f"Line_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_polyline(self, element):
        """Create a 3D polyline from SVG polyline element."""
        points = element['points']
        if len(points) < 2:
            return None
            
        # Create mesh for polyline
        mesh = bpy.data.meshes.new(name="Polyline")
        obj = bpy.data.objects.new("Polyline", mesh)
        
        # Add vertices
        vertices = []
        edges = []
        
        for i, (x, y) in enumerate(points):
            # Convert to Blender coordinates
            bx = (x - self.width/2) * self.scale_factor
            by = (self.height/2 - y) * self.scale_factor
            vertices.append((bx, by, 0))
            
            if i > 0:
                edges.append((i-1, i))
        
        # Create the mesh
        mesh.from_pydata(vertices, edges, [])
        mesh.update()
        
        # Add to scene
        bpy.context.collection.objects.link(obj)
        
        # Apply material (using stroke color for lines)
        stroke_style = element['style'].copy()
        if 'stroke' in stroke_style:
            stroke_style['fill'] = stroke_style['stroke']  # Use stroke color as fill
        self.apply_material_to_object(obj, stroke_style)
        
        # Add thickness using bevel modifier
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        stroke_width = float(element['style'].get('stroke-width', 1))
        bevel.width = stroke_width * self.scale_factor * 0.5
        bevel.segments = 2
        
        # Extrude for 3D
        solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify.thickness = self.extrude_depth
        
        # Set object name
        obj.name = f"Polyline_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_polygon(self, element):
        """Create a 3D polygon from SVG polygon element."""
        points = element['points']
        if len(points) < 3:
            return None
            
        # Create mesh for polygon
        mesh = bpy.data.meshes.new(name="Polygon")
        obj = bpy.data.objects.new("Polygon", mesh)
        
        # Add vertices
        vertices = []
        edges = []
        faces = []
        
        for i, (x, y) in enumerate(points):
            # Convert to Blender coordinates
            bx = (x - self.width/2) * self.scale_factor
            by = (self.height/2 - y) * self.scale_factor
            vertices.append((bx, by, 0))
            
            if i > 0:
                edges.append((i-1, i))
        
        # Close the polygon
        edges.append((len(points)-1, 0))
        
        # Create a face (assuming the polygon is convex and planar)
        faces.append(list(range(len(points))))
        
        # Create the mesh
        mesh.from_pydata(vertices, edges, faces)
        mesh.update()
        
        # Add to scene
        bpy.context.collection.objects.link(obj)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Extrude for 3D
        solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
        solidify.thickness = self.extrude_depth
        
        # Set object name
        obj.name = f"Polygon_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_text(self, element):
        """Create 3D text from SVG text element."""
        x = (element['x'] - self.width/2) * self.scale_factor
        y = (self.height/2 - element['y']) * self.scale_factor
        text = element['text']
        
        # Skip empty text
        if not text.strip():
            return None
        
        # Create text object
        font_size = float(element['style'].get('font-size', 12)) * self.scale_factor
        bpy.ops.object.text_add(location=(x, y, 0))
        obj = bpy.context.active_object
        
        # Set text properties
        obj.data.body = text
        obj.data.size = font_size
        obj.data.extrude = self.extrude_depth * 0.5
        
        # Try to set font based on style
        font_family = element['style'].get('font-family', 'Arial')
        try:
            # Find a font that matches the requested family
            for font in bpy.data.fonts:
                if font_family.lower() in font.name.lower():
                    obj.data.font = font
                    break
        except Exception as e:
            self.debug_log(f"Warning: Failed to set font: {e}")
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Text_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_path(self, element):
        """Create a 3D object from SVG path element."""
        path_data = element['path_data']
        if not path_data:
            return None
            
        # Check if path has fill or just stroke
        has_fill = element['style'].get('fill') and element['style'].get('fill') != 'none'
        
        # Create curve object for path
        curve = bpy.data.curves.new('Path', 'CURVE')
        curve.dimensions = '3D'
        curve.resolution_u = 12
        curve.bevel_depth = 0  # Will be set later
        curve.bevel_resolution = 4
        curve.fill_mode = 'BOTH'
        
        obj = bpy.data.objects.new("Path", curve)
        bpy.context.collection.objects.link(obj)
        
        # Create splines for each command
        is_first_point = True
        spline = None
        
        for cmd in path_data:
            cmd_type = cmd['command']
            
            if cmd_type == 'M':
                # Start a new spline
                spline = curve.splines.new('POLY')
                points = cmd['points']
                if not points:
                    continue
                    
                # Set first point
                x, y = points[0]
                bx = (x - self.width/2) * self.scale_factor
                by = (self.height/2 - y) * self.scale_factor
                
                spline.points[0].co = (bx, by, 0, 1)
                
                # Add remaining points
                for x, y in points[1:]:
                    bx = (x - self.width/2) * self.scale_factor
                    by = (self.height/2 - y) * self.scale_factor
                    
                    spline.points.add(1)
                    spline.points[-1].co = (bx, by, 0, 1)
                
                is_first_point = False
            
            elif cmd_type == 'L':
                if spline is None:
                    continue
                    
                points = cmd['points']
                for x, y in points:
                    bx = (x - self.width/2) * self.scale_factor
                    by = (self.height/2 - y) * self.scale_factor
                    
                    spline.points.add(1)
                    spline.points[-1].co = (bx, by, 0, 1)
            
            elif cmd_type == 'C':
                # Convert the spline to bezier
                if spline is None:
                    continue
                    
                # We need to convert to BEZIER type for curves
                # This is complex since we need to convert the existing spline
                # Create a new bezier spline
                bezier_spline = curve.splines.new('BEZIER')
                bezier_spline.use_cyclic_u = False
                
                # Copy existing points to bezier spline
                bezier_spline.bezier_points.add(len(spline.points) - 1)
                for i, point in enumerate(spline.points):
                    x, y = point.co.x, point.co.y
                    bezier_spline.bezier_points[i].co = (x, y, 0)
                    bezier_spline.bezier_points[i].handle_left_type = 'AUTO'
                    bezier_spline.bezier_points[i].handle_right_type = 'AUTO'
                
                # Remove old spline
                curve.splines.remove(spline)
                spline = bezier_spline
                
                # Add bezier curves
                curves = cmd['curves']
                for curve_points in curves:
                    start, cp1, cp2, end = curve_points
                    
                    # Convert points to Blender coordinates
                    bx = (end[0] - self.width/2) * self.scale_factor
                    by = (self.height/2 - end[1]) * self.scale_factor
                    
                    # Convert control points
                    cp1x = (cp1[0] - self.width/2) * self.scale_factor
                    cp1y = (self.height/2 - cp1[1]) * self.scale_factor
                    cp2x = (cp2[0] - self.width/2) * self.scale_factor
                    cp2y = (self.height/2 - cp2[1]) * self.scale_factor
                    
                    # Add new bezier point
                    spline.bezier_points.add(1)
                    spline.bezier_points[-1].co = (bx, by, 0)
                    
                    # Set handle types
                    spline.bezier_points[-2].handle_right_type = 'FREE'
                    spline.bezier_points[-1].handle_left_type = 'FREE'
                    
                    # Set handle positions
                    spline.bezier_points[-2].handle_right = (cp1x, cp1y, 0)
                    spline.bezier_points[-1].handle_left = (cp2x, cp2y, 0)
            
            elif cmd_type == 'Q':
                # Quadratic bezier - similar to cubic bezier but with one control point
                if spline is None:
                    continue
                    
                # Convert to BEZIER type
                bezier_spline = curve.splines.new('BEZIER')
                bezier_spline.use_cyclic_u = False
                
                # Copy existing points to bezier spline
                bezier_spline.bezier_points.add(len(spline.points) - 1)
                for i, point in enumerate(spline.points):
                    x, y = point.co.x, point.co.y
                    bezier_spline.bezier_points[i].co = (x, y, 0)
                    bezier_spline.bezier_points[i].handle_left_type = 'AUTO'
                    bezier_spline.bezier_points[i].handle_right_type = 'AUTO'
                
                # Remove old spline
                curve.splines.remove(spline)
                spline = bezier_spline
                
                # Add quadratic bezier curves - convert to cubic
                curves = cmd['curves']
                for curve_points in curves:
                    start, cp, end = curve_points
                    
                    # Convert points to Blender coordinates
                    bx = (end[0] - self.width/2) * self.scale_factor
                    by = (self.height/2 - end[1]) * self.scale_factor
                    
                    # Convert control point
                    cpx = (cp[0] - self.width/2) * self.scale_factor
                    cpy = (self.height/2 - cp[1]) * self.scale_factor
                    
                    # Convert quadratic to cubic bezier control points
                    # P1 = start + 2/3 * (CP - start)
                    # P2 = end + 2/3 * (CP - end)
                    start_x = spline.bezier_points[-1].co.x
                    start_y = spline.bezier_points[-1].co.y
                    
                    cp1x = start_x + 2/3 * (cpx - start_x)
                    cp1y = start_y + 2/3 * (cpy - start_y)
                    cp2x = bx + 2/3 * (cpx - bx)
                    cp2y = by + 2/3 * (cpy - by)
                    
                    # Add new bezier point
                    spline.bezier_points.add(1)
                    spline.bezier_points[-1].co = (bx, by, 0)
                    
                    # Set handle types
                    spline.bezier_points[-2].handle_right_type = 'FREE'
                    spline.bezier_points[-1].handle_left_type = 'FREE'
                    
                    # Set handle positions
                    spline.bezier_points[-2].handle_right = (cp1x, cp1y, 0)
                    spline.bezier_points[-1].handle_left = (cp2x, cp2y, 0)
            
            elif cmd_type == 'A':
                # Elliptical arcs - this is complex
                # For simplicity, we'll convert arcs to a series of cubic bezier curves
                # This is an approximation
                if spline is None:
                    continue
                    
                # Convert to BEZIER type if needed
                if spline.type != 'BEZIER':
                    bezier_spline = curve.splines.new('BEZIER')
                    bezier_spline.use_cyclic_u = False
                    
                    # Copy existing points to bezier spline
                    bezier_spline.bezier_points.add(len(spline.points) - 1)
                    for i, point in enumerate(spline.points):
                        x, y = point.co.x, point.co.y
                        bezier_spline.bezier_points[i].co = (x, y, 0)
                        bezier_spline.bezier_points[i].handle_left_type = 'AUTO'
                        bezier_spline.bezier_points[i].handle_right_type = 'AUTO'
                    
                    # Remove old spline
                    curve.splines.remove(spline)
                    spline = bezier_spline
                
                # Process arcs
                arcs = cmd['arcs']
                for arc in arcs:
                    # For simplicity, we'll just create a line to the endpoint
                    # A proper implementation would convert the arc to bezier curves
                    x, y = arc['end']
                    bx = (x - self.width/2) * self.scale_factor
                    by = (self.height/2 - y) * self.scale_factor
                    
                    spline.bezier_points.add(1)
                    spline.bezier_points[-1].co = (bx, by, 0)
                    spline.bezier_points[-1].handle_left_type = 'AUTO'
                    spline.bezier_points[-1].handle_right_type = 'AUTO'
            
            elif cmd_type == 'Z':
                if spline:
                    spline.use_cyclic_u = True
        
        # Set bevel depth based on whether it's a filled path or just stroke
        if has_fill:
            # Use extrude for filled paths
            curve.extrude = self.extrude_depth
            curve.bevel_depth = 0
        else:
            # Use bevel for stroke paths
            stroke_width = float(element['style'].get('stroke-width', 1))
            curve.bevel_depth = stroke_width * self.scale_factor * 0.5
            curve.extrude = 0
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Path_{len(bpy.data.objects)}"
        
        return obj
    
    def create_3d_group(self, element):
        """Create a 3D group from SVG group element."""
        group_id = element.get('id', f"Group_{len(bpy.data.collections)}")
        
        # Create a new collection for the group
        collection = bpy.data.collections.new(group_id)
        bpy.context.scene.collection.children.link(collection)
        
        # Process child elements
        child_objects = []
        for child in element.get('children', []):
            obj = self.create_3d_object(child)
            if obj:
                # Move the object to this collection
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                collection.objects.link(obj)
                child_objects.append(obj)
        
        # Store reference to group objects
        self.group_objects[group_id] = child_objects
        
        # Return None since we don't have a direct object but a collection
        return None
    
    def create_3d_object(self, element):
        """Create a 3D object based on element type."""
        element_type = element['type']
        
        try:
            if element_type == 'rect':
                return self.create_3d_rect(element)
            elif element_type == 'circle':
                return self.create_3d_circle(element)
            elif element_type == 'ellipse':
                return self.create_3d_ellipse(element)
            elif element_type == 'line':
                return self.create_3d_line(element)
            elif element_type == 'polyline':
                return self.create_3d_polyline(element)
            elif element_type == 'polygon':
                return self.create_3d_polygon(element)
            elif element_type == 'text':
                return self.create_3d_text(element)
            elif element_type == 'path':
                return self.create_3d_path(element)
            elif element_type == 'group':
                return self.create_3d_group(element)
            else:
                self.debug_log(f"Unhandled element type: {element_type}")
                return None
        except Exception as e:
            log(f"Error creating 3D object for {element_type}: {e}")
            traceback.print_exc()
            return None
    
    def setup_camera_and_lighting(self):
        """Set up camera and lighting for the scene."""
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
    
    def convert(self):
        """Convert the SVG file to a 3D Blender scene."""
        log(f"Converting SVG: {self.svg_path}")
        
        try:
            # Clean the scene
            clean_scene()
            
            # Parse SVG
            self.elements, self.width, self.height = self.parser.parse()
            log(f"Parsed SVG with dimensions {self.width}x{self.height} and {len(self.elements)} elements")
            
            # Create 3D objects for each element
            created_objects = 0
            for i, element in enumerate(self.elements):
                log(f"Processing element {i+1}/{len(self.elements)}: {element['type']}")
                if self.create_3d_object(element):
                    created_objects += 1
            
            log(f"Created {created_objects} 3D objects")
            
            # Setup camera and lighting
            self.setup_camera_and_lighting()
            
            return True
        except Exception as e:
            log(f"Error converting SVG to 3D: {e}")
            traceback.print_exc()
            return False

def convert_svg_to_3d(svg_path, output_path, extrude_depth=0.1, scale_factor=0.01, debug=False):
    """
    Convert an SVG file to a 3D Blender scene.
    
    Args:
        svg_path: Path to the SVG file
        output_path: Path to save the Blender file
        extrude_depth: Depth for 3D extrusion
        scale_factor: Scale factor for SVG to Blender space
        debug: Enable debug output
        
    Returns:
        True if conversion was successful, False otherwise
    """
    log(f"Converting SVG: {svg_path} to 3D model: {output_path}")
    
    try:
        # Create converter
        converter = SVGTo3DConverter(svg_path, extrude_depth, scale_factor, debug)
        
        # Convert SVG to 3D
        if converter.convert():
            # Save the file
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            bpy.ops.wm.save_as_mainfile(filepath=output_path)
            
            log(f"Successfully saved 3D model: {output_path}")
            return True
        else:
            log(f"Failed to convert SVG: {svg_path}")
            return False
            
    except Exception as e:
        log(f"Error in SVG to 3D conversion: {e}")
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
        debug = False
        
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
        
        if len(argv) >= 5:
            debug = (argv[4].lower() == 'true' or argv[4].lower() == 'debug')
        
        # Convert SVG to 3D
        result = convert_svg_to_3d(svg_path, output_path, extrude_depth, scale_factor, debug)
        
        if result:
            log("Conversion completed successfully")
            sys.exit(0)
        else:
            log("Conversion failed")
            sys.exit(1)
    else:
        log("Usage: blender --background --python enhanced_svg_to_3d.py -- input.svg output.blend [extrude_depth] [scale_factor] [debug]")
        sys.exit(1)

# Run main function if script is run directly
if __name__ == "__main__":
    main()