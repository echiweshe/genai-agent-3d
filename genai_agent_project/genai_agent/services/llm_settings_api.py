"""
LLM Settings API for GenAI Agent 3D

This module provides API endpoints for managing LLM settings from the UI.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from .llm_settings_manager import LLMSettingsManager

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/llm-settings", tags=["llm-settings"])

# Request/response models
class UpdateLLMSettingsRequest(BaseModel):
    """Model for updating LLM settings"""
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None

class LLMSettingsResponse(BaseModel):
    """Model for LLM settings response"""
    provider: str
    model: str
    type: str
    available_providers: List[Dict[str, Any]]
    api_keys: Dict[str, bool]

# LLM settings manager instance
_settings_manager = None

def get_settings_manager():
    """Get or create the LLM settings manager instance"""
    global _settings_manager
    
    if _settings_manager is None:
        _settings_manager = LLMSettingsManager()
    
    return _settings_manager

# Routes
@router.get("/", response_model=LLMSettingsResponse)
async def get_llm_settings(
    settings_manager: LLMSettingsManager = Depends(get_settings_manager)
):
    """Get current LLM settings"""
    try:
        settings = settings_manager.get_current_llm_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting LLM settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting LLM settings: {str(e)}")

@router.post("/", response_model=Dict[str, Any])
async def update_llm_settings(
    request: UpdateLLMSettingsRequest,
    settings_manager: LLMSettingsManager = Depends(get_settings_manager)
):
    """Update LLM settings"""
    try:
        # Convert request to dictionary
        settings = request.dict(exclude_unset=True)
        
        # Update settings
        success = settings_manager.update_llm_settings(settings)
        
        if success:
            # Get updated settings
            updated_settings = settings_manager.get_current_llm_settings()
            return {
                "status": "success",
                "message": "LLM settings updated successfully",
                "settings": updated_settings
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update LLM settings")
    except Exception as e:
        logger.error(f"Error updating LLM settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating LLM settings: {str(e)}")

# Function to add routes to the main application
def add_llm_settings_routes(app):
    """Add LLM settings routes to the FastAPI application"""
    app.include_router(router)
