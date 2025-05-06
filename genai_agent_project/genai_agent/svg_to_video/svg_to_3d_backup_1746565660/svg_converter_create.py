"""
SVG to 3D Converter Creation Methods

This module contains methods for creating 3D objects from SVG elements.
"""

import bpy
import os
import sys
import traceback
import math
from mathutils import Vector

from .svg_utils import log, hex_to_rgb
from .svg_converter_materials_fixed import SVGMaterialHandler


def create_material(self, style):
    """Create a Blender material from SVG style (deprecated - use SVGMaterialHandler)"""
    # Initialize material handler if not exists
    if not hasattr(self, 'material_handler'):
        self.material_handler = SVGMaterialHandler()
    
    # Use the new material handler
    fill_color = style.get('fill', '#CCCCCC')
    opacity = float(style.get('opacity', 1.0))
    fill_opacity = float(style.get('fill-opacity', opacity))
    
    return self.material_handler.create_fill_material(fill_color, fill_opacity)


def apply_material_to_object(self, obj, style):
    """Apply material to an object."""
    try:
        # Initialize material handler if not exists
        if not hasattr(self, 'material_handler'):
            self.material_handler = SVGMaterialHandler()
        
        # Use the new material handler
        return self.material_handler.apply_materials_to_object(obj, style)
    except Exception as e:
        log(f"Error applying material: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_3d_object(self, element):
    """Create a 3D object from an SVG element."""
    try:
        element_type = element.get('type', 'unknown')
        
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
            log(f"Unsupported element type: {element_type}")
            return None
    except Exception as e:
        log(f"Error creating 3D object: {e}")
        traceback.print_exc()
        return None


def create_3d_rect(self, element):
    """Create a 3D rectangle from SVG rect element."""
    try:
        # Extract rectangle properties
        x = element['x']
        y = element['y']
        width = element['width']
        height = element['height']
        rx = element.get('rx', 0)
        ry = element.get('ry', rx)
        
        log(f"Creating 3D rectangle: x={x}, y={y}, width={width}, height={height}, rx={rx}, ry={ry}")
        
        # Convert to Blender coordinates
        bx = (x - self.width/2) * self.scale_factor
        by = (self.height/2 - y) * self.scale_factor
        bw = width * self.scale_factor
        bh = height * self.scale_factor
        brx = rx * self.scale_factor
        bry = ry * self.scale_factor
        
        # Create mesh
        if rx > 0 or ry > 0:
            # Create rounded rectangle using curves
            curve = bpy.data.curves.new('RoundedRect', 'CURVE')
            curve.dimensions = '2D'
            curve.resolution_u = 12  # Smoothness of the curve
            curve.extrude = self.extrude_depth  # Extrusion depth
            curve.fill_mode = 'BOTH'
            
            # Create the spline
            spline = curve.splines.new('POLY')
            spline.use_cyclic_u = True
            
            # Number of points for corners
            corner_segments = 8
            
            # Calculate points for rounded rectangle
            points = []
            
            # Top right corner
            for i in range(corner_segments + 1):
                angle = math.pi * 1.5 + (i / corner_segments) * (math.pi / 2)
                px = bx + bw - brx + brx * math.cos(angle)
                py = by - bh + bry + bry * math.sin(angle)
                points.append((px, py, 0))
            
            # Bottom right corner
            for i in range(corner_segments + 1):
                angle = 0 + (i / corner_segments) * (math.pi / 2)
                px = bx + bw - brx + brx * math.cos(angle)
                py = by - bry + bry * math.sin(angle)
                points.append((px, py, 0))
            
            # Bottom left corner
            for i in range(corner_segments + 1):
                angle = math.pi / 2 + (i / corner_segments) * (math.pi / 2)
                px = bx + brx + brx * math.cos(angle)
                py = by - bry + bry * math.sin(angle)
                points.append((px, py, 0))
            
            # Top left corner
            for i in range(corner_segments + 1):
                angle = math.pi + (i / corner_segments) * (math.pi / 2)
                px = bx + brx + brx * math.cos(angle)
                py = by - bh + bry + bry * math.sin(angle)
                points.append((px, py, 0))
            
            # Add points to spline
            spline.points.add(len(points) - 1)  # Subtract 1 because one point already exists
            for i, point in enumerate(points):
                spline.points[i].co = (point[0], point[1], point[2], 1)
            
            # Create the object
            obj = bpy.data.objects.new('RoundedRect', curve)
            bpy.context.collection.objects.link(obj)
        else:
            # Simple rectangle using curve
            curve = bpy.data.curves.new('Rectangle', 'CURVE')
            curve.dimensions = '2D'
            curve.fill_mode = 'BOTH'
            curve.extrude = self.extrude_depth
            
            # Create spline for rectangle
            spline = curve.splines.new('POLY')
            spline.use_cyclic_u = True
            
            # Define rectangle corners
            points = [
                (bx, by, 0),          # Bottom left
                (bx + bw, by, 0),      # Bottom right
                (bx + bw, by - bh, 0), # Top right
                (bx, by - bh, 0)       # Top left
            ]
            
            # Add points to spline
            spline.points.add(len(points) - 1)
            for i, point in enumerate(points):
                spline.points[i].co = (point[0], point[1], point[2], 1)
            
            # Create object
            obj = bpy.data.objects.new('Rectangle', curve)
            bpy.context.collection.objects.link(obj)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Rectangle_{len(bpy.data.objects)}"
        
        log(f"Rectangle created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D rectangle: {e}")
        traceback.print_exc()
        return None


def create_3d_circle(self, element):
    """Create a 3D circle from SVG circle element."""
    try:
        # Extract circle properties
        cx = element['cx']
        cy = element['cy']
        r = element['r']
        
        log(f"Creating 3D circle: cx={cx}, cy={cy}, r={r}")
        
        # Convert to Blender coordinates
        bcx = (cx - self.width/2) * self.scale_factor
        bcy = (self.height/2 - cy) * self.scale_factor
        br = r * self.scale_factor
        
        # Create circle mesh
        bpy.ops.mesh.primitive_circle_add(
            radius=br,
            location=(bcx, bcy, 0),
            vertices=32
        )
        
        # Get the created object
        obj = bpy.context.active_object
        
        # Fill the circle by creating a face
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all vertices
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Create face from vertices
        bpy.ops.mesh.edge_face_add()
        
        # Extrude the face
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate=({"value": (0, 0, self.extrude_depth)})
        )
        
        # Back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Circle_{len(bpy.data.objects)}"
        
        log(f"Circle created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D circle: {e}")
        traceback.print_exc()
        return None


def create_3d_ellipse(self, element):
    """Create a 3D ellipse from SVG ellipse element."""
    try:
        # Extract ellipse properties
        cx = element['cx']
        cy = element['cy']
        rx = element['rx']
        ry = element['ry']
        
        log(f"Creating 3D ellipse: cx={cx}, cy={cy}, rx={rx}, ry={ry}")
        
        # Convert to Blender coordinates
        bcx = (cx - self.width/2) * self.scale_factor
        bcy = (self.height/2 - cy) * self.scale_factor
        brx = rx * self.scale_factor
        bry = ry * self.scale_factor
        
        # Create circle mesh (we'll scale it to make an ellipse)
        bpy.ops.mesh.primitive_circle_add(
            radius=1.0,
            location=(bcx, bcy, 0),
            vertices=32
        )
        
        # Get the created object
        obj = bpy.context.active_object
        
        # Scale to make an ellipse
        obj.scale.x = brx
        obj.scale.y = bry
        
        # Apply the scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Fill the ellipse by creating a face
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all vertices
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Create face from vertices
        bpy.ops.mesh.edge_face_add()
        
        # Extrude the face
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate=({"value": (0, 0, self.extrude_depth)})
        )
        
        # Back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Ellipse_{len(bpy.data.objects)}"
        
        log(f"Ellipse created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D ellipse: {e}")
        traceback.print_exc()
        return None


def create_3d_line(self, element):
    """Create a 3D line from SVG line element."""
    try:
        # Extract line properties
        x1 = element['x1']
        y1 = element['y1']
        x2 = element['x2']
        y2 = element['y2']
        
        log(f"Creating 3D line: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        
        # Convert to Blender coordinates
        bx1 = (x1 - self.width/2) * self.scale_factor
        by1 = (self.height/2 - y1) * self.scale_factor
        bx2 = (x2 - self.width/2) * self.scale_factor
        by2 = (self.height/2 - y2) * self.scale_factor
        
        # Get stroke width
        stroke_width = float(element['style'].get('stroke-width', 1))
        bevel_depth = stroke_width * self.scale_factor * 0.5
        
        # Create curve
        curve = bpy.data.curves.new('Line', 'CURVE')
        curve.dimensions = '3D'
        
        # Add the spline
        spline = curve.splines.new('POLY')
        spline.points.add(1)  # One point already exists
        
        # Set the points
        spline.points[0].co = (bx1, by1, 0, 1)
        spline.points[1].co = (bx2, by2, 0, 1)
        
        # Add thickness
        curve.bevel_depth = bevel_depth
        
        # Create the object
        obj = bpy.data.objects.new('Line', curve)
        bpy.context.collection.objects.link(obj)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Line_{len(bpy.data.objects)}"
        
        log(f"Line created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D line: {e}")
        traceback.print_exc()
        return None


def create_3d_polyline(self, element):
    """Create a 3D polyline from SVG polyline element."""
    try:
        # Extract points
        points = element['points']
        
        log(f"Creating 3D polyline with {len(points)} points")
        
        # Get stroke width
        stroke_width = float(element['style'].get('stroke-width', 1))
        bevel_depth = stroke_width * self.scale_factor * 0.5
        
        # Create curve
        curve = bpy.data.curves.new('Polyline', 'CURVE')
        curve.dimensions = '3D'
        
        # Add the spline
        spline = curve.splines.new('POLY')
        spline.points.add(len(points) - 1)  # One point already exists
        
        # Set the points
        for i, point in enumerate(points):
            x, y = point
            bx = (x - self.width/2) * self.scale_factor
            by = (self.height/2 - y) * self.scale_factor
            spline.points[i].co = (bx, by, 0, 1)
        
        # Add thickness
        curve.bevel_depth = bevel_depth
        
        # Create the object
        obj = bpy.data.objects.new('Polyline', curve)
        bpy.context.collection.objects.link(obj)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Polyline_{len(bpy.data.objects)}"
        
        log(f"Polyline created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D polyline: {e}")
        traceback.print_exc()
        return None


def create_3d_polygon(self, element):
    """Create a 3D polygon from SVG polygon element."""
    try:
        # Extract points
        points = element['points']
        
        log(f"Creating 3D polygon with {len(points)} points")
        
        # Create curve for polygon outline
        curve = bpy.data.curves.new('Polygon', 'CURVE')
        curve.dimensions = '2D'  # 2D for proper fill
        curve.resolution_u = 12  # Smoothness
        curve.extrude = self.extrude_depth  # Extrusion depth
        
        # Add the spline
        spline = curve.splines.new('POLY')
        spline.use_cyclic_u = True  # Close the loop
        spline.points.add(len(points) - 1)  # One point already exists
        
        # Set the points
        for i, point in enumerate(points):
            x, y = point
            bx = (x - self.width/2) * self.scale_factor
            by = (self.height/2 - y) * self.scale_factor
            spline.points[i].co = (bx, by, 0, 1)
        
        # Create the object
        obj = bpy.data.objects.new('Polygon', curve)
        bpy.context.collection.objects.link(obj)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Polygon_{len(bpy.data.objects)}"
        
        log(f"Polygon created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D polygon: {e}")
        traceback.print_exc()
        return None


def create_3d_text(self, element):
    """Create a 3D text from SVG text element."""
    try:
        # Extract text properties
        x = element['x']
        y = element['y']
        text = element['text']
        
        log(f"Creating 3D text: x={x}, y={y}, text='{text}'")
        
        # Convert to Blender coordinates
        bx = (x - self.width/2) * self.scale_factor
        by = (self.height/2 - y) * self.scale_factor
        
        # Font settings
        font_size = float(element['style'].get('font-size', 12))
        font_family = element['style'].get('font-family', 'Arial')
        
        # Create text curve
        curve = bpy.data.curves.new(text, 'FONT')
        curve.body = text
        
        # Set extrude and bevel for 3D effect
        curve.extrude = self.extrude_depth
        curve.bevel_depth = self.extrude_depth * 0.1
        
        # Try to set font if available
        try:
            font = None
            for f in bpy.data.fonts:
                if font_family.lower() in f.name.lower():
                    font = f
                    break
            
            if font:
                curve.font = font
        except:
            # If font setting fails, continue with default
            pass
        
        # Scale text based on font size (increased for better visibility)
        text_scale = (font_size / 8.0) * self.scale_factor  # Changed from /12.0 to /8.0
        
        # Create the object
        obj = bpy.data.objects.new(text, curve)
        bpy.context.collection.objects.link(obj)
        
        # Position and scale
        obj.location = (bx, by, 0)
        obj.scale = (text_scale, text_scale, text_scale)
        
        # Apply material
        self.apply_material_to_object(obj, element['style'])
        
        # Set object name
        obj.name = f"Text_{len(bpy.data.objects)}"
        
        log(f"Text created successfully: {obj.name}")
        return obj
    except Exception as e:
        log(f"Error creating 3D text: {e}")
        traceback.print_exc()
        return None
