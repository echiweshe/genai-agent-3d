
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
        # Create a list of available providers and models
        providers = [
            {
                "name": "Ollama",
                "is_local": True,
                "models": [
                    {
                        "id": "llama3:latest",
                        "name": "Llama 3",
                        "context_length": 8192,
                        "input_cost": 0.0,
                        "output_cost": 0.0
                    },
                    {
                        "id": "llama3.2:latest",
                        "name": "Llama 3.2",
                        "context_length": 8192,
                        "input_cost": 0.0,
                        "output_cost": 0.0
                    },
                    {
                        "id": "deepseek-coder:latest",
                        "name": "DeepSeek Coder",
                        "context_length": 8192,
                        "input_cost": 0.0,
                        "output_cost": 0.0
                    }
                ]
            },
            {
                "name": "OpenAI",
                "is_local": False,
                "models": [
                    {
                        "id": "gpt-4o",
                        "name": "GPT-4o",
                        "context_length": 128000,
                        "input_cost": 0.00005,
                        "output_cost": 0.00015
                    },
                    {
                        "id": "gpt-4",
                        "name": "GPT-4",
                        "context_length": 8192,
                        "input_cost": 0.00003,
                        "output_cost": 0.00006
                    },
                    {
                        "id": "gpt-3.5-turbo",
                        "name": "GPT-3.5 Turbo",
                        "context_length": 16385,
                        "input_cost": 0.000001,
                        "output_cost": 0.000002
                    }
                ]
            },
            {
                "name": "Anthropic",
                "is_local": False,
                "models": [
                    {
                        "id": "claude-3-opus-20240229",
                        "name": "Claude 3 Opus",
                        "context_length": 200000,
                        "input_cost": 0.00003,
                        "output_cost": 0.00015
                    },
                    {
                        "id": "claude-3-sonnet-20240229",
                        "name": "Claude 3 Sonnet",
                        "context_length": 200000,
                        "input_cost": 0.000003,
                        "output_cost": 0.000015
                    },
                    {
                        "id": "claude-3-haiku-20240307",
                        "name": "Claude 3 Haiku",
                        "context_length": 200000,
                        "input_cost": 0.00000025,
                        "output_cost": 0.00000125
                    },
                    {
                        "id": "claude-3.5-sonnet-20250626", 
                        "name": "Claude 3.5 Sonnet",
                        "context_length": 200000,
                        "input_cost": 0.000005,
                        "output_cost": 0.000025
                    }
                ]
            }
        ]
        
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
