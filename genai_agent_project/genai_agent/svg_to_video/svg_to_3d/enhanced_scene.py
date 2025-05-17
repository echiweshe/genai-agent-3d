"""
Enhanced scene setup for SVG to 3D conversion
Implements professional lighting, camera, and scene organization
"""

import bpy
import math
import mathutils
import os
from .svg_utils import log


class SceneEnhancer:
    """
    Provides enhanced scene setup for SVG to 3D conversion
    Improves lighting, camera, and scene organization
    """
    
    def __init__(self, scene_name="Enhanced_SVG_Scene"):
        """
        Initialize the scene enhancer
        
        Args:
            scene_name: Name for the 3D scene
        """
        self.scene_name = scene_name
        self.collections = {}
    
    def create_collection_hierarchy(self):
        """
        Create a proper collection hierarchy for scene organization
        
        Returns:
            Dictionary of created collections
        """
        try:
            log("Creating collection hierarchy...")
            
            # Create main collection
            main_collection = bpy.data.collections.new(self.scene_name)
            bpy.context.scene.collection.children.link(main_collection)
            
            # Create sub-collections for different element types
            nodes_collection = bpy.data.collections.new("Nodes")
            connectors_collection = bpy.data.collections.new("Connectors")
            labels_collection = bpy.data.collections.new("Labels")
            decorations_collection = bpy.data.collections.new("Decorations")
            
            # Create lighting and camera collections
            lighting_collection = bpy.data.collections.new("Lighting")
            cameras_collection = bpy.data.collections.new("Cameras")
            
            # Link sub-collections to main collection
            main_collection.children.link(nodes_collection)
            main_collection.children.link(connectors_collection)
            main_collection.children.link(labels_collection)
            main_collection.children.link(decorations_collection)
            main_collection.children.link(lighting_collection)
            main_collection.children.link(cameras_collection)
            
            # Store collections in dictionary
            self.collections = {
                'main': main_collection,
                'nodes': nodes_collection,
                'connectors': connectors_collection,
                'labels': labels_collection,
                'decorations': decorations_collection,
                'lighting': lighting_collection,
                'cameras': cameras_collection
            }
            
            log("Collection hierarchy created")
            return self.collections
        except Exception as e:
            log(f"Error creating collection hierarchy: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def add_object_to_collection(self, obj, element_class=None):
        """
        Add an object to the appropriate collection based on its class
        
        Args:
            obj: Blender object
            element_class: Semantic class of the element
            
        Returns:
            Boolean indicating success
        """
        try:
            # Ensure collections exist
            if not self.collections:
                self.create_collection_hierarchy()
            
            # Determine appropriate collection
            if element_class == 'text':
                target_collection = self.collections['labels']
            elif element_class in ['connector', 'line']:
                target_collection = self.collections['connectors']
            elif element_class in ['primary_node', 'secondary_node', 'node']:
                target_collection = self.collections['nodes']
            elif element_class in ['camera']:
                target_collection = self.collections['cameras']
            elif element_class in ['light']:
                target_collection = self.collections['lighting']
            else:
                target_collection = self.collections['decorations']
            
            # Remove from current collections
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            
            # Add to target collection
            target_collection.objects.link(obj)
            
            log(f"Added {obj.name} to collection: {target_collection.name}")
            return True
        except Exception as e:
            log(f"Error adding object to collection: {e}")
            return False
    
    def setup_studio_environment(self, scene_dimensions):
        """
        Set up a professional studio-like environment
        
        Args:
            scene_dimensions: Tuple of (width, height, depth) for scene
            
        Returns:
            Dictionary of created environment objects
        """
        try:
            log("Setting up studio environment...")
            
            width, height, depth = scene_dimensions
            max_dim = max(width, height)
            
            # Create studio environment with world settings
            world = bpy.context.scene.world
            if not world:
                world = bpy.data.worlds.new("Studio_Environment")
                bpy.context.scene.world = world
            
            # Configure world with subtle gradient background
            world.use_nodes = True
            nodes = world.node_tree.nodes
            links = world.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Create nodes for gradient background
            output = nodes.new('ShaderNodeOutputWorld')
            background = nodes.new('ShaderNodeBackground')
            
            # Subtle gradient with world coordinates
            coord = nodes.new('ShaderNodeTexCoord')
            mapping = nodes.new('ShaderNodeMapping')
            gradient = nodes.new('ShaderNodeTexGradient')
            color_ramp = nodes.new('ShaderNodeValToRGB')
            
            # Position nodes
            output.location = (600, 0)
            background.location = (400, 0)
            color_ramp.location = (200, 0)
            gradient.location = (0, 0)
            mapping.location = (-200, 0)
            coord.location = (-400, 0)
            
            # Configure gradient
            color_ramp.color_ramp.elements[0].position = 0.3
            color_ramp.color_ramp.elements[0].color = (0.9, 0.9, 0.95, 1.0)  # Slight blue-white
            color_ramp.color_ramp.elements[1].position = 0.7
            color_ramp.color_ramp.elements[1].color = (0.8, 0.83, 0.85, 1.0)  # Light gray-blue
            
            # Connect nodes
            links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
            links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
            links.new(color_ramp.outputs['Color'], background.inputs['Color'])
            links.new(background.outputs['Background'], output.inputs['Surface'])
            
            log("Studio environment configured")
            
            # Create environment objects
            env_objects = {}
            
            log("Studio environment setup complete")
            return env_objects
        except Exception as e:
            log(f"Error setting up studio environment: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def setup_enhanced_lighting(self, scene_bounds):
        """
        Set up professional three-point lighting
        
        Args:
            scene_bounds: Tuple of (min_x, min_y, min_z, max_x, max_y, max_z)
            
        Returns:
            Dictionary of created light objects
        """
        try:
            log("Setting up enhanced lighting...")
            
            # Ensure collections exist
            if not self.collections:
                self.create_collection_hierarchy()
            
            # Get scene dimensions
            min_x, min_y, min_z, max_x, max_y, max_z = scene_bounds
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center_z = (min_z + max_z) / 2
            
            width = max_x - min_x
            height = max_y - min_y
            depth = max_z - min_z
            
            max_dim = max(width, height, depth)
            
            # Remove existing lights
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT':
                    bpy.data.objects.remove(obj, do_unlink=True)
            
            # Create key light (main light)
            key_light = bpy.data.lights.new(name="Key_Light", type='AREA')
            key_light.energy = 10.0
            key_light.color = (1.0, 0.95, 0.9)  # Slightly warm
            key_light.shape = 'RECTANGLE'
            key_light.size = max_dim * 0.5
            key_light.size_y = max_dim * 0.3
            
            key_light_obj = bpy.data.objects.new(name="Key_Light", object_data=key_light)
            key_light_obj.location = (center_x + max_dim, center_y - max_dim, center_z + max_dim * 1.5)
            key_light_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
            
            # Add to lighting collection
            self.collections['lighting'].objects.link(key_light_obj)
            
            # Create fill light (secondary light)
            fill_light = bpy.data.lights.new(name="Fill_Light", type='AREA')
            fill_light.energy = 5.0
            fill_light.color = (0.9, 0.95, 1.0)  # Slightly cool
            fill_light.shape = 'RECTANGLE'
            fill_light.size = max_dim * 0.7
            fill_light.size_y = max_dim * 0.4
            
            fill_light_obj = bpy.data.objects.new(name="Fill_Light", object_data=fill_light)
            fill_light_obj.location = (center_x - max_dim, center_y + max_dim * 0.5, center_z + max_dim)
            fill_light_obj.rotation_euler = (math.radians(30), 0, math.radians(-135))
            
            # Add to lighting collection
            self.collections['lighting'].objects.link(fill_light_obj)
            
            # Create rim light (back light for edge definition)
            rim_light = bpy.data.lights.new(name="Rim_Light", type='SPOT')
            rim_light.energy = 7.0
            rim_light.color = (1.0, 1.0, 1.0)
            rim_light.spot_size = math.radians(60)
            rim_light.spot_blend = 0.5
            
            rim_light_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_light)
            rim_light_obj.location = (center_x, center_y - max_dim * 0.5, center_z - max_dim)
            rim_light_obj.rotation_euler = (math.radians(-120), 0, 0)
            
            # Add to lighting collection
            self.collections['lighting'].objects.link(rim_light_obj)
            
            # Create ambient light (overall fill)
            ambient_light = bpy.data.lights.new(name="Ambient_Light", type='SUN')
            ambient_light.energy = 2.0
            ambient_light.color = (0.95, 0.95, 1.0)
            
            ambient_light_obj = bpy.data.objects.new(name="Ambient_Light", object_data=ambient_light)
            ambient_light_obj.rotation_euler = (math.radians(45), math.radians(45), 0)
            
            # Add to lighting collection
            self.collections['lighting'].objects.link(ambient_light_obj)
            
            log("Enhanced lighting setup complete")
            
            # Return light objects
            lights = {
                'key': key_light_obj,
                'fill': fill_light_obj,
                'rim': rim_light_obj,
                'ambient': ambient_light_obj
            }
            
            return lights
        except Exception as e:
            log(f"Error setting up enhanced lighting: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def create_camera_system(self, scene_bounds):
        """
        Create a system of cameras for different viewing angles
        
        Args:
            scene_bounds: Tuple of (min_x, min_y, min_z, max_x, max_y, max_z)
            
        Returns:
            Dictionary of created camera objects
        """
        try:
            log("Creating camera system...")
            
            # Ensure collections exist
            if not self.collections:
                self.create_collection_hierarchy()
            
            # Get scene dimensions
            min_x, min_y, min_z, max_x, max_y, max_z = scene_bounds
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center_z = (min_z + max_z) / 2
            
            width = max_x - min_x
            height = max_y - min_y
            depth = max_z - min_z
            
            max_dim = max(width, height, depth)
            
            # Remove existing cameras
            for obj in bpy.data.objects:
                if obj.type == 'CAMERA':
                    bpy.data.objects.remove(obj, do_unlink=True)
            
            # Create ortho camera (top view)
            ortho_cam_data = bpy.data.cameras.new("Camera_Ortho")
            ortho_cam_data.type = 'ORTHO'
            ortho_cam_data.ortho_scale = max_dim * 1.1
            
            ortho_cam_obj = bpy.data.objects.new("Camera_Ortho", ortho_cam_data)
            ortho_cam_obj.location = (center_x, center_y, center_z + max_dim * 2)
            ortho_cam_obj.rotation_euler = (0, 0, 0)
            
            # Add to camera collection
            self.collections['cameras'].objects.link(ortho_cam_obj)
            
            # Create perspective camera (3/4 view)
            persp_cam_data = bpy.data.cameras.new("Camera_Perspective")
            persp_cam_data.type = 'PERSP'
            persp_cam_data.lens = 50  # 50mm perspective
            
            persp_cam_obj = bpy.data.objects.new("Camera_Perspective", persp_cam_data)
            persp_cam_obj.location = (center_x + max_dim, center_y - max_dim, center_z + max_dim)
            persp_cam_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
            
            # Add to camera collection
            self.collections['cameras'].objects.link(persp_cam_obj)
            
            # Create cinematic camera (dramatic low angle)
            cinema_cam_data = bpy.data.cameras.new("Camera_Cinematic")
            cinema_cam_data.type = 'PERSP'
            cinema_cam_data.lens = 35  # Wider angle for dramatic effect
            
            cinema_cam_obj = bpy.data.objects.new("Camera_Cinematic", cinema_cam_data)
            cinema_cam_obj.location = (center_x, center_y - max_dim * 1.2, center_z + max_dim * 0.3)
            cinema_cam_obj.rotation_euler = (math.radians(15), 0, math.radians(0))
            
            # Add to camera collection
            self.collections['cameras'].objects.link(cinema_cam_obj)
            
            # Set active camera
            bpy.context.scene.camera = ortho_cam_obj
            
            log("Camera system created")
            
            # Return camera objects
            cameras = {
                'ortho': ortho_cam_obj,
                'perspective': persp_cam_obj,
                'cinematic': cinema_cam_obj
            }
            
            return cameras
        except Exception as e:
            log(f"Error creating camera system: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def calculate_scene_bounds(self, scene_objects):
        """
        Calculate bounds of scene based on object positions
        
        Args:
            scene_objects: List of scene objects
            
        Returns:
            Tuple of (min_x, min_y, min_z, max_x, max_y, max_z)
        """
        try:
            # Initialize bounds
            min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
            max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
            
            # Check each object
            for obj in scene_objects:
                if obj.type not in ['CAMERA', 'LIGHT', 'EMPTY']:
                    # Get object bounds in world space
                    for point in obj.bound_box:
                        world_point = obj.matrix_world @ mathutils.Vector(point)
                        min_x = min(min_x, world_point.x)
                        min_y = min(min_y, world_point.y)
                        min_z = min(min_z, world_point.z)
                        max_x = max(max_x, world_point.x)
                        max_y = max(max_y, world_point.y)
                        max_z = max(max_z, world_point.z)
            
            # Add padding
            padding = 0.1
            min_x -= padding
            min_y -= padding
            min_z -= padding
            max_x += padding
            max_y += padding
            max_z += padding
            
            log(f"Scene bounds: ({min_x:.2f}, {min_y:.2f}, {min_z:.2f}) to ({max_x:.2f}, {max_y:.2f}, {max_z:.2f})")
            return (min_x, min_y, min_z, max_x, max_y, max_z)
        except Exception as e:
            log(f"Error calculating scene bounds: {e}")
            # Return default bounds
            return (-1, -1, -1, 1, 1, 1)
    
    def setup_enhanced_scene(self, scene_objects):
        """
        Set up an enhanced scene with professional lighting and cameras
        
        Args:
            scene_objects: List of scene objects
            
        Returns:
            Dictionary of created scene elements
        """
        try:
            log("Setting up enhanced scene...")
            
            # Create collection hierarchy
            self.create_collection_hierarchy()
            
            # Calculate scene bounds
            bounds = self.calculate_scene_bounds(scene_objects)
            width = bounds[3] - bounds[0]
            height = bounds[4] - bounds[1]
            depth = bounds[5] - bounds[2]
            
            # Setup studio environment
            self.setup_studio_environment((width, height, depth))
            
            # Setup enhanced lighting
            lights = self.setup_enhanced_lighting(bounds)
            
            # Create camera system
            cameras = self.create_camera_system(bounds)
            
            # Set render settings for quality output
            self.setup_render_settings()
            
            # Create a startup script to properly orient the scene when file is opened
            self.setup_startup_script(scene_objects)
            
            log("Enhanced scene setup complete")
            
            # Return scene elements
            scene_elements = {
                'collections': self.collections,
                'lights': lights,
                'cameras': cameras,
                'bounds': bounds
            }
            
            return scene_elements
        except Exception as e:
            log(f"Error setting up enhanced scene: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def setup_render_settings(self):
        """
        Configure render settings for quality output
        
        Returns:
            Boolean indicating success
        """
        try:
            log("Setting up render settings...")
            
            # Get render settings
            render = bpy.context.scene.render
            
            # Set resolution
            render.resolution_x = 1920
            render.resolution_y = 1080
            render.resolution_percentage = 100
            
            # Set quality
            render.film_transparent = True  # Transparent background option
            
            # Set to use Cycles renderer
            bpy.context.scene.render.engine = 'CYCLES'
            
            # Configure Cycles settings
            cycles = bpy.context.scene.cycles
            cycles.samples = 128  # Higher samples for better quality
            cycles.use_denoising = True
            
            # Configure output format
            render.image_settings.file_format = 'PNG'
            render.image_settings.color_mode = 'RGBA'
            render.image_settings.color_depth = '16'
            
            log("Render settings configured")
            return True
        except Exception as e:
            log(f"Error setting up render settings: {e}")
            return False
    
    def setup_startup_script(self, scene_objects):
        """
        Create a startup script for properly orienting scene on file load
        
        Args:
            scene_objects: List of scene objects
            
        Returns:
            Boolean indicating success
        """
        try:
            # Create a text block for the startup script
            script_name = "startup_script.py"
            
            # Check if script already exists
            if script_name in bpy.data.texts:
                script = bpy.data.texts[script_name]
                script.clear()
            else:
                script = bpy.data.texts.new(script_name)
            
            # Write the script content
            script.write("""
import bpy

def setup_view():
    # Frame all objects
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            override = {'area': area}
            bpy.ops.view3d.view_all(override)
            
            # Set viewport shading to rendered for better preview
            space = area.spaces.active
            space.shading.type = 'RENDERED'
            
            # Set the active camera if available
            if 'Camera_Ortho' in bpy.data.objects:
                bpy.context.scene.camera = bpy.data.objects['Camera_Ortho']
            
            # Set view to camera
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_camera(override)
                    break
            
            break

# Register handler to run on file load
def register_handler():
    bpy.app.handlers.load_post.append(lambda dummy: setup_view())

# Run setup on script execution
setup_view()
register_handler()
""")
            
            # Register the script to run when file is loaded
            if not bpy.app.is_running_modal:
                bpy.ops.text.run_script()
            
            log("Startup script created")
            return True
        except Exception as e:
            log(f"Error setting up startup script: {e}")
            return False
