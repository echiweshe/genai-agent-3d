"""
FastAPI backend for GenAI Agent 3D
"""

import os
import sys
import yaml
import logging
import asyncio
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

# Add project root to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)
    logger.info(f"Added project root to Python path: {project_root}")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import routes
from genai_agent.services.llm_api_routes import add_llm_routes
from genai_agent.services.settings_api import add_settings_routes
try:
    from routes.blender_routes import router as blender_routes_router
    logger.info("Blender routes loaded")
except ImportError as e:
    logger.warning(f"Blender routes not loaded: {e}")
    blender_routes_router = None

try:
    from routes.blender_integration_routes import router as blender_integration_router
    logger.info("Blender integration routes loaded")
except ImportError as e:
    logger.warning(f"Blender integration routes not loaded: {e}")
    blender_integration_router = None

try:
    from routes.debug_routes import router as debug_router
except ImportError as e:
    logger.warning(f"Debug routes not loaded: {e}")
    debug_router = None

try:
    from routes.svg_generator_routes import router as svg_generator_router
    logger.info("SVG Generator routes loaded")
except ImportError as e:
    logger.warning(f"SVG Generator routes not loaded: {e}")
    svg_generator_router = None

# Import the new SVG to 3D routes
try:
    from routes.svg_to_3d_routes import router as svg_to_3d_router
    logger.info("SVG to 3D routes loaded")
except ImportError as e:
    logger.warning(f"SVG to 3D routes not loaded: {e}")
    svg_to_3d_router = None

# Import the new SVG import routes
try:
    from routes.svg_import_routes import router as svg_import_router
    logger.info("SVG import routes loaded")
except ImportError as e:
    logger.warning(f"SVG import routes not loaded: {e}")
    svg_import_router = None

# Import GenAI Agent 3D components
from genai_agent.agent import GenAIAgent
from genai_agent.services.redis_bus import RedisMessageBus

# Create FastAPI app
app = FastAPI(
    title="GenAI Agent 3D API",
    description="API for interacting with the GenAI Agent 3D system",
    version="0.1.0"
)

# Determine root output directory for static files
output_dir = None
config_path = os.path.join(parent_dir, "config.yaml")
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            output_dir = config.get('paths', {}).get('output_dir')
            logger.info(f"Using output directory from config: {output_dir}")
        except Exception as e:
            logger.warning(f"Error loading output directory from config: {e}")

# Add LLM routes
add_llm_routes(app)
add_settings_routes(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving output files
if output_dir and os.path.exists(output_dir):
    app.mount("/output", StaticFiles(directory=output_dir), name="output")
    logger.info(f"Mounted output directory: {output_dir} at /output")
else:
    # If output_dir from config not found, try using the output directory relative to the parent directory
    fallback_output_dir = os.path.join(parent_dir, "output")
    if os.path.exists(fallback_output_dir):
        app.mount("/output", StaticFiles(directory=fallback_output_dir), name="output")
        logger.info(f"Mounted fallback output directory: {fallback_output_dir} at /output")
    else:
        logger.warning("No valid output directory found to mount for static file serving")

# Include routers
if blender_routes_router:
    app.include_router(blender_routes_router)

if blender_integration_router:
    app.include_router(blender_integration_router)

if debug_router:
    app.include_router(debug_router)
    
if svg_generator_router:
    app.include_router(svg_generator_router)

# Include the new SVG to 3D routes
if svg_to_3d_router:
    app.include_router(svg_to_3d_router)

# Include the new SVG import routes
if svg_import_router:
    app.include_router(svg_import_router)

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

@app.get("/models")
async def get_models():
    """Get available models - direct handler for frontend compatibility"""
    try:
        # Define output directories
        output_dir = os.path.join(parent_dir, "output")
        models_dir = os.path.join(output_dir, "models")
        
        # Ensure the directory exists
        os.makedirs(models_dir, exist_ok=True)
        
        # Look for .blend files in the models directory
        models = []
        for root, dirs, files in os.walk(models_dir):
            for file in files:
                if file.endswith('.blend') or file.endswith('.py'):
                    model_path = os.path.join(root, file)
                    rel_path = os.path.relpath(model_path, output_dir)
                    models.append({
                        "id": os.path.splitext(file)[0],
                        "name": file,
                        "path": rel_path,
                        "size": os.path.getsize(model_path),
                        "modified": os.path.getmtime(model_path)
                    })
        
        # For compatibility, return the same format as the frontend expects
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return {"status": "error", "message": str(e), "models": []}

@app.get("/diagrams")
async def get_diagrams():
    """Get available diagrams - direct handler for frontend compatibility"""
    try:
        # Define output directories
        output_dir = os.path.join(parent_dir, "output")
        diagrams_dir = os.path.join(output_dir, "diagrams")
        
        # Ensure the directory exists
        os.makedirs(diagrams_dir, exist_ok=True)
        
        # Look for diagram files in the diagrams directory
        diagrams = []
        for root, dirs, files in os.walk(diagrams_dir):
            for file in files:
                if file.endswith('.blend') or file.endswith('.py') or file.endswith('.svg') or file.endswith('.png'):
                    diagram_path = os.path.join(root, file)
                    rel_path = os.path.relpath(diagram_path, output_dir)
                    diagrams.append({
                        "id": os.path.splitext(file)[0],
                        "name": file,
                        "path": rel_path,
                        "size": os.path.getsize(diagram_path),
                        "modified": os.path.getmtime(diagram_path)
                    })
        
        # For compatibility, return the same format as the frontend expects
        return {"diagrams": diagrams}
    except Exception as e:
        logger.error(f"Error getting diagrams: {str(e)}")
        return {"status": "error", "message": str(e), "diagrams": []}

@app.get("/scenes")
async def get_scenes():
    """Get available scenes - direct handler for frontend compatibility"""
    try:
        # Define output directories
        output_dir = os.path.join(parent_dir, "output")
        scenes_dir = os.path.join(output_dir, "scenes")
        
        # Ensure the directory exists
        os.makedirs(scenes_dir, exist_ok=True)
        
        # Look for scene files in the scenes directory
        scenes = []
        for root, dirs, files in os.walk(scenes_dir):
            for file in files:
                if file.endswith('.blend') or file.endswith('.py'):
                    scene_path = os.path.join(root, file)
                    rel_path = os.path.relpath(scene_path, output_dir)
                    scenes.append({
                        "id": os.path.splitext(file)[0],
                        "name": file,
                        "path": rel_path,
                        "size": os.path.getsize(scene_path),
                        "modified": os.path.getmtime(scene_path)
                    })
        
        # For compatibility, return the same format as the frontend expects
        return {"scenes": scenes}
    except Exception as e:
        logger.error(f"Error getting scenes: {str(e)}")
        return {"status": "error", "message": str(e), "scenes": []}

@app.get("/blender-tools")
async def get_blender_tools():
    """Get available Blender tools - direct handler for frontend compatibility"""
    try:
        # Define output directories
        output_dir = os.path.join(parent_dir, "output")
        tools_dir = os.path.join(output_dir, "tools")
        
        # Ensure the directory exists
        os.makedirs(tools_dir, exist_ok=True)
        
        # Look for tool files in the tools directory
        tools = []
        for root, dirs, files in os.walk(tools_dir):
            for file in files:
                if file.endswith('.py'):
                    tool_path = os.path.join(root, file)
                    rel_path = os.path.relpath(tool_path, output_dir)
                    tools.append({
                        "id": os.path.splitext(file)[0],
                        "name": file,
                        "path": rel_path,
                        "size": os.path.getsize(tool_path),
                        "modified": os.path.getmtime(tool_path)
                    })
        
        # For compatibility, return the same format as the frontend expects
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Error getting Blender tools: {str(e)}")
        return {"status": "error", "message": str(e), "tools": []}

@app.get("/results/{filename}")
async def get_result_file(filename: str):
    try:
        # Get output directory from config
        config_path = os.path.join(parent_dir, "config.yaml")
        output_dir = None
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                    output_dir = config.get('paths', {}).get('output_dir')
                except Exception as e:
                    logger.warning(f"Error loading output directory from config: {e}")
        
        # Fallback to default if not found in config
        if not output_dir or not os.path.exists(output_dir):
            output_dir = os.path.join(parent_dir, "output")
        
        logger.info(f"Searching for {filename} in {output_dir}")
        
        # Search for the file in subdirectories
        for root, dirs, files in os.walk(output_dir):
            if filename in files:
                file_path = os.path.join(root, filename)
                logger.info(f"Found file at {file_path}")
                return FileResponse(file_path)
        
        # If file not found in output directory, check relative paths like 'models/filename'
        if '/' in filename:
            parts = filename.split('/')
            subdir = parts[0]
            file_name = parts[-1]
            
            # Check in appropriate subdirectory
            subdir_path = os.path.join(output_dir, subdir)
            if os.path.exists(subdir_path):
                for root, dirs, files in os.walk(subdir_path):
                    if file_name in files:
                        file_path = os.path.join(root, file_name)
                        logger.info(f"Found file at {file_path}")
                        return FileResponse(file_path)
        
        # If still not found, give more detailed error
        logger.warning(f"File not found: {filename} in {output_dir}")
        # List available files for debugging
        available_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                available_files.append(os.path.join(os.path.relpath(root, output_dir), file))
        
        logger.info(f"Available files: {available_files[:10]}" + ("..." if len(available_files) > 10 else ""))
        
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    except HTTPException:
        raise
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

@app.get("/api/health")
async def health_check():
    """Health check endpoint for service monitoring"""
    return {"status": "ok", "message": "Service is healthy"}
