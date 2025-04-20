"""
FastAPI backend for GenAI Agent 3D with direct route handling
This version includes direct API routes for Blender script execution
"""

import os
import sys
import yaml
import logging
import asyncio
import subprocess
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, File, UploadFile, Form, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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

# Define output directories
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# Ensure output directories exist
for subdir in ["", "models", "scenes", "diagrams", "tools", "temp"]:
    dir_path = os.path.join(BASE_OUTPUT_DIR, subdir)
    if not os.path.exists(dir_path):
        logger.info(f"Creating directory: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)

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

class BlenderExecuteRequest(BaseModel):
    script_path: str
    show_ui: bool = False

# For demo purposes, include a mock agent
class MockGenAIAgent:
    async def process_instruction(self, instruction, context=None):
        return {
            "status": "success",
            "instruction": instruction,
            "result": f"Mock result for: {instruction}",
            "context": context or {}
        }
    
    class ToolRegistry:
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
    
    def __init__(self):
        self.tool_registry = self.ToolRegistry()

# Initialize mock agent for demo
agent = MockGenAIAgent()

# Routes
@app.get("/")
async def root():
    return {"message": "GenAI Agent 3D API"}

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "ok",
        "agent": {
            "initialized": True,
            "tools": len(agent.tool_registry.get_tools()) if agent else 0
        },
        "base_output_dir": BASE_OUTPUT_DIR,
        "version": "0.1.0"
    }

@app.post("/instruction")
async def process_instruction(request: InstructionRequest):
    """Process an instruction"""
    try:
        result = await agent.process_instruction(request.instruction, request.context)
        return result
    except Exception as e:
        logger.error(f"Error processing instruction: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/tool")
async def execute_tool(request: ToolRequest):
    """Execute a specific tool"""
    try:
        result = await agent.tool_registry.execute_tool(request.tool_name, request.parameters)
        return result
    except Exception as e:
        logger.error(f"Error executing tool: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/tools")
async def get_tools():
    """Get available tools"""
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

# ====== DIRECT BLENDER SCRIPT API ROUTES ======

@app.get("/blender/list-scripts/{folder:path}")
async def list_blender_scripts(folder: str = ""):
    """List available Blender scripts in the output directory"""
    # Build the path
    logger.info(f"Listing scripts in folder: {folder}")
    
    directory = os.path.join(BASE_OUTPUT_DIR, folder)
    abs_directory = os.path.abspath(directory)
    
    logger.info(f"Directory: {directory}")
    logger.info(f"Absolute directory: {abs_directory}")
    
    # Security check
    if not abs_directory.startswith(BASE_OUTPUT_DIR):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    # Check if the directory exists
    if not os.path.exists(abs_directory):
        # Try to create it
        try:
            os.makedirs(abs_directory, exist_ok=True)
            logger.info(f"Created directory: {abs_directory}")
        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating directory: {str(e)}")
    
    if not os.path.isdir(abs_directory):
        raise HTTPException(status_code=404, detail=f"Path is not a directory: {folder}")
    
    # List all Python files in the directory
    scripts = []
    try:
        items = os.listdir(abs_directory)
        
        for filename in items:
            file_path = os.path.join(abs_directory, filename)
            if os.path.isfile(file_path) and filename.endswith('.py'):
                # Get relative path from BASE_OUTPUT_DIR
                rel_path = os.path.relpath(file_path, BASE_OUTPUT_DIR)
                script_info = {
                    "name": filename,
                    "path": rel_path.replace('\\', '/'),  # Use forward slashes for consistency
                    "full_path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path)
                }
                scripts.append(script_info)
    except Exception as e:
        logger.error(f"Error listing directory: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading directory: {str(e)}")
    
    return {
        "directory": folder,
        "scripts": scripts
    }

@app.post("/blender/execute")
async def execute_blender_script(request: BlenderExecuteRequest):
    """Execute a Blender script"""
    try:
        logger.info(f"Executing script: {request.script_path}")
        
        # Construct the full path to the script
        script_path = os.path.join(BASE_OUTPUT_DIR, request.script_path)
        abs_script_path = os.path.abspath(script_path)
        
        # Security check
        if not abs_script_path.startswith(BASE_OUTPUT_DIR):
            raise HTTPException(status_code=400, detail="Invalid script path")
        
        # Check if the script exists
        if not os.path.exists(abs_script_path):
            raise HTTPException(status_code=404, detail=f"Script not found: {request.script_path}")
        
        # For demo, just return a success message
        execution_id = f"exec_{abs_script_path.replace(':', '').replace('\\', '_').replace('/', '_')}"
        
        return {
            "status": "queued",
            "message": f"Script execution queued",
            "execution_id": execution_id,
            "script_path": request.script_path,
            "show_ui": request.show_ui
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing script: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing script: {str(e)}")

@app.get("/blender/status/{execution_id}")
async def get_blender_execution_status(execution_id: str):
    """Get the status of a Blender script execution"""
    # For demo, just return a success message
    return {
        "status": "completed",
        "execution_id": execution_id,
        "message": "Script executed successfully (mock)"
    }

@app.get("/blender/output/{execution_id}")
async def get_blender_execution_output(execution_id: str):
    """Get the output of a Blender script execution"""
    # For demo, just return a sample output
    return {
        "execution_id": execution_id,
        "output": "Example output from Blender script execution.\nThis is a mock response."
    }

# ====== DEBUG API ROUTES ======

@app.get("/debug/paths")
async def debug_paths():
    """Debug endpoint to check directory paths"""
    try:
        # Check required directories
        required_dirs = [
            BASE_OUTPUT_DIR,
            os.path.join(BASE_OUTPUT_DIR, "models"),
            os.path.join(BASE_OUTPUT_DIR, "scenes"),
            os.path.join(BASE_OUTPUT_DIR, "diagrams"),
            os.path.join(BASE_OUTPUT_DIR, "tools"),
            os.path.join(BASE_OUTPUT_DIR, "temp")
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Created missing directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {e}")
        
        # Check for scripts in each directory
        scripts = {}
        for dir_path in required_dirs:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                dir_name = os.path.basename(dir_path)
                script_files = []
                
                try:
                    for filename in os.listdir(dir_path):
                        if filename.endswith('.py'):
                            file_path = os.path.join(dir_path, filename)
                            script_files.append({
                                "name": filename,
                                "path": os.path.relpath(file_path, BASE_OUTPUT_DIR).replace('\\', '/'),
                                "size": os.path.getsize(file_path),
                                "modified": os.path.getmtime(file_path)
                            })
                except Exception as e:
                    scripts[dir_name] = {"error": str(e)}
                    continue
                
                scripts[dir_name] = script_files
        
        # Create example scripts if needed
        models_dir = os.path.join(BASE_OUTPUT_DIR, "models")
        scenes_dir = os.path.join(BASE_OUTPUT_DIR, "scenes")
        
        if os.path.exists(models_dir) and len(os.listdir(models_dir)) == 0:
            logger.info("Creating example scripts in models directory")
            # Create example cube script
            cube_script = """import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "Example_Cube"

# Create a material
mat = bpy.data.materials.new(name="CubeMaterial")
mat.diffuse_color = (1.0, 0.0, 0.0, 1.0)  # Red
cube.data.materials.append(mat)

print("Example cube created successfully!")
"""
            with open(os.path.join(models_dir, "example_cube.py"), "w") as f:
                f.write(cube_script)
        
        if os.path.exists(scenes_dir) and len(os.listdir(scenes_dir)) == 0:
            logger.info("Creating example scripts in scenes directory")
            # Create example scene script
            scene_script = """import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Ground"

# Create a material for the ground
mat_ground = bpy.data.materials.new(name="GroundMaterial")
mat_ground.diffuse_color = (0.2, 0.5, 0.2, 1.0)  # Green
plane.data.materials.append(mat_ground)

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "Building"

print("Example scene created successfully!")
"""
            with open(os.path.join(scenes_dir, "example_scene.py"), "w") as f:
                f.write(scene_script)
        
        return {
            "status": "ok",
            "script_dir": SCRIPT_DIR,
            "base_output_dir": BASE_OUTPUT_DIR,
            "required_directories": required_dirs,
            "missing_directories": missing_dirs,
            "scripts": scripts,
            "current_working_directory": os.getcwd()
        }
    except Exception as e:
        logger.error(f"Error in debug_paths: {e}")
        return {
            "status": "error",
            "message": str(e),
            "script_dir": SCRIPT_DIR,
            "base_output_dir": BASE_OUTPUT_DIR,
            "current_working_directory": os.getcwd()
        }

@app.get("/debug/check-path")
async def check_path(path: str):
    """Check if a specific path exists and get information about it"""
    try:
        # Construct the absolute path
        rel_path = path.lstrip("/").replace("/", os.sep)
        abs_path = os.path.abspath(os.path.join(BASE_OUTPUT_DIR, rel_path))
        
        # Security check
        if not abs_path.startswith(BASE_OUTPUT_DIR):
            raise HTTPException(status_code=400, detail="Invalid path: Access outside of base directory is not allowed")
        
        result = {
            "exists": os.path.exists(abs_path),
            "path": path,
            "abs_path": abs_path
        }
        
        if not result["exists"]:
            return result
        
        # Get file/directory info
        result["is_file"] = os.path.isfile(abs_path)
        result["is_dir"] = os.path.isdir(abs_path)
        result["is_python"] = path.endswith('.py')
        result["size"] = os.path.getsize(abs_path) if result["is_file"] else None
        
        # Get permissions
        result["permissions"] = {
            "read": os.access(abs_path, os.R_OK),
            "write": os.access(abs_path, os.W_OK),
            "execute": os.access(abs_path, os.X_OK)
        }
        
        # If it's a Python file, get content for inspection
        if result["is_file"] and result["is_python"] and result["size"] and result["size"] < 102400:  # Limit to 100KB
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    result["content"] = f.read()
            except Exception as e:
                result["error"] = f"Failed to read file content: {str(e)}"
        
        # If it's a directory, list contents
        if result["is_dir"]:
            try:
                contents = os.listdir(abs_path)
                result["contents"] = {
                    "items": contents,
                    "count": len(contents),
                    "files": [f for f in contents if os.path.isfile(os.path.join(abs_path, f))],
                    "directories": [d for d in contents if os.path.isdir(os.path.join(abs_path, d))]
                }
            except Exception as e:
                result["error"] = f"Failed to list directory contents: {str(e)}"
                
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking path: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking path: {str(e)}")

@app.post("/debug/run-script")
async def run_debug_script(script_name: str = "debug_paths.py"):
    """Run a debug script"""
    try:
        # Validate script name for security
        if '..' in script_name or '/' in script_name or '\\' in script_name:
            raise HTTPException(status_code=400, detail="Invalid script name")
        
        # Only allow specific debug scripts
        allowed_scripts = ['debug_paths.py', 'fix_directories.py']
        if script_name not in allowed_scripts:
            raise HTTPException(status_code=400, detail=f"Script not allowed. Allowed scripts: {', '.join(allowed_scripts)}")
        
        # Construct the script path
        script_path = os.path.join(SCRIPT_DIR, script_name)
        
        # Check if the script exists
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail=f"Script not found: {script_name}")
        
        # Run the script and capture output
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=SCRIPT_DIR
        )
        
        stdout, stderr = process.communicate(timeout=60)  # 60-second timeout
        
        # Check the return code
        if process.returncode != 0:
            return {
                "success": False,
                "output": stdout,
                "error": f"Script failed with exit code {process.returncode}. Error: {stderr}"
            }
        
        return {
            "success": True,
            "output": stdout
        }
    except subprocess.TimeoutExpired:
        process.kill()
        raise HTTPException(status_code=500, detail="Script execution timed out")
    except Exception as e:
        logger.error(f"Error executing script: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing script: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_direct:app", host="0.0.0.0", port=8000, reload=True)
