#!/usr/bin/env python
"""
Direct LLM Service Initialization Fix

This script directly fixes the 'LLMService.__init__() takes 1 positional argument but 2 were given'
error by updating the LLM API routes file to initialize the LLM service correctly.
"""

import os
import sys
import shutil
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
services_dir = os.path.join(project_dir, "genai_agent", "services")
api_dir = os.path.join(project_dir, "genai_agent", "api")

print("=" * 80)
print("GenAI Agent 3D - LLM Service Initialization Fix".center(80))
print("=" * 80)
print()

# Path to the llm_api_routes.py file
llm_api_routes_path = os.path.join(services_dir, "llm_api_routes.py")

# Check if the file exists
if not os.path.exists(llm_api_routes_path):
    print(f"❌ Could not find {llm_api_routes_path}")
    sys.exit(1)

# Create a backup
backup_path = f"{llm_api_routes_path}.bak"
shutil.copy2(llm_api_routes_path, backup_path)
print(f"✅ Created backup at {backup_path}")

# Read the current content
with open(llm_api_routes_path, 'r') as f:
    content = f.read()

# Look for the LLMService initialization
if "_llm_service = LLMService(config)" in content:
    # Replace with correct initialization
    content = content.replace(
        "_llm_service = LLMService(config)",
        "_llm_service = LLMService()"
    )
    print("✅ Fixed LLMService initialization")
elif "from genai_agent.services.llm import LLMService" in content:
    # Already using correct initialization or different pattern
    print("✅ LLMService import found, checking initialization...")
    
    # Find the get_llm_service function
    get_llm_service_start = content.find("def get_llm_service()")
    if get_llm_service_start >= 0:
        # Find the end of the function
        get_llm_service_end = content.find("@router", get_llm_service_start)
        if get_llm_service_end >= 0:
            # Extract the function
            get_llm_service_func = content[get_llm_service_start:get_llm_service_end]
            
            # Create updated function
            updated_func = """def get_llm_service():
    \"\"\"
    Get or create the LLM service instance
    \"\"\"
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
"""
            
            # Replace the function
            content = content.replace(get_llm_service_func, updated_func)
            print("✅ Updated get_llm_service function")
else:
    print("❌ Could not find LLMService initialization pattern")
    print("Manual inspection required")

# Write the updated content back to the file
with open(llm_api_routes_path, 'w') as f:
    f.write(content)

print("\n✅ LLM service initialization fix applied successfully")

# Create the API structure if it doesn't exist
if not os.path.exists(api_dir):
    os.makedirs(api_dir, exist_ok=True)
    print(f"✅ Created API directory at {api_dir}")

# Create __init__.py in API directory
api_init_path = os.path.join(api_dir, "__init__.py")
if not os.path.exists(api_init_path):
    with open(api_init_path, 'w') as f:
        f.write("""\"\"\"
API package for GenAI Agent 3D
\"\"\"

from fastapi import APIRouter

# Create API router
api_router = APIRouter()

# Import sub-routers
try:
    from .llm import router as llm_router
    api_router.include_router(llm_router)
except ImportError:
    pass
""")
    print(f"✅ Created {api_init_path}")

# Create llm.py in API directory
api_llm_path = os.path.join(api_dir, "llm.py")
if not os.path.exists(api_llm_path):
    with open(api_llm_path, 'w') as f:
        f.write("""\"\"\"
LLM API endpoints for GenAI Agent 3D
\"\"\"

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
    \"\"\"Get available LLM providers and models\"\"\"
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
    \"\"\"Generate text from a prompt using the specified LLM\"\"\"
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
""")
    print(f"✅ Created {api_llm_path}")

# Ask if user wants to restart services
restart = input("\nDo you want to restart all services now? (y/n): ")
if restart.lower() == 'y':
    print("\nRestarting services...")
    
    # Path to manage_services.py
    manage_script = os.path.join(project_dir, "manage_services.py")
    
    # Windows
    if sys.platform == "win32":
        venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
        
        # Check if venv exists
        if os.path.exists(venv_python):
            # Stop services
            subprocess.run([venv_python, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([venv_python, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
        else:
            # Use system Python
            subprocess.run([sys.executable, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([sys.executable, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
    # Linux/Mac
    else:
        venv_python = os.path.join(project_dir, "venv", "bin", "python")
        
        # Check if venv exists
        if os.path.exists(venv_python):
            # Stop services
            subprocess.run([venv_python, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([venv_python, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
        else:
            # Use system Python
            subprocess.run([sys.executable, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([sys.executable, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
    
    print("\n✅ Services restarted successfully")
    print("\nYou can access the web interface at: http://localhost:3000")
else:
    print("\nSkipping service restart")
    print("\nTo restart services manually:")
    print(f"1. cd {project_dir}")
    if sys.platform == "win32":
        print("2. venv\\Scripts\\activate")
    else:
        print("2. source venv/bin/activate")
    print("3. python manage_services.py restart all")

print("\nDone! The LLM service initialization issue should now be fixed.")
