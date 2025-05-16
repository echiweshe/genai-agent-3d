#!/usr/bin/env python
"""
Directory Setup Script for GenAI Agent 3D (Non-Admin Version)

This script creates shared directories to ensure all components
can access the same output files. This version doesn't require
administrator privileges as it uses file copying instead of symbolic links.
"""

import os
import sys
import platform
import shutil
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("setup_dirs")

def setup_directories():
    """Set up all directories and copy files as needed"""
    # Define base paths
    base_dir = r"C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d"
    output_dir = os.path.join(base_dir, "output")
    genai_project_dir = os.path.join(base_dir, "genai_agent_project")
    web_backend_dir = os.path.join(genai_project_dir, "web", "backend")
    web_frontend_dir = os.path.join(genai_project_dir, "web", "frontend")
    
    # Create main output directory if it doesn't exist
    logger.info(f"Creating main output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories
    subdirs = [
        "models", "scenes", "svg", "diagrams", "svg_to_video",
        os.path.join("svg_to_video", "svg"), os.path.join("svg_to_video", "models"),
        "blendergpt", "hunyuan", "trellis"
    ]
    
    for subdir in subdirs:
        subdir_path = os.path.join(output_dir, subdir)
        if not os.path.exists(subdir_path):
            logger.info(f"Creating subdirectory: {subdir_path}")
            os.makedirs(subdir_path, exist_ok=True)
    
    # Create or verify reference output directory in genai_agent_project
    genai_output_dir = os.path.join(genai_project_dir, "output")
    if not os.path.exists(genai_output_dir):
        logger.info(f"Creating reference output directory in genai_agent_project: {genai_output_dir}")
        os.makedirs(genai_output_dir, exist_ok=True)
    
    # Create a file to indicate this is a reference directory
    with open(os.path.join(genai_output_dir, "README.txt"), "w") as f:
        f.write("This is a reference directory pointing to the main output directory at:\n")
        f.write(f"{output_dir}\n\n")
        f.write("Files placed here will be copied to the main output directory.\n")
        f.write("Files from the main output directory will be copied here when needed.\n")
    
    # Setup web backend output directory
    web_backend_output_dir = os.path.join(web_backend_dir, "output")
    if not os.path.exists(web_backend_output_dir):
        logger.info(f"Creating web backend output directory: {web_backend_output_dir}")
        os.makedirs(web_backend_output_dir, exist_ok=True)
    
    # Setup web frontend output directory
    web_frontend_output_dir = os.path.join(web_frontend_dir, "public", "output")
    if not os.path.exists(os.path.dirname(web_frontend_output_dir)):
        logger.info(f"Creating web frontend public directory: {os.path.dirname(web_frontend_output_dir)}")
        os.makedirs(os.path.dirname(web_frontend_output_dir), exist_ok=True)
    
    if not os.path.exists(web_frontend_output_dir):
        logger.info(f"Creating web frontend output directory: {web_frontend_output_dir}")
        os.makedirs(web_frontend_output_dir, exist_ok=True)
    
    # Synchronize existing files
    synchronize_directories(output_dir, genai_output_dir)
    synchronize_directories(output_dir, web_backend_output_dir)
    synchronize_directories(output_dir, web_frontend_output_dir)
    
    # Setup file monitoring and synchronization
    logger.info("\nFile synchronization setup complete!")
    logger.info("\nIMPORTANT: Since we couldn't create symbolic links (which would require admin privileges),")
    logger.info("we've set up reference directories instead. When adding new files:")
    logger.info(" - Place them in the main output directory: " + output_dir)
    logger.info(" - Run 'python sync_output_dirs.py' to update all reference directories")
    
    # Create the sync script
    create_sync_script(output_dir, genai_output_dir, web_backend_output_dir, web_frontend_output_dir)
    
    logger.info("\nSetup complete. All output directories have been created and synchronized.")
    return True

def synchronize_directories(source_dir, target_dir):
    """Copy files from source directory to target directory"""
    logger.info(f"Synchronizing directories: {source_dir} -> {target_dir}")
    
    for root, dirs, files in os.walk(source_dir):
        # Get the relative path from source
        rel_path = os.path.relpath(root, source_dir)
        target_path = os.path.join(target_dir, rel_path) if rel_path != "." else target_dir
        
        # Create directory if it doesn't exist
        if not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
        
        # Copy files
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_path, file)
            
            # Only copy if file doesn't exist or is newer
            if not os.path.exists(target_file) or os.path.getmtime(source_file) > os.path.getmtime(target_file):
                logger.info(f"Copying file: {os.path.relpath(source_file, source_dir)} -> {os.path.relpath(target_file, target_dir)}")
                shutil.copy2(source_file, target_file)

def create_sync_script(main_dir, genai_dir, backend_dir, frontend_dir):
    """Create a script to synchronize directories"""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sync_output_dirs.py")
    
    with open(script_path, "w") as f:
        f.write("""#!/usr/bin/env python
\"\"\"
Synchronize Output Directories for GenAI Agent 3D

This script synchronizes all reference output directories with the main output directory.
Run this script whenever you add or modify files in any output directory.
\"\"\"

import os
import sys
import shutil
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sync_dirs")

def synchronize_directories(source_dir, target_dir):
    \"\"\"Copy files from source directory to target directory\"\"\"
    logger.info(f"Synchronizing directories: {source_dir} -> {target_dir}")
    
    for root, dirs, files in os.walk(source_dir):
        # Get the relative path from source
        rel_path = os.path.relpath(root, source_dir)
        target_path = os.path.join(target_dir, rel_path) if rel_path != "." else target_dir
        
        # Create directory if it doesn't exist
        if not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
        
        # Copy files
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_path, file)
            
            # Only copy if file doesn't exist or is newer
            if not os.path.exists(target_file) or os.path.getmtime(source_file) > os.path.getmtime(target_file):
                logger.info(f"Copying file: {os.path.relpath(source_file, source_dir)} -> {os.path.relpath(target_file, target_dir)}")
                shutil.copy2(source_file, target_file)

def main():
    # Define directories
    main_dir = r"{main_dir}"
    genai_dir = r"{genai_dir}"
    backend_dir = r"{backend_dir}"
    frontend_dir = r"{frontend_dir}"
    
    # Check if directories exist
    if not os.path.exists(main_dir):
        logger.error(f"Main output directory does not exist: {main_dir}")
        return 1
    
    # Synchronize directories
    logger.info("Starting directory synchronization...")
    
    # Bidirectional sync between main and genai
    synchronize_directories(main_dir, genai_dir)
    synchronize_directories(genai_dir, main_dir)
    
    # Sync from main to web
    synchronize_directories(main_dir, backend_dir)
    synchronize_directories(main_dir, frontend_dir)
    
    logger.info("Synchronization complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
""".format(
    main_dir=main_dir,
    genai_dir=genai_dir,
    backend_dir=backend_dir,
    frontend_dir=frontend_dir
))
    
    logger.info(f"Created synchronization script: {script_path}")

if __name__ == "__main__":
    logger.info("GenAI Agent 3D - Directory Setup (Non-Admin Version)")
    
    if setup_directories():
        logger.info("Setup completed successfully!")
    else:
        logger.error("Setup completed with errors. Please check the log.")
        sys.exit(1)
