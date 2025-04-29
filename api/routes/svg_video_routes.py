"""
SVG to Video API Routes

This module provides FastAPI routes for the SVG to Video pipeline.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Body
from pydantic import BaseModel
from pathlib import Path

# Import the pipeline
from genai_agent.svg_to_video.pipeline import SVGToVideoPipeline
from genai_agent.svg_to_video.utils import validate_svg, create_temp_file

# Configure logging
logger = logging.getLogger("svg_video_api")

# Create router
router = APIRouter(prefix="/api/svg-to-video", tags=["SVG to Video"])

# Create pipeline instance
pipeline = SVGToVideoPipeline({
    "blender_path": os.environ.get("BLENDER_PATH", "blender"),
    "script_dir": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'genai_agent', 'scripts'),
    "output_dir": os.environ.get("OUTPUT_DIR", "outputs"),
    "cleanup_temp": True
})

# Background tasks storage
background_tasks = {}

# Model definitions
class GenerateSVGRequest(BaseModel):
    concept: str
    provider: Optional[str] = None

class GenerateVideoRequest(BaseModel):
    concept: str
    provider: Optional[str] = None
    render_quality: Optional[str] = None
    animation_type: Optional[str] = None
    resolution: Optional[List[int]] = None

class ConvertSVGRequest(BaseModel):
    render_quality: Optional[str] = None
    animation_type: Optional[str] = None
    resolution: Optional[List[int]] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Background task handler
async def process_video_generation(task_id: str, concept: str, output_path: str, options: Dict[str, Any]):
    try:
        background_tasks[task_id] = {"status": "running", "progress": 0}
        
        # Update progress
        background_tasks[task_id]["progress"] = 10
        
        # Process through pipeline
        result = await pipeline.process(concept, output_path, options)
        
        if result["status"] == "success":
            background_tasks[task_id] = {
                "status": "completed", 
                "progress": 100,
                "result": result
            }
            logger.info(f"Task {task_id} completed successfully")
        else:
            background_tasks[task_id] = {
                "status": "failed", 
                "progress": 100,
                "error": result.get("error", "Unknown error")
            }
            logger.error(f"Task {task_id} failed: {result.get('error')}")
    
    except Exception as e:
        background_tasks[task_id] = {
            "status": "failed", 
            "progress": 100,
            "error": str(e)
        }
        logger.exception(f"Task {task_id} failed with exception")

# Routes
@router.get("/providers", response_model=List[str])
async def list_providers():
    """Get a list of available LLM providers."""
    providers = pipeline.get_available_providers()
    return providers

@router.post("/generate-svg")
async def generate_svg(request: GenerateSVGRequest):
    """Generate an SVG diagram from a concept."""
    try:
        # Generate SVG
        result = await pipeline.generate_svg_only(
            request.concept,
            provider=request.provider
        )
        
        if result["status"] != "success":
            raise HTTPException(status_code=500, detail=result.get("error", "SVG generation failed"))
        
        # Return SVG content
        return {"svg_content": result["svg_content"]}
    
    except Exception as e:
        logger.exception("SVG generation error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-video")
async def generate_video(
    background_tasks: BackgroundTasks,
    request: GenerateVideoRequest
):
    """Generate a video from a concept description."""
    try:
        # Generate task ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # Create output filename
        output_filename = f"video_{task_id}.mp4"
        output_path = os.path.join(os.environ.get("OUTPUT_DIR", "outputs"), output_filename)
        
        # Create options
        options = {}
        
        if request.provider:
            options["provider"] = request.provider
        
        if request.render_quality:
            options["render_quality"] = request.render_quality
        
        if request.animation_type:
            options["animation_type"] = request.animation_type
        
        if request.resolution and len(request.resolution) == 2:
            options["resolution"] = tuple(request.resolution)
        
        # Initialize task status
        background_tasks[task_id] = {"status": "queued", "progress": 0}
        
        # Start background task
        background_tasks.add_task(
            process_video_generation,
            task_id,
            request.concept,
            output_path,
            options
        )
        
        # Return task ID
        return {"task_id": task_id, "status": "queued"}
    
    except Exception as e:
        logger.exception("Video generation task creation error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert-svg")
async def convert_svg(
    background_tasks: BackgroundTasks,
    svg_file: UploadFile = File(...),
    render_quality: Optional[str] = Form(None),
    animation_type: Optional[str] = Form(None),
    resolution_width: Optional[int] = Form(None),
    resolution_height: Optional[int] = Form(None)
):
    """Convert an uploaded SVG file to video."""
    try:
        # Generate task ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # Create output filename
        output_filename = f"video_{task_id}.mp4"
        output_path = os.path.join(os.environ.get("OUTPUT_DIR", "outputs"), output_filename)
        
        # Save uploaded SVG to temporary file
        svg_content = await svg_file.read()
        svg_content_str = svg_content.decode("utf-8")
        
        # Validate SVG
        is_valid, message = validate_svg(svg_content_str)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid SVG: {message}")
        
        # Create temporary file
        temp_svg_path = create_temp_file(svg_content_str, ".svg")
        
        # Create options
        options = {}
        
        if render_quality:
            options["render_quality"] = render_quality
        
        if animation_type:
            options["animation_type"] = animation_type
        
        if resolution_width and resolution_height:
            options["resolution"] = (resolution_width, resolution_height)
        
        # Initialize task status
        background_tasks[task_id] = {"status": "queued", "progress": 0}
        
        # Define background task
        async def process_svg_conversion(task_id, svg_path, output_path, options):
            try:
                background_tasks[task_id] = {"status": "running", "progress": 0}
                
                # Convert SVG to video
                result = await pipeline.convert_existing_svg(svg_path, output_path, options)
                
                if result["status"] == "success":
                    background_tasks[task_id] = {
                        "status": "completed", 
                        "progress": 100,
                        "result": result
                    }
                    logger.info(f"Task {task_id} completed successfully")
                else:
                    background_tasks[task_id] = {
                        "status": "failed", 
                        "progress": 100,
                        "error": result.get("error", "Unknown error")
                    }
                    logger.error(f"Task {task_id} failed: {result.get('error')}")
                
                # Clean up temporary file
                try:
                    os.unlink(svg_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
                
            except Exception as e:
                background_tasks[task_id] = {
                    "status": "failed", 
                    "progress": 100,
                    "error": str(e)
                }
                logger.exception(f"Task {task_id} failed with exception")
        
        # Start background task
        background_tasks.add_task(
            process_svg_conversion,
            task_id,
            temp_svg_path,
            output_path,
            options
        )
        
        # Return task ID
        return {"task_id": task_id, "status": "queued"}
    
    except Exception as e:
        logger.exception("SVG conversion task creation error")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of a task."""
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return {
        "task_id": task_id,
        **background_tasks[task_id]
    }
