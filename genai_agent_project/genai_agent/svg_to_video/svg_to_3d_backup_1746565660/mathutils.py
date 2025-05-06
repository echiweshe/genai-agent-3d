"""
Mathutils stub module for Blender.

This is a stub module that provides basic classes and functions used in Blender's mathutils module.
"""

class Vector:
    """Stub for Blender's Vector class."""
    
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            self.values = list(args[0])
        else:
            self.values = list(args)
        
        self.x = self.values[0] if len(self.values) > 0 else 0
        self.y = self.values[1] if len(self.values) > 1 else 0
        self.z = self.values[2] if len(self.values) > 2 else 0
        self.w = self.values[3] if len(self.values) > 3 else 0
    
class Matrix:
    """Stub for Blender's Matrix class."""
    
    def __init__(self, *args):
        self.rows = args if args else [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

class Quaternion:
    """Stub for Blender's Quaternion class."""
    
    def __init__(self, *args):
        if len(args) == 4:
            self.w, self.x, self.y, self.z = args
        elif len(args) == 2:
            self.w, self.x, self.y, self.z = 1, 0, 0, 0

class Euler:
    """Stub for Blender's Euler class."""
    
    def __init__(self, x=0, y=0, z=0, order='XYZ'):
        self.x = x
        self.y = y
        self.z = z
        self.order = order
