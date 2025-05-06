"""
Script to synchronize SVG directories and create symbolic links for the SVG to Video pipeline.
This ensures all components can access the same files regardless of their location in the project.
"""
import os
import sys
import shutil
import logging
from pathlib import Path
import platform

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logger.info(f"Base directory: {BASE_DIR}")

# Define directory paths
DIRECTORIES = {
    "main_output": os.path.join(BASE_DIR, "output"),
    "svg_output": os.path.join(BASE_DIR, "output", "svg"),
    "svg_to_video_output": os.path.join(BASE_DIR, "output", "svg_to_video"),
    "animations_output": os.path.join(BASE_DIR, "output", "svg_to_video", "animations"),
    "models_output": os.path.join(BASE_DIR, "output", "svg_to_video", "models"),
    "videos_output": os.path.join(BASE_DIR, "output", "svg_to_video", "videos"),
    "backend_output": os.path.join(BASE_DIR, "genai_agent_project", "web", "backend", "output"),
    "svg_output_in_backend": os.path.join(BASE_DIR, "genai_agent_project", "web", "backend", "output", "svg"),
    "genai_agent_output": os.path.join(BASE_DIR, "genai_agent_project", "output"),
    "svg_output_in_genai": os.path.join(BASE_DIR, "genai_agent_project", "output", "svg"),
    "svg_to_video_in_genai": os.path.join(BASE_DIR, "genai_agent_project", "output", "svg_to_video"),
}

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist."""
    if os.path.exists(directory) and not os.path.isdir(directory):
        logger.warning(f"{directory} exists but is not a directory.")
        # Create a backup of the file
        backup_path = f"{directory}_backup"
        logger.info(f"Renaming to {backup_path}")
        os.rename(directory, backup_path)
    
    if not os.path.exists(directory):
        logger.info(f"Creating directory: {directory}")
        os.makedirs(directory, exist_ok=True)
    else:
        logger.info(f"Directory already exists: {directory}")

def can_create_symlinks():
    """Check if we can create symbolic links (admin privileges on Windows)."""
    if platform.system() != "Windows":
        return True
    
    # On Windows, try to create a test symlink
    test_source = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "symlink_test_dir")
    test_target = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "symlink_test_link")
    
    try:
        # Ensure test directory exists
        os.makedirs(test_source, exist_ok=True)
        
        # Try to create symlink
        if os.path.exists(test_target):
            os.remove(test_target)
        
        os.symlink(test_source, test_target, target_is_directory=True)
        
        # Clean up
        os.remove(test_target)
        os.rmdir(test_source)
        
        return True
    except Exception as e:
        logger.warning(f"Cannot create symbolic links (requires admin on Windows): {str(e)}")
        return False

def try_create_symbolic_link(source, target):
    """Try to create a symbolic link, return True if successful."""
    try:
        if os.path.exists(target):
            if os.path.islink(target):
                # If it's already a symbolic link, check if it points to the source
                if os.path.abspath(os.readlink(target)) == os.path.abspath(source):
                    logger.info(f"Symbolic link already exists: {target} -> {source}")
                    return True
                else:
                    # Remove the existing link if it points to a different location
                    logger.info(f"Removing existing symbolic link: {target}")
                    os.remove(target)
            else:
                # If it's a real directory, rename it
                backup_path = f"{target}_backup"
                logger.info(f"Moving existing directory {target} to {backup_path}")
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.move(target, backup_path)
        
        # Create parent directory if needed
        parent_dir = os.path.dirname(target)
        if not os.path.exists(parent_dir):
            logger.info(f"Creating parent directory: {parent_dir}")
            os.makedirs(parent_dir, exist_ok=True)
        
        # Create symbolic link
        os.symlink(source, target, target_is_directory=True)
        logger.info(f"Created symbolic link: {target} -> {source}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to create symbolic link {target} -> {source}: {str(e)}")
        if isinstance(e, OSError) and hasattr(e, 'winerror') and e.winerror == 1314:
            logger.error("Permission denied. Try running this script as Administrator.")
        return False

def sync_directory_contents(source, target):
    """Synchronize contents from source to target."""
    ensure_directory_exists(source)
    ensure_directory_exists(target)
    
    # Copy files from source to target
    source_files = os.listdir(source)
    for item in source_files:
        source_item = os.path.join(source, item)
        target_item = os.path.join(target, item)
        
        if os.path.isfile(source_item):
            if not os.path.exists(target_item) or os.path.getmtime(source_item) > os.path.getmtime(target_item):
                logger.info(f"Copying file: {source_item} -> {target_item}")
                shutil.copy2(source_item, target_item)
        elif os.path.isdir(source_item):
            ensure_directory_exists(target_item)
            sync_directory_contents(source_item, target_item)

def main():
    """Main function to synchronize SVG directories."""
    logger.info("Starting SVG directory synchronization")
    
    # Create all required directories
    for name, path in DIRECTORIES.items():
        ensure_directory_exists(path)
    
    # Determine if we can create symbolic links
    can_symlink = can_create_symlinks()
    
    # Set up synchronization
    sync_pairs = [
        (DIRECTORIES["svg_output"], DIRECTORIES["svg_output_in_backend"]),
        (DIRECTORIES["svg_output"], DIRECTORIES["svg_output_in_genai"]),
        (DIRECTORIES["svg_to_video_output"], DIRECTORIES["svg_to_video_in_genai"])
    ]
    
    if can_symlink:
        # Create symbolic links
        success = True
        for source, target in sync_pairs:
            if not try_create_symbolic_link(source, target):
                success = False
        
        if success:
            logger.info("Symbolic links created successfully")
        else:
            logger.warning("Some symbolic links could not be created, falling back to directory synchronization")
            for source, target in sync_pairs:
                sync_directory_contents(source, target)
    else:
        # Fall back to directory synchronization
        logger.info("Cannot create symbolic links, falling back to directory synchronization")
        for source, target in sync_pairs:
            sync_directory_contents(source, target)
    
    logger.info("SVG directory synchronization completed")

if __name__ == "__main__":
    main()
