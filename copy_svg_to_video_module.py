"""
Copy SVG to Video Module

This script copies the SVG to Video pipeline module from the main project
to the genai_agent_project structure to make it available to the web interface.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def copy_directory(src, dst):
    """
    Copy a directory recursively.
    
    Args:
        src: Source directory path
        dst: Destination directory path
    """
    os.makedirs(dst, exist_ok=True)
    
    # Get all files and directories in the source directory
    items = os.listdir(src)
    
    # Copy each item
    for item in items:
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        
        if os.path.isdir(src_path):
            # If it's a directory, recursively copy it
            copy_directory(src_path, dst_path)
        else:
            # If it's a file, copy it
            if not os.path.exists(dst_path) or os.path.getmtime(src_path) > os.path.getmtime(dst_path):
                logger.info(f"Copying {src_path} -> {dst_path}")
                shutil.copy2(src_path, dst_path)
            else:
                logger.info(f"Skipping unchanged file {src_path}")

def main():
    """Main function"""
    # Project paths
    project_root = os.path.abspath(os.path.dirname(__file__))
    
    # Source directory
    source_dir = os.path.join(project_root, "genai_agent", "svg_to_video")
    
    # Destination directory
    dest_dir = os.path.join(project_root, "genai_agent_project", "genai_agent", "svg_to_video")
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")
        return 1
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    logger.info(f"Copying SVG to Video module from {source_dir} to {dest_dir}")
    
    try:
        # Copy the directory recursively
        copy_directory(source_dir, dest_dir)
        
        logger.info("SVG to Video module copied successfully")
        return 0
    except Exception as e:
        logger.error(f"Error copying SVG to Video module: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
