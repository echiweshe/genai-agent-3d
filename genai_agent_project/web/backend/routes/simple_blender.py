"""
Simple Blender Execution Router for GenAI Agent 3D
This module provides a simplified router for Blender script execution
"""

import os
import sys
import json
import logging
from fastapi import APIRouter, HTTPException, Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create a router
router = APIRouter(tags=["blender"])

# Define output directories
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
BASE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
ALT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "genai_agent_project", "output")

# Choose the output directory that exists, with a preference for the direct one
if os.path.exists(BASE_OUTPUT_DIR):
    logger.info(f"Using output directory: {BASE_OUTPUT_DIR}")
elif os.path.exists(ALT_OUTPUT_DIR):
    BASE_OUTPUT_DIR = ALT_OUTPUT_DIR
    logger.info(f"Using alternative output directory: {BASE_OUTPUT_DIR}")
else:
    logger.warning(f"Creating output directory: {BASE_OUTPUT_DIR}")
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# Also ensure subdirectories exist
for subdir in ["models", "scenes", "diagrams", "tools", "temp"]:
    subdir_path = os.path.join(BASE_OUTPUT_DIR, subdir)
    if not os.path.exists(subdir_path):
        logger.info(f"Creating subdirectory: {subdir_path}")
        os.makedirs(subdir_path, exist_ok=True)

@router.get("/blender-debug")
async def blender_debug():
    """Simple debug endpoint to check if the Blender router is working"""
    return {
        "status": "ok",
        "message": "Blender router is working",
        "base_dir": SCRIPT_DIR,
        "output_dir": BASE_OUTPUT_DIR,
        "directories": {
            subdir: {
                "path": os.path.join(BASE_OUTPUT_DIR, subdir),
                "exists": os.path.exists(os.path.join(BASE_OUTPUT_DIR, subdir)),
                "files": os.listdir(os.path.join(BASE_OUTPUT_DIR, subdir)) if os.path.exists(os.path.join(BASE_OUTPUT_DIR, subdir)) else []
            } for subdir in ["models", "scenes", "diagrams", "tools", "temp"]
        }
    }

@router.get("/blender/list-scripts/{folder:path}")
async def list_blender_scripts(folder: str = ""):
    """List available Blender scripts in the output directory"""
    # Log info for debugging
    logger.info(f"Received request to list scripts in folder: {folder}")
    logger.info(f"BASE_OUTPUT_DIR: {BASE_OUTPUT_DIR}")
    
    # Build the path
    directory = os.path.join(BASE_OUTPUT_DIR, folder)
    abs_directory = os.path.abspath(directory)
    
    logger.info(f"Requested directory: {directory}")
    logger.info(f"Absolute directory path: {abs_directory}")
    
    # Security check
    if not abs_directory.startswith(BASE_OUTPUT_DIR):
        logger.warning(f"Security check failed - path is outside BASE_OUTPUT_DIR")
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    # Check if the directory exists
    if not os.path.exists(abs_directory):
        logger.warning(f"Directory does not exist: {abs_directory}")
        # Automatically create it
        try:
            os.makedirs(abs_directory, exist_ok=True)
            logger.info(f"Created directory: {abs_directory}")
        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating directory: {str(e)}")
    
    if not os.path.isdir(abs_directory):
        logger.error(f"Path exists but is not a directory: {abs_directory}")
        raise HTTPException(status_code=404, detail=f"Path is not a directory: {folder}")
    
    # List all Python files in the directory
    scripts = []
    try:
        items = os.listdir(abs_directory)
        logger.info(f"Found {len(items)} items in directory")
        
        for filename in items:
            file_path = os.path.join(abs_directory, filename)
            if os.path.isfile(file_path) and filename.endswith('.py'):
                # Get relative path from BASE_OUTPUT_DIR
                rel_path = os.path.relpath(file_path, BASE_OUTPUT_DIR)
                script_info = {
                    "name": filename,
                    "path": rel_path.replace('\\', '/'),  # Use forward slashes for consistency
                    "full_path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path)
                }
                scripts.append(script_info)
                logger.info(f"Added script: {filename}, path: {rel_path}")
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading directory: {str(e)}")
    
    logger.info(f"Returning {len(scripts)} scripts")
    return {
        "directory": folder,
        "scripts": scripts
    }

@router.get("/debug/paths")
async def debug_paths():
    """Debug endpoint to check directory paths"""
    try:
        # Check required directories
        required_dirs = [
            BASE_OUTPUT_DIR,
            os.path.join(BASE_OUTPUT_DIR, "models"),
            os.path.join(BASE_OUTPUT_DIR, "scenes"),
            os.path.join(BASE_OUTPUT_DIR, "diagrams"),
            os.path.join(BASE_OUTPUT_DIR, "tools"),
            os.path.join(BASE_OUTPUT_DIR, "temp")
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Created missing directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {e}")
        
        # Check for scripts in each directory
        scripts = {}
        for dir_path in required_dirs:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                dir_name = os.path.basename(dir_path)
                script_files = []
                
                try:
                    for filename in os.listdir(dir_path):
                        if filename.endswith('.py'):
                            file_path = os.path.join(dir_path, filename)
                            script_files.append({
                                "name": filename,
                                "path": os.path.relpath(file_path, BASE_OUTPUT_DIR).replace('\\', '/'),
                                "size": os.path.getsize(file_path),
                                "modified": os.path.getmtime(file_path)
                            })
                except Exception as e:
                    scripts[dir_name] = {"error": str(e)}
                    continue
                
                scripts[dir_name] = script_files
        
        # Create example scripts if needed
        models_dir = os.path.join(BASE_OUTPUT_DIR, "models")
        scenes_dir = os.path.join(BASE_OUTPUT_DIR, "scenes")
        
        if os.path.exists(models_dir) and len(os.listdir(models_dir)) == 0:
            logger.info("Creating example scripts in models directory")
            # Code to create example scripts would go here
        
        if os.path.exists(scenes_dir) and len(os.listdir(scenes_dir)) == 0:
            logger.info("Creating example scripts in scenes directory")
            # Code to create example scenes would go here
        
        return {
            "status": "ok",
            "script_dir": SCRIPT_DIR,
            "base_output_dir": BASE_OUTPUT_DIR,
            "required_directories": required_dirs,
            "missing_directories": missing_dirs,
            "scripts": scripts,
            "current_working_directory": os.getcwd()
        }
    except Exception as e:
        logger.error(f"Error in debug_paths: {e}")
        return {
            "status": "error",
            "message": str(e),
            "script_dir": SCRIPT_DIR,
            "base_output_dir": BASE_OUTPUT_DIR,
            "current_working_directory": os.getcwd()
        }
