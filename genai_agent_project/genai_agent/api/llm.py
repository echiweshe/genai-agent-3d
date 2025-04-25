
"""
LLM API endpoints for GenAI Agent 3D
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

# Import LLM service
from ..services.llm import LLMService

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/llm", tags=["llm"])

# Create LLM service instance
llm_service = LLMService()

# Pydantic models for request/response
class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class GenerateResponse(BaseModel):
    text: str
    
class Provider(BaseModel):
    name: str
    is_local: bool
    models: List[Dict[str, Any]]

@router.get("/providers")
async def get_providers():
    """Get available LLM providers and models"""
    try:
        # Initialize LLM service if needed
        if not llm_service.initialized:
            await llm_service.initialize()
            
        # Get providers from LLM service
        return llm_service.get_providers()
    except Exception as e:
        logger.error(f"Error fetching providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text from a prompt using the specified LLM"""
    try:
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
            
        # Generate text
        text = await llm_service.generate(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            parameters=request.parameters
        )
        
        return GenerateResponse(text=text)
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
