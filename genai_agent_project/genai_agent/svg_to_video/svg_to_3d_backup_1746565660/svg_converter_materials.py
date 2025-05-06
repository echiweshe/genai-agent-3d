"""
Enhanced material handling for SVG to 3D converter

This module provides improved material creation and application for SVG elements,
properly handling strokes, fills, and their various properties.
"""

import bpy
import mathutils
from .svg_utils import log, hex_to_rgb


class SVGMaterialHandler:
    """Handles material creation and application for SVG elements"""
    
    def __init__(self):
        self.material_cache = {}
        self.stroke_material_cache = {}
    
    def create_fill_material(self, fill_color, opacity=1.0):
        """Create a material for filled shapes"""
        if not fill_color or fill_color.lower() == 'none':
            return None
        
        # Check cache first
        cache_key = f"fill_{fill_color}_{opacity}"
        if cache_key in self.material_cache:
            return self.material_cache[cache_key]
        
        # Create new material
        material_name = f"SVG_Fill_{len(self.material_cache)}"
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        
        # Set up nodes
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        
        # Position nodes
        output.location = (300, 0)
        principled.location = (0, 0)
        
        # Connect nodes
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Set color
        r, g, b, a = hex_to_rgb(fill_color)
        principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
        principled.inputs['Alpha'].default_value = a * opacity
        
        # Set other properties
        principled.inputs['Roughness'].default_value = 0.5
        principled.inputs['Metallic'].default_value = 0.0
        
        if 'Specular IOR Level' in principled.inputs:  # Blender 4.x
            principled.inputs['Specular IOR Level'].default_value = 0.5
        elif 'Specular' in principled.inputs:  # Blender 3.x
            principled.inputs['Specular'].default_value = 0.5
        
        # Configure material settings
        material.use_backface_culling = False
        if opacity < 1.0 or a < 1.0:
            material.blend_method = 'BLEND'
            material.use_backface_culling = False
            material.show_transparent_back = False
        
        # Set viewport color
        material.diffuse_color = (r, g, b, a * opacity)
        
        # Cache and return
        self.material_cache[cache_key] = material
        return material
    
    def create_stroke_material(self, stroke_color, stroke_width=1.0, opacity=1.0):
        """Create a material for stroked shapes"""
        if not stroke_color or stroke_color.lower() == 'none':
            return None
        
        # Check cache first
        cache_key = f"stroke_{stroke_color}_{stroke_width}_{opacity}"
        if cache_key in self.stroke_material_cache:
            return self.stroke_material_cache[cache_key]
        
        # Create new material
        material_name = f"SVG_Stroke_{len(self.stroke_material_cache)}"
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        
        # Set up nodes
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        
        # Clear default nodes
        nodes.clear()
        
        # Create nodes
        output = nodes.new('ShaderNodeOutputMaterial')
        principled = nodes.new('ShaderNodeBsdfPrincipled')
        
        # Position nodes
        output.location = (300, 0)
        principled.location = (0, 0)
        
        # Connect nodes
        links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
        # Set color
        r, g, b, a = hex_to_rgb(stroke_color)
        principled.inputs['Base Color'].default_value = (r, g, b, 1.0)
        principled.inputs['Alpha'].default_value = a * opacity
        
        # Set other properties - strokes are often more glossy
        principled.inputs['Roughness'].default_value = 0.3
        principled.inputs['Metallic'].default_value = 0.0
        
        if 'Specular IOR Level' in principled.inputs:  # Blender 4.x
            principled.inputs['Specular IOR Level'].default_value = 0.7
        elif 'Specular' in principled.inputs:  # Blender 3.x
            principled.inputs['Specular'].default_value = 0.7
        
        # Configure material settings
        material.use_backface_culling = False
        if opacity < 1.0 or a < 1.0:
            material.blend_method = 'BLEND'
            material.show_transparent_back = False
        
        # Set viewport color
        material.diffuse_color = (r, g, b, a * opacity)
        
        # Cache and return
        self.stroke_material_cache[cache_key] = material
        return material
    
    def apply_materials_to_object(self, obj, style):
        """Apply both fill and stroke materials to an object"""
        fill_color = style.get('fill', '#000000')
        stroke_color = style.get('stroke', None)
        stroke_width = float(style.get('stroke-width', 1.0))
        opacity = float(style.get('opacity', 1.0))
        fill_opacity = float(style.get('fill-opacity', opacity))
        stroke_opacity = float(style.get('stroke-opacity', opacity))
        
        # Clear existing materials
        obj.data.materials.clear()
        
        # Apply fill material
        if fill_color and fill_color.lower() != 'none':
            fill_mat = self.create_fill_material(fill_color, fill_opacity)
            if fill_mat:
                obj.data.materials.append(fill_mat)
        
        # For objects with both fill and stroke, we might need to create separate geometry
        # For now, we'll prioritize the fill for solid objects
        if stroke_color and stroke_color.lower() != 'none':
            stroke_mat = self.create_stroke_material(stroke_color, stroke_width, stroke_opacity)
            if stroke_mat:
                # If no fill material, use stroke as primary material
                if len(obj.data.materials) == 0:
                    obj.data.materials.append(stroke_mat)
                # TODO: Implement separate stroke geometry for objects with both fill and stroke
        
        # Special handling for curve objects
        if obj.type == 'CURVE':
            # Set curve properties based on whether it has fill or stroke
            if fill_color and fill_color.lower() != 'none':
                obj.data.fill_mode = 'BOTH'
                obj.data.use_fill_caps = True
            else:
                obj.data.fill_mode = 'NONE'
            
            # Set bevel for stroked curves
            if stroke_color and stroke_color.lower() != 'none':
                obj.data.bevel_depth = stroke_width * 0.01  # Scale factor
                obj.data.bevel_resolution = 2
        
        # Update object color for viewport display
        if obj.data.materials:
            first_mat = obj.data.materials[0]
            obj.color = first_mat.diffuse_color
        
        return True
    
    def create_gradient_material(self, gradient_data):
        """Create a material with gradient (placeholder for future implementation)"""
        # TODO: Implement gradient material creation
        # For now, return a solid color material using the first stop color
        stops = gradient_data.get('stops', [])
        if stops:
            first_color = stops[0].get('color', '#808080')
            return self.create_fill_material(first_color)
        return None
    
    def create_pattern_material(self, pattern_data):
        """Create a material with pattern (placeholder for future implementation)"""
        # TODO: Implement pattern material creation
        # For now, return a default material
        return self.create_fill_material('#808080')
