"""
Fixed material handling for SVG to 3D converter
Corrects transparency and stroke issues
"""

import bpy
import mathutils
from svg_utils import log, hex_to_rgb


class SVGMaterialHandler:
    """Fixed material handler for SVG elements"""
    
    def __init__(self):
        self.material_cache = {}
    
    def create_material(self, color, opacity=1.0, material_type='fill'):
        """Create a material for SVG elements with proper transparency"""
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
    
    def create_stroke_material(self, color, opacity=1.0):
        """Create a stroke material"""
        return self.create_material(color, opacity, 'stroke')
    
    def create_fill_material(self, color, opacity=1.0):
        """Create a fill material"""
        return self.create_material(color, opacity, 'fill')
    
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
        if obj.type == 'MESH':
            # For meshes (circles, etc.)
            has_fill = fill_color and fill_color.lower() != 'none'
            has_stroke = stroke_color and stroke_color.lower() != 'none'
            
            # Apply fill material if specified
            if has_fill:
                fill_mat = self.create_fill_material(fill_color, fill_opacity)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                    log(f"  Applied fill material: {fill_mat.name}")
            
            # Apply stroke using solidify modifier if specified
            if has_stroke:
                # Create stroke material
                stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity)
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
                
                # Apply fill material
                fill_mat = self.create_fill_material(fill_color, fill_opacity)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                    log(f"  Applied fill material: {fill_mat.name}")
                
                # Set bevel for stroke effect
                obj.data.bevel_depth = stroke_width * 0.01
                obj.data.bevel_resolution = 2
                
                # Apply stroke material
                stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity)
                if stroke_mat:
                    obj.data.materials.append(stroke_mat)
                    log(f"  Applied stroke material: {stroke_mat.name}")
                
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
                # Stroke only - use BACK mode for stroke-only effect
                obj.data.fill_mode = 'BACK'  # Changed from 'FULL' to valid mode
                obj.data.bevel_depth = stroke_width * 0.01
                obj.data.bevel_resolution = 2
                
                stroke_mat = self.create_stroke_material(stroke_color, stroke_opacity)
                if stroke_mat:
                    obj.data.materials.append(stroke_mat)
                    log(f"  Applied stroke material: {stroke_mat.name}")
            
            # Set extrusion
            obj.data.extrude = 0.1
        
        elif obj.type == 'FONT':
            # For text objects
            if fill_color and fill_color.lower() != 'none':
                fill_mat = self.create_fill_material(fill_color, fill_opacity)
                if fill_mat:
                    obj.data.materials.append(fill_mat)
                    log(f"  Applied fill material to text: {fill_mat.name}")
            
            # Set text extrusion
            obj.data.extrude = 0.05
        
        # Set object transparency flags
        if obj.data.materials:
            needs_transparency = opacity < 1.0 or fill_opacity < 1.0 or stroke_opacity < 1.0
            obj.show_transparent = needs_transparency
            
            # For viewport display
            obj.color = obj.data.materials[0].diffuse_color
        
        return True
