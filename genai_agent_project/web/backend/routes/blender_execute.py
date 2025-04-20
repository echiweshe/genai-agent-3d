"""
API routes for executing Blender scripts
"""
import os
import sys
import uuid
import subprocess
import tempfile
import asyncio
from typing import Dict, Optional, List
from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, Depends
from pydantic import BaseModel

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import necessary modules
try:
    from web.backend.websocket_manager import WebSocketManager
except ImportError:
    # Try alternative paths
    try:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from websocket_manager import WebSocketManager
    except ImportError:
        print("Warning: WebSocketManager import failed. Real-time updates will be disabled.")
        # Define a mock WebSocketManager if import fails
        class WebSocketManager:
            async def connect(self, websocket): pass
            async def disconnect(self, websocket): pass
            async def broadcast(self, message): pass

# Create router
router = APIRouter()

# WebSocket manager for real-time updates
ws_manager = WebSocketManager()

# Path to output directory
BASE_OUTPUT_DIR = os.path.join(project_root, "output")

# Dictionary to store script execution status
script_executions = {}

class BlenderScriptRequest(BaseModel):
    """Request model for executing a Blender script"""
    script_path: str
    show_ui: bool = False

class BlenderScriptResponse(BaseModel):
    """Response model for a Blender script execution request"""
    execution_id: str
    status: str
    message: str

def create_blender_wrapper(script_path):
    """Create a wrapper script that properly executes a Blender script"""
    # Get absolute path to the script
    abs_script_path = os.path.abspath(script_path)
    
    # Create a temporary wrapper script
    wrapper_content = f"""
import bpy
import sys
import os

# Ensure the script directory is in the path
script_dir = os.path.dirname(r"{abs_script_path}")
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Load and execute the script content
try:
    print(f"\\n{'='*80}")
    print(f"EXECUTING SCRIPT: {abs_script_path}")
    print(f"{'='*80}\\n")
    
    with open(r"{abs_script_path}", 'r') as f:
        script_content = f.read()
    
    # Execute the script in Blender's environment
    exec(script_content)
    
    print(f"\\n{'='*80}")
    print(f"SCRIPT EXECUTION COMPLETED SUCCESSFULLY")
    print(f"{'='*80}\\n")
except Exception as e:
    print(f"\\n{'='*80}")
    print(f"ERROR EXECUTING SCRIPT: {{e}}")
    print(f"{'='*80}\\n")
    raise
"""
    
    # Write wrapper to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(wrapper_content)
        wrapper_path = f.name
    
    return wrapper_path

def find_blender_executable():
    """Find the Blender executable"""
    if sys.platform == "win32":
        # Look for Blender in common Windows locations
        common_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender\blender.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return "blender"  # Hope it's in the PATH
    elif sys.platform == "darwin":  # macOS
        common_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/Applications/Blender/Blender.app/Contents/MacOS/Blender"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return "blender"  # Hope it's in the PATH
    else:  # Linux
        return "blender"  # Use system Blender

async def run_blender_script_task(script_path, execution_id, show_ui=False):
    """Background task to run a Blender script"""
    try:
        # Update status to running
        script_executions[execution_id] = {
            "status": "running",
            "message": "Script execution in progress",
            "output": []
        }
        
        # Notify connected clients
        await ws_manager.broadcast({"type": "blender_script_update", "data": {
            "execution_id": execution_id,
            "status": "running",
            "message": "Script execution in progress"
        }})
        
        # Find Blender executable
        blender_path = find_blender_executable()
        
        # Create wrapper script
        wrapper_path = create_blender_wrapper(script_path)
        
        try:
            # Build Blender command
            cmd = [blender_path]
            if not show_ui:
                cmd.append("--background")
            cmd.extend(["--python", wrapper_path])
            
            # Update status with command
            script_executions[execution_id]["message"] = f"Running command: {' '.join(cmd)}"
            await ws_manager.broadcast({"type": "blender_script_update", "data": {
                "execution_id": execution_id,
                "status": "running",
                "message": script_executions[execution_id]["message"]
            }})
            
            # Run the process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            # Stream the output
            output_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                line_text = line.decode('utf-8', errors='replace')
                print(line_text, end='')
                output_lines.append(line_text)
                
                # Store output
                script_executions[execution_id]["output"] = output_lines
                
                # Send updates via WebSocket
                await ws_manager.broadcast({"type": "blender_script_output", "data": {
                    "execution_id": execution_id,
                    "line": line_text
                }})
            
            # Wait for completion
            await process.wait()
            
            if process.returncode == 0:
                script_executions[execution_id]["status"] = "completed"
                script_executions[execution_id]["message"] = "Script execution completed successfully"
            else:
                script_executions[execution_id]["status"] = "failed"
                script_executions[execution_id]["message"] = f"Script execution failed with exit code: {process.returncode}"
            
            # Notify connected clients
            await ws_manager.broadcast({"type": "blender_script_update", "data": {
                "execution_id": execution_id,
                "status": script_executions[execution_id]["status"],
                "message": script_executions[execution_id]["message"]
            }})
            
        finally:
            # Clean up the temporary wrapper
            if os.path.exists(wrapper_path):
                try:
                    os.remove(wrapper_path)
                except:
                    pass
                    
    except Exception as e:
        # Update status to failed
        script_executions[execution_id] = {
            "status": "failed",
            "message": f"Error: {str(e)}",
            "output": []
        }
        
        # Notify connected clients
        await ws_manager.broadcast({"type": "blender_script_update", "data": {
            "execution_id": execution_id,
            "status": "failed",
            "message": f"Error: {str(e)}"
        }})

@router.post("/blender/execute", response_model=BlenderScriptResponse)
async def execute_blender_script(request: BlenderScriptRequest, background_tasks: BackgroundTasks):
    """Execute a Blender script and return the execution ID"""
    # Validate the script path
    script_path = request.script_path
    
    # Handle both absolute and relative paths
    if not os.path.isabs(script_path):
        script_path = os.path.join(BASE_OUTPUT_DIR, script_path)
    
    # Security check - make sure the script is within the output directory
    abs_script_path = os.path.abspath(script_path)
    if not abs_script_path.startswith(BASE_OUTPUT_DIR):
        raise HTTPException(status_code=400, detail="Invalid script path. Must be within the output directory.")
    
    # Check if the script exists
    if not os.path.exists(abs_script_path):
        raise HTTPException(status_code=404, detail=f"Script not found: {abs_script_path}")
    
    # Create a unique ID for this execution
    execution_id = str(uuid.uuid4())
    
    # Initialize the execution status
    script_executions[execution_id] = {
        "status": "queued",
        "message": "Script execution queued",
        "output": []
    }
    
    # Start the execution in a background task
    background_tasks.add_task(
        run_blender_script_task, 
        abs_script_path, 
        execution_id,
        request.show_ui
    )
    
    return BlenderScriptResponse(
        execution_id=execution_id,
        status="queued",
        message="Script execution queued"
    )

@router.get("/blender/status/{execution_id}")
async def get_blender_script_status(execution_id: str):
    """Get the status of a Blender script execution"""
    if execution_id not in script_executions:
        raise HTTPException(status_code=404, detail=f"Execution ID not found: {execution_id}")
    
    return {
        "execution_id": execution_id,
        "status": script_executions[execution_id]["status"],
        "message": script_executions[execution_id]["message"]
    }

@router.get("/blender/output/{execution_id}")
async def get_blender_script_output(execution_id: str):
    """Get the output of a Blender script execution"""
    if execution_id not in script_executions:
        raise HTTPException(status_code=404, detail=f"Execution ID not found: {execution_id}")
    
    return {
        "execution_id": execution_id,
        "status": script_executions[execution_id]["status"],
        "message": script_executions[execution_id]["message"],
        "output": "".join(script_executions[execution_id]["output"])
    }

@router.websocket("/ws/blender/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for real-time updates on script execution"""
    await ws_manager.connect(websocket)
    
    try:
        # Send initial status if the execution exists
        if execution_id in script_executions:
            await websocket.send_json({
                "type": "blender_script_status",
                "data": {
                    "execution_id": execution_id,
                    "status": script_executions[execution_id]["status"],
                    "message": script_executions[execution_id]["message"]
                }
            })
            
            # Send existing output
            if script_executions[execution_id]["output"]:
                await websocket.send_json({
                    "type": "blender_script_full_output",
                    "data": {
                        "execution_id": execution_id,
                        "output": "".join(script_executions[execution_id]["output"])
                    }
                })
        
        # Keep the connection open until client disconnects
        while True:
            await asyncio.sleep(1)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        await ws_manager.disconnect(websocket)

@router.get("/blender/list-scripts/{folder:path}")
async def list_blender_scripts(folder: str = ""):
    """List available Blender scripts in the output directory"""
    # Build the path
    directory = os.path.join(BASE_OUTPUT_DIR, folder)
    
    # Security check
    abs_directory = os.path.abspath(directory)
    if not abs_directory.startswith(BASE_OUTPUT_DIR):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    # Check if the directory exists
    if not os.path.exists(abs_directory) or not os.path.isdir(abs_directory):
        raise HTTPException(status_code=404, detail=f"Directory not found: {folder}")
    
    # List all Python files in the directory
    scripts = []
    for filename in os.listdir(abs_directory):
        file_path = os.path.join(abs_directory, filename)
        if os.path.isfile(file_path) and filename.endswith('.py'):
            # Get relative path from BASE_OUTPUT_DIR
            rel_path = os.path.relpath(file_path, BASE_OUTPUT_DIR)
            scripts.append({
                "name": filename,
                "path": rel_path.replace('\\', '/'),  # Use forward slashes for consistency
                "full_path": file_path,
                "size": os.path.getsize(file_path),
                "modified": os.path.getmtime(file_path)
            })
    
    return {
        "directory": folder,
        "scripts": scripts
    }
