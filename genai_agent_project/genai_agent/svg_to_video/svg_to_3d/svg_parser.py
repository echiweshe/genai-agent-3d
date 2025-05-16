"""
Enhanced SVG Parser Module

This module contains the SVGParser class for parsing SVG files.
It extracts elements like rectangles, circles, lines, polygons, and paths
from SVG files and prepares them for 3D conversion.
"""

import os
import sys
import xml.etree.ElementTree as ET
import traceback
import math
import re
from mathutils import Vector, Matrix
from .svg_utils import log


class SVGParser:
    """Enhanced SVG Parser with path support."""
    
    def __init__(self, debug=False):
        """
        Initialize the SVG parser.
        
        Args:
            debug: Enable debug output
        """
        self.svg_path = None
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
    
    def parse(self, svg_path):
        """Parse the SVG file and extract elements."""
        self.svg_path = svg_path
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
            
            # Return data in the format expected by the converter
            return {
                'elements': self.elements,
                'width': self.width,
                'height': self.height
            }
            
        except Exception as e:
            log(f"Error parsing SVG: {e}")
            traceback.print_exc()
            return None
    
    from .svg_parser_elements import (
        _process_element, _parse_style, _parse_transform, _apply_transform,
        _parse_rect, _parse_circle, _parse_ellipse, _parse_line, 
        _parse_polyline, _parse_polygon, _parse_text, _parse_path, _parse_path_data
    )
