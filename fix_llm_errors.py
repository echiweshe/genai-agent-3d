#!/usr/bin/env python3
"""
Fix for LLM-related errors in GenAI Agent 3D

This script:
1. Creates the api directory structure if it doesn't exist
2. Makes sure the LLM API implementation is working properly
3. Fixes any issues with Ollama connection
"""

import os
import sys
import re
import shutil
from datetime import datetime
import yaml

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    return backup_path

def create_api_structure():
    """Create the API directory structure if it doesn't exist"""
    project_root = "C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d\\genai_agent_project\\genai_agent"
    api_dir = os.path.join(project_root, "api")
    
    # Create api directory if it doesn't exist
    if not os.path.exists(api_dir):
        os.makedirs(api_dir)
        print(f"✅ Created API directory at {api_dir}")
    
    # Create __init__.py if it doesn't exist
    init_py = os.path.join(api_dir, "__init__.py")
    if not os.path.exists(init_py):
        with open(init_py, 'w') as f:
            f.write('"""API package for GenAI Agent 3D"""')
        print(f"✅ Created API __init__.py at {init_py}")
    
    # Create llm.py API file
    llm_py = os.path.join(api_dir, "llm.py")
    llm_content = """
"""API for LLM interactions in GenAI Agent 3D"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import logging
import json
import uuid

# Import services
from ..services.llm import LLMService

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Shared LLM service instance
_llm_service = None

def get_llm_service():
    """Get or create the LLM service instance"""
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService()
    
    return _llm_service

# Request/response models
class GenerateRequest(BaseModel):
    """Model for text generation request"""
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GenerateResponse(BaseModel):
    """Model for text generation response"""
    text: str
    status: str = "success"

class ProviderModel(BaseModel):
    """Model for LLM provider information"""
    id: str
    name: str
    context_length: Optional[int] = None
    input_cost: Optional[float] = None
    output_cost: Optional[float] = None

class Provider(BaseModel):
    """Model for LLM provider"""
    name: str
    is_local: bool
    models: List[ProviderModel]

# WebSocket connection manager
class LLMConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, client_id: str, message: Any):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = LLMConnectionManager()

# Routes
@router.get("/providers")
async def get_providers():
    """Get available LLM providers and models"""
    try:
        llm_service = get_llm_service()
        await llm_service.initialize()
        providers = llm_service.get_providers()
        return providers
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text with a language model"""
    try:
        llm_service = get_llm_service()
        
        result = await llm_service.generate(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            parameters=request.parameters
        )
        
        return {"text": result, "status": "success"}
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for streaming LLM responses"""
    await manager.connect(client_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different request types
            req_type = data.get("type")
            request_id = data.get("request_id", str(uuid.uuid4()))
            
            if req_type == "generate":
                # Handle text generation request
                prompt = data.get("prompt", "")
                provider = data.get("provider")
                model = data.get("model")
                parameters = data.get("parameters", {})
                
                # Send acknowledgment
                await manager.send_message(client_id, {
                    "type": "ack",
                    "request_id": request_id,
                    "message": "Processing generation request"
                })
                
                # Process in background
                asyncio.create_task(handle_generate_ws(
                    client_id, request_id, prompt, provider, model, parameters
                ))
            
            elif req_type == "ping":
                await manager.send_message(client_id, {
                    "type": "pong",
                    "request_id": request_id
                })
            
            else:
                await manager.send_message(client_id, {
                    "type": "error",
                    "request_id": request_id,
                    "message": f"Unknown request type: {req_type}"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await manager.send_message(client_id, {
                "type": "error",
                "message": str(e)
            })
        except:
            pass
        manager.disconnect(client_id)

async def handle_generate_ws(client_id, request_id, prompt, provider, model, parameters):
    """Handle text generation via WebSocket"""
    try:
        llm_service = get_llm_service()
        
        # Send processing status
        await manager.send_message(client_id, {
            "type": "status",
            "request_id": request_id,
            "status": "processing"
        })
        
        # Generate text
        result = await llm_service.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            parameters=parameters
        )
        
        # Send result
        await manager.send_message(client_id, {
            "type": "result",
            "request_id": request_id,
            "text": result
        })
    
    except Exception as e:
        logger.error(f"Error in WebSocket text generation: {str(e)}")
        await manager.send_message(client_id, {
            "type": "error",
            "request_id": request_id,
            "message": str(e)
        })
"""
    
    # Write content to file (creating a backup if it exists)
    if os.path.exists(llm_py):
        backup_file(llm_py)
    
    with open(llm_py, 'w') as f:
        f.write(llm_content)
    
    print(f"✅ Created API LLM file at {llm_py}")
    return True

def fix_llm_service():
    """Fix issues with the LLM service"""
    llm_service_path = "C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d\\genai_agent_project\\genai_agent\\services\\llm.py"
    
    if not os.path.exists(llm_service_path):
        print(f"❌ LLM service file not found at {llm_service_path}")
        return False
    
    # Create backup
    backup_file(llm_service_path)
    
    # Read file
    with open(llm_service_path, 'r') as f:
        content = f.read()
    
    # Update the _generate_ollama method to include better error handling
    ollama_method_pattern = re.compile(r'async def _generate_ollama.*?raise\s*\n', re.DOTALL)
    
    improved_ollama_method = """    async def _generate_ollama(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Generate text using Ollama API"""
        base_url = self.providers.get("ollama", {}).get("base_url", "http://127.0.0.1:11434")
        
        # Map our generic parameters to Ollama specific ones
        ollama_params = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": parameters.get("temperature", 0.7),
                "num_predict": parameters.get("max_tokens", 2048)
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/api/generate",
                    json=ollama_params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
                else:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return f"Error: {error_msg}. Please make sure Ollama is running and the model is installed."
        except httpx.ConnectError:
            error_msg = f"Could not connect to Ollama at {base_url}. Please make sure Ollama is running."
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error generating text with Ollama: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    """
    
    # Replace the method
    modified_content = ollama_method_pattern.sub(improved_ollama_method, content)
    
    # Write back to file
    with open(llm_service_path, 'w') as f:
        f.write(modified_content)
    
    print("✅ Updated LLM service with more robust Ollama implementation")
    return True

def fix_llm_api_routes():
    """Update the LLM API routes to use the new API structure"""
    routes_file = "C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d\\genai_agent_project\\genai_agent\\services\\llm_api_routes.py"
    
    if not os.path.exists(routes_file):
        print(f"❌ LLM API routes file not found at {routes_file}")
        return False
    
    # Create backup
    backup_file(routes_file)
    
    # Create updated content
    updated_content = """
"""
Simplified LLM API routes for GenAI Agent 3D.
This file uses the new API structure.
"""

from fastapi import APIRouter, FastAPI
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Import the router from the API package
# If the import fails, we'll create a simplified router
try:
    from ..api.llm import router as llm_router
    USING_NEW_API = True
except ImportError:
    from fastapi import HTTPException
    from pydantic import BaseModel, Field
    from typing import Dict, Any, List, Optional
    
    # Create a fallback router
    logger.warning("Using fallback LLM router - API package not found")
    llm_router = APIRouter(prefix="/api/llm", tags=["llm"])
    USING_NEW_API = False
    
    # LLM service instance
    _llm_service = None
    
    # Basic models
    class GenerateRequest(BaseModel):
        """Model for text generation request"""
        prompt: str
        provider: Optional[str] = None
        model: Optional[str] = None
        parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    def get_llm_service():
        """Get or create the LLM service instance"""
        global _llm_service
        
        if _llm_service is None:
            try:
                # Import the LLM service
                from ..services.llm import LLMService
                
                # Create a new LLM service instance
                _llm_service = LLMService()
            except Exception as e:
                logger.error(f"Error creating LLM service: {str(e)}")
                raise
        
        return _llm_service
    
    @llm_router.get("/providers")
    async def get_providers():
        """Get available LLM providers and models"""
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
                        }
                    ]
                }
            ]
            
            return providers
        except Exception as e:
            logger.error(f"Error getting providers: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")
    
    @llm_router.post("/generate")
    async def generate_text(request: GenerateRequest):
        """Generate text with a language model"""
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

def add_llm_routes(app: FastAPI):
    """
    Add LLM routes to the FastAPI application
    """
    global USING_NEW_API, llm_router
    
    # Try to ensure the LLM service is initialized
    if not USING_NEW_API:
        try:
            # Attempt to pre-initialize LLM service
            service = get_llm_service()
            logger.info("LLM Service pre-initialized")
        except Exception as e:
            logger.warning(f"Could not pre-initialize LLM service: {e}")
    
    # Include the router
    app.include_router(llm_router, prefix="/api" if USING_NEW_API else "")
    logger.info(f"Added LLM routes to application (using {'new' if USING_NEW_API else 'fallback'} API)")
"""
    
    # Write updated content
    with open(routes_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ Updated LLM API routes to use the new API structure")
    return True

def update_test_page():
    """Make sure the LLM test page works properly"""
    # This would add or modify a test page in the frontend
    # For now, we'll just log that this step was skipped
    print("⚠️ LLM test page update skipped (requires frontend modifications)")
    return True

if __name__ == "__main__":
    print("="*80)
    print("               GenAI Agent 3D - LLM Error Fixes               ")
    print("="*80)
    
    success = True
    
    print("\n1. Creating API structure...")
    if not create_api_structure():
        success = False
    
    print("\n2. Fixing LLM service...")
    if not fix_llm_service():
        success = False
    
    print("\n3. Updating LLM API routes...")
    if not fix_llm_api_routes():
        success = False
    
    print("\n4. Updating test page...")
    if not update_test_page():
        # Not critical, so don't set success to False
        pass
    
    if success:
        print("\n✅ All LLM fixes applied successfully!")
        
        # Ask if user wants to restart services
        restart = input("Do you want to restart all services now? (y/n): ")
        if restart.lower() == 'y':
            print("Restarting services...")
            os.system('cd C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d && python manage_services.py restart all')
            print("Services restarted!")
        else:
            print("Skipping service restart")
            print("To restart services manually:")
            print("cd C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d")
            print("python manage_services.py restart all")
    else:
        print("\n⚠️ Some fixes could not be applied.")
        print("Please check the error messages above and fix manually if needed.")
