
"""
API for settings management
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/settings", tags=["settings"])

# Settings file path
SETTINGS_FILE = "settings.json"

# Get settings file path
def get_settings_file():
    # Get project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_dir, SETTINGS_FILE)

# Models
class UpdateSettingsRequest(BaseModel):
    section: str
    settings: Dict[str, Any]

# Utility to load settings
def load_settings():
    try:
        settings_file = get_settings_file()
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return {}

# Utility to save settings
def save_settings(settings):
    try:
        settings_file = get_settings_file()
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return False

@router.get("")
async def get_settings():
    """
    Get all settings
    """
    try:
        settings = load_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")

@router.post("")
async def update_settings(request: UpdateSettingsRequest):
    """
    Update settings
    """
    try:
        settings = load_settings()
        
        # Update the specified section
        if request.section not in settings:
            settings[request.section] = {}
        
        # Update settings
        settings[request.section].update(request.settings)
        
        # Save settings
        if save_settings(settings):
            return {"status": "success", "message": "Settings updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save settings")
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

# Define function to add settings routes to the main application
def add_settings_routes(app):
    """
    Add settings routes to the FastAPI application
    """
    app.include_router(router)
