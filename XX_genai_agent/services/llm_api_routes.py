"""
FastAPI routes for LLM service
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Response, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import json
import time
import logging

# Import the LLM service manager
from genai_agent.services.llm_service_manager import LLMServiceManager

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/llm", tags=["llm"])

# LLM Service Manager instance
_llm_service_manager = None

async def get_llm_service_manager():
    """
    Get or create the LLM Service Manager
    """
    global _llm_service_manager
    
    if _llm_service_manager is None:
        # Create and initialize service manager
        _llm_service_manager = LLMServiceManager()
        await _llm_service_manager.initialize()
    
    return _llm_service_manager

# Request models
class GenerateRequest(BaseModel):
    """Model for text generation request"""
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timeout: Optional[int] = 120

class TaskClassificationRequest(BaseModel):
    """Model for task classification request"""
    instruction: str
    provider: Optional[str] = None
    model: Optional[str] = None

class TaskPlanningRequest(BaseModel):
    """Model for task planning request"""
    task: Dict[str, Any]
    available_tools: List[Dict[str, Any]]
    provider: Optional[str] = None
    model: Optional[str] = None

@router.get("/providers")
async def get_providers(service_manager: LLMServiceManager = Depends(get_llm_service_manager)):
    """
    Get available LLM providers and models
    """
    try:
        providers = await service_manager.get_available_providers()
        return providers
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")

@router.post("/generate")
async def generate_text(
    request: GenerateRequest,
    service_manager: LLMServiceManager = Depends(get_llm_service_manager)
):
    """
    Generate text with a language model
    """
    try:
        # Set reasonable timeout limits
        timeout = min(max(request.timeout or 120, 10), 300)  # Between 10s and 5min
        
        # Call the LLM service
        result = await service_manager.request(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            parameters=request.parameters,
            timeout=timeout
        )
        
        # Check for errors
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail=f"Request timed out after {timeout}s")
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

@router.post("/classify-task")
async def classify_task(
    request: TaskClassificationRequest,
    service_manager: LLMServiceManager = Depends(get_llm_service_manager)
):
    """
    Classify a user instruction into a structured task
    """
    try:
        result = await service_manager.classify_task(
            instruction=request.instruction,
            provider=request.provider,
            model=request.model
        )
        
        return result
    except Exception as e:
        logger.error(f"Error classifying task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error classifying task: {str(e)}")

@router.post("/plan-task")
async def plan_task_execution(
    request: TaskPlanningRequest,
    service_manager: LLMServiceManager = Depends(get_llm_service_manager)
):
    """
    Plan the execution of a task using available tools
    """
    try:
        # Call the task planning method
        # Note: We need to implement this method in the service manager
        result = await service_manager.plan_task_execution(
            task=request.task,
            available_tools=request.available_tools,
            provider=request.provider,
            model=request.model
        )
        
        return result
    except Exception as e:
        logger.error(f"Error planning task execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error planning task execution: {str(e)}")

# WebSocket support for LLM streaming responses
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

class LLMWebsocketManager:
    """Manager for LLM WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """Disconnect a client"""
        self.active_connections.pop(client_id, None)
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_json(message)
                    return True
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id}: {str(e)}")
                    self.disconnect(client_id)
            else:
                self.disconnect(client_id)
        
        return False

# WebSocket manager instance
websocket_manager = LLMWebsocketManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    client_id: str,
    service_manager: LLMServiceManager = Depends(get_llm_service_manager)
):
    """
    WebSocket endpoint for real-time LLM interactions
    """
    await websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type", "")
            
            if message_type == "generate":
                # Extract parameters
                prompt = data.get("prompt", "")
                provider = data.get("provider")
                model = data.get("model")
                parameters = data.get("parameters", {})
                request_id = data.get("request_id", f"req_{int(time.time())}")
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "ack",
                    "request_id": request_id,
                    "status": "processing"
                })
                
                try:
                    # Generate text
                    result = await service_manager.request(
                        prompt=prompt,
                        provider=provider,
                        model=model,
                        parameters=parameters
                    )
                    
                    # Send result
                    await websocket.send_json({
                        "type": "result",
                        "request_id": request_id,
                        "status": "completed" if "error" not in result else "error",
                        "result": result
                    })
                
                except Exception as e:
                    logger.error(f"Error generating text via WebSocket: {str(e)}")
                    
                    # Send error
                    await websocket.send_json({
                        "type": "result",
                        "request_id": request_id,
                        "status": "error",
                        "error": str(e)
                    })
            
            elif message_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": time.time()
                })
            
            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "error": f"Unknown message type: {message_type}"
                })
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass
        
        websocket_manager.disconnect(client_id)

# Define function to add LLM routes to the main application
def add_llm_routes(app):
    """
    Add LLM routes to the FastAPI application
    """
    app.include_router(router)
    
    # Shutdown event to close the service manager
    @app.on_event("shutdown")
    async def shutdown_event():
        global _llm_service_manager
        if _llm_service_manager is not None:
            await _llm_service_manager.close()
