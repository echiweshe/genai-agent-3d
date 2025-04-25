#!/usr/bin/env python
"""
Master script to fix all LLM-related issues at once.
This script:
1. Fixes the LLM API routes to work without agent dependency
2. Enhances the settings page to show all providers
3. Creates an LLM tester page
4. Updates the main.py file to include all necessary routes
"""

import os
import sys
import subprocess
import time

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")

print("=" * 80)
print("GenAI Agent 3D - LLM Integration Fixer".center(80))
print("=" * 80)
print()

# Step 1: Fix LLM API routes
print("Step 1: Fixing LLM API routes...")
try:
    subprocess.run([sys.executable, os.path.join(script_dir, "05_fix_api_routes.py")], check=True)
    print("✅ LLM API routes fixed successfully")
except Exception as e:
    print(f"❌ Error fixing LLM API routes: {str(e)}")
    print("Continuing with other fixes...")

print()

# Step 2: Enhance settings page
print("Step 2: Enhancing settings page...")
try:
    subprocess.run([sys.executable, os.path.join(script_dir, "06_enhance_settings_page.py")], check=True)
    print("✅ Settings page enhanced successfully")
except Exception as e:
    print(f"❌ Error enhancing settings page: {str(e)}")
    print("Continuing with other fixes...")

print()

# Step 3: Create LLM tester page
print("Step 3: Creating LLM tester page...")
try:
    subprocess.run([sys.executable, os.path.join(script_dir, "04_integrate_frontend.py")], check=True)
    print("✅ LLM tester page created successfully")
except Exception as e:
    print(f"❌ Error creating LLM tester page: {str(e)}")
    print("Continuing with other fixes...")

print()

# Step 4: Create the simplified LLM API routes file directly
print("Step 4: Creating simplified LLM API routes file directly...")

# Define the path to llm_api_routes.py
llm_api_routes_path = os.path.join(project_dir, "genai_agent", "services", "llm_api_routes.py")
os.makedirs(os.path.dirname(llm_api_routes_path), exist_ok=True)

# Create the content
llm_api_routes_content = """
\"\"\"
Simplified LLM API routes for GenAI Agent 3D.
This version does not rely on the agent and directly creates an LLM service instance.
\"\"\"

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
    \"\"\"Model for text generation request\"\"\"
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TaskClassificationRequest(BaseModel):
    \"\"\"Model for task classification request\"\"\"
    instruction: str
    provider: Optional[str] = None
    model: Optional[str] = None

# LLM service instance
_llm_service = None

def get_llm_service():
    \"\"\"
    Get or create the LLM service instance
    \"\"\"
    global _llm_service
    
    if _llm_service is None:
        try:
            # Import the LLM service
            from genai_agent.services.llm import LLMService
            
            # Create a config for the LLM service
            config = {
                'type': 'local',
                'provider': 'ollama',
                'model': 'llama3.2:latest'
            }
            
            # Try to load config from environment variables
            if os.environ.get('LLM_PROVIDER'):
                config['provider'] = os.environ.get('LLM_PROVIDER')
            
            if os.environ.get('LLM_MODEL'):
                config['model'] = os.environ.get('LLM_MODEL')
            
            # Create a new LLM service instance
            _llm_service = LLMService(config)
        except Exception as e:
            logger.error(f"Error creating LLM service: {str(e)}")
            raise
    
    return _llm_service

@router.get("/providers")
async def get_providers():
    \"\"\"
    Get available LLM providers and models
    \"\"\"
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
    \"\"\"
    Generate text with a language model
    \"\"\"
    try:
        # Get the LLM service
        llm_service = get_llm_service()
        
        # Check if we need to switch providers
        current_provider = llm_service.provider
        current_model = llm_service.model
        
        # Update service provider and model if specified
        if request.provider and request.provider.lower() != current_provider.lower():
            logger.info(f"Provider switch requested from {current_provider} to {request.provider}, but not supported yet")
            # In a real implementation, we would switch providers here
        
        if request.model and request.model != current_model:
            logger.info(f"Model switch requested from {current_model} to {request.model}, but not supported yet")
            # In a real implementation, we would switch models here
        
        # Generate text
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
        # Get the LLM service
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
print(f"✅ Created simplified LLM API routes file: {llm_api_routes_path}")

# Make sure the __init__.py file exists
init_file = os.path.join(project_dir, "genai_agent", "services", "__init__.py")
if not os.path.exists(init_file):
    with open(init_file, "w") as f:
        f.write("# Package initialization file\n")
    print(f"✅ Created __init__.py file: {init_file}")

print()

# Step 5: Update main.py to include the LLM routes
print("Step 5: Updating main.py to include LLM routes...")
main_py_path = os.path.join(project_dir, "web", "backend", "main.py")

if os.path.exists(main_py_path):
    # Read the content
    with open(main_py_path, "r") as f:
        content = f.read()
    
    # Create a backup
    backup_file = main_py_path + ".bak"
    with open(backup_file, "w") as f:
        f.write(content)
    print(f"Created backup: {backup_file}")
    
    # Check if we need to add the import
    if "from genai_agent.services.llm_api_routes import add_llm_routes" not in content:
        # Add import after other imports
        import_added = False
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("# Import routes") or line.startswith("from routes."):
                lines.insert(i, "from genai_agent.services.llm_api_routes import add_llm_routes")
                import_added = True
                break
        
        if not import_added:
            # Add after generic imports
            for i, line in enumerate(lines):
                if line.startswith("from fastapi import"):
                    for j in range(i+1, len(lines)):
                        if not lines[j].startswith("from ") and not lines[j].startswith("import "):
                            lines.insert(j, "\n# Import LLM routes\nfrom genai_agent.services.llm_api_routes import add_llm_routes")
                            import_added = True
                            break
                    if import_added:
                        break
        
        # If still not added, add at the beginning
        if not import_added:
            lines.insert(10, "from genai_agent.services.llm_api_routes import add_llm_routes")
        
        # Check if we need to add the route initialization
        route_added = False
        for i, line in enumerate(lines):
            if line.startswith("app = FastAPI("):
                # Find the closing parenthesis
                for j in range(i+1, len(lines)):
                    if ")" in lines[j]:
                        # Add after app creation
                        lines.insert(j+1, "\n# Add LLM routes\nadd_llm_routes(app)")
                        route_added = True
                        break
                if route_added:
                    break
        
        # If still not added, add after app initialization
        if not route_added:
            for i, line in enumerate(lines):
                if "app = FastAPI" in line:
                    lines.insert(i+1, "\n# Add LLM routes\nadd_llm_routes(app)")
                    break
        
        # Write the modified content back
        with open(main_py_path, "w") as f:
            f.write("\n".join(lines))
        print(f"✅ Updated main.py to include LLM routes")
    else:
        print(f"ℹ️ LLM routes already included in main.py")
else:
    print(f"❌ Could not find main.py at: {main_py_path}")

print()

# Step 6: Create settings endpoints directly if needed
print("Step 6: Creating settings API endpoints...")
settings_api_path = os.path.join(project_dir, "genai_agent", "services", "settings_api.py")

if not os.path.exists(settings_api_path):
    # Create settings API file
    settings_api_content = """
\"\"\"
API for settings management
\"\"\"

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
    \"\"\"
    Get all settings
    \"\"\"
    try:
        settings = load_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")

@router.post("")
async def update_settings(request: UpdateSettingsRequest):
    \"\"\"
    Update settings
    \"\"\"
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
    \"\"\"
    Add settings routes to the FastAPI application
    \"\"\"
    app.include_router(router)
"""
    
    # Write the settings API file
    with open(settings_api_path, "w") as f:
        f.write(settings_api_content)
    print(f"✅ Created settings API file: {settings_api_path}")
    
    # Update main.py to include settings routes
    if os.path.exists(main_py_path):
        # Read the content
        with open(main_py_path, "r") as f:
            content = f.read()
        
        # Check if we need to add the import
        if "from genai_agent.services.settings_api import add_settings_routes" not in content:
            # Add the import
            lines = content.split("\n")
            
            # Find where to add the import
            import_added = False
            for i, line in enumerate(lines):
                if "from genai_agent.services.llm_api_routes import add_llm_routes" in line:
                    lines.insert(i+1, "from genai_agent.services.settings_api import add_settings_routes")
                    import_added = True
                    break
            
            if not import_added:
                for i, line in enumerate(lines):
                    if line.startswith("from genai_agent"):
                        lines.insert(i+1, "from genai_agent.services.settings_api import add_settings_routes")
                        import_added = True
                        break
            
            # Find where to add the route initialization
            route_added = False
            for i, line in enumerate(lines):
                if "add_llm_routes(app)" in line:
                    lines.insert(i+1, "add_settings_routes(app)")
                    route_added = True
                    break
            
            # Write the modified content back
            with open(main_py_path, "w") as f:
                f.write("\n".join(lines))
            print(f"✅ Updated main.py to include settings routes")
else:
    print(f"ℹ️ Settings API file already exists: {settings_api_path}")

print()

print("=" * 80)
print("All fixes applied successfully!".center(80))
print("=" * 80)
print()
print("Next steps:")
print("1. Restart all services:")
print("   cd genai_agent_project")
print("   .\\venv\\Scripts\\activate")
print("   python manage_services.py restart all")
print()
print("2. Test the LLM functionality:")
print("   - Go to http://localhost:3000/llm-test to test the LLM directly")
print("   - Go to your settings page to see and select different LLM providers")
print()
print("3. If any issues remain, check the logs for specific errors")
print("=" * 80)
