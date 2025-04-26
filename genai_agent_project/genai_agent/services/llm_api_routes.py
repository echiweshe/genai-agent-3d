"""
Simplified LLM API routes for GenAI Agent 3D.
This version does not rely on the agent and directly creates an LLM service instance.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/llm", tags=["llm"])

# Request models
class GenerateRequest(BaseModel):
    """Model for text generation request"""
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TaskClassificationRequest(BaseModel):
    """Model for task classification request"""
    instruction: str
    provider: Optional[str] = None
    model: Optional[str] = None

# LLM service instance
_llm_service = None

def get_llm_service():
    """
    Get or create the LLM service instance
    """
    global _llm_service
    
    if _llm_service is None:
        try:
            # Import the LLM service
            from genai_agent.services.llm import LLMService
            
            # Create a new LLM service instance (without passing config)
            _llm_service = LLMService()
        except Exception as e:
            logger.error(f"Error creating LLM service: {str(e)}")
            raise
    
    return _llm_service

@router.get("/providers")
async def get_providers():
    """
    Get available LLM providers and models
    """
    try:
        # Get the LLM service
        llm_service = get_llm_service()
        
        # Initialize the service if needed
        if not llm_service.initialized:
            await llm_service.initialize()
        
        # Get the providers
        providers = llm_service.get_providers()
        
        # Add cost information (not available from the LLM service)
        for provider in providers:
            if provider["name"] == "Ollama":
                for model in provider["models"]:
                    model["context_length"] = 8192
                    model["input_cost"] = 0.0
                    model["output_cost"] = 0.0
            elif provider["name"] == "OpenAI":
                for model in provider["models"]:
                    if model["id"] == "gpt-4o":
                        model["context_length"] = 128000
                        model["input_cost"] = 0.00005
                        model["output_cost"] = 0.00015
                    elif model["id"] == "gpt-4":
                        model["context_length"] = 8192
                        model["input_cost"] = 0.00003
                        model["output_cost"] = 0.00006
                    else:  # gpt-3.5-turbo
                        model["context_length"] = 16385
                        model["input_cost"] = 0.000001
                        model["output_cost"] = 0.000002
            elif provider["name"] == "Anthropic":
                for model in provider["models"]:
                    if "opus" in model["id"]:
                        model["context_length"] = 200000
                        model["input_cost"] = 0.00003
                        model["output_cost"] = 0.00015
                    elif "sonnet" in model["id"]:
                        model["context_length"] = 200000
                        model["input_cost"] = 0.000003
                        model["output_cost"] = 0.000015
                    else:  # haiku
                        model["context_length"] = 200000
                        model["input_cost"] = 0.00000025
                        model["output_cost"] = 0.00000125
            elif provider["name"] == "Hunyuan3D":
                for model in provider["models"]:
                    model["context_length"] = 8192
                    model["input_cost"] = 0.0001
                    model["output_cost"] = 0.0005
        
        return providers
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")

@router.post("/generate")
async def generate_text(request: GenerateRequest):
    """
    Generate text with a language model
    """
    try:
        # Get the LLM service
        llm_service = get_llm_service()
        
        # Generate text
        result = await llm_service.generate(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            parameters=request.parameters
        )
        
        return {"text": result, "status": "success"}
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

@router.post("/classify-task")
async def classify_task(request: TaskClassificationRequest):
    """
    Classify a user instruction into a structured task
    """
    try:
        # This is just a placeholder - the actual implementation would use the LLM
        # to classify the task into a structured format
        return {
            "task_type": "unknown",
            "confidence": 0.0,
            "details": {
                "instruction": request.instruction
            }
        }
    except Exception as e:
        logger.error(f"Error classifying task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error classifying task: {str(e)}")

# Define function to add LLM routes to the main application
def add_llm_routes(app):
    """
    Add LLM routes to the FastAPI application
    """
    app.include_router(router)
