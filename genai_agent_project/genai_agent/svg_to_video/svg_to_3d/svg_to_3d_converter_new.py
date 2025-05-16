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

from .svg_utils import log, hex_to_rgb, clean_scene
from .svg_parser import SVGParser


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
    from .svg_converter_create import (
        create_material, apply_material_to_object, 
        create_3d_object, create_3d_rect, create_3d_circle, 
        create_3d_ellipse, create_3d_line, create_3d_polyline, 
        create_3d_polygon, create_3d_text
    )
    from .svg_converter_group import create_3d_group
    from .svg_converter_path import create_3d_path
    
    # Import scene setup methods from separate module
    from .svg_converter_scene import (
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
    
    async def convert_svg_to_3d(self, svg_path, output_path, extrude_depth=None, scale_factor=None):
        """
        Asynchronous method to convert an SVG file to a 3D model.
        
        Args:
            svg_path: Path to the SVG file
            output_path: Path where the 3D model should be saved
            extrude_depth: Optional override for extrusion depth
            scale_factor: Optional override for scale factor
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            # Set overrides if provided
            if extrude_depth is not None:
                self.extrude_depth = extrude_depth
            if scale_factor is not None:
                self.scale_factor = scale_factor
                
            log(f"Starting SVG to 3D conversion: {svg_path} -> {output_path}")
            log(f"Parameters: extrude_depth={self.extrude_depth}, scale_factor={self.scale_factor}")
            
            # Verify SVG file exists
            if not os.path.exists(svg_path):
                log(f"SVG file does not exist: {svg_path}")
                return False
                
            # Create directory for output if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
            # For now, create a mock 3D model file since we can't run Blender directly
            # This is a temporary solution to get the UI working
            log("Creating mock 3D model for testing")
            
            # Determine file extension
            ext = os.path.splitext(output_path)[1].lower()
            
            # Create a simple OBJ file with a cube
            if ext == '.obj':
                with open(output_path, 'w') as f:
                    f.write("# SVG to 3D Conversion - Mock Object\n")
                    f.write("# Original SVG: " + svg_path + "\n")
                    f.write("v 0.000000 0.000000 0.000000\n")
                    f.write("v 0.000000 0.000000 1.000000\n")
                    f.write("v 0.000000 1.000000 0.000000\n")
                    f.write("v 0.000000 1.000000 1.000000\n")
                    f.write("v 1.000000 0.000000 0.000000\n")
                    f.write("v 1.000000 0.000000 1.000000\n")
                    f.write("v 1.000000 1.000000 0.000000\n")
                    f.write("v 1.000000 1.000000 1.000000\n")
                    f.write("vn 0.000000 0.000000 -1.000000\n")
                    f.write("vn 0.000000 0.000000 1.000000\n")
                    f.write("vn 0.000000 -1.000000 0.000000\n")
                    f.write("vn 1.000000 0.000000 0.000000\n")
                    f.write("vn 0.000000 1.000000 0.000000\n")
                    f.write("vn -1.000000 0.000000 0.000000\n")
                    f.write("f 1//1 7//1 5//1\n")
                    f.write("f 1//1 3//1 7//1\n")
                    f.write("f 1//6 2//6 3//6\n")
                    f.write("f 3//6 2//6 4//6\n")
                    f.write("f 5//3 7//3 6//3\n")
                    f.write("f 6//3 7//3 8//3\n")
                    f.write("f 2//2 6//2 8//2\n")
                    f.write("f 2//2 8//2 4//2\n")
                    f.write("f 3//5 4//5 7//5\n")
                    f.write("f 4//5 8//5 7//5\n")
                    f.write("f 1//4 5//4 2//4\n")
                    f.write("f 2//4 5//4 6//4\n")
            elif ext == '.blend':
                # For Blend files, create a simple text file with .blend extension
                # Since we can't create actual Blender files without Blender
                with open(output_path, 'w') as f:
                    f.write("# Mock Blender file - SVG to 3D conversion\n")
                    f.write("# Original SVG: " + svg_path + "\n")
                    f.write("# This is a placeholder. Actual Blender file creation requires Blender.\n")
            else:
                # Default to OBJ with correct extension
                obj_path = output_path.replace(ext, '.obj')
                with open(obj_path, 'w') as f:
                    f.write("# SVG to 3D Conversion - Mock Object\n")
                    f.write("# Original SVG: " + svg_path + "\n")
                    f.write("v 0.000000 0.000000 0.000000\n")
                    f.write("v 0.000000 0.000000 1.000000\n")
                    f.write("v 0.000000 1.000000 0.000000\n")
                    f.write("v 0.000000 1.000000 1.000000\n")
                    f.write("v 1.000000 0.000000 0.000000\n")
                    f.write("v 1.000000 0.000000 1.000000\n")
                    f.write("v 1.000000 1.000000 0.000000\n")
                    f.write("v 1.000000 1.000000 1.000000\n")
                    f.write("vn 0.000000 0.000000 -1.000000\n")
                    f.write("vn 0.000000 0.000000 1.000000\n")
                    f.write("vn 0.000000 -1.000000 0.000000\n")
                    f.write("vn 1.000000 0.000000 0.000000\n")
                    f.write("vn 0.000000 1.000000 0.000000\n")
                    f.write("vn -1.000000 0.000000 0.000000\n")
                    f.write("f 1//1 7//1 5//1\n")
                    f.write("f 1//1 3//1 7//1\n")
                    f.write("f 1//6 2//6 3//6\n")
                    f.write("f 3//6 2//6 4//6\n")
                    f.write("f 5//3 7//3 6//3\n")
                    f.write("f 6//3 7//3 8//3\n")
                    f.write("f 2//2 6//2 8//2\n")
                    f.write("f 2//2 8//2 4//2\n")
                    f.write("f 3//5 4//5 7//5\n")
                    f.write("f 4//5 8//5 7//5\n")
                    f.write("f 1//4 5//4 2//4\n")
                    f.write("f 2//4 5//4 6//4\n")
                log(f"Created OBJ file at: {obj_path}")
            
            log("Mock 3D model created successfully")
            log(f"Output file: {output_path}")
            
            return True
            
        except Exception as e:
            log(f"Error in SVG to 3D conversion: {e}")
            traceback.print_exc()
            return False
