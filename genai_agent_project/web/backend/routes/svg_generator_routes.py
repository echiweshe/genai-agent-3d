"""
SVG Generator Routes

This module provides FastAPI routes for the SVG Generator component.
"""

import os
import sys
import uuid
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body

# Import for reading config
import yaml

# Add project root to Python path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Define variables with default values
SVG_GENERATOR_AVAILABLE = False
SVG_TO_3D_AVAILABLE = False
ANIMATION_AVAILABLE = False
RENDERING_AVAILABLE = False
llm_factory = None
svg_to_3d_converter = None
model_animator = None
video_renderer = None

# Import SVG Generator and related components
try:
    # Try importing from project structure first
    from genai_agent.svg_to_video.llm_integrations.llm_factory import get_llm_factory
    
    # Ensure environment variables are properly set
    from env_checker import setup_env_variables
    env_setup_success = setup_env_variables()
    logger.info(f"Environment setup success: {env_setup_success}")
    
    # Initialize LLM factory
    llm_factory = get_llm_factory()
    SVG_GENERATOR_AVAILABLE = True
    
    # Try importing SVG to 3D converter
    try:
        from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter
        svg_to_3d_converter = SVGTo3DConverter(debug=True)
        SVG_TO_3D_AVAILABLE = True
        logger.info("SVG to 3D converter is available")
    except ImportError as e:
        logger.warning(f"SVG to 3D converter not available: {e}")
        SVG_TO_3D_AVAILABLE = False
    
    # Try importing animation module
    try:
        from genai_agent.svg_to_video.animation import ModelAnimator
        model_animator = ModelAnimator()
        ANIMATION_AVAILABLE = True
        logger.info("Model animator is available")
    except ImportError as e:
        logger.warning(f"Model animator not available: {e}")
        ANIMATION_AVAILABLE = False
    
    # Try importing rendering module
    try:
        from genai_agent.svg_to_video.rendering import VideoRenderer
        video_renderer = VideoRenderer()
        RENDERING_AVAILABLE = True
        logger.info("Video renderer is available")
    except ImportError as e:
        logger.warning(f"Video renderer not available: {e}")
        RENDERING_AVAILABLE = False
        
except ImportError as e:
    logger.warning(f"SVG Generator not available from project structure: {e}")
    try:
        # If not found in project structure, try importing from the root structure
        sys.path.append(project_root)
        logger.info(f"Added project root to Python path: {project_root}")
        
        from genai_agent.svg_to_video.llm_integrations.llm_factory import get_llm_factory
        llm_factory = get_llm_factory()
        SVG_GENERATOR_AVAILABLE = True
        
        # Try importing SVG to 3D converter
        try:
            from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter
            svg_to_3d_converter = SVGTo3DConverter(debug=True)
            SVG_TO_3D_AVAILABLE = True
            logger.info("SVG to 3D converter is available")
        except ImportError as e:
            logger.warning(f"SVG to 3D converter not available: {e}")
            SVG_TO_3D_AVAILABLE = False
        
        # Try importing animation module
        try:
            from genai_agent.svg_to_video.animation import ModelAnimator
            model_animator = ModelAnimator()
            ANIMATION_AVAILABLE = True
            logger.info("Model animator is available")
        except ImportError as e:
            logger.warning(f"Model animator not available: {e}")
            ANIMATION_AVAILABLE = False
        
        # Try importing rendering module
        try:
            from genai_agent.svg_to_video.rendering import VideoRenderer
            video_renderer = VideoRenderer()
            RENDERING_AVAILABLE = True
            logger.info("Video renderer is available")
        except ImportError as e:
            logger.warning(f"Video renderer not available: {e}")
            RENDERING_AVAILABLE = False
    except ImportError as e:
        logger.warning(f"SVG Generator not available: {e}")
        SVG_GENERATOR_AVAILABLE = False
        SVG_TO_3D_AVAILABLE = False
        ANIMATION_AVAILABLE = False
        RENDERING_AVAILABLE = False

# Create router
router = APIRouter(tags=["svg_generator"])

# Load configuration from config.yaml
config_path = os.path.join(os.path.dirname(__file__), '../../../config.yaml')
try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded configuration from {config_path}")
except Exception as e:
    logger.warning(f"Error loading config from {config_path}: {str(e)}")
    config = {'paths': {}}

# Define output directories from config if available, otherwise use defaults
OUTPUT_DIR = config.get('paths', {}).get('output_dir', os.path.join(project_root, "output"))
SVG_OUTPUT_DIR = config.get('paths', {}).get('svg_output_dir', os.path.join(OUTPUT_DIR, "svg"))
DIAGRAMS_OUTPUT_DIR = config.get('paths', {}).get('diagrams_output_dir', os.path.join(OUTPUT_DIR, "diagrams"))
MODELS_OUTPUT_DIR = config.get('paths', {}).get('models_output_dir', os.path.join(OUTPUT_DIR, "models"))
ANIMATIONS_OUTPUT_DIR = config.get('paths', {}).get('animations_output_dir', os.path.join(OUTPUT_DIR, "animations"))
VIDEOS_OUTPUT_DIR = config.get('paths', {}).get('videos_output_dir', os.path.join(OUTPUT_DIR, "videos"))

# Special path for svg_to_video output
SVG_TO_VIDEO_DIR = os.path.join(OUTPUT_DIR, "svg_to_video")
SVG_TO_VIDEO_SVG_DIR = os.path.join(SVG_TO_VIDEO_DIR, "svg")

# Log the output directories
logger.info(f"Output directory: {OUTPUT_DIR}")
logger.info(f"SVG output directory: {SVG_OUTPUT_DIR}")
logger.info(f"SVG to Video SVG directory: {SVG_TO_VIDEO_SVG_DIR}")

# Ensure output directories exist
os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)
os.makedirs(DIAGRAMS_OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_OUTPUT_DIR, exist_ok=True)
os.makedirs(ANIMATIONS_OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEOS_OUTPUT_DIR, exist_ok=True)
os.makedirs(SVG_TO_VIDEO_SVG_DIR, exist_ok=True)

@router.get("/svg-generator/health")
async def health_check():
    """
    Simple health check endpoint for the SVG Generator API.
    """
    return {
        "status": "success",
        "message": "SVG Generator API is healthy",
        "available": SVG_GENERATOR_AVAILABLE,
        "svg_to_3d_available": SVG_TO_3D_AVAILABLE,
        "animation_available": ANIMATION_AVAILABLE,
        "rendering_available": RENDERING_AVAILABLE
    }

@router.post("/svg-generator/generate")
async def generate_svg(
    description: str = Body(..., description="The description of the diagram"),
    diagram_type: str = Body("flowchart", description="Type of diagram"),
    provider: Optional[str] = Body(None, description="LLM provider to use"),
    name: Optional[str] = Body(None, description="Name for the diagram")
):
    """
    Generate an SVG diagram from a description using an LLM.
    """
    if not SVG_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="SVG Generator is not available. Check server logs for details."
        )
    
    try:
        # Initialize the LLM factory if needed
        await llm_factory.initialize()
        
        # Get available providers
        providers = llm_factory.get_providers()
        provider_ids = [p["id"] for p in providers]
        
        # If provider not specified or not available, use first available
        if not provider or provider not in provider_ids:
            if "claude-direct" in provider_ids:
                provider = "claude-direct"
            elif provider_ids:
                provider = provider_ids[0]
            else:
                raise HTTPException(
                    status_code=503,
                    detail="No LLM providers available for SVG generation."
                )
        
        # Generate a unique ID and filename
        diagram_id = str(uuid.uuid4())
        
        # Generate a name if not provided
        if not name:
            name = f"Diagram-{diagram_id[:8]}"
        
        # Create filename
        filename = f"{name.replace(' ', '_')}.svg"
        
        # Define output paths - save to both svg directories and diagrams directory
        svg_path = os.path.join(SVG_OUTPUT_DIR, filename)
        svg_to_video_path = os.path.join(SVG_TO_VIDEO_SVG_DIR, filename)
        diagram_path = os.path.join(DIAGRAMS_OUTPUT_DIR, filename)
        
        # Generate SVG
        logger.info(f"Generating SVG with provider: {provider}, diagram type: {diagram_type}")
        
        # Verify ANTHROPIC_API_KEY is available
        if 'claude' in provider and os.environ.get("ANTHROPIC_API_KEY"):
            logger.info(f"Using Anthropic API key: {os.environ.get('ANTHROPIC_API_KEY')[:8]}...")
        
        # Generate SVG - no fallbacks, strict error handling
        try:
            svg_content = await llm_factory.generate_svg(
                provider=provider,
                concept=description,
                style=diagram_type,
                temperature=0.4
            )
            
            # Validate SVG content
            if not svg_content or not svg_content.strip().startswith("<svg"):
                logger.error(f"Invalid SVG content returned from LLM: {svg_content[:100] if svg_content else 'None'}")
                raise ValueError("Invalid SVG content returned from LLM")
                
            # Log the first few characters of the SVG content
            logger.info(f"Generated SVG content (first 100 chars): {svg_content[:100]}...")
        except Exception as e:
            logger.error(f"Error generating SVG: {str(e)}", exc_info=True)
            # Return a clear error - no fallbacks
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate SVG: {str(e)}"
            )
        
        # Save SVG to all output locations
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        with open(svg_to_video_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        with open(diagram_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        # Return success response
        return {
            "status": "success",
            "message": "SVG diagram generated successfully",
            "diagram_id": diagram_id,
            "name": name,
            "file_path": f"diagrams/{filename}",
            "svg_path": f"svg/{filename}",
            "code": svg_content,
            "provider": provider,
            "diagram_type": diagram_type
        }
    
    except Exception as e:
        logger.error(f"Error generating SVG: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate SVG: {str(e)}"
        )

@router.get("/svg-generator/providers")
async def get_providers():
    """
    Get available LLM providers for SVG generation.
    """
    if not SVG_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="SVG Generator is not available. Check server logs for details."
        )
    
    try:
        # Initialize the LLM factory if needed
        await llm_factory.initialize()
        
        # Get available providers
        providers = llm_factory.get_providers()
        
        return {
            "status": "success",
            "providers": providers
        }
    
    except Exception as e:
        logger.error(f"Error getting providers: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get providers: {str(e)}"
        )

@router.get("/svg-generator/diagram-types")
async def get_diagram_types():
    """
    Get available diagram types for SVG generation.
    """
    # Define available diagram types
    diagram_types = [
        {"id": "flowchart", "name": "Flowchart", "description": "Diagram showing process flow"},
        {"id": "network", "name": "Network Diagram", "description": "Diagram showing network topology"},
        {"id": "sequence", "name": "Sequence Diagram", "description": "Diagram showing sequence of interactions"},
        {"id": "class", "name": "Class Diagram", "description": "UML diagram showing classes and relationships"},
        {"id": "er", "name": "Entity Relationship Diagram", "description": "Diagram showing database structure"},
        {"id": "mindmap", "name": "Mind Map", "description": "Hierarchical diagram for organizing information"},
        {"id": "general", "name": "General Diagram", "description": "Generic diagram type"}
    ]
    
    return {
        "status": "success",
        "diagram_types": diagram_types
    }

@router.get("/svg-generator/capabilities")
async def get_capabilities():
    """
    Get SVG to Video pipeline capabilities.
    """
    return {
        "status": "success",
        "svg_generator_available": SVG_GENERATOR_AVAILABLE,
        "svg_to_3d_available": SVG_TO_3D_AVAILABLE,
        "animation_available": ANIMATION_AVAILABLE,
        "rendering_available": RENDERING_AVAILABLE
    }

@router.post("/svg-generator/convert-to-3d")
async def convert_svg_to_3d(
    svg_path: str = Body(..., description="Path to the SVG file"),
    name: Optional[str] = Body(None, description="Name for the 3D model")
):
    """
    Convert an SVG diagram to a 3D model.
    """
    if not SVG_GENERATOR_AVAILABLE or not SVG_TO_3D_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="SVG to 3D conversion is not available. Check server logs for details."
        )
    
    try:
        # Parse SVG path
        if svg_path.startswith("diagrams/") or svg_path.startswith("svg/"):
            # Path is relative to output directory
            full_svg_path = os.path.join(OUTPUT_DIR, svg_path)
        else:
            # Assume path is absolute
            full_svg_path = svg_path
        
        # Ensure SVG file exists
        if not os.path.exists(full_svg_path):
            raise HTTPException(
                status_code=404,
                detail=f"SVG file not found at {full_svg_path}"
            )
        
        # Generate a name for the model if not provided
        if not name:
            name = f"Model-{os.path.basename(full_svg_path).replace('.svg', '')}"
        
        # Define output path
        model_filename = f"{name.replace(' ', '_')}.blend"
        model_path = os.path.join(MODELS_OUTPUT_DIR, model_filename)
        
        # Convert SVG to 3D
        logger.info(f"Converting SVG to 3D model: {full_svg_path} -> {model_path}")
        
        # Check if svg_to_3d_converter is a mock or has proper implementation
        if not hasattr(svg_to_3d_converter, 'convert_svg_to_3d') or not callable(getattr(svg_to_3d_converter, 'convert_svg_to_3d')):
            logger.error("SVG to 3D converter is not properly implemented")
            raise NotImplementedError("SVG to 3D conversion is not properly implemented")
            
        result = await svg_to_3d_converter.convert_svg_to_3d(
            svg_path=full_svg_path,
            output_path=model_path
        )
        
        if not result:
            logger.error("SVG to 3D conversion failed with no specific error message")
            raise HTTPException(
                status_code=500,
                detail="Failed to convert SVG to 3D model - check logs for details"
            )
        
        # Verify the model file exists
        if not os.path.exists(model_path):
            logger.error(f"Model file not created at expected path: {model_path}")
            raise HTTPException(
                status_code=500,
                detail="SVG to 3D conversion did not produce a model file"
            )
        
        # Return success response
        return {
            "status": "success",
            "message": "SVG converted to 3D model successfully",
            "name": name,
            "model_path": f"models/{model_filename}",
            "full_path": model_path
        }
    
    except NotImplementedError as e:
        logger.error(f"SVG to 3D conversion not implemented: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=501,  # Not Implemented
            detail=f"SVG to 3D conversion is not implemented: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error converting SVG to 3D: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to convert SVG to 3D: {str(e)}"
        )

@router.post("/svg-generator/animate-model")
async def animate_model(
    model_path: str = Body(..., description="Path to the 3D model file"),
    name: Optional[str] = Body(None, description="Name for the animated model"),
    animation_type: str = Body("simple", description="Type of animation to apply")
):
    """
    Add animation to a 3D model.
    """
    if not ANIMATION_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Animation module is not available. Check server logs for details."
        )
    
    try:
        # Parse model path
        if model_path.startswith("models/"):
            # Path is relative to output directory
            full_model_path = os.path.join(OUTPUT_DIR, model_path)
        else:
            # Assume path is absolute
            full_model_path = model_path
        
        # Ensure model file exists
        if not os.path.exists(full_model_path):
            raise HTTPException(
                status_code=404,
                detail=f"Model file not found at {full_model_path}"
            )
        
        # Generate a name for the animated model if not provided
        if not name:
            name = f"Animated-{os.path.basename(full_model_path).replace('.blend', '')}"
        
        # Define output path
        animated_filename = f"{name.replace(' ', '_')}.blend"
        animated_path = os.path.join(ANIMATIONS_OUTPUT_DIR, animated_filename)
        
        # Check if model_animator is properly implemented
        if not hasattr(model_animator, 'animate_model') or not callable(getattr(model_animator, 'animate_model')):
            logger.error("Model animator is not properly implemented")
            raise NotImplementedError("Model animation is not properly implemented")
            
        # Add animation to the model
        logger.info(f"Animating 3D model: {full_model_path} -> {animated_path}")
        try:
            result = await model_animator.animate_model(
                model_path=full_model_path,
                output_path=animated_path,
                animation_type=animation_type
            )
        except NotImplementedError as e:
            # Explicitly catch NotImplementedError from the model_animator
            logger.error(f"Model animation not implemented: {str(e)}")
            raise HTTPException(
                status_code=501,  # Not Implemented
                detail=f"Model animation is not implemented: {str(e)}"
            )
        
        if not result:
            logger.error("Model animation failed with no specific error message")
            raise HTTPException(
                status_code=500,
                detail="Failed to animate 3D model - check logs for details"
            )
        
        # Verify the animated model file exists
        if not os.path.exists(animated_path):
            logger.error(f"Animated model file not created at expected path: {animated_path}")
            raise HTTPException(
                status_code=500,
                detail="Model animation did not produce an output file"
            )
        
        # Return success response
        return {
            "status": "success",
            "message": "Model animated successfully",
            "name": name,
            "animated_model_path": f"animations/{animated_filename}",
            "full_path": animated_path
        }
    
    except NotImplementedError as e:
        logger.error(f"Model animation not implemented: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=501,  # Not Implemented
            detail=f"Model animation is not implemented: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error animating model: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to animate model: {str(e)}"
        )

@router.post("/svg-generator/render-video")
async def render_video(
    animated_model_path: str = Body(..., description="Path to the animated model file"),
    name: Optional[str] = Body(None, description="Name for the video"),
    quality: str = Body("medium", description="Quality of the rendering"),
    duration: int = Body(10, description="Duration of the video in seconds")
):
    """
    Render an animated model to video.
    """
    if not RENDERING_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Rendering module is not available. Check server logs for details."
        )
    
    try:
        # Parse animated model path
        if animated_model_path.startswith("animations/"):
            # Path is relative to output directory
            full_animated_path = os.path.join(OUTPUT_DIR, animated_model_path)
        else:
            # Assume path is absolute
            full_animated_path = animated_model_path
        
        # Ensure animated model file exists
        if not os.path.exists(full_animated_path):
            raise HTTPException(
                status_code=404,
                detail=f"Animated model file not found at {full_animated_path}"
            )
        
        # Generate a name for the video if not provided
        if not name:
            name = f"Video-{os.path.basename(full_animated_path).replace('.blend', '')}"
        
        # Define output path
        video_filename = f"{name.replace(' ', '_')}.mp4"
        video_path = os.path.join(VIDEOS_OUTPUT_DIR, video_filename)
        
        # Check if video_renderer is properly implemented
        if not hasattr(video_renderer, 'render_video') or not callable(getattr(video_renderer, 'render_video')):
            logger.error("Video renderer is not properly implemented")
            raise NotImplementedError("Video rendering is not properly implemented")
        
        # Render the video
        logger.info(f"Rendering video: {full_animated_path} -> {video_path}")
        try:
            result = await video_renderer.render_video(
                model_path=full_animated_path,
                output_path=video_path,
                quality=quality,
                duration=duration
            )
        except NotImplementedError as e:
            # Explicitly catch NotImplementedError from the video_renderer
            logger.error(f"Video rendering not implemented: {str(e)}")
            raise HTTPException(
                status_code=501,  # Not Implemented
                detail=f"Video rendering is not implemented: {str(e)}"
            )
        
        if not result:
            logger.error("Video rendering failed with no specific error message")
            raise HTTPException(
                status_code=500,
                detail="Failed to render video - check logs for details"
            )
        
        # Verify the video file exists
        if not os.path.exists(video_path):
            logger.error(f"Video file not created at expected path: {video_path}")
            raise HTTPException(
                status_code=500,
                detail="Video rendering did not produce an output file"
            )
        
        # Return success response
        return {
            "status": "success",
            "message": "Video rendered successfully",
            "name": name,
            "video_path": f"videos/{video_filename}",
            "full_path": video_path
        }
    
    except NotImplementedError as e:
        logger.error(f"Video rendering not implemented: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=501,  # Not Implemented
            detail=f"Video rendering is not implemented: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error rendering video: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render video: {str(e)}"
        )
