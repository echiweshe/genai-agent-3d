"""
API Routes for SVG to Video Pipeline

This module defines the API routes for the SVG to Video pipeline.
"""

import os
import json
import tempfile
import uuid
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Body, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

from genai_agent.svg_to_video.llm_integrations.llm_factory import LLMFactory
from genai_agent.svg_to_video.pipeline import SVGToVideoPipeline
from genai_agent.svg_to_video.utils import save_uploaded_file, ensure_directory_exists

# Import port configurations
import sys
import os
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "ports.json")
try:
    with open(config_path, "r") as f:
        ports_config = json.load(f)
except Exception as e:
    print(f"Warning: Could not load port configuration: {e}")
    ports_config = {"services": {"svg_to_video_backend": 8001}}

# Load the port for the SVG to Video backend
SVG_VIDEO_PORT = ports_config.get("services", {}).get("svg_to_video_backend", 8001)

# Create router
router = APIRouter(prefix="/api/svg-to-video")

# Initialize LLM factory
llm_factory = LLMFactory()

# Create a task manager to keep track of running tasks
task_manager = {}

# Create pipeline
pipeline = SVGToVideoPipeline()

# Model definitions
class GenerateSVGRequest(BaseModel):
    concept: str
    provider: str = "claude"
    model: Optional[str] = None
    style: Optional[str] = None

class ConvertSVGRequest(BaseModel):
    svg_content: str
    animation_type: str = "standard"
    quality: str = "medium"

class GenerateVideoRequest(BaseModel):
    concept: str
    provider: str = "claude"
    model: Optional[str] = None
    style: Optional[str] = None
    animation_type: str = "standard"
    quality: str = "medium"

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float = 0.0
    result: Optional[str] = None
    error: Optional[str] = None

# Routes
@router.get("/providers")
async def get_providers() -> List[Dict[str, Any]]:
    """Get a list of available LLM providers."""
    return llm_factory.get_providers()

@router.post("/generate-svg")
async def generate_svg(
    request: Union[GenerateSVGRequest, None] = None,
    concept: str = Form(None),
    provider: str = Form("claude"),
    model: Optional[str] = Form(None),
    style: Optional[str] = Form(None)
) -> Dict[str, str]:
    """
    Generate an SVG diagram from a concept.
    
    Accepts either a JSON request body or form data.
    """
    # Handle both JSON and form data
    if request is not None:
        concept = request.concept
        provider = request.provider
        model = request.model
        style = request.style
    elif concept is None:
        raise HTTPException(status_code=400, detail="Concept is required")
    
    try:
        svg_content = llm_factory.generate_svg(provider, concept, model, style)
        
        # Create a temporary file for the SVG
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")
        ensure_directory_exists(output_dir)
        
        file_id = str(uuid.uuid4())
        svg_file = os.path.join(output_dir, f"{file_id}.svg")
        
        # Save the SVG
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        return {
            "svg_content": svg_content,
            "file_id": file_id,
            "file_path": svg_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert-svg")
async def convert_svg(
    svg_file: Optional[UploadFile] = File(None),
    svg_content: Optional[str] = Form(None),
    animation_type: str = Form("standard"),
    quality: str = Form("medium")
) -> Dict[str, str]:
    """
    Convert an SVG file to a video.
    
    Accepts either an uploaded SVG file or SVG content as form data.
    """
    try:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")
        ensure_directory_exists(output_dir)
        
        # Generate unique IDs for input and output files
        file_id = str(uuid.uuid4())
        
        # Handle uploaded file or content
        if svg_file:
            svg_path = os.path.join(output_dir, f"{file_id}.svg")
            save_uploaded_file(svg_file, svg_path)
        elif svg_content:
            svg_path = os.path.join(output_dir, f"{file_id}.svg")
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
        else:
            raise HTTPException(status_code=400, detail="Either svg_file or svg_content must be provided")
        
        # Create a task ID
        task_id = str(uuid.uuid4())
        
        # Start conversion in a background task
        output_path = os.path.join(output_dir, f"{file_id}.mp4")
        task_manager[task_id] = {
            "status": "pending",
            "progress": 0.0,
            "result": None,
            "error": None
        }
        
        # Start a background task to convert SVG to video
        # For now, just update the task status
        # In a real implementation, this would start a background task
        task_manager[task_id]["status"] = "processing"
        
        # Run the pipeline
        try:
            pipeline.convert_svg_to_video(svg_path, output_path, animation_type, quality)
            task_manager[task_id]["status"] = "completed"
            task_manager[task_id]["progress"] = 1.0
            task_manager[task_id]["result"] = output_path
        except Exception as e:
            task_manager[task_id]["status"] = "failed"
            task_manager[task_id]["error"] = str(e)
            raise
        
        return {
            "task_id": task_id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-video")
async def generate_video(
    request: Union[GenerateVideoRequest, None] = None,
    concept: str = Form(None),
    provider: str = Form("claude"),
    model: Optional[str] = Form(None),
    style: Optional[str] = Form(None),
    animation_type: str = Form("standard"),
    quality: str = Form("medium")
) -> Dict[str, str]:
    """
    Generate a video from a concept description.
    
    Accepts either a JSON request body or form data.
    """
    # Handle both JSON and form data
    if request is not None:
        concept = request.concept
        provider = request.provider
        model = request.model
        style = request.style
        animation_type = request.animation_type
        quality = request.quality
    elif concept is None:
        raise HTTPException(status_code=400, detail="Concept is required")
    
    try:
        # Generate SVG
        svg_content = llm_factory.generate_svg(provider, concept, model, style)
        
        # Create temporary files
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")
        ensure_directory_exists(output_dir)
        
        file_id = str(uuid.uuid4())
        svg_path = os.path.join(output_dir, f"{file_id}.svg")
        output_path = os.path.join(output_dir, f"{file_id}.mp4")
        
        # Save the SVG
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        # Create a task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        task_manager[task_id] = {
            "status": "pending",
            "progress": 0.0,
            "result": None,
            "error": None
        }
        
        # Start a background task to convert SVG to video
        # For now, just update the task status
        # In a real implementation, this would start a background task
        task_manager[task_id]["status"] = "processing"
        
        # Run the pipeline
        try:
            pipeline.convert_svg_to_video(svg_path, output_path, animation_type, quality)
            task_manager[task_id]["status"] = "completed"
            task_manager[task_id]["progress"] = 1.0
            task_manager[task_id]["result"] = output_path
        except Exception as e:
            task_manager[task_id]["status"] = "failed"
            task_manager[task_id]["error"] = str(e)
            raise
        
        return {
            "task_id": task_id,
            "status": "processing",
            "svg_content": svg_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}")
async def get_task_status(task_id: str) -> TaskStatus:
    """Get the status of a task."""
    if task_id not in task_manager:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task = task_manager[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        result=task["result"],
        error=task["error"]
    )

@router.get("/download/{file_id}")
async def download_file(file_id: str) -> FileResponse:
    """Download a generated file."""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs")
    
    # Check for video file
    video_path = os.path.join(output_dir, f"{file_id}.mp4")
    if os.path.exists(video_path):
        return FileResponse(video_path, media_type="video/mp4", filename=f"{file_id}.mp4")
    
    # Check for SVG file
    svg_path = os.path.join(output_dir, f"{file_id}.svg")
    if os.path.exists(svg_path):
        return FileResponse(svg_path, media_type="image/svg+xml", filename=f"{file_id}.svg")
    
    raise HTTPException(status_code=404, detail=f"File {file_id} not found")
