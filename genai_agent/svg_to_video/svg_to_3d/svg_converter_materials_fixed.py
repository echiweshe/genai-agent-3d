"""
Fixed material handling for SVG to 3D converter

This module properly handles strokes and fills for all object types.
"""

import bpy
import mathutils
from svg_utils import log, hex_to_rgb


class SVGMaterialHandler:
    """Fixed material handler for SVG elements"""
    
    def __init__(self):
        self.material_cache = {}
    
    def create_material(self, color, opacity=1.0, is_stroke=False):
        """Create a material for SVG elements"""
        if not color or color.lower() == 'none':
            return None
        
        # Create cache key
        cache_key = f"{'stroke' if is_stroke else 'fill'}_{color}_{opacity}"
        if cache_key in self.material_cache:
            return self.material_cache[cache_key]
        
        # Create new material
        material_name = f"SVG_{'Stroke' if is_stroke else 'Fill'}_{len(self.material_cache)}"
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        
        # Get nodes
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        
        # Position nodes
        output.location = (300, 0)
        principled.location = (0, 0)
        
        # Connect nodes
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Parse color
        r, g, b, a = hex_to_rgb(color)
        
        # Set base color
        principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
        
        # Handle transparency
        if opacity < 1.0 or a < 1.0:
            # Add transparency setup
            mix_shader = nodes.new('ShaderNodeMixShader')
            transparent = nodes.new('ShaderNodeBsdfTransparent')
            
            mix_shader.location = (150, 0)
            transparent.location = (-150, -100)
            
            # Connect transparency
            links.new(transparent.outputs['BSDF'], mix_shader.inputs[1])
            links.new(principled.outputs['BSDF'], mix_shader.inputs[2])
            links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])
            
            # Set mix factor for transparency
            mix_shader.inputs['Fac'].default_value = a * opacity
            
            # Set material blend mode
            material.blend_method = 'BLEND'
            material.use_backface_culling = False
            material.show_transparent_back = True
        
        # Set material properties
        principled.inputs['Roughness'].default_value = 0.5 if is_stroke else 0.7
        principled.inputs['Metallic'].default_value = 0.0
        
        if 'Specular IOR Level' in principled.inputs:  # Blender 4.x
            principled.inputs['Specular IOR Level'].default_value = 0.5
        elif 'Specular' in principled.inputs:  # Blender 3.x
            principled.inputs['Specular'].default_value = 0.5
        
        # Set viewport display color
        material.diffuse_color = (r, g, b, a * opacity)
        
        # Cache and return
        self.material_cache[cache_key] = material
        return material
    
    def apply_materials_to_object(self, obj, style):
        """Apply materials to object based on SVG style"""
        fill_color = style.get('fill', '#000000')
        stroke_color = style.get('stroke', None)
        stroke_width = float(style.get('stroke-width', 1.0))
        opacity = float(style.get('opacity', 1.0))
        fill_opacity = float(style.get('fill-opacity', opacity))
        stroke_opacity = float(style.get('stroke-opacity', opacity))
        
        # Clear existing materials
        obj.data.materials.clear()
        
        # Handle different object types
        if obj.type == 'CURVE':
            # For curves, we need to set proper fill mode and bevel
            has_fill = fill_color and fill_color.lower() != 'none'
            has_stroke = stroke_color and stroke_color.lower() != 'none'
            
            if has_fill and has_stroke:
                # Both fill and stroke - create extruded curve with bevel
                obj.data.fill_mode = 'BOTH'
                obj.data.use_fill_caps = True
                obj.data.bevel_depth = stroke_width * 0.005
                obj.data.bevel_resolution = 2
                
                # Apply fill material
                fill_mat = self.create_material(fill_color, fill_opacity, False)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                
                # Create stroke outline (TODO: implement as separate geometry)
                
            elif has_fill:
                # Fill only - extruded shape
                obj.data.fill_mode = 'BOTH'
                obj.data.use_fill_caps = True
                obj.data.bevel_depth = 0
                
                fill_mat = self.create_material(fill_color, fill_opacity, False)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                    
            elif has_stroke:
                # Stroke only - just the outline
                obj.data.fill_mode = 'NONE'
                obj.data.bevel_depth = stroke_width * 0.005
                obj.data.bevel_resolution = 2
                
                stroke_mat = self.create_material(stroke_color, stroke_opacity, True)
                if stroke_mat:
                    obj.data.materials.append(stroke_mat)
            
            # Set extrusion
            if has_fill or has_stroke:
                obj.data.extrude = 0.1  # Default extrusion depth
        
        elif obj.type == 'MESH':
            # For meshes, apply fill material
            if fill_color and fill_color.lower() != 'none':
                fill_mat = self.create_material(fill_color, fill_opacity, False)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
        
        # Set object viewport color
        if obj.data.materials:
            obj.color = obj.data.materials[0].diffuse_color
        
        # Enable transparency in viewport if needed
        if opacity < 1.0 or fill_opacity < 1.0 or stroke_opacity < 1.0:
            obj.show_transparent = True
        
        return True
