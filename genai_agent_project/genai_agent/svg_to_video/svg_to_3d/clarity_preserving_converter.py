"""
Enhanced SVG to 3D Converter Module (Clarity-Preserving Version)

This module converts parsed SVG elements to professional-grade 3D Blender objects
while preserving the clarity and readability of the original diagram.
Uses a minimal extrusion depth of 0.0005 for optimal clarity.
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
from .enhanced_geometry_preserve_clarity import GeometryEnhancer
from .enhanced_scene import SceneEnhancer


class ClarityPreservingSVGTo3DConverter:
    """Convert SVG elements to professional-grade 3D Blender objects while preserving diagram clarity."""
    
    def __init__(self, svg_path, extrude_depth=0.0005, scale_factor=0.01, 
                 style_preset='professional', use_enhanced_features=True, debug=False,
                 custom_elements=False):
        """
        Initialize the clarity-preserving SVG to 3D converter.
        
        Args:
            svg_path: Path to the SVG file
            extrude_depth: Depth for 3D extrusion (default: 0.0005 - reduced for maximum clarity)
            scale_factor: Scale factor for SVG to Blender space (default: 0.01)
            style_preset: Visual style preset ('technical', 'organic', 'professional')
            use_enhanced_features: Whether to use enhanced features (materials, geometry, etc.)
            debug: Enable debug output
            custom_elements: Whether to use element-specific treatment
        """
        self.svg_path = svg_path
        self.extrude_depth = extrude_depth  # Now defaults to 0.0005 (changed from 0.005)
        self.scale_factor = scale_factor
        self.style_preset = style_preset
        self.use_enhanced_features = use_enhanced_features
        self.debug = debug
        self.custom_elements = custom_elements
        
        self.parser = SVGParser(svg_path, debug)
        self.width = 0
        self.height = 0
        self.elements = []
        
        # Initialize enhancers if enhanced features are enabled
        if self.use_enhanced_features:
            self.material_handler = EnhancedSVGMaterialHandler()
            self.geometry_enhancer = GeometryEnhancer(extrude_depth, bevel_width=0.0002)  # Reduced bevel width for clarity
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
    
    def parse_svg(self):
        """Parse the SVG file and extract elements."""
        try:
            log(f"Parsing SVG file: {self.svg_path}")
            
            # Parse SVG file
            self.parser.parse()
            
            # Get document dimensions
            self.width = self.parser.width
            self.height = self.parser.height
            
            # Get elements
            self.elements = self.parser.elements
            
            log(f"SVG parsed. Width: {self.width}, Height: {self.height}, Elements: {len(self.elements)}")
            return True
        except Exception as e:
            log(f"Error parsing SVG: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def setup_scene(self):
        """Set up the Blender scene for conversion."""
        try:
            # Clean up scene
            clean_scene()
            
            # Create camera and lights
            if self.use_enhanced_features:
                self.scene_enhancer.setup_scene(self.width * self.scale_factor, self.height * self.scale_factor, style_preset=self.style_preset)
            else:
                # Simple camera setup
                bpy.ops.object.camera_add(location=(0, 0, 10))
                camera = bpy.context.active_object
                camera.name = "SVGCamera"
                
                # Simple light setup
                bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
                light = bpy.context.active_object
                light.name = "SVGLight"
                light.data.energy = 2.0
            
            return True
        except Exception as e:
            log(f"Error setting up scene: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_element(self, element):
        """
        Convert a single SVG element to a 3D object.
        
        Args:
            element: SVG element dictionary
            
        Returns:
            Blender object or None if conversion failed
        """
        try:
            element_type = element.get('type', 'unknown')
            element_id = element.get('id', f"SVG_{element_type}_{len(self.created_objects)}")
            style = element.get('style', {})
            
            self.debug_log(f"Converting element: {element_id} (type: {element_type})")
            
            # Skip elements without proper attributes
            if 'attributes' not in element:
                self.debug_log(f"Skipping element without attributes: {element_id}")
                return None
            
            # Get element attributes
            attributes = element.get('attributes', {})
            
            # Determine element class for appropriate treatment
            element_class = self.material_handler.classify_element(element_type, style, attributes)
            
            # Create blender object based on element type
            blender_obj = None
            
            if element_type == 'rect':
                # Create rectangle
                x = float(attributes.get('x', 0)) * self.scale_factor
                y = float(attributes.get('y', 0)) * self.scale_factor
                width = float(attributes.get('width', 10)) * self.scale_factor
                height = float(attributes.get('height', 10)) * self.scale_factor
                
                # Create curve for rectangle
                bpy.ops.curve.primitive_bezier_curve_add()
                curve = bpy.context.active_object
                curve.name = element_id
                
                # Set curve points for rectangle
                curve.data.splines.clear()
                curve.data.splines.new('POLY')
                curve.data.splines[0].points.add(3)  # 4 points total for a rectangle
                
                # Set points (need to flip y-coordinate)
                curve.data.splines[0].points[0].co = Vector((x, -y, 0, 1))
                curve.data.splines[0].points[1].co = Vector((x + width, -y, 0, 1))
                curve.data.splines[0].points[2].co = Vector((x + width, -(y + height), 0, 1))
                curve.data.splines[0].points[3].co = Vector((x, -(y + height), 0, 1))
                
                # Make it cyclic (closed)
                curve.data.splines[0].use_cyclic_u = True
                
                # Set curve properties
                curve.data.dimensions = '2D'
                curve.data.fill_mode = 'BOTH'
                
                blender_obj = curve
                
            elif element_type == 'circle':
                # Create circle
                cx = float(attributes.get('cx', 0)) * self.scale_factor
                cy = float(attributes.get('cy', 0)) * self.scale_factor
                r = float(attributes.get('r', 5)) * self.scale_factor
                
                # Create circle mesh
                bpy.ops.mesh.primitive_circle_add(vertices=32, radius=r, location=(cx, -cy, 0))
                circle = bpy.context.active_object
                circle.name = element_id
                
                blender_obj = circle
                
            elif element_type == 'ellipse':
                # Create ellipse
                cx = float(attributes.get('cx', 0)) * self.scale_factor
                cy = float(attributes.get('cy', 0)) * self.scale_factor
                rx = float(attributes.get('rx', 5)) * self.scale_factor
                ry = float(attributes.get('ry', 3)) * self.scale_factor
                
                # Create circle and scale it to ellipse
                bpy.ops.mesh.primitive_circle_add(vertices=32, radius=1.0, location=(cx, -cy, 0))
                ellipse = bpy.context.active_object
                ellipse.name = element_id
                ellipse.scale = (rx, ry, 1.0)
                
                # Apply scale to make it a real ellipse
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                
                blender_obj = ellipse
                
            elif element_type == 'line':
                # Create line
                x1 = float(attributes.get('x1', 0)) * self.scale_factor
                y1 = float(attributes.get('y1', 0)) * self.scale_factor
                x2 = float(attributes.get('x2', 10)) * self.scale_factor
                y2 = float(attributes.get('y2', 10)) * self.scale_factor
                
                # Create curve for line
                bpy.ops.curve.primitive_bezier_curve_add()
                curve = bpy.context.active_object
                curve.name = element_id
                
                # Set curve points for line
                curve.data.splines.clear()
                curve.data.splines.new('POLY')
                curve.data.splines[0].points.add(1)  # 2 points total for a line
                
                # Set points (need to flip y-coordinate)
                curve.data.splines[0].points[0].co = Vector((x1, -y1, 0, 1))
                curve.data.splines[0].points[1].co = Vector((x2, -y2, 0, 1))
                
                # Set curve properties for line appearance
                curve.data.dimensions = '2D'
                curve.data.fill_mode = 'FULL'
                
                blender_obj = curve
                
            elif element_type == 'polyline':
                # Create polyline from points
                points_str = attributes.get('points', '0,0 10,10')
                points_pairs = [p.strip() for p in points_str.split()]
                
                # Create curve for polyline
                bpy.ops.curve.primitive_bezier_curve_add()
                curve = bpy.context.active_object
                curve.name = element_id
                
                # Set curve points for polyline
                curve.data.splines.clear()
                curve.data.splines.new('POLY')
                
                # Parse point pairs
                point_coords = []
                for pp in points_pairs:
                    if ',' in pp:
                        x, y = pp.split(',')
                        point_coords.append((float(x) * self.scale_factor, -float(y) * self.scale_factor, 0))
                
                # Add points to curve
                if len(point_coords) > 1:
                    curve.data.splines[0].points.add(len(point_coords) - 1)
                    
                    for i, (x, y, z) in enumerate(point_coords):
                        curve.data.splines[0].points[i].co = Vector((x, y, z, 1))
                
                # Set curve properties
                curve.data.dimensions = '2D'
                curve.data.fill_mode = 'FULL'
                
                blender_obj = curve
                
            elif element_type == 'polygon':
                # Create polygon from points
                points_str = attributes.get('points', '0,0 10,10 0,10')
                points_pairs = [p.strip() for p in points_str.split()]
                
                # Create curve for polygon
                bpy.ops.curve.primitive_bezier_curve_add()
                curve = bpy.context.active_object
                curve.name = element_id
                
                # Set curve points for polygon
                curve.data.splines.clear()
                curve.data.splines.new('POLY')
                
                # Parse point pairs
                point_coords = []
                for pp in points_pairs:
                    if ',' in pp:
                        x, y = pp.split(',')
                        point_coords.append((float(x) * self.scale_factor, -float(y) * self.scale_factor, 0))
                
                # Add points to curve
                if len(point_coords) > 1:
                    curve.data.splines[0].points.add(len(point_coords) - 1)
                    
                    for i, (x, y, z) in enumerate(point_coords):
                        curve.data.splines[0].points[i].co = Vector((x, y, z, 1))
                
                # Make it cyclic (closed)
                curve.data.splines[0].use_cyclic_u = True
                
                # Set curve properties
                curve.data.dimensions = '2D'
                curve.data.fill_mode = 'BOTH'
                
                blender_obj = curve
                
            elif element_type == 'path':
                # SVG path handling
                d = attributes.get('d', '')
                if not d:
                    return None
                
                # Create a temporary file to import the path
                temp_svg = f"{os.path.splitext(self.svg_path)[0]}_temp_path.svg"
                
                # Create minimal SVG file with just this path
                with open(temp_svg, 'w') as f:
                    f.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}">
  <path d="{d}" style="fill:none;stroke:#000000;stroke-width:1px;" />
</svg>''')
                
                # Import the SVG
                try:
                    bpy.ops.import_curve.svg(filepath=temp_svg)
                    
                    # Get the imported curve
                    imported_curves = [obj for obj in bpy.context.selected_objects if obj.type == 'CURVE']
                    
                    if imported_curves:
                        curve = imported_curves[0]
                        curve.name = element_id
                        
                        # Set curve properties
                        curve.data.dimensions = '2D'
                        
                        # Determine if the path is closed (fill) or open (stroke)
                        if style.get('fill', 'none').lower() == 'none':
                            curve.data.fill_mode = 'FULL'  # Stroke only
                        else:
                            curve.data.fill_mode = 'BOTH'  # Fill and stroke
                        
                        blender_obj = curve
                except Exception as e:
                    log(f"Error importing path: {e}")
                    
                # Clean up temp file
                try:
                    os.remove(temp_svg)
                except:
                    pass
                
            elif element_type == 'text':
                # Create text object
                text_content = element.get('content', '')
                if not text_content:
                    return None
                
                x = float(attributes.get('x', 0)) * self.scale_factor
                y = float(attributes.get('y', 0)) * self.scale_factor
                
                # Create text object
                bpy.ops.object.text_add(location=(x, -y, 0))
                text_obj = bpy.context.active_object
                text_obj.name = element_id
                text_obj.data.body = text_content
                
                # Set text properties
                text_obj.data.align_x = 'LEFT'
                text_obj.data.align_y = 'CENTER'
                
                # Set font size based on attributes
                font_size = style.get('font-size', '12px')
                if font_size.endswith('px'):
                    font_size = float(font_size[:-2]) * self.scale_factor * 0.7  # Convert px to Blender units
                else:
                    font_size = float(font_size) * self.scale_factor * 0.7
                
                text_obj.data.size = font_size
                
                blender_obj = text_obj
            
            # Apply materials if object was created
            if blender_obj:
                # Store style for later use in material application
                blender_obj.style = style
                
                # Store element type
                blender_obj.svg_type = element_type
                
                # Store element attributes
                blender_obj.svg_attributes = attributes
                
                # Apply enhanced geometry
                if self.use_enhanced_features:
                    # Determine importance based on attributes
                    importance = 'normal'
                    if element_class == 'primary_node':
                        importance = 'high'
                    elif element_class in ['secondary_node', 'decoration']:
                        importance = 'normal'
                    elif element_class == 'connector':
                        importance = 'low'
                    
                    # Apply enhanced geometry
                    self.geometry_enhancer.enhance_object_geometry(
                        blender_obj, element_type, element_class, 
                        style_type=self.style_preset, 
                        importance=importance,
                        custom_elements=self.custom_elements
                    )
                    
                    # Apply materials
                    self.material_handler.apply_materials_to_object(
                        blender_obj, style, element_type, 
                        use_presets=True, 
                        style_preset=self.style_preset
                    )
                    
                    # Add subtle displacement for professional style
                    if self.style_preset == 'professional' and self.custom_elements:
                        self.geometry_enhancer.add_subtle_displacement(
                            blender_obj, element_class, self.style_preset
                        )
                
                # Add to created objects list
                self.created_objects.append(blender_obj)
                
                return blender_obj
            
            return None
        
        except Exception as e:
            log(f"Error converting element {element.get('id', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def finalize_scene(self):
        """Finalize the scene after converting all elements."""
        try:
            if self.use_enhanced_features:
                # Create collections for organization
                primary_nodes_coll = bpy.data.collections.new("PrimaryNodes")
                secondary_nodes_coll = bpy.data.collections.new("SecondaryNodes")
                connectors_coll = bpy.data.collections.new("Connectors")
                text_coll = bpy.data.collections.new("Text")
                decorations_coll = bpy.data.collections.new("Decorations")
                
                # Add collections to scene
                for coll in [primary_nodes_coll, secondary_nodes_coll, connectors_coll, text_coll, decorations_coll]:
                    bpy.context.scene.collection.children.link(coll)
                
                # Organize objects into collections
                for obj in self.created_objects:
                    # Remove from scene collection
                    bpy.context.scene.collection.objects.unlink(obj)
                    
                    # Add to appropriate collection
                    if 'geometry_class' in obj:
                        if obj['geometry_class'] == 'primary_node':
                            primary_nodes_coll.objects.link(obj)
                        elif obj['geometry_class'] == 'secondary_node':
                            secondary_nodes_coll.objects.link(obj)
                        elif obj['geometry_class'] == 'connector':
                            connectors_coll.objects.link(obj)
                        elif obj['geometry_class'] == 'text':
                            text_coll.objects.link(obj)
                        else:
                            decorations_coll.objects.link(obj)
                    else:
                        # Fallback to scene collection
                        bpy.context.scene.collection.objects.link(obj)
                
                # Create shadow catcher
                shadow_catcher = self.geometry_enhancer.create_shadow_catcher(self.created_objects, self.style_preset)
                
                # Set up final camera position
                self.scene_enhancer.position_camera_for_objects(self.created_objects, margin=1.2)
                
                # Set up final lighting
                self.scene_enhancer.enhance_lighting(self.style_preset)
                
                # Set up final render settings
                self.scene_enhancer.setup_render_settings(self.style_preset)
            
            return True
        except Exception as e:
            log(f"Error finalizing scene: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert(self):
        """
        Convert SVG to 3D model.
        
        Returns:
            Path to the saved Blender file or None if conversion failed
        """
        try:
            # Parse SVG
            if not self.parse_svg():
                return None
            
            # Set up scene
            if not self.setup_scene():
                return None
            
            # Convert elements
            log(f"Converting {len(self.elements)} SVG elements to 3D")
            for element in self.elements:
                self.convert_element(element)
            
            # Finalize scene
            if not self.finalize_scene():
                return None
            
            # Save Blender file
            output_file = os.path.splitext(self.svg_path)[0]
            if self.use_enhanced_features:
                if self.style_preset == 'professional':
                    output_file += "_professional"
                else:
                    output_file += "_enhanced"
            else:
                output_file += "_basic"
            
            output_file += ".blend"
            
            log(f"Saving 3D model to: {output_file}")
            bpy.ops.wm.save_as_mainfile(filepath=output_file)
            
            return output_file
            
        except Exception as e:
            log(f"Error converting SVG to 3D: {e}")
            import traceback
            traceback.print_exc()
            return None
