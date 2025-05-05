"""
Enhanced SVG to 3D Conversion Blender Script

A Blender script for converting SVG files to 3D models with improved:
- SVG path handling
- More robust parsing
- Better error handling
- Support for advanced SVG features

Part 1: Enhanced SVG Parser with Path Support
"""

import bpy
import os
import sys
import xml.etree.ElementTree as ET
import traceback
import math
import re
from mathutils import Vector, Matrix

def log(message):
    """Print a message with a prefix."""
    print(f"[SVG2-3D] {message}")

class SVGParser:
    """Enhanced SVG Parser with path support."""
    
    def __init__(self, svg_path, debug=False):
        """
        Initialize the SVG parser.
        
        Args:
            svg_path: Path to the SVG file
            debug: Enable debug output
        """
        self.svg_path = svg_path
        self.debug = debug
        self.elements = []
        self.width = 800
        self.height = 600
        self.viewBox = None
        self.element_counts = {
            'rect': 0,
            'circle': 0,
            'ellipse': 0,
            'line': 0,
            'text': 0,
            'path': 0,
            'polyline': 0,
            'polygon': 0,
            'group': 0,
            'other': 0
        }
        self.ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    def debug_log(self, message):
        """Debug logging function."""
        if self.debug:
            log(f"DEBUG: {message}")
    
    def parse(self):
        """Parse the SVG file and extract elements."""
        log(f"Parsing SVG: {self.svg_path}")
        
        try:
            # Parse SVG file
            tree = ET.parse(self.svg_path)
            root = tree.getroot()
            
            # Extract namespace if present
            if '}' in root.tag:
                ns_str = root.tag.split('}')[0].strip('{')
                self.ns = {'svg': ns_str}
            
            # Get SVG dimensions
            if 'viewBox' in root.attrib:
                self.viewBox = root.attrib['viewBox'].split()
                self.width = float(self.viewBox[2])
                self.height = float(self.viewBox[3])
            else:
                self.width = float(root.attrib.get('width', '800').replace('px', ''))
                self.height = float(root.attrib.get('height', '600').replace('px', ''))
            
            log(f"SVG dimensions: {self.width} x {self.height}")
            
            # Process the root element and its children
            self._process_element(root)
            
            # Log summary
            log(f"Parsed elements: {sum(self.element_counts.values())} total")
            for elem_type, count in self.element_counts.items():
                if count > 0:
                    self.debug_log(f"  - {elem_type}: {count}")
            
            return self.elements, self.width, self.height
            
        except Exception as e:
            log(f"Error parsing SVG: {e}")
            traceback.print_exc()
            return [], 800, 600
    
    def _process_element(self, element, parent_transform=None):
        """
        Process an SVG element and its children recursively.
        
        Args:
            element: The SVG element to process
            parent_transform: Transform from parent elements
        """
        # Get element tag without namespace
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}')[1]
        
        # Extract transform if present
        transform = element.attrib.get('transform', None)
        transform_matrix = self._parse_transform(transform, parent_transform)
        
        # Parse style
        style = self._parse_style(element)
        
        # Process element based on tag
        if tag == 'svg':
            # Process children of svg root
            for child in element:
                self._process_element(child, transform_matrix)
                
        elif tag == 'g':
            # Process group
            self.element_counts['group'] += 1
            group_id = element.attrib.get('id', f"group_{self.element_counts['group']}")
            
            # Create a group element
            group_elem = {
                'type': 'group',
                'id': group_id,
                'transform': transform_matrix,
                'style': style,
                'children': []
            }
            
            # Process child elements
            for child in element:
                child_elements = self._process_element(child, transform_matrix)
                if child_elements:
                    if isinstance(child_elements, list):
                        group_elem['children'].extend(child_elements)
                    else:
                        group_elem['children'].append(child_elements)
            
            self.elements.append(group_elem)
            return group_elem
            
        elif tag == 'rect':
            # Process rectangle
            elem = self._parse_rect(element, style, transform_matrix)
            if elem:
                self.element_counts['rect'] += 1
                self.elements.append(elem)
                return elem
                
        elif tag == 'circle':
            # Process circle
            elem = self._parse_circle(element, style, transform_matrix)
            if elem:
                self.element_counts['circle'] += 1
                self.elements.append(elem)
                return elem
                
        elif tag == 'ellipse':
            # Process ellipse
            elem = self._parse_ellipse(element, style, transform_matrix)
            if elem:
                self.element_counts['ellipse'] += 1
                self.elements.append(elem)
                return elem
                
        elif tag == 'line':
            # Process line
            elem = self._parse_line(element, style, transform_matrix)
            if elem:
                self.element_counts['line'] += 1
                self.elements.append(elem)
                return elem
                
        elif tag == 'polyline':
            # Process polyline
            elem = self._parse_polyline(element, style, transform_matrix)
            if elem:
                self.element_counts['polyline'] += 1
                self.elements.append(elem)
                return elem
                
        elif tag == 'polygon':
            # Process polygon
            elem = self._parse_polygon(element, style, transform_matrix)
            if elem:
                self.element_counts['polygon'] += 1
                self.elements.append(elem)
                return elem
                
        elif tag == 'path':
            # Process path
            elem = self._parse_path(element, style, transform_matrix)
            if elem:
                self.element_counts['path'] += 1
                self.elements.append(elem)
                return elem
                
        elif tag == 'text':
            # Process text
            elem = self._parse_text(element, style, transform_matrix)
            if elem:
                self.element_counts['text'] += 1
                self.elements.append(elem)
                return elem
                
        else:
            self.element_counts['other'] += 1
            self.debug_log(f"Unhandled element type: {tag}")
            
        return None

    def _parse_style(self, element):
        """Parse style attributes from an element."""
        # Default style values
        style = {
            'fill': '#CCCCCC',
            'stroke': None,
            'stroke-width': 1,
            'opacity': 1.0,
            'font-size': 12,
            'text-align': 'left',
            'font-family': 'Arial'
        }
        
        # Extract style attribute if present
        if 'style' in element.attrib:
            style_attr = element.attrib['style']
            # Parse CSS-like style string
            for item in style_attr.split(';'):
                if ':' in item:
                    key, value = item.split(':', 1)
                    style[key.strip()] = value.strip()
        
        # Override with direct attributes
        for key in style.keys():
            if key in element.attrib:
                style[key] = element.attrib[key]
        
        # Special case for common attributes
        if 'fill' in element.attrib:
            style['fill'] = element.attrib['fill']
        if 'stroke' in element.attrib:
            style['stroke'] = element.attrib['stroke']
        if 'stroke-width' in element.attrib:
            style['stroke-width'] = element.attrib['stroke-width']
        if 'opacity' in element.attrib:
            style['opacity'] = float(element.attrib['opacity'])
        
        # Handle 'none' values
        if style['fill'] == 'none':
            style['fill'] = None
        
        return style
    
    def _parse_transform(self, transform_str, parent_transform=None):
        """
        Parse SVG transform attribute and return a transformation matrix.
        """
        # Start with identity matrix or parent transform
        if parent_transform:
            matrix = parent_transform.copy()
        else:
            matrix = Matrix.Identity(3)
        
        if not transform_str:
            return matrix
        
        # Parse transform string
        transform_str = transform_str.strip()
        transforms = re.findall(r'(\w+)\s*\(([^)]*)\)', transform_str)
        
        for transform_type, params_str in transforms:
            params = [float(p) for p in re.findall(r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', params_str)]
            
            if transform_type == 'translate':
                tx = params[0]
                ty = params[1] if len(params) > 1 else 0
                translate_matrix = Matrix.Translation(Vector((tx, ty, 0)))
                matrix = translate_matrix @ matrix
                
            elif transform_type == 'scale':
                sx = params[0]
                sy = params[1] if len(params) > 1 else sx
                scale_matrix = Matrix.Scale(sx, 3, Vector((1, 0, 0))) @ Matrix.Scale(sy, 3, Vector((0, 1, 0)))
                matrix = scale_matrix @ matrix
                
            elif transform_type == 'rotate':
                angle = params[0]
                if len(params) > 2:
                    cx, cy = params[1], params[2]
                    # Translate to origin, rotate, translate back
                    t1 = Matrix.Translation(Vector((-cx, -cy, 0)))
                    r = Matrix.Rotation(math.radians(angle), 3, 'Z')
                    t2 = Matrix.Translation(Vector((cx, cy, 0)))
                    rotation_matrix = t2 @ r @ t1
                else:
                    # Rotate around origin
                    rotation_matrix = Matrix.Rotation(math.radians(angle), 3, 'Z')
                matrix = rotation_matrix @ matrix
                
            elif transform_type == 'matrix':
                # SVG matrix is (a, b, c, d, e, f) which corresponds to:
                # [a c e]
                # [b d f]
                # [0 0 1]
                if len(params) >= 6:
                    a, b, c, d, e, f = params[:6]
                    transform_matrix = Matrix((
                        (a, c, e),
                        (b, d, f),
                        (0, 0, 1)
                    ))
                    matrix = transform_matrix @ matrix
        
        return matrix
    
    def _apply_transform(self, x, y, transform_matrix):
        """Apply transformation matrix to a point."""
        if transform_matrix:
            point = Vector((x, y, 1))
            transformed = transform_matrix @ point
            return transformed.x, transformed.y
        return x, y

    def _parse_rect(self, element, style, transform_matrix):
        """Parse a rectangle element."""
        try:
            x = float(element.attrib.get('x', 0))
            y = float(element.attrib.get('y', 0))
            width = float(element.attrib.get('width', 0))
            height = float(element.attrib.get('height', 0))
            rx = float(element.attrib.get('rx', 0))
            ry = float(element.attrib.get('ry', rx))  # If ry is not specified, use rx
            
            # Apply transform if present
            if transform_matrix:
                # Transform the four corners and calculate the new bounds
                corners = [
                    self._apply_transform(x, y, transform_matrix),
                    self._apply_transform(x + width, y, transform_matrix),
                    self._apply_transform(x, y + height, transform_matrix),
                    self._apply_transform(x + width, y + height, transform_matrix)
                ]
                
                # Find the bounding box
                min_x = min(p[0] for p in corners)
                min_y = min(p[1] for p in corners)
                max_x = max(p[0] for p in corners)
                max_y = max(p[1] for p in corners)
                
                x, y = min_x, min_y
                width, height = max_x - min_x, max_y - min_y
            
            return {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'rx': rx,
                'ry': ry,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing rectangle: {e}")
            return None
    
    def _parse_circle(self, element, style, transform_matrix):
        """Parse a circle element."""
        try:
            cx = float(element.attrib.get('cx', 0))
            cy = float(element.attrib.get('cy', 0))
            r = float(element.attrib.get('r', 0))
            
            # Apply transform if present
            if transform_matrix:
                cx, cy = self._apply_transform(cx, cy, transform_matrix)
                # Note: For proper handling, scaling should be applied to radius
                # This is simplified and might not handle all transformations correctly
            
            return {
                'type': 'circle',
                'cx': cx,
                'cy': cy,
                'r': r,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing circle: {e}")
            return None
    
    def _parse_ellipse(self, element, style, transform_matrix):
        """Parse an ellipse element."""
        try:
            cx = float(element.attrib.get('cx', 0))
            cy = float(element.attrib.get('cy', 0))
            rx = float(element.attrib.get('rx', 0))
            ry = float(element.attrib.get('ry', 0))
            
            # Apply transform if present
            if transform_matrix:
                cx, cy = self._apply_transform(cx, cy, transform_matrix)
                # Note: For proper handling, scaling should be applied to radii
                # This is simplified and might not handle all transformations correctly
            
            return {
                'type': 'ellipse',
                'cx': cx,
                'cy': cy,
                'rx': rx,
                'ry': ry,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing ellipse: {e}")
            return None
    
    def _parse_line(self, element, style, transform_matrix):
        """Parse a line element."""
        try:
            x1 = float(element.attrib.get('x1', 0))
            y1 = float(element.attrib.get('y1', 0))
            x2 = float(element.attrib.get('x2', 0))
            y2 = float(element.attrib.get('y2', 0))
            
            # Apply transform if present
            if transform_matrix:
                x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                x2, y2 = self._apply_transform(x2, y2, transform_matrix)
            
            return {
                'type': 'line',
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing line: {e}")
            return None

    def _parse_polyline(self, element, style, transform_matrix):
        """Parse a polyline element."""
        try:
            points_str = element.attrib.get('points', '')
            points = []
            
            # Parse points string
            pairs = re.findall(r'([-+]?[0-9]*\.?[0-9]+)[,\s]+([-+]?[0-9]*\.?[0-9]+)', points_str)
            for x_str, y_str in pairs:
                x, y = float(x_str), float(y_str)
                if transform_matrix:
                    x, y = self._apply_transform(x, y, transform_matrix)
                points.append((x, y))
            
            return {
                'type': 'polyline',
                'points': points,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing polyline: {e}")
            return None
    
    def _parse_polygon(self, element, style, transform_matrix):
        """Parse a polygon element."""
        try:
            points_str = element.attrib.get('points', '')
            points = []
            
            # Parse points string
            pairs = re.findall(r'([-+]?[0-9]*\.?[0-9]+)[,\s]+([-+]?[0-9]*\.?[0-9]+)', points_str)
            for x_str, y_str in pairs:
                x, y = float(x_str), float(y_str)
                if transform_matrix:
                    x, y = self._apply_transform(x, y, transform_matrix)
                points.append((x, y))
            
            return {
                'type': 'polygon',
                'points': points,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing polygon: {e}")
            return None
    
    def _parse_text(self, element, style, transform_matrix):
        """Parse a text element."""
        try:
            x = float(element.attrib.get('x', 0))
            y = float(element.attrib.get('y', 0))
            
            # Apply transform if present
            if transform_matrix:
                x, y = self._apply_transform(x, y, transform_matrix)
            
            # Get text content - handle both direct content and tspan elements
            text_content = ""
            if element.text:
                text_content += element.text
            
            # Process tspan elements
            for tspan in element.findall('.//tspan', self.ns):
                if tspan.text:
                    text_content += tspan.text
            
            # Default to empty string if no text found
            text_content = text_content.strip() or ""
            
            return {
                'type': 'text',
                'x': x,
                'y': y,
                'text': text_content,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing text: {e}")
            return None
    
    def _parse_path(self, element, style, transform_matrix):
        """Parse a path element with enhanced path commands support."""
        try:
            d = element.attrib.get('d', '')
            
            if not d:
                return None
                
            # Parse path data
            path_data = self._parse_path_data(d, transform_matrix)
            
            return {
                'type': 'path',
                'path_data': path_data,
                'style': style,
                'transform': transform_matrix
            }
        except Exception as e:
            log(f"Error parsing path: {e}")
            return None

    def _parse_path_data(self, d, transform_matrix):
        """
        Parse SVG path data string into a list of path commands.
        Handles SVG path commands: M, m, L, l, H, h, V, v, C, c, S, s, Q, q, T, t, A, a, Z, z
        """
        if not d:
            return []
            
        # Command patterns
        command_pattern = r'([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)'
        
        # Extract commands and parameters
        commands = []
        matches = re.findall(command_pattern, d)
        
        current_point = (0, 0)  # Current point for relative commands
        start_point = (0, 0)    # Start point for closepath
        last_control_point = None  # For smooth curves
        
        for cmd, params_str in matches:
            # Parse parameters for this command
            params = []
            if cmd != 'Z' and cmd != 'z':
                # Extract all numbers from the parameters string
                params = [float(p) for p in re.findall(r'[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', params_str)]
            
            # Process command based on type
            if cmd == 'M' or cmd == 'm':  # Moveto
                is_relative = (cmd == 'm')
                points = []
                
                # First point is treated as moveto
                if len(params) >= 2:
                    x, y = params[0], params[1]
                    if is_relative:
                        x += current_point[0]
                        y += current_point[1]
                    
                    if transform_matrix:
                        x, y = self._apply_transform(x, y, transform_matrix)
                        
                    current_point = (x, y)
                    start_point = current_point  # Update start point for closepath
                    points.append((x, y))
                
                # Remaining points are treated as lineto
                for i in range(2, len(params), 2):
                    if i+1 < len(params):
                        x, y = params[i], params[i+1]
                        if is_relative:
                            x += current_point[0]
                            y += current_point[1]
                        
                        if transform_matrix:
                            x, y = self._apply_transform(x, y, transform_matrix)
                            
                        current_point = (x, y)
                        points.append((x, y))
                
                if points:
                    commands.append({
                        'command': 'M',
                        'points': points
                    })
            
            elif cmd == 'L' or cmd == 'l':  # Lineto
                is_relative = (cmd == 'l')
                points = []
                
                for i in range(0, len(params), 2):
                    if i+1 < len(params):
                        x, y = params[i], params[i+1]
                        if is_relative:
                            x += current_point[0]
                            y += current_point[1]
                        
                        if transform_matrix:
                            x, y = self._apply_transform(x, y, transform_matrix)
                            
                        current_point = (x, y)
                        points.append((x, y))
                
                if points:
                    commands.append({
                        'command': 'L',
                        'points': points
                    })
            
            elif cmd == 'H' or cmd == 'h':  # Horizontal lineto
                is_relative = (cmd == 'h')
                points = []
                
                for x in params:
                    if is_relative:
                        x += current_point[0]
                    
                    # For horizontal lines, y remains the same
                    y = current_point[1]
                    
                    if transform_matrix:
                        x, y = self._apply_transform(x, y, transform_matrix)
                        
                    current_point = (x, y)
                    points.append((x, y))
                
                if points:
                    commands.append({
                        'command': 'L',  # Convert to regular lineto for simplicity
                        'points': points
                    })
            
            elif cmd == 'V' or cmd == 'v':  # Vertical lineto
                is_relative = (cmd == 'v')
                points = []
                
                for y in params:
                    if is_relative:
                        y += current_point[1]
                    
                    # For vertical lines, x remains the same
                    x = current_point[0]
                    
                    if transform_matrix:
                        x, y = self._apply_transform(x, y, transform_matrix)
                        
                    current_point = (x, y)
                    points.append((x, y))
                
                if points:
                    commands.append({
                        'command': 'L',  # Convert to regular lineto for simplicity
                        'points': points
                    })
            
            elif cmd == 'C' or cmd == 'c':  # Cubic Bezier curve
                is_relative = (cmd == 'c')
                curves = []
                
                for i in range(0, len(params), 6):
                    if i+5 < len(params):
                        x1, y1 = params[i], params[i+1]      # First control point
                        x2, y2 = params[i+2], params[i+3]    # Second control point
                        x, y = params[i+4], params[i+5]      # End point
                        
                        if is_relative:
                            x1 += current_point[0]
                            y1 += current_point[1]
                            x2 += current_point[0]
                            y2 += current_point[1]
                            x += current_point[0]
                            y += current_point[1]
                        
                        if transform_matrix:
                            x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                            x2, y2 = self._apply_transform(x2, y2, transform_matrix)
                            x, y = self._apply_transform(x, y, transform_matrix)
                        
                        curves.append((
                            current_point,  # Start point
                            (x1, y1),       # Control point 1
                            (x2, y2),       # Control point 2
                            (x, y)          # End point
                        ))
                        
                        current_point = (x, y)
                        last_control_point = (x2, y2)  # Store for smooth curves
                
                if curves:
                    commands.append({
                        'command': 'C',
                        'curves': curves
                    })
            
            elif cmd == 'S' or cmd == 's':  # Smooth cubic Bezier curve
                is_relative = (cmd == 's')
                curves = []
                
                for i in range(0, len(params), 4):
                    if i+3 < len(params):
                        # The first control point is the reflection of the second control point
                        # of the previous command relative to the current point
                        if last_control_point and commands and commands[-1]['command'] in ('C', 'S'):
                            # Reflect previous control point
                            x1 = 2 * current_point[0] - last_control_point[0]
                            y1 = 2 * current_point[1] - last_control_point[1]
                        else:
                            # If previous command was not a cubic Bezier, the first control point is the current point
                            x1, y1 = current_point
                        
                        x2, y2 = params[i], params[i+1]    # Second control point
                        x, y = params[i+2], params[i+3]    # End point
                        
                        if is_relative:
                            x2 += current_point[0]
                            y2 += current_point[1]
                            x += current_point[0]
                            y += current_point[1]
                        
                        if transform_matrix:
                            x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                            x2, y2 = self._apply_transform(x2, y2, transform_matrix)
                            x, y = self._apply_transform(x, y, transform_matrix)
                        
                        curves.append((
                            current_point,  # Start point
                            (x1, y1),       # Control point 1 (reflected)
                            (x2, y2),       # Control point 2
                            (x, y)          # End point
                        ))
                        
                        current_point = (x, y)
                        last_control_point = (x2, y2)  # Store for future smooth curves
                
                if curves:
                    commands.append({
                        'command': 'C',  # Convert to regular cubic Bezier
                        'curves': curves
                    })
            
            elif cmd == 'Q' or cmd == 'q':  # Quadratic Bezier curve
                is_relative = (cmd == 'q')
                curves = []
                
                for i in range(0, len(params), 4):
                    if i+3 < len(params):
                        x1, y1 = params[i], params[i+1]    # Control point
                        x, y = params[i+2], params[i+3]    # End point
                        
                        if is_relative:
                            x1 += current_point[0]
                            y1 += current_point[1]
                            x += current_point[0]
                            y += current_point[1]
                        
                        if transform_matrix:
                            x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                            x, y = self._apply_transform(x, y, transform_matrix)
                        
                        curves.append((
                            current_point,  # Start point
                            (x1, y1),       # Control point
                            (x, y)          # End point
                        ))
                        
                        current_point = (x, y)
                        last_control_point = (x1, y1)  # Store for smooth curves
                
                if curves:
                    commands.append({
                        'command': 'Q',
                        'curves': curves
                    })
            
            elif cmd == 'T' or cmd == 't':  # Smooth quadratic Bezier curve
                is_relative = (cmd == 't')
                curves = []
                
                for i in range(0, len(params), 2):
                    if i+1 < len(params):
                        # The control point is the reflection of the control point
                        # of the previous command relative to the current point
                        if last_control_point and commands and commands[-1]['command'] in ('Q', 'T'):
                            # Reflect previous control point
                            x1 = 2 * current_point[0] - last_control_point[0]
                            y1 = 2 * current_point[1] - last_control_point[1]
                        else:
                            # If previous command was not a quadratic Bezier, use current point
                            x1, y1 = current_point
                        
                        x, y = params[i], params[i+1]    # End point
                        
                        if is_relative:
                            x += current_point[0]
                            y += current_point[1]
                        
                        if transform_matrix:
                            x1, y1 = self._apply_transform(x1, y1, transform_matrix)
                            x, y = self._apply_transform(x, y, transform_matrix)
                        
                        curves.append((
                            current_point,  # Start point
                            (x1, y1),       # Control point (reflected)
                            (x, y)          # End point
                        ))
                        
                        current_point = (x, y)
                        last_control_point = (x1, y1)
                
                if curves:
                    commands.append({
                        'command': 'Q',  # Convert to regular quadratic Bezier
                        'curves': curves
                    })
            
            elif cmd == 'A' or cmd == 'a':  # Elliptical arc
                is_relative = (cmd == 'a')
                arcs = []
                
                for i in range(0, len(params), 7):
                    if i+6 < len(params):
                        rx = params[i]       # X radius
                        ry = params[i+1]     # Y radius
                        angle = params[i+2]  # X-axis rotation
                        large_arc = int(params[i+3]) != 0  # Large arc flag
                        sweep = int(params[i+4]) != 0      # Sweep flag
                        x, y = params[i+5], params[i+6]    # End point
                        
                        if is_relative:
                            x += current_point[0]
                            y += current_point[1]
                        
                        if transform_matrix:
                            # Note: This is a simplification. For proper handling,
                            # the arc parameters should be transformed correctly
                            x, y = self._apply_transform(x, y, transform_matrix)
                        
                        arcs.append({
                            'start': current_point,
                            'end': (x, y),
                            'rx': rx,
                            'ry': ry,
                            'angle': angle,
                            'large_arc': large_arc,
                            'sweep': sweep
                        })
                        
                        current_point = (x, y)
                
                if arcs:
                    commands.append({
                        'command': 'A',
                        'arcs': arcs
                    })
            
            elif cmd == 'Z' or cmd == 'z':  # Closepath
                if current_point != start_point:
                    commands.append({
                        'command': 'L',
                        'points': [start_point]
                    })
                    current_point = start_point
                    
                commands.append({
                    'command': 'Z'
                })
        
        return commands



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
        Apply material to an object based on style attributes with error handling.
        
        Args:
            obj: Blender object
            style: Style dictionary with 'fill', 'stroke', etc.
        """
        try:
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
        except Exception as e:
            self.debug_log(f"Warning: Failed to apply material: {e}")
            # Create a default material as fallback
            default_material = bpy.data.materials.new(name="Default_Material")
            default_material.diffuse_color = (0.8, 0.8, 0.8, 1.0)
            
            try:
                # Try to assign the default material
                if obj.data.materials:
                    obj.data.materials[0] = default_material
                else:
                    obj.data.materials.append(default_material)
            except:
                pass  # If even this fails, just continue without a material
            
            return default_material
    
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
                # Elliptical arcs
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
                
                # Process arcs - convert to bezier segments
                arcs = cmd['arcs']
                for arc in arcs:
                    # Get arc parameters
                    start_point = arc['start']
                    end_point = arc['end']
                    rx, ry = arc['rx'], arc['ry']
                    angle = arc['angle']
                    large_arc = arc['large_arc']
                    sweep = arc['sweep']
                    
                    # Convert to Blender coordinates
                    start_x = (start_point[0] - self.width/2) * self.scale_factor
                    start_y = (self.height/2 - start_point[1]) * self.scale_factor
                    end_x = (end_point[0] - self.width/2) * self.scale_factor
                    end_y = (self.height/2 - end_point[1]) * self.scale_factor
                    
                    # For better arc approximation, add multiple bezier points
                    # This is a simplified approximation using 4 points
                    spline.bezier_points.add(3)  # Add 3 more points (4 total for the arc)
                    
                    # Place points evenly along the arc (this is an approximation)
                    for i in range(4):
                        t = i / 3.0  # Parameter from 0 to 1
                        # Simple circular interpolation (this can be improved)
                        theta = math.pi * t * (1 if sweep else -1)
                        if large_arc:
                            theta += math.pi
                            
                        # Calculate point on approximated arc
                        px = (start_x + end_x) / 2 + rx * math.cos(theta) * (1 if sweep else -1)
                        py = (start_y + end_y) / 2 + ry * math.sin(theta) * (1 if sweep else -1)
                        
                        # Set point position
                        if i > 0:  # Skip the first point (it's already there)
                            idx = -4 + i
                            spline.bezier_points[idx].co = (px, py, 0)
                            spline.bezier_points[idx].handle_left_type = 'AUTO'
                            spline.bezier_points[idx].handle_right_type = 'AUTO'
                    
                    # Ensure the last point is exactly at the end position
                    spline.bezier_points[-1].co = (end_x, end_y, 0)

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
        
        try:
            # Ensure we're in the right context
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Add camera with direct creation instead of operator
            cam_data = bpy.data.cameras.new(name="Camera")
            camera = bpy.data.objects.new("Camera", cam_data)
            bpy.context.collection.objects.link(camera)
            
            # Set camera position and rotation
            camera.location = (0, -5, 5)
            camera.rotation_euler = (math.radians(45), 0, 0)
            
            # Make this the active camera
            bpy.context.scene.camera = camera
            
            # Add sun light with direct creation
            sun_data = bpy.data.lights.new(name="Sun", type='SUN')
            sun_data.energy = 2.0
            sun = bpy.data.objects.new("Sun", sun_data)
            sun.location = (2, -2, 5)
            bpy.context.collection.objects.link(sun)
            
            # Add fill light
            area_data = bpy.data.lights.new(name="Fill", type='AREA')
            area_data.energy = 1.5
            area = bpy.data.objects.new("Fill", area_data)
            area.location = (-3, 3, 3)
            area.scale = (5, 5, 1)
            bpy.context.collection.objects.link(area)
            
            log("Camera and lighting setup complete")
        except Exception as e:
            log(f"Warning: Camera and lighting setup failed: {e}")
            # Continue even if camera setup fails
    
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