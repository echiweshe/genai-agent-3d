"""
Scene Manager for managing 3D scenes
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional

from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.models.scene import Scene, SceneObject

logger = logging.getLogger(__name__)

class SceneManager:
    """
    Service for managing 3D scenes
    
    Handles creation, modification, and retrieval of scenes.
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any] = None):
        """
        Initialize Scene Manager
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Configuration parameters
        """
        self.redis_bus = redis_bus
        self.config = config or {}
        self.scenes = {}  # In-memory scene storage
        
        # Redis key prefix for scene storage
        self.key_prefix = "scene:"
        
        logger.info("Scene Manager initialized")
    
    async def create_scene(self, scene_data: Dict[str, Any]) -> str:
        """
        Create a new scene
        
        Args:
            scene_data: Scene data
                - name: Scene name
                - description: Scene description
                - objects: List of scene objects
                
        Returns:
            Scene ID
        """
        # Generate scene ID
        scene_id = str(uuid.uuid4())
        
        # Create scene
        scene = Scene(
            id=scene_id,
            name=scene_data.get('name', f"Scene {scene_id[:8]}"),
            description=scene_data.get('description', ''),
            objects=self._create_scene_objects(scene_data.get('objects', []))
        )
        
        # Store scene
        await self._store_scene(scene)
        
        # Notify scene creation
        await self.redis_bus.publish('scene:created', {
            'scene_id': scene_id,
            'name': scene.name
        })
        
        logger.info(f"Created scene: {scene.name} ({scene_id})")
        return scene_id
    
    async def get_scene(self, scene_id: str) -> Optional[Scene]:
        """
        Get a scene by ID
        
        Args:
            scene_id: Scene ID
            
        Returns:
            Scene instance or None if not found
        """
        # Check in-memory cache
        if scene_id in self.scenes:
            return self.scenes[scene_id]
        
        # Get from Redis
        scene_key = f"{self.key_prefix}{scene_id}"
        
        if await self.redis_bus.connect():
            try:
                scene_data = await self.redis_bus.redis.get(scene_key)
                if scene_data:
                    scene_dict = json.loads(scene_data.decode('utf-8'))
                    scene = Scene.from_dict(scene_dict)
                    
                    # Add to cache
                    self.scenes[scene_id] = scene
                    
                    return scene
            except Exception as e:
                logger.error(f"Error retrieving scene {scene_id}: {str(e)}")
        
        logger.warning(f"Scene {scene_id} not found")
        return None
    
    async def update_scene(self, scene_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a scene
        
        Args:
            scene_id: Scene ID
            updates: Scene updates
                - name: New scene name
                - description: New scene description
                - objects: Updated list of scene objects
                
        Returns:
            True if updated successfully, False otherwise
        """
        # Get scene
        scene = await self.get_scene(scene_id)
        if not scene:
            logger.warning(f"Cannot update scene {scene_id}: not found")
            return False
        
        # Update scene
        if 'name' in updates:
            scene.name = updates['name']
        
        if 'description' in updates:
            scene.description = updates['description']
        
        if 'objects' in updates:
            # Replace or update objects
            new_objects = self._create_scene_objects(updates['objects'])
            
            if updates.get('replace_objects', False):
                # Replace all objects
                scene.objects = new_objects
            else:
                # Update existing objects and add new ones
                existing_ids = {obj.id for obj in scene.objects}
                new_ids = {obj.id for obj in new_objects}
                
                # Add new objects
                for obj in new_objects:
                    if obj.id not in existing_ids:
                        scene.objects.append(obj)
                
                # Update existing objects
                for i, obj in enumerate(scene.objects):
                    if obj.id in new_ids:
                        # Find the new object with the same ID
                        new_obj = next((o for o in new_objects if o.id == obj.id), None)
                        if new_obj:
                            scene.objects[i] = new_obj
        
        # Store updated scene
        await self._store_scene(scene)
        
        # Notify scene update
        await self.redis_bus.publish('scene:updated', {
            'scene_id': scene_id,
            'name': scene.name
        })
        
        logger.info(f"Updated scene: {scene.name} ({scene_id})")
        return True
    
    async def delete_scene(self, scene_id: str) -> bool:
        """
        Delete a scene
        
        Args:
            scene_id: Scene ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        # Get scene
        scene = await self.get_scene(scene_id)
        if not scene:
            logger.warning(f"Cannot delete scene {scene_id}: not found")
            return False
        
        # Delete from Redis
        scene_key = f"{self.key_prefix}{scene_id}"
        
        if await self.redis_bus.connect():
            try:
                await self.redis_bus.redis.delete(scene_key)
            except Exception as e:
                logger.error(f"Error deleting scene {scene_id} from Redis: {str(e)}")
                return False
        
        # Remove from cache
        if scene_id in self.scenes:
            del self.scenes[scene_id]
        
        # Notify scene deletion
        await self.redis_bus.publish('scene:deleted', {
            'scene_id': scene_id,
            'name': scene.name
        })
        
        logger.info(f"Deleted scene: {scene.name} ({scene_id})")
        return True
    
    async def list_scenes(self) -> List[Dict[str, Any]]:
        """
        List all scenes
        
        Returns:
            List of scene summaries
        """
        scenes = []
        
        # Get from Redis
        if await self.redis_bus.connect():
            try:
                scene_keys = await self.redis_bus.redis.keys(f"{self.key_prefix}*")
                
                for key in scene_keys:
                    scene_id = key.decode('utf-8')[len(self.key_prefix):]
                    scene = await self.get_scene(scene_id)
                    
                    if scene:
                        scenes.append({
                            'id': scene.id,
                            'name': scene.name,
                            'description': scene.description,
                            'object_count': len(scene.objects)
                        })
            except Exception as e:
                logger.error(f"Error listing scenes from Redis: {str(e)}")
        
        return scenes
    
    async def get_scene_details(self, scene_id: str) -> Dict[str, Any]:
        """
        Get detailed scene information
        
        Args:
            scene_id: Scene ID
            
        Returns:
            Scene details
        """
        scene = await self.get_scene(scene_id)
        if not scene:
            return {'error': f"Scene {scene_id} not found"}
        
        return scene.to_dict()
    
    async def add_object_to_scene(self, scene_id: str, object_data: Dict[str, Any]) -> Optional[str]:
        """
        Add an object to a scene
        
        Args:
            scene_id: Scene ID
            object_data: Object data
                - type: Object type
                - name: Object name
                - position: Object position [x, y, z]
                - rotation: Object rotation [x, y, z]
                - scale: Object scale [x, y, z]
                - properties: Object properties
                
        Returns:
            Object ID if added successfully, None otherwise
        """
        # Get scene
        scene = await self.get_scene(scene_id)
        if not scene:
            logger.warning(f"Cannot add object to scene {scene_id}: scene not found")
            return None
        
        # Create object
        obj = self._create_scene_object(object_data)
        
        # Add to scene
        scene.objects.append(obj)
        
        # Store updated scene
        await self._store_scene(scene)
        
        # Notify object addition
        await self.redis_bus.publish('scene:object:added', {
            'scene_id': scene_id,
            'object_id': obj.id,
            'object_name': obj.name,
            'object_type': obj.type
        })
        
        logger.info(f"Added object {obj.name} ({obj.id}) to scene {scene.name} ({scene_id})")
        return obj.id
    
    async def update_object(self, scene_id: str, object_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an object in a scene
        
        Args:
            scene_id: Scene ID
            object_id: Object ID
            updates: Object updates
                - name: New object name
                - position: New object position
                - rotation: New object rotation
                - scale: New object scale
                - properties: New object properties
                
        Returns:
            True if updated successfully, False otherwise
        """
        # Get scene
        scene = await self.get_scene(scene_id)
        if not scene:
            logger.warning(f"Cannot update object in scene {scene_id}: scene not found")
            return False
        
        # Find object
        obj_index = next((i for i, obj in enumerate(scene.objects) if obj.id == object_id), None)
        if obj_index is None:
            logger.warning(f"Cannot update object {object_id} in scene {scene_id}: object not found")
            return False
        
        # Update object
        obj = scene.objects[obj_index]
        
        if 'name' in updates:
            obj.name = updates['name']
        
        if 'position' in updates:
            obj.position = updates['position']
        
        if 'rotation' in updates:
            obj.rotation = updates['rotation']
        
        if 'scale' in updates:
            obj.scale = updates['scale']
        
        if 'properties' in updates:
            obj.properties.update(updates['properties'])
        
        # Store updated scene
        await self._store_scene(scene)
        
        # Notify object update
        await self.redis_bus.publish('scene:object:updated', {
            'scene_id': scene_id,
            'object_id': object_id,
            'object_name': obj.name
        })
        
        logger.info(f"Updated object {obj.name} ({object_id}) in scene {scene.name} ({scene_id})")
        return True
    
    async def remove_object(self, scene_id: str, object_id: str) -> bool:
        """
        Remove an object from a scene
        
        Args:
            scene_id: Scene ID
            object_id: Object ID
            
        Returns:
            True if removed successfully, False otherwise
        """
        # Get scene
        scene = await self.get_scene(scene_id)
        if not scene:
            logger.warning(f"Cannot remove object from scene {scene_id}: scene not found")
            return False
        
        # Find object
        obj_index = next((i for i, obj in enumerate(scene.objects) if obj.id == object_id), None)
        if obj_index is None:
            logger.warning(f"Cannot remove object {object_id} from scene {scene_id}: object not found")
            return False
        
        # Get object name for logging
        obj_name = scene.objects[obj_index].name
        
        # Remove object
        scene.objects.pop(obj_index)
        
        # Store updated scene
        await self._store_scene(scene)
        
        # Notify object removal
        await self.redis_bus.publish('scene:object:removed', {
            'scene_id': scene_id,
            'object_id': object_id,
            'object_name': obj_name
        })
        
        logger.info(f"Removed object {obj_name} ({object_id}) from scene {scene.name} ({scene_id})")
        return True
    
    async def export_scene(self, scene_id: str, format: str = 'json') -> Dict[str, Any]:
        """
        Export a scene in a specific format
        
        Args:
            scene_id: Scene ID
            format: Export format ('json', 'blender')
            
        Returns:
            Exported scene data
        """
        scene = await self.get_scene(scene_id)
        if not scene:
            return {'error': f"Scene {scene_id} not found"}
        
        if format == 'json':
            return scene.to_dict()
        elif format == 'blender':
            # Convert to Blender Python script format
            return self._export_to_blender(scene)
        else:
            return {'error': f"Unsupported export format: {format}"}
    
    def _create_scene_objects(self, objects_data: List[Dict[str, Any]]) -> List[SceneObject]:
        """
        Create a list of scene objects from data
        
        Args:
            objects_data: List of object data
            
        Returns:
            List of SceneObject instances
        """
        return [self._create_scene_object(obj_data) for obj_data in objects_data]
    
    def _create_scene_object(self, object_data: Dict[str, Any]) -> SceneObject:
        """
        Create a scene object from data
        
        Args:
            object_data: Object data
            
        Returns:
            SceneObject instance
        """
        # Generate object ID if not provided
        object_id = object_data.get('id', str(uuid.uuid4()))
        
        return SceneObject(
            id=object_id,
            type=object_data.get('type', 'unknown'),
            name=object_data.get('name', f"Object {object_id[:8]}"),
            position=object_data.get('position', [0, 0, 0]),
            rotation=object_data.get('rotation', [0, 0, 0]),
            scale=object_data.get('scale', [1, 1, 1]),
            properties=object_data.get('properties', {})
        )
    
    async def _store_scene(self, scene: Scene) -> bool:
        """
        Store a scene in Redis
        
        Args:
            scene: Scene instance
            
        Returns:
            True if stored successfully, False otherwise
        """
        # Store in memory
        self.scenes[scene.id] = scene
        
        # Store in Redis
        scene_key = f"{self.key_prefix}{scene.id}"
        scene_data = json.dumps(scene.to_dict())
        
        if await self.redis_bus.connect():
            try:
                await self.redis_bus.redis.set(scene_key, scene_data)
                return True
            except Exception as e:
                logger.error(f"Error storing scene {scene.id} in Redis: {str(e)}")
                return False
        
        return False
    
    def _export_to_blender(self, scene: Scene) -> Dict[str, Any]:
        """
        Export scene to Blender Python script format
        
        Args:
            scene: Scene instance
            
        Returns:
            Dictionary with Blender script
        """
        # Create Blender script
        script_lines = [
            "import bpy",
            "import math",
            "",
            "# Clear existing objects",
            "bpy.ops.object.select_all(action='SELECT')",
            "bpy.ops.object.delete()",
            "",
            f"# Scene: {scene.name}",
            f"# {scene.description}",
            ""
        ]
        
        # Add objects
        for obj in scene.objects:
            script_lines.extend(self._object_to_blender(obj))
        
        # Add camera and light if not present
        if not any(obj.type == 'camera' for obj in scene.objects):
            script_lines.extend([
                "# Add default camera",
                "bpy.ops.object.camera_add(location=(5, -5, 5))",
                "camera = bpy.context.active_object",
                "camera.rotation_euler = (math.radians(55), 0, math.radians(45))",
                "bpy.context.scene.camera = camera",
                ""
            ])
        
        if not any(obj.type == 'light' for obj in scene.objects):
            script_lines.extend([
                "# Add default light",
                "bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 10))",
                ""
            ])
        
        return {
            'script': "\n".join(script_lines),
            'scene_name': scene.name,
            'object_count': len(scene.objects)
        }
    
    def _object_to_blender(self, obj: SceneObject) -> List[str]:
        """
        Convert a scene object to Blender Python script lines
        
        Args:
            obj: SceneObject instance
            
        Returns:
            List of script lines
        """
        lines = [f"# Object: {obj.name} (Type: {obj.type})"]
        
        if obj.type == 'cube':
            lines.extend([
                f"bpy.ops.mesh.primitive_cube_add(size=1, location=({obj.position[0]}, {obj.position[1]}, {obj.position[2]}))",
                f"cube = bpy.context.active_object",
                f"cube.name = '{obj.name}'",
                f"cube.rotation_euler = ({obj.rotation[0]}, {obj.rotation[1]}, {obj.rotation[2]})",
                f"cube.scale = ({obj.scale[0]}, {obj.scale[1]}, {obj.scale[2]})",
            ])
            
            # Add material if specified
            if 'material' in obj.properties:
                mat_name = obj.properties.get('material', {}).get('name', 'Material')
                color = obj.properties.get('material', {}).get('color', [0.8, 0.8, 0.8, 1.0])
                
                lines.extend([
                    f"# Add material to {obj.name}",
                    f"if '{mat_name}' not in bpy.data.materials:",
                    f"    mat = bpy.data.materials.new(name='{mat_name}')",
                    f"    mat.diffuse_color = ({color[0]}, {color[1]}, {color[2]}, {color[3] if len(color) > 3 else 1.0})",
                    f"else:",
                    f"    mat = bpy.data.materials['{mat_name}']",
                    f"",
                    f"cube.data.materials.append(mat)"
                ])
        
        elif obj.type == 'plane':
            size = obj.properties.get('size', 1.0)
            lines.extend([
                f"bpy.ops.mesh.primitive_plane_add(size={size}, location=({obj.position[0]}, {obj.position[1]}, {obj.position[2]}))",
                f"plane = bpy.context.active_object",
                f"plane.name = '{obj.name}'",
                f"plane.rotation_euler = ({obj.rotation[0]}, {obj.rotation[1]}, {obj.rotation[2]})",
                f"plane.scale = ({obj.scale[0]}, {obj.scale[1]}, {obj.scale[2]})",
            ])
            
            # Add material if specified
            if 'material' in obj.properties:
                mat_name = obj.properties.get('material', {}).get('name', 'Material')
                color = obj.properties.get('material', {}).get('color', [0.8, 0.8, 0.8, 1.0])
                
                lines.extend([
                    f"# Add material to {obj.name}",
                    f"if '{mat_name}' not in bpy.data.materials:",
                    f"    mat = bpy.data.materials.new(name='{mat_name}')",
                    f"    mat.diffuse_color = ({color[0]}, {color[1]}, {color[2]}, {color[3] if len(color) > 3 else 1.0})",
                    f"else:",
                    f"    mat = bpy.data.materials['{mat_name}']",
                    f"",
                    f"plane.data.materials.append(mat)"
                ])
        
        elif obj.type == 'sphere':
            radius = obj.properties.get('radius', 1.0)
            lines.extend([
                f"bpy.ops.mesh.primitive_uv_sphere_add(radius={radius}, location=({obj.position[0]}, {obj.position[1]}, {obj.position[2]}))",
                f"sphere = bpy.context.active_object",
                f"sphere.name = '{obj.name}'",
                f"sphere.rotation_euler = ({obj.rotation[0]}, {obj.rotation[1]}, {obj.rotation[2]})",
                f"sphere.scale = ({obj.scale[0]}, {obj.scale[1]}, {obj.scale[2]})",
            ])
            
            # Add material if specified
            if 'material' in obj.properties:
                mat_name = obj.properties.get('material', {}).get('name', 'Material')
                color = obj.properties.get('material', {}).get('color', [0.8, 0.8, 0.8, 1.0])
                
                lines.extend([
                    f"# Add material to {obj.name}",
                    f"if '{mat_name}' not in bpy.data.materials:",
                    f"    mat = bpy.data.materials.new(name='{mat_name}')",
                    f"    mat.diffuse_color = ({color[0]}, {color[1]}, {color[2]}, {color[3] if len(color) > 3 else 1.0})",
                    f"else:",
                    f"    mat = bpy.data.materials['{mat_name}']",
                    f"",
                    f"sphere.data.materials.append(mat)"
                ])
        
        elif obj.type == 'camera':
            lines.extend([
                f"bpy.ops.object.camera_add(location=({obj.position[0]}, {obj.position[1]}, {obj.position[2]}))",
                f"camera = bpy.context.active_object",
                f"camera.name = '{obj.name}'",
                f"camera.rotation_euler = ({obj.rotation[0]}, {obj.rotation[1]}, {obj.rotation[2]})",
                f"bpy.context.scene.camera = camera"
            ])
        
        elif obj.type == 'light':
            light_type = obj.properties.get('light_type', 'SUN')
            energy = obj.properties.get('energy', 1.0)
            
            lines.extend([
                f"bpy.ops.object.light_add(type='{light_type}', radius=1, location=({obj.position[0]}, {obj.position[1]}, {obj.position[2]}))",
                f"light = bpy.context.active_object",
                f"light.name = '{obj.name}'",
                f"light.data.energy = {energy}"
            ])
        
        else:
            # Generic object creation
            lines.extend([
                f"# Unknown object type: {obj.type}",
                f"# Create an empty object as placeholder",
                f"bpy.ops.object.empty_add(type='PLAIN_AXES', location=({obj.position[0]}, {obj.position[1]}, {obj.position[2]}))",
                f"empty = bpy.context.active_object",
                f"empty.name = '{obj.name}'",
                f"empty.rotation_euler = ({obj.rotation[0]}, {obj.rotation[1]}, {obj.rotation[2]})",
                f"empty.scale = ({obj.scale[0]}, {obj.scale[1]}, {obj.scale[2]})",
            ])
        
        lines.append("")  # Add empty line after each object
        return lines
