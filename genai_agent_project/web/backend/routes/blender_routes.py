"""
Blender Integration Routes

This module provides API endpoints for:
1. Checking Blender availability
2. Opening 3D models in Blender
3. Downloading 3D model files
4. Debugging path issues
"""

import os
import subprocess
import sys
import logging
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Body, status, Response, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/blender", tags=["blender"])

# Pydantic models for request validation
class OpenModelRequest(BaseModel):
    model_path: str
    new_instance: bool = True

class BlenderHealthResponse(BaseModel):
    status: str
    path: Optional[str] = None
    version: Optional[str] = None
    error: Optional[str] = None

# Define functions to find Blender path
def find_blender_path() -> Optional[str]:
    """Find Blender executable path based on common installation locations."""
    # Check environment variables first
    blender_path = os.environ.get("BLENDER_PATH")
    if blender_path and os.path.exists(blender_path):
        return blender_path

    # Read from config file if environment variable is not set
    config_path = os.path.join(os.getcwd(), "config.yaml")
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if config and "blender" in config and "path" in config["blender"]:
                    path = config["blender"]["path"]
                    if os.path.exists(path):
                        return path
        except Exception as e:
            logger.error(f"Error reading config file: {e}")

    # Check common installation paths based on OS
    possible_paths = []
    
    if platform.system() == "Windows":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        
        # Check Blender 3.6.x and up
        for version in range(43, 35, -1):  # 4.3 down to 3.6
            major = version // 10
            minor = version % 10
            possible_paths.extend([
                f"{program_files}\\Blender Foundation\\Blender {major}.{minor}\\blender.exe",
                f"{program_files_x86}\\Blender Foundation\\Blender {major}.{minor}\\blender.exe",
            ])
    elif platform.system() == "Darwin":  # macOS
        for version in range(43, 35, -1):  # 4.3 down to 3.6
            major = version // 10
            minor = version % 10
            possible_paths.append(f"/Applications/Blender {major}.{minor}/Blender.app/Contents/MacOS/Blender")
        possible_paths.append("/Applications/Blender/Blender.app/Contents/MacOS/Blender")
    else:  # Linux
        possible_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/snap/bin/blender"
        ]
    
    # Check if any of the paths exist
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def get_blender_version(blender_path: str) -> Optional[str]:
    """Get the Blender version by running blender --version."""
    try:
        result = subprocess.run([blender_path, "--version"], 
                               capture_output=True, 
                               text=True, 
                               timeout=5)
        if result.returncode == 0:
            # Parse the version from the output (e.g., "Blender 3.6.0")
            version_line = result.stdout.strip().split('\n')[0]
            return version_line
        return None
    except Exception as e:
        logger.error(f"Error getting Blender version: {e}")
        return None

# API endpoints
@router.get("/health", response_model=BlenderHealthResponse)
async def check_blender_health():
    """Check if Blender is available and return its version."""
    blender_path = find_blender_path()
    
    if not blender_path:
        return {"status": "unavailable", "error": "Blender not found"}
    
    version = get_blender_version(blender_path)
    if not version:
        return {
            "status": "unavailable", 
            "path": blender_path,
            "error": "Blender found but unable to get version"
        }
    
    return {
        "status": "available",
        "path": blender_path,
        "version": version
    }

@router.post("/open-model")
async def open_model_in_blender(
    request: OpenModelRequest,
    background_tasks: BackgroundTasks
):
    """
    Open a 3D model in Blender.
    
    This endpoint launches Blender with the specified model file.
    """
    model_path = request.model_path
    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model file not found: {model_path}"
        )
    
    # Find Blender executable
    blender_path = find_blender_path()
    if not blender_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Blender executable not found"
        )
    
    # Function to launch Blender in the background
    def launch_blender():
        try:
            # Normalize path for the OS
            norm_path = os.path.normpath(model_path)
            
            # Construct Blender command
            cmd = [blender_path]
            if os.path.exists(norm_path):
                cmd.append(norm_path)
            
            # Launch Blender
            logger.info(f"Launching Blender with command: {' '.join(cmd)}")
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
        except Exception as e:
            logger.error(f"Error launching Blender: {e}")
    
    # Add the task to run in the background
    background_tasks.add_task(launch_blender)
    
    return {
        "status": "success",
        "message": "Launching Blender to open the model",
        "model_path": model_path
    }

@router.get("/download")
async def download_model(path: str = Query(...)):
    """
    Download a 3D model file.
    
    This endpoint returns the specified 3D model file for download.
    """
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {path}"
        )
    
    return FileResponse(
        path=path,
        filename=os.path.basename(path),
        media_type="application/octet-stream"
    )

@router.get("/debug-paths")
async def debug_paths():
    """
    Debug endpoint to help troubleshoot Blender path issues.
    
    Returns information about the system environment and search paths.
    """
    # Collect debug information
    debug_info = {
        "platform": platform.system(),
        "architecture": platform.architecture(),
        "python_version": sys.version,
        "current_directory": os.getcwd(),
        "environment_variables": {
            "BLENDER_PATH": os.environ.get("BLENDER_PATH", "Not set"),
            "PROGRAM_FILES": os.environ.get("ProgramFiles", "Not available"),
            "PROGRAM_FILES_X86": os.environ.get("ProgramFiles(x86)", "Not available"),
        },
        "blender_search_results": {
            "found_path": find_blender_path(),
            "possible_locations_existence": {}
        }
    }
    
    # Check existence of common Blender locations
    possible_locations = []
    if platform.system() == "Windows":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        for version in range(43, 35, -1):  # 4.3 down to 3.6
            major = version // 10
            minor = version % 10
            possible_locations.append(
                f"{program_files}\\Blender Foundation\\Blender {major}.{minor}\\blender.exe"
            )
    elif platform.system() == "Darwin":
        for version in range(43, 35, -1):
            major = version // 10
            minor = version % 10
            possible_locations.append(
                f"/Applications/Blender {major}.{minor}/Blender.app/Contents/MacOS/Blender"
            )
    else:
        possible_locations = ["/usr/bin/blender", "/usr/local/bin/blender"]
    
    # Check if each location exists
    for location in possible_locations:
        debug_info["blender_search_results"]["possible_locations_existence"][location] = os.path.exists(location)
    
    # Try to read config file
    config_info = {"exists": False, "content": None, "error": None}
    config_path = os.path.join(os.getcwd(), "config.yaml")
    config_info["path"] = config_path
    
    if os.path.exists(config_path):
        config_info["exists"] = True
        try:
            import yaml
            with open(config_path, "r") as f:
                config_info["content"] = yaml.safe_load(f)
        except Exception as e:
            config_info["error"] = str(e)
    
    debug_info["config_file"] = config_info
    
    return debug_info

# Export the router for use in the main app
# Usage: app.include_router(blender_routes.router)
