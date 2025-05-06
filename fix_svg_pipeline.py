"""
Script to fix common issues with the SVG to Video pipeline.
This helps ensure proper setup and functioning of all components.
"""
import os
import sys
import logging
import subprocess
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_directory_structure():
    """Fix SVG directory structure issues."""
    logger.info("Fixing directory structure...")
    
    # Run the sync_svg_directories.py script
    try:
        subprocess.run([sys.executable, "sync_svg_directories.py"], check=True)
        logger.info("Directory structure fixed successfully")
        return True
    except Exception as e:
        logger.error(f"Error fixing directory structure: {str(e)}")
        return False

def fix_svg_to_3d_converter():
    """Fix SVG to 3D converter issues."""
    logger.info("Fixing SVG to 3D converter issues...")
    
    # Path to the SVG to 3D converter script
    converter_path = os.path.join("genai_agent_project", "genai_agent", "svg_to_video", "svg_to_3d", "svg_to_3d.py")
    
    if not os.path.exists(converter_path):
        logger.error(f"SVG to 3D converter script not found: {converter_path}")
        return False
    
    try:
        # Read the script
        with open(converter_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for problematic f-strings with backslashes
        if '\\\\' in content and 'replace' in content:
            # Simple fix: replace problematic escaped backslashes
            content = content.replace(r"filepath=r\"{svg_path.replace('\\', '\\\\')}\"", r"filepath=r\"{svg_path}\"")
            content = content.replace(r"output_file = r\"{output_file.replace('\\', '\\\\')}\"", r"output_file = r\"{output_file}\"")
            
            # Write back the fixed script
            with open(converter_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("SVG to 3D converter script fixed successfully")
        else:
            logger.info("SVG to 3D converter script appears to be fine")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing SVG to 3D converter: {str(e)}")
        return False

def fix_blender_path():
    """Fix Blender path issues."""
    logger.info("Fixing Blender path...")
    
    # Run the update_blender_path.py script
    try:
        subprocess.run([sys.executable, "update_blender_path.py"], check=True)
        logger.info("Blender path fixed successfully")
        return True
    except Exception as e:
        logger.error(f"Error fixing Blender path: {str(e)}")
        return False

def ensure_mathutils_stub():
    """Ensure mathutils stub module exists."""
    logger.info("Checking mathutils stub module...")
    
    # Path to the mathutils stub module
    mathutils_path = os.path.join("genai_agent_project", "genai_agent", "svg_to_video", "svg_to_3d", "mathutils.py")
    
    if os.path.exists(mathutils_path):
        logger.info("mathutils stub module already exists")
        return True
    
    logger.info("Creating mathutils stub module...")
    
    # Simple stub implementation
    stub_content = """\"\"\"
Stub implementation of mathutils module used by Blender.
This is used when the actual Blender mathutils module is not available.
\"\"\"
import math
import logging

logger = logging.getLogger(__name__)
logger.info("Using stub implementation of mathutils module")

class Vector:
    \"\"\"Stub implementation of mathutils.Vector\"\"\"
    
    def __init__(self, values=(0, 0, 0)):
        \"\"\"Initialize a new Vector with the given values.\"\"\"
        if isinstance(values, (list, tuple)):
            self._values = list(values)
        else:
            self._values = [0, 0, 0]
    
    def __getitem__(self, key):
        \"\"\"Get the value at the given index.\"\"\"
        return self._values[key]
    
    def __setitem__(self, key, value):
        \"\"\"Set the value at the given index.\"\"\"
        self._values[key] = value
    
    def __len__(self):
        \"\"\"Get the length of the vector.\"\"\"
        return len(self._values)
    
    def __repr__(self):
        \"\"\"Get a string representation of the vector.\"\"\"
        return f"Vector({self._values})"
    
    def __add__(self, other):
        \"\"\"Add two vectors.\"\"\"
        if isinstance(other, Vector):
            return Vector([a + b for a, b in zip(self._values, other._values)])
        else:
            return Vector([a + other for a in self._values])
    
    def __sub__(self, other):
        \"\"\"Subtract two vectors.\"\"\"
        if isinstance(other, Vector):
            return Vector([a - b for a, b in zip(self._values, other._values)])
        else:
            return Vector([a - other for a in self._values])
    
    def copy(self):
        \"\"\"Create a copy of this vector.\"\"\"
        return Vector(self._values.copy())
    
    def length(self):
        \"\"\"Get the length (magnitude) of this vector.\"\"\"
        return math.sqrt(sum(a * a for a in self._values))
    
    def normalized(self):
        \"\"\"Get a normalized copy of this vector.\"\"\"
        length = self.length()
        if length > 0:
            return Vector([a / length for a in self._values])
        return Vector(self._values)
    
    def normalize(self):
        \"\"\"Normalize this vector in place.\"\"\"
        length = self.length()
        if length > 0:
            for i in range(len(self._values)):
                self._values[i] /= length
        return self

class Matrix:
    \"\"\"Stub implementation of mathutils.Matrix\"\"\"
    
    def __init__(self, rows=None):
        \"\"\"Initialize a new Matrix with the given rows.\"\"\"
        if rows is None:
            # Identity matrix
            self._rows = [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ]
        else:
            self._rows = [list(row) for row in rows]
    
    def __getitem__(self, key):
        \"\"\"Get the row at the given index.\"\"\"
        return self._rows[key]
    
    def __setitem__(self, key, value):
        \"\"\"Set the row at the given index.\"\"\"
        self._rows[key] = list(value)
    
    def __len__(self):
        \"\"\"Get the number of rows in the matrix.\"\"\"
        return len(self._rows)
    
    def __repr__(self):
        \"\"\"Get a string representation of the matrix.\"\"\"
        return f"Matrix({self._rows})"
    
    def copy(self):
        \"\"\"Create a copy of this matrix.\"\"\"
        return Matrix([row.copy() for row in self._rows])

# Export the classes
__all__ = ['Vector', 'Matrix']
"""
    
    try:
        # Create the stub module
        with open(mathutils_path, 'w', encoding='utf-8') as f:
            f.write(stub_content)
        
        logger.info("mathutils stub module created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating mathutils stub module: {str(e)}")
        return False

def restart_backend():
    """Restart the backend service."""
    logger.info("Restarting backend service...")
    
    # Path to the manage_services.py script
    manage_services = os.path.join("genai_agent_project", "manage_services.py")
    
    if not os.path.exists(manage_services):
        logger.error(f"manage_services.py script not found: {manage_services}")
        return False
    
    try:
        subprocess.run([sys.executable, manage_services, "restart", "backend"], check=True)
        logger.info("Backend service restarted successfully")
        return True
    except Exception as e:
        logger.error(f"Error restarting backend service: {str(e)}")
        return False

def main():
    """Main function to fix SVG pipeline issues."""
    logger.info("Starting SVG pipeline fix script...")
    
    # List of fix functions to run
    fix_functions = [
        fix_directory_structure,
        fix_svg_to_3d_converter,
        fix_blender_path,
        ensure_mathutils_stub
    ]
    
    # Run each fix function
    success = True
    for fix_func in fix_functions:
        if not fix_func():
            success = False
    
    # Restart backend service if all fixes succeeded
    if success:
        restart_backend()
    
    logger.info("SVG pipeline fix script completed")
    
    print("\nFix process completed. Please check the logs for details.")
    if success:
        print("All issues appear to be fixed successfully.")
    else:
        print("Some issues could not be fixed. Please review the logs.")
    
    print("\nYou can now try using the SVG to Video pipeline.")

if __name__ == "__main__":
    main()
