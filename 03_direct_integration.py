#!/usr/bin/env python
"""
Script to directly integrate the LLM services into the project.
This script creates the necessary files in the correct locations directly.
"""

import os
import sys
import shutil

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")

# Define directories to create
directories = [
    os.path.join(project_dir, "genai_agent", "services"),
]

# Create directories
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

# Create __init__.py files to make them proper Python packages
for directory in directories:
    init_file = os.path.join(directory, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Package initialization file\n")
        print(f"Created: {init_file}")

# Create the llm_api_routes.py file directly
llm_api_routes_path = os.path.join(project_dir, "genai_agent", "services", "llm_api_routes.py")
llm_api_routes_content = """
\"\"\"
Simple LLM API routes for GenAI Agent 3D.
This is a simplified version that directly interfaces with the existing LLM service.
\"\"\"

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import logging

# Import the existing LLM service
from genai_agent.services.llm import LLMService

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/llm", tags=["llm"])

# Request models
class GenerateRequest(BaseModel):
    \"\"\"Model for text generation request\"\"\"
    prompt: str
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TaskClassificationRequest(BaseModel):
    \"\"\"Model for task classification request\"\"\"
    instruction: str
    model: Optional[str] = None

# LLM service instance
_llm_service = None

def get_llm_service():
    \"\"\"
    Get the LLM service instance
    \"\"\"
    global _llm_service
    
    if _llm_service is None:
        from genai_agent.agent import agent
        if agent and agent.llm_service:
            _llm_service = agent.llm_service
        else:
            # Create a new instance if agent is not available
            from genai_agent.services.llm import LLMService
            _llm_service = LLMService({})
    
    return _llm_service

@router.get("/providers")
async def get_providers():
    \"\"\"
    Get available LLM providers and models
    \"\"\"
    try:
        # For now, just return a simplified version with the default model
        llm_service = get_llm_service()
        model_name = llm_service.model
        provider_name = llm_service.provider
        
        return [
            {
                "name": provider_name.capitalize(),
                "is_local": True,
                "models": [
                    {
                        "id": model_name,
                        "name": model_name.split(":")[0].capitalize(),
                        "context_length": 8192,
                        "input_cost": 0.0,
                        "output_cost": 0.0
                    }
                ]
            }
        ]
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")

@router.post("/generate")
async def generate_text(request: GenerateRequest):
    \"\"\"
    Generate text with a language model
    \"\"\"
    try:
        llm_service = get_llm_service()
        
        # Generate text using the existing LLM service
        result = await llm_service.generate(
            prompt=request.prompt,
            parameters=request.parameters
        )
        
        return {"text": result, "status": "success"}
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

@router.post("/classify-task")
async def classify_task(request: TaskClassificationRequest):
    \"\"\"
    Classify a user instruction into a structured task
    \"\"\"
    try:
        llm_service = get_llm_service()
        
        # Call the task classification method
        result = await llm_service.classify_task(request.instruction)
        
        return result
    except Exception as e:
        logger.error(f"Error classifying task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error classifying task: {str(e)}")

# Define function to add LLM routes to the main application
def add_llm_routes(app):
    \"\"\"
    Add LLM routes to the FastAPI application
    \"\"\"
    app.include_router(router)
"""

with open(llm_api_routes_path, "w") as f:
    f.write(llm_api_routes_content)
print(f"Created: {llm_api_routes_path}")

# Update the main.py file to import the llm_api_routes
main_py_path = os.path.join(project_dir, "web", "backend", "main.py")

if os.path.exists(main_py_path):
    with open(main_py_path, "r") as f:
        content = f.read()
    
    # Check if the import already exists
    if "from genai_agent.services.llm_api_routes import add_llm_routes" not in content:
        # Add the import after the other imports
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("# Import routes") or line.startswith("from routes."):
                lines.insert(i, "from genai_agent.services.llm_api_routes import add_llm_routes")
                break
        
        # Add the call to add_llm_routes after the app is created
        for i, line in enumerate(lines):
            if line.startswith("app = FastAPI("):
                # Find the closing parenthesis
                for j in range(i+1, len(lines)):
                    if ")" in lines[j]:
                        # Insert after the app creation
                        lines.insert(j+1, "\n# Add LLM routes\nadd_llm_routes(app)")
                        break
                break
        
        # Write the modified content back
        with open(main_py_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Updated: {main_py_path}")
    else:
        print(f"No changes needed for {main_py_path}, import already exists")
else:
    print(f"Warning: {main_py_path} not found")

print("\nSimplified integration complete.")
print("\nNext steps:")
print("1. Restart all services: python manage_services.py restart all")
print("2. Check if the backend starts successfully")
