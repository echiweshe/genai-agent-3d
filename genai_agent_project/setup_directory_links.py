#!/usr/bin/env python
"""
Directory Junction Setup Script for GenAI Agent 3D

This script creates symbolic links/junctions to ensure all components
can access the same output files from their expected locations.
Works on both Windows and Linux/MacOS.
"""

import os
import sys
import platform
import shutil
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("setup_dirs")

def is_admin():
    """Check if script is running with admin/root privileges"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def create_symlink(source, target):
    """Create a symbolic link or directory junction"""
    if os.path.exists(target):
        logger.info(f"Removing existing link/directory: {target}")
        try:
            if os.path.islink(target) or os.path.isdir(target) and platform.system() == "Windows":
                # On Windows, rmdir removes both directories and junctions
                os.rmdir(target)
            else:
                # For regular files or Linux/Mac symlinks
                os.unlink(target)
        except Exception as e:
            logger.error(f"Error removing {target}: {str(e)}")
            return False
    
    try:
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(target)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        if platform.system() == "Windows":
            # Use directory junction on Windows
            subprocess.run(["mklink", "/J", target, source], shell=True, check=True)
            logger.info(f"Created directory junction: {target} -> {source}")
        else:
            # Use symbolic link on Linux/Mac
            os.symlink(source, target, target_is_directory=True)
            logger.info(f"Created symbolic link: {target} -> {source}")
        return True
    except Exception as e:
        logger.error(f"Error creating link from {source} to {target}: {str(e)}")
        return False

def setup_directories():
    """Set up all directories and links"""
    # Define base paths
    base_dir = r"C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d" if platform.system() == "Windows" else "/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d"
    
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
    
    # Create links/junctions
    links = [
        (output_dir, os.path.join(genai_project_dir, "output")),
        (output_dir, os.path.join(web_backend_dir, "output")),
        (output_dir, os.path.join(web_frontend_dir, "public", "output"))
    ]
    
    success = True
    for source, target in links:
        if not create_symlink(source, target):
            success = False
    
    return success

if __name__ == "__main__":
    logger.info("GenAI Agent 3D - Directory Link Setup")
    
    if not is_admin():
        logger.warning("This script should be run with administrator/root privileges.")
        if platform.system() == "Windows":
            logger.info("Please run as administrator.")
        else:
            logger.info("Please run with sudo.")
        sys.exit(1)
    
    if setup_directories():
        logger.info("Setup complete. All components now point to the same output directory.")
    else:
        logger.error("Setup completed with errors. Please check the log.")
        sys.exit(1)
