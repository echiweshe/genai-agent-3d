#!/usr/bin/env python
"""
Script to fix API routes in the GenAI Agent 3D project.
This script adds new LLM API endpoints and updates existing ones to support LLM integration.
"""

import os
import sys
import re
import glob
import json

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
backend_dir = os.path.join(project_dir, "genai_agent")
api_dir = os.path.join(backend_dir, "api")

print("=" * 80)
print("GenAI Agent 3D - API Route Fixer".center(80))
print("=" * 80)
print()

# Ensure api directory exists
os.makedirs(api_dir, exist_ok=True)

# 1. Create LLM API router
llm_router_path = os.path.join(api_dir, "llm.py")
print(f"Creating LLM API router at {llm_router_path}...")

llm_router_content = """from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from ..services.llm import LLMService
from ..config import get_settings

# Initialize router
router = APIRouter(prefix="/llm", tags=["llm"])

# Create service instance
settings = get_settings()
llm_service = LLMService()

# Pydantic models for request/response
class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    
class GenerateResponse(BaseModel):
    text: str
    
class Provider(BaseModel):
    name: str
    is_local: bool
    models: List[Dict[str, Any]]

# Routes
@router.get("/providers")
async def get_providers():
    \"\"\"Get available LLM providers and models\"\"\"
    return llm_service.get_providers()

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    \"\"\"Generate text from a prompt using the specified LLM\"\"\"
    try:
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
            
        # Use provider & model from request or from config
        provider = request.provider or settings.llm.get("provider", "ollama")
        model = request.model or settings.llm.get("model", "llama3.2:latest")
        parameters = request.parameters or {}
        
        result = await llm_service.generate(
            request.prompt,
            provider=provider,
            model=model,
            parameters=parameters
        )
        
        return GenerateResponse(text=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

with open(llm_router_path, 'w') as f:
    f.write(llm_router_content)
print("✅ Created LLM API router")

# 2. Update main API router to include LLM routes
main_router_path = os.path.join(api_dir, "__init__.py")

# Check if the file exists, if not create it
if not os.path.exists(main_router_path):
    print(f"Creating main API router at {main_router_path}...")
    
    main_router_content = """from fastapi import APIRouter
from .llm import router as llm_router

api_router = APIRouter()
api_router.include_router(llm_router)

# Add other routers here
"""
    
    with open(main_router_path, 'w') as f:
        f.write(main_router_content)
    print("✅ Created main API router")
else:
    # Update existing router to include LLM routes
    print(f"Updating main API router at {main_router_path}...")
    
    with open(main_router_path, 'r') as f:
        content = f.read()
    
    # Add import if not exists
    if "from .llm import router as llm_router" not in content:
        import_statement = "from .llm import router as llm_router"
        content = re.sub(
            r'(from fastapi import APIRouter.*?)\n',
            f'\\1\n{import_statement}\n',
            content,
            1,
            re.DOTALL
        )
    
    # Add router include if not exists
    if "api_router.include_router(llm_router)" not in content:
        include_statement = "api_router.include_router(llm_router)"
        
        # Check if there's already include_router statements
        if "api_router.include_router" in content:
            content = re.sub(
                r'(api_router\.include_router\(.*?\))',
                f'\\1\n{include_statement}',
                content,
                1
            )
        else:
            content = re.sub(
                r'(api_router = APIRouter\(\).*?)\n',
                f'\\1\n{include_statement}\n',
                content,
                1,
                re.DOTALL
            )
    
    with open(main_router_path, 'w') as f:
        f.write(content)
    print("✅ Updated main API router")

# 3. Update main.py to include API router
main_path = os.path.join(project_dir, "main.py")

print(f"Checking main FastAPI app at {main_path}...")

if os.path.exists(main_path):
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Check if API router is imported
    api_import_exists = re.search(r'from genai_agent\.api import api_router', content) is not None
    
    # Check if API router is included
    api_include_exists = re.search(r'app\.include_router\(api_router\)', content) is not None
    
    if not api_import_exists or not api_include_exists:
        print(f"Updating main FastAPI app to include API router...")
        
        if not api_import_exists:
            # Add import after other imports
            content = re.sub(
                r'(from .+?\n)(?:(?:from .+?\n)*)(?:\s*\n)',
                f'\\1from genai_agent.api import api_router\n\n',
                content
            )
        
        if not api_include_exists:
            # Add include_router call at appropriate spot
            content = re.sub(
                r'(app = FastAPI\(.*?\)\s*)',
                f'\\1\n\n# Include API routers\napp.include_router(api_router, prefix="/api")\n',
                content,
                1,
                re.DOTALL
            )
        
        with open(main_path, 'w') as f:
            f.write(content)
        print("✅ Updated main FastAPI app")
    else:
        print("✅ API router already included in main FastAPI app")
else:
    print("❌ Could not find main.py file")

print("\nAPI routes setup complete! 🎉")
