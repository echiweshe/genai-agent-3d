"""
Enhanced geometry handling for SVG to 3D conversion
Modified to preserve diagram clarity while adding subtle 3D effects
"""

import bpy
import math
import mathutils
from .svg_utils import log


class GeometryEnhancer:
    """
    Provides enhanced geometry handling for SVG to 3D conversion
    Preserves diagram clarity with minimal 3D enhancements
    """
    
    def __init__(self, base_extrude_depth=0.0005, bevel_width=0.0002):
        """
        Initialize the geometry enhancer with minimized default values
        
        Args:
            base_extrude_depth: Base extrusion depth for 3D objects (reduced to 0.0005 for clarity)
            bevel_width: Default bevel width for enhanced edges (reduced to 0.0002 for clarity)
        """
        self.base_extrude_depth = base_extrude_depth
        self.bevel_width = bevel_width
        self.min_depth = base_extrude_depth * 0.5
        self.max_depth = base_extrude_depth * 2.0
    
    def determine_extrusion_depth(self, element_type, element_class, importance='normal', custom_elements=False):
        """
        Determine appropriate extrusion depth based on element type and context
        Significantly reduced to preserve clarity
        
        Args:
            element_type: SVG element type (rect, circle, text, etc.)
            element_class: Semantic class ('node', 'connector', 'text', etc.)
            importance: Importance level ('high', 'normal', 'low')
            custom_elements: Whether to use element-specific treatment
            
        Returns:
            Calculated extrusion depth
        """
        base_depth = self.base_extrude_depth
        
        if not custom_elements:
            # Standard clarity preservation mode with uniform extrusion
            depth = base_depth * 0.8
        else:
            # Element-specific treatment for optimal visual hierarchy
            if element_class == 'primary_node':
                # Primary nodes get slightly more extrusion to stand out
                depth = base_depth * 1.2
            elif element_class == 'secondary_node':
                # Secondary nodes get standard extrusion
                depth = base_depth * 0.9
            elif element_class == 'connector':
                # Connectors get minimal extrusion to stay in background
                depth = base_depth * 0.3
            elif element_class == 'text':
                # Text gets minimal extrusion for optimal readability
                depth = base_depth * 0.2
            else:
                # Default extrusion
                depth = base_depth * 0.6
            
            # Adjust based on importance
            if importance == 'high':
                depth *= 1.2
            elif importance == 'low':
                depth *= 0.7
        
        # Ensure within limits
        depth = max(self.min_depth, min(depth, self.max_depth))
        
        log(f"Calculated extrusion depth for {element_type} ({element_class}): {depth}")
        return depth
    
    def apply_bevels(self, obj, element_class=None, style_type=None, custom_elements=False):
        """
        Apply subtle bevels to an object based on its type and class
        
        Args:
            obj: Blender object
            element_class: Semantic class of the element
            style_type: Style type ('technical', 'organic', 'professional', etc.)
            custom_elements: Whether to use element-specific treatment
            
        Returns:
            Modified Blender object
        """
        try:
            # Determine bevel parameters based on element class and style
            if style_type == 'professional':
                # Professional style with refined bevels
                if custom_elements and element_class == 'primary_node':
                    # More pronounced bevels for primary nodes
                    bevel_width = self.bevel_width * 1.5
                    segments = 3
                    profile = 0.6
                elif custom_elements and element_class == 'connector':
                    # Very subtle bevels for connectors
                    bevel_width = self.bevel_width * 0.3
                    segments = 2
                    profile = 0.5
                elif custom_elements and element_class == 'text':
                    # Minimal bevels for text to ensure readability
                    bevel_width = self.bevel_width * 0.2
                    segments = 2
                    profile = 0.4
                else:
                    # Standard professional bevels
                    bevel_width = self.bevel_width * 0.8
                    segments = 3
                    profile = 0.5
            elif style_type == 'technical' or element_class in ['connector', 'primary_node']:
                # Clean bevels for technical elements
                bevel_width = self.bevel_width * 0.6
                segments = 2
                profile = 0.7
            elif style_type == 'organic' or element_class == 'secondary_node':
                # Smoother bevels for organic shapes
                bevel_width = self.bevel_width * 0.8
                segments = 3
                profile = 0.3
            elif element_class == 'text':
                # Almost imperceptible bevels for text
                bevel_width = self.bevel_width * 0.2
                segments = 1
                profile = 0.5
            else:
                # Default subtle bevel settings
                bevel_width = self.bevel_width * 0.5
                segments = 2
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
                obj.data.bevel_depth = bevel_width * 3.5  # Slightly increased for better visibility
                obj.data.bevel_resolution = max(1, segments - 1)
                
                log(f"Applied curve bevel to {obj.name} (depth: {bevel_width * 3.5}, resolution: {segments - 1})")
            elif obj.type == 'FONT':
                # Text bevels
                obj.data.bevel_depth = bevel_width * 1.2  # Slightly increased for text readability
                obj.data.bevel_resolution = 2  # Higher resolution for text
                
                log(f"Applied text bevel to {obj.name} (depth: {bevel_width * 1.2}, resolution: 2)")
            
            return obj
        except Exception as e:
            log(f"Error applying bevels: {e}")
            import traceback
            traceback.print_exc()
            return obj
    
    def optimize_curve_resolution(self, curve_obj, importance='normal', style_type=None):
        """
        Optimize curve resolution based on element importance and style
        
        Args:
            curve_obj: Blender curve object
            importance: Importance level ('high', 'normal', 'low')
            style_type: Style type for resolution adaptation
            
        Returns:
            Modified curve object
        """
        try:
            if not curve_obj or curve_obj.type != 'CURVE':
                return curve_obj
            
            # Base resolution based on style type
            if style_type == 'professional':
                base_resolution = 12  # Higher base resolution for professional style
            elif style_type == 'technical':
                base_resolution = 10  # Standard resolution for technical style
            else:
                base_resolution = 8  # Default resolution
            
            # Adjust based on importance
            if importance == 'high':
                resolution = base_resolution * 1.2
            elif importance == 'low':
                resolution = base_resolution * 0.8
            else:
                resolution = base_resolution
            
            # Apply resolution
            curve_obj.data.resolution_u = int(resolution)
            
            log(f"Optimized curve resolution for {curve_obj.name}: {curve_obj.data.resolution_u}")
            return curve_obj
        except Exception as e:
            log(f"Error optimizing curve resolution: {e}")
            return curve_obj
    
    def preserve_shape_profile(self, obj, element_type, element_class=None, custom_elements=False):
        """
        Preserve the original shape profile by adjusting geometry
        
        Args:
            obj: Blender object
            element_type: Type of SVG element
            element_class: Semantic class of the element
            custom_elements: Whether to use element-specific treatment
            
        Returns:
            Modified object
        """
        try:
            # For rectangles, ensure they remain flat and recognizable
            if element_type == 'rect' and obj.type == 'CURVE':
                # Set fill mode to properly display the shape
                obj.data.fill_mode = 'BOTH'
                # Ensure extrusion goes backward rather than in both directions
                obj.data.offset = 0.0 if custom_elements else 1.0
                
            # For circles and ellipses, preserve their distinctive shape
            elif element_type in ['circle', 'ellipse'] and obj.type == 'MESH':
                # Apply smooth shading for circles and ellipses
                if obj.data.polygons:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.shade_smooth()
                
            # For text, ensure it remains readable
            elif element_type == 'text' and obj.type == 'FONT':
                # Ensure text is extruded backward for better readability
                obj.data.offset = 0.0 if custom_elements else 1.0
                # Reduce any shadowing effect
                obj.data.use_fill_deform = False
                
            # For connectors, make them stand out but not dominate
            elif element_type in ['line', 'polyline', 'path'] and obj.style.get('fill', '').lower() == 'none':
                # Apply minimal treatment for connectors
                pass
                
            return obj
        except Exception as e:
            log(f"Error preserving shape profile: {e}")
            return obj
    
    def enhance_object_geometry(self, obj, element_type, element_class, style_type=None, importance='normal', custom_elements=False):
        """
        Apply geometry enhancements with optimal clarity preservation
        
        Args:
            obj: Blender object
            element_type: SVG element type
            element_class: Semantic class of element
            style_type: Style type for the object
            importance: Importance level
            custom_elements: Whether to use element-specific treatment
            
        Returns:
            Enhanced Blender object
        """
        try:
            # Skip if object is None
            if obj is None:
                return None
            
            log(f"Enhancing geometry for {obj.name} ({element_type}, {element_class})")
            
            # Preserve the original shape profile
            obj = self.preserve_shape_profile(obj, element_type, element_class, custom_elements)
            
            # Apply extrusion for appropriate object types
            if obj.type == 'CURVE':
                # Determine appropriate extrusion depth
                extrude_depth = self.determine_extrusion_depth(element_type, element_class, importance, custom_elements)
                
                # Apply extrusion to curve
                obj.data.extrude = extrude_depth
                log(f"Applied extrusion to curve: {extrude_depth}")
                
                # Optimize curve resolution
                self.optimize_curve_resolution(obj, importance, style_type)
            
            elif obj.type == 'FONT':
                # Determine appropriate extrusion depth for text
                extrude_depth = self.determine_extrusion_depth('text', 'text', importance, custom_elements)
                
                # Apply extrusion to text to preserve readability
                obj.data.extrude = extrude_depth
                log(f"Applied extrusion to text: {extrude_depth}")
            
            # Apply bevels to enhance edges
            self.apply_bevels(obj, element_class, style_type, custom_elements)
            
            # Add custom properties for animation system
            obj['geometry_class'] = element_class
            obj['geometry_importance'] = importance
            obj['style_type'] = style_type or 'default'
            
            return obj
        except Exception as e:
            log(f"Error enhancing object geometry: {e}")
            import traceback
            traceback.print_exc()
            return obj
    
    def create_shadow_catcher(self, scene_objects, style_type=None):
        """
        Create an optimized shadow catcher plane underneath all objects
        
        Args:
            scene_objects: List of objects in the scene
            style_type: Style type for shadow customization
            
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
            padding = 3.0  # Increased padding for better composition
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
            z_offset = -self.base_extrude_depth * 3.0  # Increased offset for better shadow separation
            
            if style_type == 'professional':
                z_offset = -self.base_extrude_depth * 5.0  # Greater separation for professional style
            
            bpy.ops.mesh.primitive_plane_add(
                size=1.0,
                location=(center_x, center_y, z_offset)
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
            
            # Different material setup based on style
            if style_type == 'professional':
                # Professional style with subtle gradient
                mix_shader = nodes.new('ShaderNodeMixShader')
                diffuse1 = nodes.new('ShaderNodeBsdfDiffuse')
                diffuse2 = nodes.new('ShaderNodeBsdfDiffuse')
                gradient = nodes.new('ShaderNodeTexGradient')
                mapping = nodes.new('ShaderNodeMapping')
                texcoord = nodes.new('ShaderNodeTexCoord')
                
                # Set colors
                diffuse1.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
                diffuse2.inputs[0].default_value = (0.85, 0.85, 0.85, 1.0)
                
                # Connect nodes
                links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
                links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
                links.new(gradient.outputs['Color'], mix_shader.inputs['Fac'])
                links.new(diffuse1.outputs[0], mix_shader.inputs[1])
                links.new(diffuse2.outputs[0], mix_shader.inputs[2])
                links.new(mix_shader.outputs[0], output.inputs[0])
                
                # Setup mapping
                mapping.inputs['Rotation'].default_value[2] = 0.5
            else:
                # Standard shadow catcher
                diffuse = nodes.new('ShaderNodeBsdfDiffuse')
                diffuse.inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
                links.new(diffuse.outputs[0], output.inputs[0])
            
            # Assign material
            shadow_catcher.data.materials.append(shadow_material)
            
            # Mark as shadow catcher for Cycles
            shadow_catcher.is_shadow_catcher = True
            
            log(f"Created optimized shadow catcher: {shadow_catcher.name}")
            return shadow_catcher
        except Exception as e:
            log(f"Error creating shadow catcher: {e}")
            return None
            
    def add_subtle_displacement(self, obj, element_class=None, style_type=None):
        """
        Add subtle displacement to the surface for increased realism
        Only used for professional style
        
        Args:
            obj: Blender object
            element_class: Element class for customization
            style_type: Style type
            
        Returns:
            Modified object
        """
        try:
            # Only apply to professional style and specific elements
            if style_type != 'professional' or obj.type not in ['MESH', 'CURVE']:
                return obj
                
            # Only apply to primary and secondary nodes
            if element_class not in ['primary_node', 'secondary_node']:
                return obj
                
            # Create a noise texture for displacement
            displacement_mat = bpy.data.materials.new(f"{obj.name}_displacement")
            displacement_mat.use_nodes = True
            
            # Get node tree
            nodes = displacement_mat.node_tree.nodes
            links = displacement_mat.node_tree.links
            
            # Get the default principled BSDF
            principled = nodes.get('Principled BSDF')
            
            # Create nodes
            noise = nodes.new('ShaderNodeTexNoise')
            disp = nodes.new('ShaderNodeDisplacement')
            
            # Configure noise
            noise.inputs['Scale'].default_value = 50.0  # High frequency for subtle effect
            noise.inputs['Detail'].default_value = 6.0  # High detail
            noise.inputs['Roughness'].default_value = 0.7
            
            # Configure displacement
            disp.inputs['Scale'].default_value = 0.0002  # Very subtle displacement
            
            # Connect nodes
            links.new(noise.outputs['Fac'], disp.inputs['Height'])
            links.new(disp.outputs['Displacement'], nodes['Material Output'].inputs['Displacement'])
            
            # Add material
            if len(obj.data.materials) > 0:
                # Existing material - keep it and just add the displacement effect
                original_mat = obj.data.materials[0]
                if original_mat.use_nodes:
                    # Add displacement to original material
                    orig_nodes = original_mat.node_tree.nodes
                    orig_links = original_mat.node_tree.links
                    
                    noise_node = orig_nodes.new('ShaderNodeTexNoise')
                    disp_node = orig_nodes.new('ShaderNodeDisplacement')
                    
                    # Configure nodes
                    noise_node.inputs['Scale'].default_value = 50.0
                    noise_node.inputs['Detail'].default_value = 6.0
                    noise_node.inputs['Roughness'].default_value = 0.7
                    disp_node.inputs['Scale'].default_value = 0.0002
                    
                    # Connect nodes
                    orig_links.new(noise_node.outputs['Fac'], disp_node.inputs['Height'])
                    orig_links.new(disp_node.outputs['Displacement'], orig_nodes['Material Output'].inputs['Displacement'])
            else:
                # No existing material - add the new one
                obj.data.materials.append(displacement_mat)
            
            log(f"Added subtle displacement to {obj.name}")
            return obj
        except Exception as e:
            log(f"Error adding displacement: {e}")
            return obj
