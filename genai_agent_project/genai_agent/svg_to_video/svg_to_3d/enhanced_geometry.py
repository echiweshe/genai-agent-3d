"""
Enhanced geometry handling for SVG to 3D conversion
Implements smarter extrusion, bevels, and curve optimization
"""

import bpy
import math
import mathutils
from .svg_utils import log


class GeometryEnhancer:
    """
    Provides enhanced geometry handling for SVG to 3D conversion
    Improves object quality and appearance through various geometry enhancements
    """
    
    def __init__(self, base_extrude_depth=0.1, bevel_width=0.01):
        """
        Initialize the geometry enhancer
        
        Args:
            base_extrude_depth: Base extrusion depth for 3D objects
            bevel_width: Default bevel width for enhanced edges
        """
        self.base_extrude_depth = base_extrude_depth
        self.bevel_width = bevel_width
        self.min_depth = base_extrude_depth * 0.3
        self.max_depth = base_extrude_depth * 1.5
    
    def determine_extrusion_depth(self, element_type, element_class, importance='normal'):
        """
        Determine appropriate extrusion depth based on element type and context
        
        Args:
            element_type: SVG element type (rect, circle, text, etc.)
            element_class: Semantic class ('node', 'connector', 'text', etc.)
            importance: Importance level ('high', 'normal', 'low')
            
        Returns:
            Calculated extrusion depth
        """
        base_depth = self.base_extrude_depth
        
        # Adjust depth based on element type and class
        if element_class == 'primary_node':
            # Primary nodes get full extrusion
            depth = base_depth * 1.2
        elif element_class == 'secondary_node':
            # Secondary nodes get normal extrusion
            depth = base_depth
        elif element_class == 'connector':
            # Connectors get reduced extrusion
            depth = base_depth * 0.5
        elif element_class == 'text':
            # Text gets moderate extrusion
            depth = base_depth * 0.7
        else:
            # Default extrusion
            depth = base_depth
        
        # Adjust based on importance
        if importance == 'high':
            depth *= 1.2
        elif importance == 'low':
            depth *= 0.8
        
        # Ensure within limits
        depth = max(self.min_depth, min(depth, self.max_depth))
        
        log(f"Calculated extrusion depth for {element_type} ({element_class}): {depth}")
        return depth
    
    def apply_bevels(self, obj, element_class=None, style_type=None):
        """
        Apply appropriate bevels to an object based on its type and class
        
        Args:
            obj: Blender object
            element_class: Semantic class of the element
            style_type: Style type ('technical', 'organic', etc.)
            
        Returns:
            Modified Blender object
        """
        try:
            # Determine bevel parameters based on element class and style
            if style_type == 'technical' or element_class in ['connector', 'primary_node']:
                # Sharp bevels for technical elements
                bevel_width = self.bevel_width
                segments = 2
                profile = 0.7  # More angular profile
            elif style_type == 'organic' or element_class == 'secondary_node':
                # Smoother bevels for organic shapes
                bevel_width = self.bevel_width * 1.5
                segments = 4
                profile = 0.3  # Rounder profile
            elif element_class == 'text':
                # Fine bevels for text
                bevel_width = self.bevel_width * 0.5
                segments = 3
                profile = 0.5
            else:
                # Default bevel settings
                bevel_width = self.bevel_width
                segments = 3
                profile = 0.5
            
            # Add bevel modifier
            if obj.type == 'MESH':
                # Use modifier for mesh objects
                bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
                bevel.width = bevel_width
                bevel.segments = segments
                bevel.profile = profile
                bevel.limit_method = 'ANGLE'
                bevel.angle_limit = math.radians(45)
                
                log(f"Applied bevel modifier to {obj.name} (width: {bevel_width}, segments: {segments})")
            elif obj.type == 'CURVE':
                # Use bevel settings for curve objects
                obj.data.bevel_depth = bevel_width * 10  # Different scale for curves
                obj.data.bevel_resolution = segments - 1  # Adjust for curve bevel resolution
                
                log(f"Applied curve bevel to {obj.name} (depth: {bevel_width * 10}, resolution: {segments - 1})")
            elif obj.type == 'FONT':
                # Text bevels
                obj.data.bevel_depth = bevel_width * 5
                obj.data.bevel_resolution = segments - 1
                
                log(f"Applied text bevel to {obj.name} (depth: {bevel_width * 5}, resolution: {segments - 1})")
            
            return obj
        except Exception as e:
            log(f"Error applying bevels: {e}")
            import traceback
            traceback.print_exc()
            return obj
    
    def optimize_curve_resolution(self, curve_obj, importance='normal'):
        """
        Optimize curve resolution based on element importance
        
        Args:
            curve_obj: Blender curve object
            importance: Importance level ('high', 'normal', 'low')
            
        Returns:
            Modified curve object
        """
        try:
            if not curve_obj or curve_obj.type != 'CURVE':
                return curve_obj
            
            # Set resolution based on importance
            if importance == 'high':
                curve_obj.data.resolution_u = 12  # Higher resolution for important curves
            elif importance == 'low':
                curve_obj.data.resolution_u = 6   # Lower resolution for background elements
            else:
                curve_obj.data.resolution_u = 8   # Default resolution
            
            log(f"Optimized curve resolution for {curve_obj.name}: {curve_obj.data.resolution_u}")
            return curve_obj
        except Exception as e:
            log(f"Error optimizing curve resolution: {e}")
            return curve_obj
    
    def enhance_object_geometry(self, obj, element_type, element_class, style_type=None, importance='normal'):
        """
        Apply all geometry enhancements to an object
        
        Args:
            obj: Blender object
            element_type: SVG element type
            element_class: Semantic class of element
            style_type: Style type for the object
            importance: Importance level
            
        Returns:
            Enhanced Blender object
        """
        try:
            # Skip if object is None
            if obj is None:
                return None
            
            log(f"Enhancing geometry for {obj.name} ({element_type}, {element_class})")
            
            # Apply extrusion for appropriate object types
            if obj.type == 'CURVE':
                # Determine appropriate extrusion depth
                extrude_depth = self.determine_extrusion_depth(element_type, element_class, importance)
                
                # Apply extrusion to curve
                obj.data.extrude = extrude_depth
                log(f"Applied extrusion to curve: {extrude_depth}")
                
                # Optimize curve resolution
                self.optimize_curve_resolution(obj, importance)
            
            elif obj.type == 'FONT':
                # Determine appropriate extrusion depth for text
                extrude_depth = self.determine_extrusion_depth('text', 'text', importance)
                
                # Apply extrusion to text
                obj.data.extrude = extrude_depth
                log(f"Applied extrusion to text: {extrude_depth}")
            
            # Apply bevels to enhance edges
            self.apply_bevels(obj, element_class, style_type)
            
            # Add custom properties for animation system
            obj['geometry_class'] = element_class
            obj['geometry_importance'] = importance
            
            return obj
        except Exception as e:
            log(f"Error enhancing object geometry: {e}")
            import traceback
            traceback.print_exc()
            return obj
    
    def create_shadow_catcher(self, scene_objects):
        """
        Create a shadow catcher plane underneath all objects
        
        Args:
            scene_objects: List of objects in the scene
            
        Returns:
            Shadow catcher object
        """
        try:
            # Determine bounds of all objects
            min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
            
            for obj in scene_objects:
                if obj.type not in ['CAMERA', 'LIGHT', 'EMPTY']:
                    # Get object bounds
                    for point in obj.bound_box:
                        # Transform point to world space
                        world_point = obj.matrix_world @ mathutils.Vector(point)
                        min_x = min(min_x, world_point.x)
                        min_y = min(min_y, world_point.y)
                        max_x = max(max_x, world_point.x)
                        max_y = max(max_y, world_point.y)
            
            # Add padding
            padding = 2.0
            min_x -= padding
            min_y -= padding
            max_x += padding
            max_y += padding
            
            # Calculate dimensions and center
            width = max_x - min_x
            height = max_y - min_y
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            # Create plane
            bpy.ops.mesh.primitive_plane_add(
                size=1.0,
                location=(center_x, center_y, -self.base_extrude_depth * 0.5)
            )
            
            # Get the created object
            shadow_catcher = bpy.context.active_object
            shadow_catcher.name = "ShadowCatcher"
            
            # Scale to cover all objects
            shadow_catcher.scale.x = width
            shadow_catcher.scale.y = height
            
            # Create shadow catcher material
            shadow_material = bpy.data.materials.new("ShadowCatcherMaterial")
            shadow_material.use_nodes = True
            shadow_material.node_tree.nodes.clear()
            
            # Get node tree
            nodes = shadow_material.node_tree.nodes
            links = shadow_material.node_tree.links
            
            # Create nodes
            output = nodes.new('ShaderNodeOutputMaterial')
            diffuse = nodes.new('ShaderNodeBsdfDiffuse')
            diffuse.inputs[0].default_value = (0.8, 0.8, 0.8, 1.0)
            
            # Connect nodes
            links.new(diffuse.outputs[0], output.inputs[0])
            
            # Assign material
            shadow_catcher.data.materials.append(shadow_material)
            
            # Mark as shadow catcher for Cycles
            shadow_catcher.is_shadow_catcher = True
            
            log(f"Created shadow catcher: {shadow_catcher.name}")
            return shadow_catcher
        except Exception as e:
            log(f"Error creating shadow catcher: {e}")
            return None
