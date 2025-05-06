"""
Restore SVG to 3D Modules

This script restores the full modular SVG to 3D converter from the backup location
to the current project location.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define source and destination paths
project_dir = os.path.abspath(os.path.dirname(__file__))
source_dir = os.path.join(project_dir, "XX_genai_agent", "svg_to_video", "svg_to_3d")
dest_dir = os.path.join(project_dir, "genai_agent_project", "genai_agent", "svg_to_video", "svg_to_3d")

# Create a backup of current destination directory
def backup_current_files():
    """Backup current SVG to 3D module files."""
    if os.path.exists(dest_dir):
        backup_dir = f"{dest_dir}_backup_{int(Path(dest_dir).stat().st_mtime)}"
        logger.info(f"Creating backup of current SVG to 3D module at: {backup_dir}")
        shutil.copytree(dest_dir, backup_dir)
        logger.info("Backup created successfully")

# Copy files from source to destination
def copy_module_files():
    """Copy SVG to 3D module files from backup to current location."""
    logger.info(f"Copying SVG to 3D modules from {source_dir} to {dest_dir}")
    
    # First verify source directory exists
    if not os.path.exists(source_dir):
        logger.error(f"Source directory not found: {source_dir}")
        return False
    
    # Get list of files in source directory
    source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    logger.info(f"Found {len(source_files)} files in source directory")
    
    # Clear destination directory
    if os.path.exists(dest_dir):
        for item in os.listdir(dest_dir):
            item_path = os.path.join(dest_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        logger.info(f"Cleared destination directory: {dest_dir}")
    else:
        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        logger.info(f"Created destination directory: {dest_dir}")
    
    # Copy files from source to destination
    for filename in source_files:
        source_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(dest_dir, filename)
        shutil.copy2(source_file, dest_file)
        logger.info(f"Copied {filename}")
    
    # Copy any subdirectories if present
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(dest_dir, item)
        if os.path.isdir(source_item):
            shutil.copytree(source_item, dest_item)
            logger.info(f"Copied directory {item}")
    
    # Check if mathutils.py exists in destination directory
    mathutils_path = os.path.join(dest_dir, "mathutils.py")
    if not os.path.exists(mathutils_path):
        # Create a simple mathutils stub module
        logger.info("Creating mathutils stub module...")
        with open(mathutils_path, "w") as f:
            f.write("""\"\"\"
Mathutils stub module for Blender.

This is a stub module that provides basic classes and functions used in Blender's mathutils module.
\"\"\"

class Vector:
    \"\"\"Stub for Blender's Vector class.\"\"\"
    
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
    \"\"\"Stub for Blender's Matrix class.\"\"\"
    
    def __init__(self, *args):
        self.rows = args if args else [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

class Quaternion:
    \"\"\"Stub for Blender's Quaternion class.\"\"\"
    
    def __init__(self, *args):
        if len(args) == 4:
            self.w, self.x, self.y, self.z = args
        elif len(args) == 2:
            self.w, self.x, self.y, self.z = 1, 0, 0, 0

class Euler:
    \"\"\"Stub for Blender's Euler class.\"\"\"
    
    def __init__(self, x=0, y=0, z=0, order='XYZ'):
        self.x = x
        self.y = y
        self.z = z
        self.order = order
""")
        logger.info("Created mathutils stub module")
    
    logger.info("SVG to 3D modules copied successfully")
    return True

# Update imports in the copied files if needed
def update_imports():
    """Update imports in the copied files to match the new project structure."""
    logger.info("Checking and updating imports in SVG to 3D modules...")
    
    for filename in os.listdir(dest_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(dest_dir, filename)
            
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if file contains relative imports
            if 'from .' in content or 'import .' in content:
                logger.info(f"File {filename} contains relative imports, no changes needed")
                continue
            
            # Check for absolute imports that need updating
            updated_content = content
            if 'svg_parser' in content or 'svg_converter' in content or 'svg_utils' in content:
                # Add relative import prefix if needed
                updated_content = content.replace('import svg_', 'from . import svg_')
                updated_content = updated_content.replace('from svg_', 'from .svg_')
                
                # Write updated content back to file
                if updated_content != content:
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    logger.info(f"Updated imports in {filename}")
    
    logger.info("Import updates complete")

# Create output directories
def create_output_directories():
    """Create necessary output directories."""
    logger.info("Creating output directories...")
    
    output_dirs = [
        os.path.join(project_dir, "output", "models"),
        os.path.join(project_dir, "output", "svg_to_video", "models")
    ]
    
    for directory in output_dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created/verified directory: {directory}")
    
    logger.info("Output directories created successfully")

# Main function
def main():
    """Main function to restore SVG to 3D modules."""
    logger.info("Starting SVG to 3D module restoration...")
    
    # Create backup of current files
    backup_current_files()
    
    # Copy module files
    if not copy_module_files():
        logger.error("Failed to copy SVG to 3D modules")
        return
    
    # Update imports if needed
    update_imports()
    
    # Create output directories
    create_output_directories()
    
    logger.info("SVG to 3D module restoration completed successfully!")
    logger.info("Please restart the backend service to apply changes.")

if __name__ == "__main__":
    main()
