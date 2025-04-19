"""
FastAPI backend for GenAI Agent 3D
"""

import os
import sys
import yaml
import logging
import asyncio
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import GenAI Agent 3D components
from genai_agent.agent import GenAIAgent
from genai_agent.services.redis_bus import RedisMessageBus

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GenAI Agent 3D API",
    description="API for interacting with the GenAI Agent 3D system",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define models
class InstructionRequest(BaseModel):
    instruction: str
    context: Optional[Dict[str, Any]] = None

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class ConfigurationRequest(BaseModel):
    section: str
    key: str
    value: Any

# Initialize agent and services based on configuration
agent = None
redis_bus = None

# Check if running in test mode
TEST_MODE = os.environ.get("GENAI_TEST_MODE", "false").lower() == "true"

async def initialize_services():
    """Initialize services and agent"""
    global agent, redis_bus, TEST_MODE

    try:
        if TEST_MODE:
            logger.info("Initializing services in TEST MODE")
            # In test mode, use mock objects
            from unittest.mock import MagicMock
            
            class MockRedisMessageBus:
                async def connect(self):
                    logger.info("MockRedisMessageBus connected")
                    return True
                
                async def disconnect(self):
                    logger.info("MockRedisMessageBus disconnected")
                    return True
                
                async def ping(self):
                    return {"status": "ok", "message": "PONG (test mode)"}
            
            class MockToolRegistry:
                def get_tools(self):
                    return [
                        type('Tool', (), {"name": "scene_generator", "description": "Generate 3D scenes"}),
                        type('Tool', (), {"name": "model_generator", "description": "Generate 3D models"}),
                        type('Tool', (), {"name": "test_tool", "description": "Tool for testing"})
                    ]
                
                async def execute_tool(self, tool_name, parameters):
                    logger.info(f"Mock executing tool: {tool_name} with parameters: {parameters}")
                    return {
                        "status": "success",
                        "tool": tool_name,
                        "result": f"Mock result for {tool_name}",
                        "parameters": parameters
                    }
            
            class MockGenAIAgent:
                def __init__(self):
                    self.tool_registry = MockToolRegistry()
                
                async def process_instruction(self, instruction, context=None):
                    logger.info(f"Mock processing instruction: {instruction}")
                    return {
                        "status": "success",
                        "instruction": instruction,
                        "result": f"Mock result for: {instruction}",
                        "context": context or {}
                    }
                
                async def close(self):
                    logger.info("MockGenAIAgent closed")
                    return True
            
            # Initialize mock services
            redis_bus = MockRedisMessageBus()
            await redis_bus.connect()
            
            agent = MockGenAIAgent()
            
            logger.info("Mock services initialized successfully")
            return True
        else:
            # Normal initialization
            # Load configuration
            config_path = os.path.join(parent_dir, "config.yaml")
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Initialize Redis bus
            redis_config = config.get('redis', {})
            redis_bus = RedisMessageBus(redis_config)
            await redis_bus.connect()
            
            # Initialize agent
            agent = GenAIAgent(config)
            
            logger.info("Services initialized successfully")
            return True
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        return False

# Connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# Routes
@app.get("/")
async def root():
    return {"message": "GenAI Agent 3D API"}

@app.get("/status")
async def get_status():
    """Get system status"""
    global agent, redis_bus
    
    if not agent or not redis_bus:
        initialized = await initialize_services()
        if not initialized:
            return {"status": "error", "message": "Failed to initialize services"}
    
    try:
        # Get Redis status
        redis_status = await redis_bus.ping()
        
        # Get agent status
        agent_status = {
            "initialized": agent is not None,
            "tools": len(agent.tool_registry.get_tools()) if agent else 0
        }
        
        return {
            "status": "ok",
            "agent": agent_status,
            "redis": redis_status,
            "version": "0.1.0"
        }
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/instruction")
async def process_instruction(request: InstructionRequest):
    """Process an instruction"""
    global agent
    
    if not agent:
        initialized = await initialize_services()
        if not initialized:
            return {"status": "error", "message": "Failed to initialize services"}
    
    try:
        result = await agent.process_instruction(request.instruction, request.context)
        return result
    except Exception as e:
        logger.error(f"Error processing instruction: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/tool")
async def execute_tool(request: ToolRequest):
    """Execute a specific tool"""
    global agent
    
    if not agent:
        initialized = await initialize_services()
        if not initialized:
            return {"status": "error", "message": "Failed to initialize services"}
    
    try:
        result = await agent.tool_registry.execute_tool(request.tool_name, request.parameters)
        return result
    except Exception as e:
        logger.error(f"Error executing tool: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/tools")
async def get_tools():
    """Get available tools"""
    global agent
    
    if not agent:
        initialized = await initialize_services()
        if not initialized:
            return {"status": "error", "message": "Failed to initialize services"}
    
    try:
        tools = agent.tool_registry.get_tools()
        tool_info = [
            {
                "name": tool.name,
                "description": tool.description
            } for tool in tools
        ]
        return {"status": "success", "tools": tool_info}
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/config")
async def get_config():
    """Get configuration"""
    try:
        config_path = os.path.join(parent_dir, "config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Remove sensitive information
        if 'llm' in config and 'api_key' in config['llm']:
            config['llm']['api_key'] = '***'
        
        return {"status": "success", "config": config}
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/config")
async def update_config(request: ConfigurationRequest):
    """Update configuration"""
    try:
        config_path = os.path.join(parent_dir, "config.yaml")
        
        # Read existing config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update config
        if request.section not in config:
            config[request.section] = {}
        
        config[request.section][request.key] = request.value
        
        # Write updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for processing"""
    try:
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(parent_dir, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        return {
            "status": "success", 
            "message": "File uploaded successfully",
            "filename": file.filename,
            "path": file_path
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/results/{filename}")
async def get_result_file(filename: str):
    """Get a result file"""
    try:
        # Check file extension
        output_dir = os.path.join(parent_dir, "output")
        
        # Search for the file in subdirectories
        for root, dirs, files in os.walk(output_dir):
            if filename in files:
                file_path = os.path.join(root, filename)
                return FileResponse(file_path)
        
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error getting result file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get('type', '')
            
            if message_type == 'instruction':
                # Process instruction
                instruction = data.get('instruction', '')
                context = data.get('context', {})
                
                # Send acknowledgment
                await manager.send_message({"type": "ack", "message": "Instruction received"}, websocket)
                
                # Process instruction in background
                asyncio.create_task(process_instruction_ws(instruction, context, websocket))
            
            elif message_type == 'tool':
                # Execute tool
                tool_name = data.get('tool_name', '')
                parameters = data.get('parameters', {})
                
                # Send acknowledgment
                await manager.send_message({"type": "ack", "message": "Tool execution request received"}, websocket)
                
                # Execute tool in background
                asyncio.create_task(execute_tool_ws(tool_name, parameters, websocket))
            
            elif message_type == 'ping':
                # Send pong response
                await manager.send_message({"type": "pong"}, websocket)
            
            else:
                # Unknown message type
                await manager.send_message({"type": "error", "message": f"Unknown message type: {message_type}"}, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await manager.send_message({"type": "error", "message": str(e)}, websocket)
        except:
            pass
        manager.disconnect(websocket)

async def process_instruction_ws(instruction: str, context: Dict[str, Any], websocket: WebSocket):
    """Process instruction and send updates via WebSocket"""
    global agent
    
    if not agent:
        initialized = await initialize_services()
        if not initialized:
            await manager.send_message({"type": "error", "message": "Failed to initialize services"}, websocket)
            return
    
    try:
        # Send processing update
        await manager.send_message({"type": "status", "status": "processing", "message": "Processing instruction"}, websocket)
        
        # Process instruction
        result = await agent.process_instruction(instruction, context)
        
        # Send result
        await manager.send_message({"type": "result", "result": result}, websocket)
    except Exception as e:
        logger.error(f"Error processing instruction via WebSocket: {str(e)}")
        await manager.send_message({"type": "error", "message": str(e)}, websocket)

async def execute_tool_ws(tool_name: str, parameters: Dict[str, Any], websocket: WebSocket):
    """Execute tool and send updates via WebSocket"""
    global agent
    
    if not agent:
        initialized = await initialize_services()
        if not initialized:
            await manager.send_message({"type": "error", "message": "Failed to initialize services"}, websocket)
            return
    
    try:
        # Send processing update
        await manager.send_message({"type": "status", "status": "processing", "message": f"Executing tool: {tool_name}"}, websocket)
        
        # Execute tool
        result = await agent.tool_registry.execute_tool(tool_name, parameters)
        
        # Send result
        await manager.send_message({"type": "result", "result": result}, websocket)
    except Exception as e:
        logger.error(f"Error executing tool via WebSocket: {str(e)}")
        await manager.send_message({"type": "error", "message": str(e)}, websocket)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_services()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global agent, redis_bus
    
    if agent:
        await agent.close()
    
    if redis_bus:
        await redis_bus.disconnect()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
