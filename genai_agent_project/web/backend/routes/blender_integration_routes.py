"""
Routes for Blender integration.
This module provides API endpoints for opening 3D models in Blender.
"""
import os
import sys
import logging
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import helper functions for Blender integration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genai_agent.svg_to_video.scripts.open_in_blender import open_model_in_blender, get_blender_path

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/blender",
    tags=["blender"],
    responses={404: {"description": "Not found"}},
)

class OpenInBlenderRequest(BaseModel):
    """Request model for opening a 3D model in Blender."""
    model_path: str
    new_instance: bool = True

@router.get("/health")
async def health_check():
    """Check if Blender is available."""
    blender_path = get_blender_path()
    
    if not blender_path:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable", "message": "Blender executable not found."}
        )
    
    return {"status": "available", "blender_path": blender_path}

@router.post("/open-model")
async def open_model(request: OpenInBlenderRequest):
    """Open a 3D model in Blender."""
    model_path = request.model_path
    new_instance = request.new_instance
    
    # Load config to get the output directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    config_path = os.path.join(project_root, "config.yaml")
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            output_dir = config.get('paths', {}).get('output_dir')
    except Exception as e:
        logger.warning(f"Error loading config: {str(e)}")
        output_dir = os.path.join(project_root, "output")
    
    # Process model path
    if not os.path.isabs(model_path):
        # Check if it starts with models/, output/, etc.
        if model_path.startswith(('models/', 'output/models/')):
            # Replace output/ prefix if present
            if model_path.startswith('output/'):
                model_path = model_path[7:]
            # Replace models/ prefix with the full output/models/ path
            if model_path.startswith('models/'):
                model_path = os.path.join(output_dir, model_path)
        else:
            # Try direct path first
            if not os.path.exists(model_path):
                # Then check in output/models
                possible_path = os.path.join(output_dir, "models", model_path)
                if os.path.exists(possible_path):
                    model_path = possible_path
                else:
                    # Search for the file in output directory
                    found = False
                    for root, dirs, files in os.walk(output_dir):
                        if os.path.basename(model_path) in files:
                            model_path = os.path.join(root, os.path.basename(model_path))
                            found = True
                            break
                    
                    if not found:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Model file not found: {model_path}"
                        )
    
    # Ensure path exists
    if not os.path.exists(model_path):
        logger.error(f"Model file not found after path resolution: {model_path}")
        # List available files in models directory for debugging
        models_dir = os.path.join(output_dir, "models")
        available_models = []
        if os.path.exists(models_dir):
            for root, dirs, files in os.walk(models_dir):
                for file in files:
                    relative_path = os.path.relpath(os.path.join(root, file), output_dir)
                    available_models.append(relative_path)
        
        logger.info(f"Available models: {available_models[:10]}" + ("..." if len(available_models) > 10 else ""))
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model file not found: {model_path}"
        )
    
    logger.info(f"Opening model in Blender: {model_path}")
    success = open_model_in_blender(model_path, new_instance)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to open model in Blender"
        )
    
    return {"status": "success", "message": "Model opened in Blender", "path": model_path}

@router.get("/check-integration")
async def check_blender_integration():
    """Check the Blender integration status."""
    blender_path = get_blender_path()
    
    if not blender_path:
        return {
            "status": "unavailable",
            "message": "Blender executable not found.",
            "details": {
                "blender_path": None,
                "env_var_set": "BLENDER_PATH" in os.environ,
                "checked_paths": [
                    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                    r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                    r"/usr/bin/blender",
                    r"/Applications/Blender.app/Contents/MacOS/Blender"
                ]
            }
        }
    
    # Try to run a simple Blender check
    try:
        result = subprocess.run(
            [blender_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        version_info = result.stdout.strip() if result.returncode == 0 else None
        
        return {
            "status": "available" if result.returncode == 0 else "error",
            "message": "Blender integration is working" if result.returncode == 0 else "Blender installation found but error running version check",
            "details": {
                "blender_path": blender_path,
                "version_info": version_info,
                "return_code": result.returncode,
                "error": result.stderr if result.returncode != 0 else None
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking Blender integration: {str(e)}",
            "details": {
                "blender_path": blender_path,
                "error": str(e)
            }
        }

@router.get("/debug-path-issues")
async def debug_path_issues():
    """Debug path issues for Blender integration."""
    # Check for environment variables
    env_vars = {
        "BLENDER_PATH": os.environ.get("BLENDER_PATH"),
        "PATH": os.environ.get("PATH"),
        "PYTHONPATH": os.environ.get("PYTHONPATH"),
        "PWD": os.environ.get("PWD") or os.getcwd(),
    }
    
    # Check for common Blender paths
    blender_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        r"/usr/bin/blender",
        r"/Applications/Blender.app/Contents/MacOS/Blender"
    ]
    
    blender_path_checks = {path: os.path.exists(path) for path in blender_paths}
    
    # Check for .env file and config.yaml
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    env_file_path = os.path.join(project_root, ".env")
    config_yaml_path = os.path.join(project_root, "config.yaml")
    
    env_file_exists = os.path.exists(env_file_path)
    config_yaml_exists = os.path.exists(config_yaml_path)
    
    # Read .env file if it exists
    env_file_content = None
    if env_file_exists:
        try:
            with open(env_file_path, 'r') as f:
                env_file_content = f.read()
        except Exception as e:
            env_file_content = f"Error reading .env file: {str(e)}"
    
    # Read config.yaml if it exists
    config_yaml_content = None
    if config_yaml_exists:
        try:
            with open(config_yaml_path, 'r') as f:
                config_yaml_content = f.read()
        except Exception as e:
            config_yaml_content = f"Error reading config.yaml file: {str(e)}"
    
    return {
        "status": "debug_info",
        "environment_variables": env_vars,
        "blender_path_checks": blender_path_checks,
        "config_files": {
            "env_file": {
                "exists": env_file_exists,
                "path": env_file_path,
                "content": env_file_content
            },
            "config_yaml": {
                "exists": config_yaml_exists,
                "path": config_yaml_path,
                "content": config_yaml_content
            }
        }
    }
