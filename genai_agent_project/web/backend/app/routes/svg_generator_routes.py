
"""
Routes for SVG generator functionality.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
import os
import sys
from pathlib import Path

# Add the project directory to the path
project_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, str(project_dir))

# Import SVG generator
try:
    from genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator import generate_svg
except ImportError as e:
    print(f"Error importing SVG generator: {e}")

# Import SVG to 3D converter if available
try:
    from genai_agent_project.genai_agent.svg_to_video.svg_to_3d import svg_to_3d
    svg_to_3d_available = True
except ImportError:
    svg_to_3d_available = False

# Import animation and rendering if available
try:
    from genai_agent_project.genai_agent.svg_to_video.animation import animate_model
    from genai_agent_project.genai_agent.svg_to_video.rendering import render_video
    animation_available = True
    rendering_available = True
except ImportError:
    animation_available = False
    rendering_available = False

router = APIRouter(prefix="/svg-generator", tags=["svg-generator"])

class SVGGenerationRequest(BaseModel):
    prompt: str
    diagram_type: str = "flowchart"
    provider: str = "claude"
    output_path: Optional[str] = None

class SVGTo3DRequest(BaseModel):
    svg_path: str
    output_path: Optional[str] = None
    extrude_height: float = 10.0
    scale_factor: float = 1.0

class AnimationRequest(BaseModel):
    model_path: str
    output_path: Optional[str] = None
    animation_type: str = "rotation"
    duration: float = 5.0

class RenderingRequest(BaseModel):
    animation_path: str
    output_path: Optional[str] = None
    resolution: str = "720p"
    quality: str = "medium"

@router.get("/capabilities")
async def get_capabilities():
    """Get the capabilities of the SVG to Video pipeline."""
    return {
        "svg_generation": True,
        "svg_to_3d": svg_to_3d_available,
        "animation": animation_available,
        "rendering": rendering_available,
        "providers": ["claude", "openai", "mock"],
        "diagram_types": ["flowchart", "network_diagram", "sequence_diagram", "entity_relationship", "class_diagram"]
    }

@router.post("/generate-svg")
async def generate_svg_endpoint(request: SVGGenerationRequest):
    """Generate an SVG based on a text description."""
    try:
        # Use the consolidated output directory
        output_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename if not provided
        if not request.output_path:
            import uuid
            output_file = output_dir / f"{uuid.uuid4()}.svg"
        else:
            output_file = Path(request.output_path)
            
            # Ensure the output file is in the output directory
            if not str(output_file).startswith(str(output_dir)):
                output_file = output_dir / output_file.name
        
        # Generate the SVG
        result = generate_svg(
            prompt=request.prompt,
            diagram_type=request.diagram_type,
            output_file=str(output_file),
            provider=request.provider
        )
        
        if result and os.path.isfile(output_file):
            return {
                "success": True,
                "svg_path": str(output_file),
                "message": "SVG generated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate SVG")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SVG: {str(e)}")

@router.post("/convert-to-3d")
async def convert_to_3d_endpoint(request: SVGTo3DRequest):
    """Convert an SVG to a 3D model."""
    if not svg_to_3d_available:
        raise HTTPException(status_code=501, detail="SVG to 3D conversion is not available")
    
    try:
        # Use the consolidated output directory
        output_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/models")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename if not provided
        if not request.output_path:
            import uuid
            output_file = output_dir / f"{uuid.uuid4()}.obj"
        else:
            output_file = Path(request.output_path)
            
            # Ensure the output file is in the output directory
            if not str(output_file).startswith(str(output_dir)):
                output_file = output_dir / output_file.name
        
        # Convert the SVG to 3D
        result = svg_to_3d(
            svg_path=request.svg_path,
            output_file=str(output_file),
            extrude_height=request.extrude_height,
            scale_factor=request.scale_factor
        )
        
        if result and os.path.isfile(output_file):
            return {
                "success": True,
                "model_path": str(output_file),
                "message": "SVG converted to 3D successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to convert SVG to 3D")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting SVG to 3D: {str(e)}")

@router.post("/animate-model")
async def animate_model_endpoint(request: AnimationRequest):
    """Animate a 3D model."""
    if not animation_available:
        raise HTTPException(status_code=501, detail="Animation is not available")
    
    try:
        # Use the consolidated output directory
        output_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/animations")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename if not provided
        if not request.output_path:
            import uuid
            output_file = output_dir / f"{uuid.uuid4()}.blend"
        else:
            output_file = Path(request.output_path)
            
            # Ensure the output file is in the output directory
            if not str(output_file).startswith(str(output_dir)):
                output_file = output_dir / output_file.name
        
        # Animate the model
        result = animate_model(
            model_path=request.model_path,
            output_file=str(output_file),
            animation_type=request.animation_type,
            duration=request.duration
        )
        
        if result and os.path.isfile(output_file):
            return {
                "success": True,
                "animation_path": str(output_file),
                "message": "Model animated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to animate model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error animating model: {str(e)}")

@router.post("/render-video")
async def render_video_endpoint(request: RenderingRequest):
    """Render an animated model to video."""
    if not rendering_available:
        raise HTTPException(status_code=501, detail="Rendering is not available")
    
    try:
        # Use the consolidated output directory
        output_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/videos")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename if not provided
        if not request.output_path:
            import uuid
            output_file = output_dir / f"{uuid.uuid4()}.mp4"
        else:
            output_file = Path(request.output_path)
            
            # Ensure the output file is in the output directory
            if not str(output_file).startswith(str(output_dir)):
                output_file = output_dir / output_file.name
        
        # Render the video
        result = render_video(
            animation_path=request.animation_path,
            output_file=str(output_file),
            resolution=request.resolution,
            quality=request.quality
        )
        
        if result and os.path.isfile(output_file):
            return {
                "success": True,
                "video_path": str(output_file),
                "message": "Video rendered successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to render video")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering video: {str(e)}")
