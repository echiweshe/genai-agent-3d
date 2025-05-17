"""
Enhanced SVG to 3D Converter Module

This module converts parsed SVG elements to professional-grade 3D Blender objects.
It integrates improved materials, geometry, and scene organization.
"""

import bpy
import os
import sys
import traceback
import math
import mathutils
from mathutils import Vector, Matrix

from .svg_utils import log, hex_to_rgb, clean_scene
from .svg_parser import SVGParser
from .enhanced_materials import EnhancedSVGMaterialHandler
from .enhanced_geometry import GeometryEnhancer
from .enhanced_scene import SceneEnhancer


class EnhancedSVGTo3DConverter:
    """Convert SVG elements to professional-grade 3D Blender objects."""
    
    def __init__(self, svg_path, extrude_depth=0.1, scale_factor=0.01, 
                 style_preset='technical', use_enhanced_features=True, debug=False):
        """
        Initialize the enhanced SVG to 3D converter.
        
        Args:
            svg_path: Path to the SVG file
            extrude_depth: Depth for 3D extrusion (default: 0.1)
            scale_factor: Scale factor for SVG to Blender space (default: 0.01)
            style_preset: Visual style preset ('technical', 'organic', 'glossy', 'metal')
            use_enhanced_features: Whether to use enhanced features (materials, geometry, etc.)
            debug: Enable debug output
        """
        self.svg_path = svg_path
        self.extrude_depth = extrude_depth
        self.scale_factor = scale_factor
        self.style_preset = style_preset
        self.use_enhanced_features = use_enhanced_features
        self.debug = debug
        
        self.parser = SVGParser(svg_path, debug)
        self.width = 0
        self.height = 0
        self.elements = []
        
        # Initialize enhancers if enhanced features are enabled
        if self.use_enhanced_features:
            self.material_handler = EnhancedSVGMaterialHandler()
            self.geometry_enhancer = GeometryEnhancer(extrude_depth, bevel_width=0.01)
            self.scene_enhancer = SceneEnhancer(scene_name=os.path.basename(svg_path))
        else:
            # Use original material handler as fallback
            from .svg_converter_materials_fixed import SVGMaterialHandler
            self.material_handler = SVGMaterialHandler()
        
        # Storage for created objects
        self.created_objects = []
        self.group_objects = {}
    
    def debug_log(self, message):
        """Debug logging function."""
        if self.debug:
            log(f"DEBUG: {message}")
    
    # Import creation methods from separate modules - replaced with enhanced versions
    def create_material(self, style, element_type=None, element_class=None):
        """Create a material for an SVG element."""
        if self.use_enhanced_features:
            # Use the enhanced material handler
            fill_color = style.get('fill', '#CCCCCC')
            opacity = float(style.get('opacity', 1.0))
            fill_opacity = float(style.get('fill-opacity', opacity))
            
            return self.material_handler.create_fill_material(fill_color, fill_opacity, element_class)
        else:
            # Use the original material handler
            fill_color = style.get('fill', '#CCCCCC')
            opacity = float(style.get('opacity', 1.0))
            fill_opacity = float(style.get('fill-opacity', opacity))
            
            return self.material_handler.create_fill_material(fill_color, fill_opacity)
    
    def apply_material_to_object(self, obj, style, element_type=None):
        """Apply material to an object."""
        try:
            if self.use_enhanced_features:
                # Classify element for better material application
                element_class = self.classify_element(element_type, style)
                
                # Apply enhanced materials
                return self.material_handler.apply_materials_to_object(obj, style, element_type, use_presets=True)
            else:
                # Use original material handler
                return self.material_handler.apply_materials_to_object(obj, style)
        except Exception as e:
            log(f"Error applying material: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def classify_element(self, element_type, style):
        """
        Determine semantic class of an element for specialized handling.
        
        Args:
            element_type: Type of SVG element
            style: Style dictionary
            
        Returns:
            Element class string ('primary_node', 'connector', etc.)
        """
        if element_type == 'text':
            return 'text'
        
        if element_type in ['line', 'polyline'] or (element_type == 'path' and style.get('fill', '').lower() == 'none'):
            return 'connector'
        
        if element_type in ['rect', 'circle', 'ellipse', 'polygon']:
            return 'primary_node'
        
        return 'decoration'
    
    def enhance_object_geometry(self, obj, element_type, style):
        """Apply geometry enhancements to the object."""
        if self.use_enhanced_features and obj:
            # Classify element
            element_class = self.classify_element(element_type, style)
            
            # Apply geometry enhancements
            return self.geometry_enhancer.enhance_object_geometry(
                obj, 
                element_type, 
                element_class, 
                style_type=self.style_preset, 
                importance='high' if element_class == 'primary_node' else 'normal'
            )
        return obj
    
    def create_3d_object(self, element):
        """Create a 3D object from an SVG element."""
        try:
            element_type = element.get('type', 'unknown')
            
            log(f"Creating 3D object of type {element_type}")
            
            # Create base object using appropriate function
            if element_type == 'rect':
                obj = self.create_3d_rect(element)
            elif element_type == 'circle':
                obj = self.create_3d_circle(element)
            elif element_type == 'ellipse':
                obj = self.create_3d_ellipse(element)
            elif element_type == 'line':
                obj = self.create_3d_line(element)
            elif element_type == 'polyline':
                obj = self.create_3d_polyline(element)
            elif element_type == 'polygon':
                obj = self.create_3d_polygon(element)
            elif element_type == 'text':
                obj = self.create_3d_text(element)
            elif element_type == 'path':
                obj = self.create_3d_path(element)
            elif element_type == 'group':
                obj = self.create_3d_group(element)
            else:
                log(f"Unsupported element type: {element_type}")
                return None
            
            # If object was created successfully
            if obj:
                # Apply geometry enhancements
                obj = self.enhance_object_geometry(obj, element_type, element.get('style', {}))
                
                # Store object for later organization
                self.created_objects.append(obj)
                
                # Add to appropriate collection if using enhanced features
                if self.use_enhanced_features:
                    element_class = self.classify_element(element_type, element.get('style', {}))
                    self.scene_enhancer.add_object_to_collection(obj, element_class)
                
                # Store original element info as custom properties
                obj['svg_type'] = element_type
                obj['svg_element'] = element.get('id', '')
                
                if element.get('id'):
                    obj.name = f"{element_type.capitalize()}_{element.get('id')}"
                
                log(f"Created 3D object: {obj.name}")
            
            return obj
        except Exception as e:
            log(f"Error creating 3D object: {e}")
            traceback.print_exc()
            return None
    
    # Import primary creation methods
    from .svg_converter_create import (
        create_3d_rect, create_3d_circle, create_3d_ellipse, create_3d_line, 
        create_3d_polyline, create_3d_polygon, create_3d_text
    )
    
    from .svg_converter_group import create_3d_group
    from .svg_converter_path import create_3d_path
    
    def setup_camera_and_lighting(self):
        """
        Set up camera and lighting for the 3D scene.
        Uses the enhanced scene setup if enhanced features are enabled.
        """
        try:
            log("Setting up camera and lighting...")
            
            if self.use_enhanced_features and self.created_objects:
                # Use enhanced scene setup
                scene_elements = self.scene_enhancer.setup_enhanced_scene(self.created_objects)
                log("Enhanced camera and lighting setup complete")
                return True
            else:
                # Use original setup
                from .svg_converter_scene import setup_camera_and_lighting as original_setup
                return original_setup(self)
        except Exception as e:
            log(f"Error setting up camera and lighting: {e}")
            traceback.print_exc()
            return False
    
    def setup_default_view(self):
        """Set up the default view in Blender."""
        try:
            # Set up view for all 3D viewports
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    space = area.spaces.active
                    space.region_3d.view_perspective = 'ORTHO'  # Orthographic view
                    space.region_3d.view_rotation = (1, 0, 0, 0)  # Top view
                    
                    # Set view to camera view
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            override = {'area': area, 'region': region}
                            bpy.ops.view3d.view_camera(override)
                            break
            
            log("Default view setup complete")
            return True
        except Exception as e:
            log(f"Error setting up default view: {e}")
            return False
    
    def setup_startup_script(self, scene_objects):
        """Create a startup script for setting up the view when file is opened."""
        try:
            if self.use_enhanced_features:
                # Use enhanced startup script setup
                return self.scene_enhancer.setup_startup_script(scene_objects)
            else:
                # Use original setup
                from .svg_converter_scene import setup_startup_script as original_setup
                return original_setup(self, scene_objects)
        except Exception as e:
            log(f"Error setting up startup script: {e}")
            return False
    
    def create_shadow_catcher(self):
        """Create a shadow catcher plane underneath the scene."""
        try:
            if self.use_enhanced_features and self.created_objects:
                # Use enhanced geometry enhancer to create shadow catcher
                return self.geometry_enhancer.create_shadow_catcher(self.created_objects)
            return None
        except Exception as e:
            log(f"Error creating shadow catcher: {e}")
            return None
    
    def convert(self):
        """Convert the SVG file to a 3D Blender scene with enhanced features."""
        log(f"Converting SVG with enhanced features: {self.svg_path}")
        
        try:
            # Clean the scene
            clean_scene()
            
            # Parse SVG
            self.elements, self.width, self.height = self.parser.parse()
            log(f"Parsed SVG with dimensions {self.width}x{self.height} and {len(self.elements)} elements")
            
            # Output detailed element info for debugging
            for i, element in enumerate(self.elements):
                self.debug_log(f"Element {i+1}: Type={element['type']}")
            
            # Initialize collections if using enhanced features
            if self.use_enhanced_features:
                self.scene_enhancer.create_collection_hierarchy()
            
            # Create 3D objects for each element
            created_objects = 0
            for i, element in enumerate(self.elements):
                log(f"Processing element {i+1}/{len(self.elements)}: {element['type']}")
                
                # Set the active collection to the scene collection to ensure objects are created in the right place
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
                
                # Ensure we're in object mode
                if bpy.context.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                
                obj = self.create_3d_object(element)
                if obj:
                    created_objects += 1
                    log(f"Added {element['type']} object to scene: {obj.name}")
                else:
                    log(f"Failed to create object for {element['type']}")
            
            log(f"Created {created_objects} 3D objects out of {len(self.elements)} elements")
            
            # Verify objects in scene
            scene_objects = [obj for obj in bpy.context.scene.objects if obj.type not in ['CAMERA', 'LIGHT', 'EMPTY']]
            log(f"Scene contains {len(scene_objects)} objects (excluding cameras and lights)")
            
            # Check if we have any objects to work with
            if created_objects == 0:
                log("Warning: No 3D objects were created from SVG elements")
                # We'll still continue to set up camera and lighting
            
            # Ensure all objects are visible
            for obj in bpy.data.objects:
                obj.hide_viewport = False
                obj.hide_render = False
            
            # Create shadow catcher if enhanced features are enabled
            if self.use_enhanced_features:
                self.create_shadow_catcher()
            
            # Setup camera and lighting
            self.setup_camera_and_lighting()
            
            # Set up the default view for saved file
            self.setup_default_view()
            
            # Create startup script for proper view when file is opened
            self.setup_startup_script(scene_objects)
            
            log("Enhanced conversion completed")
            return True
        except Exception as e:
            log(f"Error converting SVG to 3D: {e}")
            traceback.print_exc()
            return False


# Factory function to get appropriate converter
def get_svg_converter(svg_path, extrude_depth=0.1, scale_factor=0.01, use_enhanced=True, style_preset='technical', debug=False):
    """Return appropriate SVG converter based on settings"""
    if use_enhanced:
        return EnhancedSVGTo3DConverter(
            svg_path, 
            extrude_depth=extrude_depth,
            scale_factor=scale_factor,
            style_preset=style_preset,
            use_enhanced_features=True,
            debug=debug
        )
    else:
        # Import the original converter for fallback
        from .svg_converter import SVGTo3DConverter
        return SVGTo3DConverter(
            svg_path, 
            extrude_depth=extrude_depth,
            scale_factor=scale_factor,
            debug=debug
        )
