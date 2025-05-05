"""
SVG Parser Elements Module

Contains the implementation of parsing different SVG elements.
Used by the SVGParser class.
"""

import re
import math
import traceback
from mathutils import Vector, Matrix
from svg_utils import log


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
        from mathutils import Matrix
        matrix = Matrix.Identity(4)  # Use 4x4 matrix for homogeneous coordinates
    
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
            translate_matrix = Matrix.Translation((tx, ty, 0))
            matrix = matrix @ translate_matrix
            
        elif transform_type == 'scale':
            sx = params[0]
            sy = params[1] if len(params) > 1 else sx
            sz = 1  # Keep z-scale as 1
            scale_matrix = Matrix.Scale(sx, 4, (1, 0, 0)) @ Matrix.Scale(sy, 4, (0, 1, 0)) @ Matrix.Scale(sz, 4, (0, 0, 1))
            matrix = matrix @ scale_matrix
            
        elif transform_type == 'rotate':
            angle = params[0]
            if len(params) > 2:
                cx, cy = params[1], params[2]
                # Translate to origin, rotate, translate back
                t1 = Matrix.Translation((-cx, -cy, 0))
                r = Matrix.Rotation(math.radians(angle), 4, 'Z')
                t2 = Matrix.Translation((cx, cy, 0))
                rotation_matrix = t2 @ r @ t1
            else:
                # Rotate around origin
                rotation_matrix = Matrix.Rotation(math.radians(angle), 4, 'Z')
            matrix = matrix @ rotation_matrix
            
        elif transform_type == 'matrix':
            # SVG matrix is (a, b, c, d, e, f) which corresponds to:
            # [a c e]
            # [b d f]
            # [0 0 1]
            if len(params) >= 6:
                a, b, c, d, e, f = params[:6]
                transform_matrix = Matrix((
                    (a, c, 0, e),
                    (b, d, 0, f),
                    (0, 0, 1, 0),
                    (0, 0, 0, 1)
                ))
                matrix = matrix @ transform_matrix
    
    return matrix


def _apply_transform(self, x, y, transform_matrix):
    """Apply transformation matrix to a point."""
    if transform_matrix:
        # Convert 2D point to homogeneous coordinates (add z=0 and w=1)
        from mathutils import Vector
        point = Vector((x, y, 0, 1))
        transformed = transform_matrix @ point
        # Return x, y components (ignore z and w)
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
        
        # Check for valid dimensions
        if width <= 0 or height <= 0:
            log(f"Invalid rectangle dimensions: {width}x{height}")
            return None
        
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
        
        # Check for valid radius
        if r <= 0:
            log(f"Invalid circle radius: {r}")
            return None
        
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
        
        # Check for valid radii
        if rx <= 0 or ry <= 0:
            log(f"Invalid ellipse radii: {rx}x{ry}")
            return None
        
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
        
        # Check if line has length
        if (x1 == x2 and y1 == y2):
            log(f"Zero-length line at ({x1}, {y1})")
            return None
        
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
        
        # Check if we have enough points
        if len(points) < 2:
            log(f"Polyline with too few points: {len(points)}")
            return None
        
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
        
        # Check if we have enough points for a polygon
        if len(points) < 3:
            log(f"Warning: Polygon with less than 3 points: {len(points)}")
            return None
        
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
        # Check if x and y coordinates are present
        if 'x' not in element.attrib or 'y' not in element.attrib:
            log("Text element missing x or y coordinates, using defaults")
            x = float(element.attrib.get('x', 0))
            y = float(element.attrib.get('y', 0))
        else:
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
        
        # If text is empty, log warning and return None
        if not text_content:
            log("Empty text content, skipping")
            return None
        
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

# Moved to svg_parser_paths.py to keep file size manageable
from svg_parser_paths import _parse_path, _parse_path_data
