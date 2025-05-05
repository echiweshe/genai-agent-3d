"""
SVG to 3D Converter - New Implementation

This is a new implementation of the SVG to 3D converter that properly works with the modular structure.
"""

import bpy
import os
import sys
import traceback
import math
from mathutils import Vector, Matrix

from svg_utils import log, hex_to_rgb, clean_scene
from svg_parser import SVGParser


class SVGTo3DConverter:
    """Convert SVG elements to 3D Blender objects."""
    
    def __init__(self, extrude_depth=0.1, scale_factor=0.01, debug=False):
        """
        Initialize the SVG to 3D converter.
        
        Args:
            extrude_depth: Depth for 3D extrusion (default: 0.1)
            scale_factor: Scale factor for SVG to Blender space (default: 0.01)
            debug: Enable debug output
        """
        self.extrude_depth = extrude_depth
        self.scale_factor = scale_factor
        self.debug = debug
        self.width = 0
        self.height = 0
        self.elements = []
        self.material_cache = {}
        self.group_objects = {}
    
    def debug_log(self, message):
        """Debug logging function."""
        if self.debug:
            log(f"DEBUG: {message}")
    
    # Import creation methods from separate modules
    from svg_converter_create import (
        create_material, apply_material_to_object, 
        create_3d_object, create_3d_rect, create_3d_circle, 
        create_3d_ellipse, create_3d_line, create_3d_polyline, 
        create_3d_polygon, create_3d_text
    )
    from svg_converter_group import create_3d_group
    from svg_converter_path import create_3d_path
    
    # Import scene setup methods from separate module
    from svg_converter_scene import (
        setup_camera_and_lighting, setup_default_view, setup_startup_script
    )
    
    def convert(self, svg_data):
        """
        Convert parsed SVG data to a 3D Blender scene.
        
        Args:
            svg_data: Dictionary containing parsed SVG data
                     Should have 'elements', 'width', and 'height' keys
        
        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            # Extract data from the svg_data dictionary
            self.elements = svg_data.get('elements', [])
            self.width = svg_data.get('width', 800)
            self.height = svg_data.get('height', 600)
            
            log(f"Converting SVG with dimensions {self.width}x{self.height} and {len(self.elements)} elements")
            
            # Clean the scene
            clean_scene()
            
            # Create 3D objects for each element
            created_objects = 0
            for i, element in enumerate(self.elements):
                log(f"Processing element {i+1}/{len(self.elements)}: {element['type']}")
                
                # Set the active collection to the scene collection
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
                
                # Ensure we're in object mode
                if bpy.context.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                
                obj = self.create_3d_object(element)
                if obj:
                    created_objects += 1
                    log(f"Created {element['type']} object: {obj.name}")
                else:
                    log(f"Failed to create object for {element['type']}")
            
            log(f"Created {created_objects} 3D objects out of {len(self.elements)} elements")
            
            # Setup camera and lighting
            self.setup_camera_and_lighting()
            
            # Set up the default view
            self.setup_default_view()
            
            # Get list of created objects for startup script
            scene_objects = [obj for obj in bpy.context.scene.objects if obj.type not in ['CAMERA', 'LIGHT', 'EMPTY']]
            
            # Create startup script for proper view when file is opened
            self.setup_startup_script(scene_objects)
            
            log("Conversion completed successfully")
            return True
            
        except Exception as e:
            log(f"Error converting SVG to 3D: {e}")
            traceback.print_exc()
            return False
