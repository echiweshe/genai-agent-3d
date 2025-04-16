"""
Scene model classes for 3D scenes
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class SceneObject:
    """
    Represents an object in a 3D scene
    """
    id: str
    type: str
    name: str
    position: List[float] = field(default_factory=lambda: [0, 0, 0])
    rotation: List[float] = field(default_factory=lambda: [0, 0, 0])
    scale: List[float] = field(default_factory=lambda: [1, 1, 1])
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'position': self.position,
            'rotation': self.rotation,
            'scale': self.scale,
            'properties': self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneObject':
        """
        Create from dictionary
        
        Args:
            data: Dictionary representation
            
        Returns:
            SceneObject instance
        """
        return cls(
            id=data.get('id'),
            type=data.get('type'),
            name=data.get('name'),
            position=data.get('position', [0, 0, 0]),
            rotation=data.get('rotation', [0, 0, 0]),
            scale=data.get('scale', [1, 1, 1]),
            properties=data.get('properties', {})
        )

@dataclass
class Scene:
    """
    Represents a 3D scene
    """
    id: str
    name: str
    description: str = ""
    objects: List[SceneObject] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'objects': [obj.to_dict() for obj in self.objects],
            'properties': self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scene':
        """
        Create from dictionary
        
        Args:
            data: Dictionary representation
            
        Returns:
            Scene instance
        """
        objects = [
            SceneObject.from_dict(obj_data)
            for obj_data in data.get('objects', [])
        ]
        
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description', ''),
            objects=objects,
            properties=data.get('properties', {})
        )
    
    def get_object(self, object_id: str) -> Optional[SceneObject]:
        """
        Get an object by ID
        
        Args:
            object_id: Object ID
            
        Returns:
            SceneObject instance or None if not found
        """
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None
    
    def get_objects_by_type(self, object_type: str) -> List[SceneObject]:
        """
        Get objects by type
        
        Args:
            object_type: Object type
            
        Returns:
            List of SceneObject instances
        """
        return [obj for obj in self.objects if obj.type == object_type]
