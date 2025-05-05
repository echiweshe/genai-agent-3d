"""
Final fixed material handling for SVG to 3D converter

This module properly handles materials for all SVG elements.
"""

import bpy
import mathutils
from svg_utils import log, hex_to_rgb


class SVGMaterialHandler:
    """Material handler for SVG elements - final version"""
    
    def __init__(self):
        self.material_cache = {}
    
    def create_material(self, color, opacity=1.0, material_type='fill'):
        """Create a material for SVG elements"""
        if not color or color.lower() == 'none':
            return None
        
        # Create cache key
        cache_key = f"{material_type}_{color}_{opacity}"
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
        
        # Set the base color
        principled_node.inputs['Base Color'].default_value = (r, g, b, 1.0)
        
        # Set material properties
        principled_node.inputs['Roughness'].default_value = 0.5
        principled_node.inputs['Metallic'].default_value = 0.0
        
        # Set specular for Blender 4.x
        if 'Specular IOR Level' in principled_node.inputs:
            principled_node.inputs['Specular IOR Level'].default_value = 0.5
        elif 'Specular' in principled_node.inputs:
            principled_node.inputs['Specular'].default_value = 0.5
        
        # Handle transparency
        if opacity < 1.0:
            # Set alpha
            principled_node.inputs['Alpha'].default_value = opacity
            
            # Configure blend mode
            material.blend_method = 'BLEND'
            material.use_backface_culling = False
            material.show_transparent_back = False
            
            # Connect with alpha
            links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        else:
            # Opaque material
            links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        
        # Set viewport display color
        material.diffuse_color = (r, g, b, opacity)
        
        # Cache and return
        self.material_cache[cache_key] = material
        return material
    
    def create_fill_material(self, color, opacity=1.0):
        """Create a fill material"""
        return self.create_material(color, opacity, 'fill')
    
    def create_stroke_material(self, color, opacity=1.0):
        """Create a stroke material"""
        return self.create_material(color, opacity, 'stroke')
    
    def apply_materials_to_object(self, obj, style):
        """Apply materials to object based on SVG style"""
        fill_color = style.get('fill', '#000000')
        stroke_color = style.get('stroke', None)
        stroke_width = float(style.get('stroke-width', 1.0))
        opacity = float(style.get('opacity', 1.0))
        fill_opacity = float(style.get('fill-opacity', opacity))
        stroke_opacity = float(style.get('stroke-opacity', opacity))
        
        # Debug logging
        log(f"Applying materials to {obj.name}:")
        log(f"  Fill: {fill_color} (opacity: {fill_opacity})")
        log(f"  Stroke: {stroke_color} (opacity: {stroke_opacity}, width: {stroke_width})")
        
        # Clear existing materials
        obj.data.materials.clear()
        
        # Handle different object types
        if obj.type == 'CURVE':
            has_fill = fill_color and fill_color.lower() != 'none'
            has_stroke = stroke_color and stroke_color.lower() != 'none'
            
            if has_fill and has_stroke:
                # Both fill and stroke
                obj.data.fill_mode = 'BOTH'
                obj.data.use_fill_caps = True
                
                # Apply fill material
                fill_mat = self.create_fill_material(fill_color, fill_opacity)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                    log(f"  Applied fill material: {fill_mat.name}")
                
                # Set bevel for stroke effect
                obj.data.bevel_depth = stroke_width * 0.01
                obj.data.bevel_resolution = 2
                
                # TODO: Apply stroke as separate geometry or material slot
                
            elif has_fill:
                # Fill only
                obj.data.fill_mode = 'BOTH'
                obj.data.use_fill_caps = True
                obj.data.bevel_depth = 0
                
                fill_mat = self.create_fill_material(fill_color, fill_opacity)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                    log(f"  Applied fill material: {fill_mat.name}")
                
            elif has_stroke:
                # Stroke only
                obj.data.fill_mode = 'FULL'  # Use FULL mode but with bevel only for stroke-only effect
                obj.data.bevel_depth = stroke_width * 0.01
                obj.data.bevel_resolution = 2
                
                stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity)
                if stroke_mat:
                    obj.data.materials.append(stroke_mat)
                    log(f"  Applied stroke material: {stroke_mat.name}")
            
            # Set extrusion
            obj.data.extrude = 0.1
            
        elif obj.type == 'MESH':
            # For meshes, apply fill material
            if fill_color and fill_color.lower() != 'none':
                fill_mat = self.create_fill_material(fill_color, fill_opacity)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                    log(f"  Applied fill material: {fill_mat.name}")
        
        # Set object color for viewport
        if obj.data.materials:
            obj.color = obj.data.materials[0].diffuse_color
            obj.show_transparent = opacity < 1.0 or fill_opacity < 1.0 or stroke_opacity < 1.0
        
        return True
