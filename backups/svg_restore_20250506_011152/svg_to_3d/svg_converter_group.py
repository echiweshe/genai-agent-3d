"""
SVG to 3D Converter Group Method

This module contains the group creation method for the SVG to 3D converter.
"""

import bpy
from svg_utils import log


def create_3d_group(self, element):
    """Create a 3D group from SVG group element."""
    try:
        group_id = element.get('id', f"Group_{len(bpy.data.collections)}")
        
        log(f"Creating 3D group: {group_id}")
        
        # Create a new collection for the group
        collection = bpy.data.collections.new(group_id)
        bpy.context.scene.collection.children.link(collection)
        
        # Create an empty object to serve as the group's parent
        group_obj = bpy.data.objects.new(group_id, None)
        bpy.context.collection.objects.link(group_obj)
        
        # Process child elements
        child_objects = []
        for child in element.get('children', []):
            obj = self.create_3d_object(child)
            if obj:
                # Parent the object to our group object
                obj.parent = group_obj
                
                # Move the object to this collection
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                collection.objects.link(obj)
                
                child_objects.append(obj)
        
        # Store reference to group objects
        self.group_objects[group_id] = child_objects
        
        log(f"Group created successfully: {group_id} with {len(child_objects)} child objects")
        return group_obj
    except Exception as e:
        log(f"Error creating 3D group: {e}")
        import traceback
        traceback.print_exc()
        return None
