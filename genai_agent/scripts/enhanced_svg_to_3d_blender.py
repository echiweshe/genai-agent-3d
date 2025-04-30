"""
Enhanced SVG to 3D Conversion Blender Script

This script is executed by Blender to convert SVG elements to 3D objects.
It parses an SVG file and creates corresponding 3D objects in Blender with improved:
- SVG path handling
- Group support
- Text rendering
- Error handling
- Material creation

Usage:
    blender --background --python enhanced_svg_to_3d_blender.py -- --svg input.svg --output output.blend [--extrude 0.1] [--scale 1.0] [--debug]
"""

import bpy
import os
import sys
import xml.etree.ElementTree as ET
import mathutils
import math
import re
import argparse
import traceback
import json
from math import sin, cos, radians
from xml.etree.ElementTree import ParseError

# Define SVG namespace
SVG_NS = {'svg': 'http://www.w3.org/2000/svg'}

class SVGParser:
    """SVG Parser with enhanced capabilities for path parsing and groups."""
    
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
            'group': 0,
            'polyline': 0,
            'polygon': 0,
            'other': 0
        }
    
    def log(self, message):
        """Debug logging function."""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def parse(self):
        """Parse the SVG file and extract elements."""
        try:
            tree = ET.parse(self.svg_path)
            root = tree.getroot()
            
            # Extract namespace if present
            tag = root.tag
            if '}' in tag:
                self.ns = {'svg': tag.split('}')[0].strip('{')}
            else:
                self.ns = SVG_NS
                
            # Extract viewBox dimensions
            if 'viewBox' in root.attrib:
                self.viewBox = root.attrib['viewBox'].split()
                self.width = float(self.viewBox[2])
                self.height = float(self.viewBox[3])
            else:
                self.width = float(root.attrib.get('width', '800').strip('px'))
                self.height = float(root.attrib.get('height', '600').strip('px'))
                
            self.log(f"SVG dimensions: {self.width}x{self.height}")
            
            # Process all elements including the root for possible child elements
            self._process_element(root)
            
            # Log element counts
            self.log(f"Parsed elements: {json.dumps(self.element_counts, indent=2)}")
            
            return self.elements, self.width, self.height
            
        except ParseError as e:
            print(f"Error parsing SVG file: {e}")
            raise
        except Exception as e:
            print(f"Error in SVG parsing: {e}")
            traceback.print_exc()
            raise
    
    def _process_element(self, element, parent_transform=None):
        """
        Process an SVG element and its children recursively.
        
        Args:
            element: The SVG element to process
            parent_transform: Transform matrix from parent elements
        """
        # Get element tag without namespace
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}')[1]
        
        # Extract transform if present
        transform = element.attrib.get('transform', None)
        transform_matrix = self._parse_transform(transform, parent_transform)
        
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
                'style': self._parse_style(element),
                'children': []
            }
            
            # Process child elements
            for child in element:
                child_element = self._process_single_element(child, transform_matrix)
                if child_element:
                    group_elem['children'].append(child_element)
            
            self.elements.append(group_elem)
            
        else:
            # Process individual element
            elem = self._process_single_element(element, transform_matrix)
            if elem:
                self.elements.append(elem)
    
    def _process_single_element(self, element, parent_transform=None):
        """Process a single SVG element and return its data structure."""
        # Get element tag without namespace
        tag = element.tag
        if '}' in tag:
            tag = tag.split('}')[1]
            
        # Extract transform if present and combine with parent
        transform = element.attrib.get('transform', None)
        transform_matrix = self._parse_transform(transform, parent_transform)
        
        # Parse style attributes
        style = self._parse_style(element)
        
        try:
            if tag == 'rect':
                self.element_counts['rect'] += 1
                return self._parse_rect(element, style, transform_matrix)
                
            elif tag == 'circle':
                self.element_counts['circle'] += 1
                return self._parse_circle(element, style, transform_matrix)
                
            elif tag == 'ellipse':
                self.element_counts['ellipse'] += 1
                return self._parse_ellipse(element, style, transform_matrix)
                
            elif tag == 'line':
                self.element_counts['line'] += 1
                return self._parse_line(element, style, transform_matrix)
                
            elif tag == 'polyline':
                self.element_counts['polyline'] += 1
                return self._parse_polyline(element, style, transform_matrix)
                
            elif tag == 'polygon':
                self.element_counts['polygon'] += 1
                return self._parse_polygon(element, style, transform_matrix)
                
            elif tag == 'path':
                self.element_counts['path'] += 1
                return self._parse_path(element, style, transform_matrix)
                
            elif tag == 'text':
                self.element_counts['text'] += 1
                return self._parse_text(element, style, transform_matrix)
                
            elif tag in ('g', 'svg'):
                # Process group
                for child in element:
                    child_element = self._process_single_element(child, transform_matrix)
                    if child_element:
                        self.elements.append(child_element)
                return None
                
            else:
                self.element_counts['other'] += 1
                self.log(f"Unhandled element type: {tag}")
                return None
                
        except Exception as e:
            print(f"Error processing SVG element {tag}: {e}")
            traceback.print_exc()
            return None
    
    def _parse_style(self, element):
        """Parse style attributes from an element."""
        # Default style values
        style = {
            'fill': '#CCCCCC',
            'stroke': None,
            'stroke-width': 1,
            'opacity': 1,
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
        
        # Handle 'none' values
        if style['fill'] == 'none':
            style['fill'] = None
        
        return style
    
    def _parse_transform(self, transform_str, parent_transform=None):
        """
        Parse SVG transform attribute and return a transformation matrix.
        Supports translate, scale, rotate, matrix transforms.
        """
        # Start with identity matrix or parent transform
        if parent_transform:
            matrix = parent_transform.copy()
        else:
            matrix = mathutils.Matrix.Identity(3)
        
        if not transform_str:
            return matrix
        
        # Parse transform string
        transform_str = transform_str.strip()
        transforms = re.findall(r'(\w+)\s*\(([^)]*)\)', transform_str)
        
        for transform_type, params_str in transforms:
            params = [float(p) for p in re.findall(r'[-+]?[0-9]*\.?[0-9]+', params_str)]
            
            if transform_type == 'translate':
                tx = params[0]
                ty = params[1] if len(params) > 1 else 0
                translate_matrix = mathutils.Matrix.Translation(mathutils.Vector((tx, ty, 0)))
                matrix = translate_matrix @ matrix
                
            elif transform_type == 'scale':
                sx = params[0]
                sy = params[1] if len(params) > 1 else sx
                scale_matrix = mathutils.Matrix.Scale(sx, 3, (1, 0, 0)) @ mathutils.Matrix.Scale(sy, 3, (0, 1, 0))
                matrix = scale_matrix @ matrix
                
            elif transform_type == 'rotate':
                angle = params[0]
                if len(params) > 2:
                    cx, cy = params[1], params[2]
                    # Translate to origin, rotate, translate back
                    t1 = mathutils.Matrix.Translation(mathutils.Vector((-cx, -cy, 0)))
                    r = mathutils.Matrix.Rotation(math.radians(angle), 3, 'Z')
                    t2 = mathutils.Matrix.Translation(mathutils.Vector((cx, cy, 0)))
                    rotation_matrix = t2 @ r @ t1
                else:
                    # Rotate around origin
                    rotation_matrix = mathutils.Matrix.Rotation(math.radians(angle), 3, 'Z')
                matrix = rotation_matrix @ matrix
                
            elif transform_type == 'matrix':
                # SVG matrix is (a, b, c, d, e, f) which corresponds to:
                # [a c e]
                # [b d f]
                # [0 0 1]
                if len(params) >= 6:
                    a, b, c, d, e, f = params[:6]
                    transform_matrix = mathutils.Matrix((
                        (a, c, e),
                        (b, d, f),
                        (0, 0, 1)
                    ))
                    matrix = transform_matrix @ matrix
        
        return matrix
    
    def _apply_transform(self, x, y, transform_matrix):
        """Apply transformation matrix to a point."""
        if transform_matrix:
            point = mathutils.Vector((x, y, 1))
            transformed = transform_matrix @ point
            return transformed.x, transformed.y
        return x, y
