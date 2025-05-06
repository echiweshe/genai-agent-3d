"""
Stub module for mathutils to prevent import errors.
This allows the code to run even without the actual Blender mathutils module.
"""

class Vector:
    """Stub Vector class that mimics Blender's Vector."""
    def __init__(self, coords=(0, 0, 0)):
        self.x = coords[0] if len(coords) > 0 else 0
        self.y = coords[1] if len(coords) > 1 else 0
        self.z = coords[2] if len(coords) > 2 else 0
        
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
        
    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        else:
            raise IndexError("Vector index out of range")
            
    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Vector index out of range")
    
    def __len__(self):
        return 3
        
    def __repr__(self):
        return f"Vector(({self.x}, {self.y}, {self.z}))"
        
    def copy(self):
        return Vector((self.x, self.y, self.z))
        
    def normalize(self):
        length = (self.x**2 + self.y**2 + self.z**2)**0.5
        if length != 0:
            self.x /= length
            self.y /= length
            self.z /= length
        return self

class Matrix:
    """Stub Matrix class that mimics Blender's Matrix."""
    def __init__(self, rows=None):
        if rows is None:
            self.rows = [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0]
            ]
        else:
            self.rows = rows
            
    def __repr__(self):
        return f"Matrix({self.rows})"
        
    @classmethod
    def Identity(cls, size=4):
        matrix = cls()
        return matrix
        
    @classmethod
    def Translation(cls, vector):
        matrix = cls()
        matrix.rows[0][3] = vector[0]
        matrix.rows[1][3] = vector[1]
        matrix.rows[2][3] = vector[2]
        return matrix
        
    @classmethod
    def Rotation(cls, angle, size, axis):
        matrix = cls()
        # This is a simplified rotation matrix
        return matrix
