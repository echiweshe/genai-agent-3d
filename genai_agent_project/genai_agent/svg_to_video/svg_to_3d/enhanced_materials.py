"""
Enhanced material handling for SVG to 3D converter
Implements PBR materials with improved visual quality and specialized presets
"""

import bpy
import mathutils
import random
from .svg_utils import log, hex_to_rgb


class EnhancedSVGMaterialHandler:
    """Provides professional-grade materials for SVG to 3D conversion"""
    
    def __init__(self):
        self.material_cache = {}
        self.preset_cache = {}
        
    def create_pbr_material(self, color, opacity=1.0, material_type='fill', element_class=None):
        """
        Create a physically-based material with realistic properties
        
        Args:
            color: Hex color code or color name
            opacity: Opacity value (0.0-1.0)
            material_type: Type of material ('fill', 'stroke', etc.)
            element_class: Semantic class of element ('node', 'connector', 'text', etc.)
        
        Returns:
            Blender material object
        """
        if not color or color.lower() == 'none':
            return None
        
        # Create cache key
        cache_key = f"{material_type}_{color}_{opacity}_{element_class}"
        if cache_key in self.material_cache:
            return self.material_cache[cache_key]
        
        # Create new material
        material_name = f"SVG_{material_type}_{color.replace('#', '')}_{int(opacity*100)}"
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        
        # Get node tree
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create nodes
        output_node = nodes.new('ShaderNodeOutputMaterial')
        principled_node = nodes.new('ShaderNodeBsdfPrincipled')
        
        # Position nodes
        output_node.location = (300, 0)
        principled_node.location = (0, 0)
        
        # Parse color and set it
        r, g, b, a = hex_to_rgb(color)
        
        # Set base properties based on element class
        if element_class == 'node':
            # Nodes (boxes, containers) - slightly glossy
            principled_node.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled_node.inputs['Roughness'].default_value = 0.3
            principled_node.inputs['Specular'].default_value = 0.4
            principled_node.inputs['Metallic'].default_value = 0.0
            
            # Add subtle variation to color for visual interest
            color_var = nodes.new('ShaderNodeTexNoise')
            color_var.inputs['Scale'].default_value = 20.0
            color_var.inputs['Detail'].default_value = 2.0
            color_var.inputs['Roughness'].default_value = 0.7
            color_var.location = (-200, 100)
            
            # Mix color with variation
            color_mix = nodes.new('ShaderNodeMixRGB')
            color_mix.blend_type = 'OVERLAY'
            color_mix.inputs[0].default_value = 0.03  # Subtle effect
            color_mix.inputs[1].default_value = (r, g, b, 1.0)
            color_mix.location = (-200, 0)
            
            # Connect noise to mix factor
            links.new(color_var.outputs['Fac'], color_mix.inputs[2])
            
            # Connect mix output to base color
            links.new(color_mix.outputs[0], principled_node.inputs['Base Color'])
            
        elif element_class == 'connector':
            # Connectors (lines, arrows) - more metallic
            principled_node.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled_node.inputs['Roughness'].default_value = 0.2
            principled_node.inputs['Specular'].default_value = 0.5
            principled_node.inputs['Metallic'].default_value = 0.7
            
        elif element_class == 'text':
            # Text - crisp and slightly glossy
            principled_node.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled_node.inputs['Roughness'].default_value = 0.2
            principled_node.inputs['Specular'].default_value = 0.6
            principled_node.inputs['Metallic'].default_value = 0.1
            principled_node.inputs['Clearcoat'].default_value = 0.2
            
        else:
            # Default material properties
            principled_node.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled_node.inputs['Roughness'].default_value = 0.5
            principled_node.inputs['Metallic'].default_value = 0.0
            principled_node.inputs['Specular'].default_value = 0.3
        
        # Handle transparency - connect alpha
        principled_node.inputs['Alpha'].default_value = opacity
        
        # Connect shader to output
        links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        
        # Configure material blend mode for transparency
        if opacity < 1.0:
            material.blend_method = 'BLEND'
            material.use_backface_culling = False
            material.show_transparent_back = False
        else:
            material.blend_method = 'OPAQUE'
        
        # Set viewport display color with opacity
        material.diffuse_color = (r, g, b, opacity)
        
        # Cache and return
        self.material_cache[cache_key] = material
        return material
    
    def create_stroke_material(self, color, opacity=1.0, element_class=None):
        """Create a stroke material with appropriate properties"""
        # Strokes should be slightly more metallic/glossy than fills
        return self.create_pbr_material(color, opacity, 'stroke', element_class)
    
    def create_fill_material(self, color, opacity=1.0, element_class=None):
        """Create a fill material with appropriate properties"""
        return self.create_pbr_material(color, opacity, 'fill', element_class)
    
    def classify_element(self, element_type, style, attributes=None):
        """
        Determine the semantic class of an SVG element
        
        Args:
            element_type: SVG element type (rect, circle, text, etc.)
            style: Style attributes dictionary
            attributes: Additional element attributes
            
        Returns:
            Element class string ('node', 'connector', 'text', etc.)
        """
        if element_type == 'text':
            return 'text'
        
        if element_type in ['line', 'polyline'] or (element_type == 'path' and style.get('fill', '').lower() == 'none'):
            return 'connector'
        
        if element_type in ['rect', 'circle', 'ellipse', 'polygon']:
            # Check size if attributes available
            if attributes and 'width' in attributes and 'height' in attributes:
                if attributes['width'] > 50 or attributes['height'] > 50:
                    return 'primary_node'
                else:
                    return 'secondary_node'
            return 'node'
        
        return 'decoration'
    
    def get_material_preset(self, preset_name, base_color):
        """
        Get a predefined material preset
        
        Args:
            preset_name: Name of the preset ('technical', 'organic', 'professional', etc.)
            base_color: Base color to use for the preset
            
        Returns:
            Blender material
        """
        # Parse base color
        r, g, b, a = hex_to_rgb(base_color)
        
        # Create cache key
        cache_key = f"{preset_name}_{base_color}"
        if cache_key in self.preset_cache:
            return self.preset_cache[cache_key]
        
        # Create new material
        material = bpy.data.materials.new(name=f"Preset_{preset_name}")
        material.use_nodes = True
        
        # Get nodes
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create output and shader
        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        
        # Position nodes
        output.location = (300, 0)
        principled.location = (0, 0)
        
        # Connect shader to output
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Configure based on preset
        if preset_name == 'professional':
            # Professional preset - refined, modern look with subtle effects
            # Set base color
            principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
            
            # Refined material properties for a premium look
            principled.inputs['Metallic'].default_value = 0.2
            principled.inputs['Roughness'].default_value = 0.15  # Smoother finish
            principled.inputs['Specular'].default_value = 0.6    # Stronger highlights
            principled.inputs['Clearcoat'].default_value = 0.3   # Subtle clearcoat
            principled.inputs['Clearcoat Roughness'].default_value = 0.1
            principled.inputs['Sheen'].default_value = 0.05      # Subtle sheen
            
            # Add subtle color variation with noise texture
            noise_tex = nodes.new('ShaderNodeTexNoise')
            noise_tex.inputs['Scale'].default_value = 100.0      # Fine grain noise
            noise_tex.inputs['Detail'].default_value = 8.0       # High detail
            noise_tex.inputs['Roughness'].default_value = 0.5
            noise_tex.inputs['Distortion'].default_value = 0.1
            noise_tex.location = (-400, 100)
            
            # Map noise to a subtle color variation
            mapping = nodes.new('ShaderNodeMapping')
            mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
            mapping.location = (-600, 100)
            
            # Get texture coordinates
            tex_coord = nodes.new('ShaderNodeTexCoord')
            tex_coord.location = (-800, 100)
            
            # Create color variations
            color_ramp = nodes.new('ShaderNodeValToRGB')
            color_ramp.location = (-200, 100)
            
            # Set color ramp stops for subtle variation
            color_ramp.color_ramp.elements[0].position = 0.4
            color_ramp.color_ramp.elements[0].color = (r*0.95, g*0.95, b*0.95, 1.0)  # Slightly darker
            color_ramp.color_ramp.elements[1].position = 0.6
            color_ramp.color_ramp.elements[1].color = (min(r*1.05, 1.0), min(g*1.05, 1.0), min(b*1.05, 1.0), 1.0)  # Slightly lighter
            
            # Mix original color with variation
            mix_rgb = nodes.new('ShaderNodeMixRGB')
            mix_rgb.blend_type = 'OVERLAY'
            mix_rgb.inputs[0].default_value = 0.1  # Subtle effect
            mix_rgb.inputs[1].default_value = (r, g, b, 1.0)  # Original color
            mix_rgb.location = (0, 150)
            
            # Create subtle bump for surface detail
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = 0.02  # Very subtle
            bump.inputs['Distance'].default_value = 0.01
            bump.location = (-200, -100)
            
            # Connect nodes
            links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])
            links.new(noise_tex.outputs['Fac'], color_ramp.inputs['Fac'])
            links.new(noise_tex.outputs['Fac'], bump.inputs['Height'])
            links.new(color_ramp.outputs['Color'], mix_rgb.inputs[2])
            links.new(mix_rgb.outputs['Color'], principled.inputs['Base Color'])
            links.new(bump.outputs['Normal'], principled.inputs['Normal'])
            
        elif preset_name == 'technical':
            # Technical preset - clean, slightly metallic
            principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled.inputs['Metallic'].default_value = 0.3
            principled.inputs['Roughness'].default_value = 0.2
            principled.inputs['Specular'].default_value = 0.5
            
        elif preset_name == 'organic':
            # Organic preset - soft, matte
            principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled.inputs['Metallic'].default_value = 0.0
            principled.inputs['Roughness'].default_value = 0.7
            principled.inputs['Specular'].default_value = 0.2
            principled.inputs['Sheen'].default_value = 0.1
            
            # Add subtle texture
            noise = nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 30.0
            noise.inputs['Detail'].default_value = 6.0
            noise.inputs['Roughness'].default_value = 0.6
            noise.location = (-200, 100)
            
            # Use noise for bump
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = 0.03
            bump.location = (-200, -100)
            
            # Connect noise to bump
            links.new(noise.outputs['Fac'], bump.inputs['Height'])
            
            # Connect bump to normal
            links.new(bump.outputs['Normal'], principled.inputs['Normal'])
            
        elif preset_name == 'glossy':
            # Glossy preset - shiny, reflective
            principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled.inputs['Metallic'].default_value = 0.1
            principled.inputs['Roughness'].default_value = 0.1
            principled.inputs['Specular'].default_value = 0.8
            principled.inputs['Clearcoat'].default_value = 0.3
            principled.inputs['Clearcoat Roughness'].default_value = 0.1
            
        elif preset_name == 'metal':
            # Metal preset - metallic, reflective
            principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled.inputs['Metallic'].default_value = 0.9
            principled.inputs['Roughness'].default_value = 0.2
            principled.inputs['Specular'].default_value = 0.8
            
            # Add subtle anisotropic effect for metal
            principled.inputs['Anisotropic'].default_value = 0.2
            principled.inputs['Anisotropic Rotation'].default_value = 0.0
            
        else:
            # Default preset
            principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
            principled.inputs['Metallic'].default_value = 0.0
            principled.inputs['Roughness'].default_value = 0.5
            principled.inputs['Specular'].default_value = 0.5
        
        # Cache and return
        self.preset_cache[cache_key] = material
        return material
    
    def apply_materials_to_object(self, obj, style, element_type=None, use_presets=True, style_preset='technical'):
        """
        Apply enhanced materials to an object based on SVG style
        
        Args:
            obj: Blender object
            style: SVG style dictionary
            element_type: SVG element type
            use_presets: Whether to use material presets
            style_preset: Style preset to use ('technical', 'organic', 'professional', etc.)
            
        Returns:
            Boolean indicating success
        """
        try:
            fill_color = style.get('fill', '#000000')
            stroke_color = style.get('stroke', None)
            stroke_width = float(style.get('stroke-width', 1.0))
            opacity = float(style.get('opacity', 1.0))
            fill_opacity = float(style.get('fill-opacity', opacity))
            stroke_opacity = float(style.get('stroke-opacity', opacity))
            
            # Determine element class for appropriate material settings
            element_class = self.classify_element(element_type, style)
            
            log(f"Applying enhanced materials to {obj.name} (class: {element_class}):")
            log(f"  Fill: {fill_color} (opacity: {fill_opacity})")
            log(f"  Stroke: {stroke_color} (opacity: {stroke_opacity}, width: {stroke_width})")
            log(f"  Style preset: {style_preset}")
            
            # Clear existing materials
            obj.data.materials.clear()
            
            # Handle different object types
            if obj.type == 'MESH':
                # For meshes (circles, etc.)
                has_fill = fill_color and fill_color.lower() != 'none'
                has_stroke = stroke_color and stroke_color.lower() != 'none'
                
                # Apply fill material if specified
                if has_fill:
                    # Choose appropriate material preset
                    if use_presets:
                        if style_preset == 'professional':
                            fill_mat = self.get_material_preset('professional', fill_color)
                        elif element_class in ['primary_node', 'node']:
                            fill_mat = self.get_material_preset('technical', fill_color)
                        elif element_class == 'secondary_node':
                            fill_mat = self.get_material_preset('organic', fill_color)
                        else:
                            fill_mat = self.create_fill_material(fill_color, fill_opacity, element_class)
                    else:
                        fill_mat = self.create_fill_material(fill_color, fill_opacity, element_class)
                    
                    if fill_mat:
                        obj.data.materials.append(fill_mat)
                        log(f"  Applied enhanced fill material: {fill_mat.name}")
                
                # Apply stroke using solidify modifier if specified
                if has_stroke:
                    # Choose appropriate stroke material
                    if use_presets:
                        if style_preset == 'professional':
                            stroke_mat = self.get_material_preset('professional', stroke_color)
                        elif element_class == 'connector':
                            stroke_mat = self.get_material_preset('metal', stroke_color)
                        else:
                            stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity, element_class)
                    else:
                        stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity, element_class)
                    
                    if stroke_mat:
                        # Add solidify modifier for stroke effect
                        solidify = obj.modifiers.new(name="Stroke", type='SOLIDIFY')
                        solidify.thickness = stroke_width * 0.02  # Scale factor
                        solidify.offset = 1  # Offset outward
                        solidify.use_rim = True
                        solidify.use_rim_only = True
                        
                        # Add stroke material as second material
                        obj.data.materials.append(stroke_mat)
                        solidify.material_offset = 1  # Use second material for rim
                        
                        log(f"  Added stroke as solidify modifier with material: {stroke_mat.name}")
            
            elif obj.type == 'CURVE':
                has_fill = fill_color and fill_color.lower() != 'none'
                has_stroke = stroke_color and stroke_color.lower() != 'none'
                
                if has_fill and has_stroke:
                    # Both fill and stroke
                    obj.data.fill_mode = 'BOTH'
                    obj.data.use_fill_caps = True
                    
                    # Apply fill material with presets if appropriate
                    if use_presets:
                        if style_preset == 'professional':
                            fill_mat = self.get_material_preset('professional', fill_color)
                        elif element_class in ['primary_node', 'node']:
                            fill_mat = self.get_material_preset('technical', fill_color)
                        elif element_class == 'secondary_node':
                            fill_mat = self.get_material_preset('organic', fill_color)
                        else:
                            fill_mat = self.create_fill_material(fill_color, fill_opacity, element_class)
                    else:
                        fill_mat = self.create_fill_material(fill_color, fill_opacity, element_class)
                    
                    if fill_mat:
                        obj.data.materials.append(fill_mat)
                        log(f"  Applied enhanced fill material: {fill_mat.name}")
                    
                    # Set bevel for stroke effect
                    obj.data.bevel_depth = stroke_width * 0.01
                    obj.data.bevel_resolution = 2
                    
                    # Apply stroke material with presets if appropriate
                    if use_presets:
                        if style_preset == 'professional':
                            stroke_mat = self.get_material_preset('professional', stroke_color)
                        elif element_class == 'connector':
                            stroke_mat = self.get_material_preset('metal', stroke_color)
                        else:
                            stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity, element_class)
                    else:
                        stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity, element_class)
                    
                    if stroke_mat:
                        obj.data.materials.append(stroke_mat)
                        log(f"  Applied enhanced stroke material: {stroke_mat.name}")
                
                elif has_fill:
                    # Fill only
                    obj.data.fill_mode = 'BOTH'
                    obj.data.use_fill_caps = True
                    obj.data.bevel_depth = 0
                    
                    # Apply fill material with presets if appropriate
                    if use_presets:
                        if style_preset == 'professional':
                            fill_mat = self.get_material_preset('professional', fill_color)
                        elif element_class in ['primary_node', 'node']:
                            fill_mat = self.get_material_preset('technical', fill_color)
                        elif element_class == 'secondary_node':
                            fill_mat = self.get_material_preset('organic', fill_color)
                        else:
                            fill_mat = self.create_fill_material(fill_color, fill_opacity, element_class)
                    else:
                        fill_mat = self.create_fill_material(fill_color, fill_opacity, element_class)
                    
                    if fill_mat:
                        obj.data.materials.append(fill_mat)
                        log(f"  Applied enhanced fill material: {fill_mat.name}")
                
                elif has_stroke:
                    # Stroke only - use FRONT mode for stroke-only effect
                    obj.data.fill_mode = 'FRONT'
                    obj.data.bevel_depth = stroke_width * 0.01
                    obj.data.bevel_resolution = 2
                    
                    # Apply stroke material with presets if appropriate
                    if use_presets:
                        if style_preset == 'professional':
                            stroke_mat = self.get_material_preset('professional', stroke_color)
                        elif element_class == 'connector':
                            stroke_mat = self.get_material_preset('metal', stroke_color)
                        else:
                            stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity, element_class)
                    else:
                        stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity, element_class)
                    
                    if stroke_mat:
                        obj.data.materials.append(stroke_mat)
                        log(f"  Applied enhanced stroke material: {stroke_mat.name}")
            
            elif obj.type == 'FONT':
                # For text objects
                if fill_color and fill_color.lower() != 'none':
                    # Text material based on style preset
                    if use_presets:
                        if style_preset == 'professional':
                            fill_mat = self.get_material_preset('professional', fill_color)
                        else:
                            fill_mat = self.get_material_preset('glossy', fill_color)
                    else:
                        fill_mat = self.create_fill_material(fill_color, fill_opacity, 'text')
                    
                    if fill_mat:
                        obj.data.materials.append(fill_mat)
                        log(f"  Applied enhanced text material: {fill_mat.name}")
                
                # Set text extrusion - adjusted based on style
                if style_preset == 'professional':
                    obj.data.extrude = 0.03  # Reduced extrusion for professional style
                    obj.data.bevel_depth = 0.003  # Reduced bevel for cleaner look
                    obj.data.bevel_resolution = 3  # Higher resolution for smoother edges
                else:
                    obj.data.extrude = 0.05
                    obj.data.bevel_depth = 0.005
                    obj.data.bevel_resolution = 2
            
            # Add custom properties for animation system
            obj['material_class'] = element_class
            obj['style_preset'] = style_preset
            
            # Set object transparency flags
            if obj.data.materials:
                needs_transparency = opacity < 1.0 or fill_opacity < 1.0 or stroke_opacity < 1.0
                obj.show_transparent = needs_transparency
                
                # For viewport display
                obj.color = obj.data.materials[0].diffuse_color
            
            return True
        except Exception as e:
            log(f"Error applying enhanced materials: {e}")
            import traceback
            traceback.print_exc()
            return False


# Factory function to get material handler
def get_material_handler(enhanced=True):
    """Return appropriate material handler based on settings"""
    if enhanced:
        return EnhancedSVGMaterialHandler()
    else:
        # Import the original handler for fallback
        from .svg_converter_materials_fixed import SVGMaterialHandler
        return SVGMaterialHandler()
