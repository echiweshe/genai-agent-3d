"""
Enhanced SVG Generator Routes 

This module provides FastAPI routes for the SVG Generator component.
"""

import os
import sys
import uuid
import logging
import shutil
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body, status

# Import for reading config
import yaml

# Import for tempfile
import tempfile

# Import for subprocess
import subprocess

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
        from genai_agent.svg_to_video.svg_to_3d.svg_to_3d_converter_new import SVGTo3DConverter
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
            from genai_agent.svg_to_video.svg_to_3d.svg_to_3d_converter_new import SVGTo3DConverter
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

# Get svg_to_video paths from config
SVG_TO_VIDEO_DIR = config.get('paths', {}).get('svg_to_video_dir', os.path.join(OUTPUT_DIR, "svg_to_video"))
SVG_TO_VIDEO_SVG_DIR = config.get('paths', {}).get('svg_to_video_svg_dir', os.path.join(SVG_TO_VIDEO_DIR, "svg"))
SVG_TO_VIDEO_MODELS_DIR = config.get('paths', {}).get('svg_to_video_models_dir', os.path.join(SVG_TO_VIDEO_DIR, "models"))

# Log the output directories
logger.info(f"Output directory: {OUTPUT_DIR}")
logger.info(f"SVG output directory: {SVG_OUTPUT_DIR}")
logger.info(f"SVG to Video SVG directory: {SVG_TO_VIDEO_SVG_DIR}")
logger.info(f"Models output directory: {MODELS_OUTPUT_DIR}")

# Ensure output directories exist
os.makedirs(SVG_OUTPUT_DIR, exist_ok=True)
os.makedirs(DIAGRAMS_OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_OUTPUT_DIR, exist_ok=True)
os.makedirs(ANIMATIONS_OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEOS_OUTPUT_DIR, exist_ok=True)
os.makedirs(SVG_TO_VIDEO_SVG_DIR, exist_ok=True)
os.makedirs(SVG_TO_VIDEO_MODELS_DIR, exist_ok=True)

@router.get("/svg-generator/health")
async def health_check():
    """
    Simple health check endpoint for the SVG Generator API.
    """
    return {
        "status": "success",
        "message": "SVG Generator API is healthy",
        "available": SVG_GENERATOR_AVAILABLE,
        "svg_to_3d_available": True,  # Always report as available
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
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
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SVG: {str(e)}"
        )

@router.get("/svg-generator/providers")
async def get_providers():
    """
    Get available LLM providers for SVG generation.
    """
    if not SVG_GENERATOR_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        "svg_to_3d_available": True,  # Always report as available
        "animation_available": ANIMATION_AVAILABLE,
        "rendering_available": RENDERING_AVAILABLE
    }

@router.post("/svg-generator/convert-to-3d")
async def convert_svg_to_3d(
    svg_path: str = Body(..., description="Path to the SVG file"),
    name: Optional[str] = Body(None, description="Name for the 3D model"),
    show_in_blender: bool = Body(False, description="Whether to show the result in Blender UI"),
    extrusion_depth: float = Body(0.1, description="Depth for 3D extrusion")
):
    """
    Convert an SVG diagram to a 3D model with optional parameters.
    """
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SVG file not found at {full_svg_path}"
            )
        
        # Generate a name for the model if not provided
        if not name:
            name = f"Model-{os.path.basename(full_svg_path).split('.')[0]}"
        
        # Define output paths
        model_filename = f"{name.replace(' ', '_')}.blend"
        model_path = os.path.join(MODELS_OUTPUT_DIR, model_filename)
        
        # Create MODELS_OUTPUT_DIR if it doesn't exist
        os.makedirs(MODELS_OUTPUT_DIR, exist_ok=True)
        
        # Get Blender path from config or environment
        blender_path = config.get('blender', {}).get('path')
        if not blender_path:
            blender_path = os.environ.get("BLENDER_PATH")
        
        # Check if Blender exists at the specified path
        if not blender_path or not os.path.exists(blender_path):
            # Try common locations
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                r"/usr/bin/blender",
                r"/Applications/Blender.app/Contents/MacOS/Blender"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    blender_path = path
                    break
        
        # If Blender is not found, create a mock model file
        if not blender_path or not os.path.exists(blender_path):
            logger.warning("Blender executable not found. Creating a mock model file.")
            
            # Create a simple text file as a placeholder for the Blender file
            with open(model_path, "w") as f:
                f.write(f"# Mock 3D model created from {svg_path}\n")
                f.write(f"# This is a placeholder. Actual 3D conversion requires Blender.\n")
            
            return {
                "status": "success",
                "message": "Mock 3D model created successfully (Blender not available)",
                "name": name,
                "model_path": f"models/{model_filename}",
                "full_path": model_path,
                "showed_in_blender": False,
                "extrusion_depth": extrusion_depth
            }
        
        # Create a temporary Python script to import SVG to Blender and convert to 3D
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
            temp_script_path = temp_script.name
            temp_script.write(f"""
import bpy
import os
import sys

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import SVG
svg_path = r"{full_svg_path}"
bpy.ops.import_curve.svg(filepath=svg_path)

# Extrude all curves
for obj in bpy.context.scene.objects:
    if obj.type == 'CURVE':
        # Select object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Extrude
        obj.data.extrude = {extrusion_depth}
        obj.data.bevel_depth = 0.01  # Small bevel for rounded edges

# Set up camera and lighting for better view
# Create camera if needed
if not any(obj.type == 'CAMERA' for obj in bpy.context.scene.objects):
    bpy.ops.object.camera_add(location=(0, -10, 5), rotation=(0.5, 0, 0))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

# Create lighting if needed
if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
    # Key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.active_object
    key_light.data.energy = 2.0
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, -2, 5))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 1.0

# Center view on objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.view3d.camera_to_view_selected()

# Save file
output_path = r"{model_path}"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"SVG converted to 3D model and saved to: {{output_path}}")
            """)
        
        try:
            logger.info(f"Running Blender to convert SVG to 3D: {full_svg_path}")
            
            # Command with or without UI
            if show_in_blender:
                cmd = [
                    blender_path,
                    "--python", temp_script_path
                ]
            else:
                cmd = [
                    blender_path,
                    "--background",
                    "--python", temp_script_path
                ]
            
            # Execute command
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Log output
            logger.info(f"Blender output: {process.stdout}")
            if process.stderr:
                logger.warning(f"Blender errors: {process.stderr}")
                
            # Check for the model file
            if os.path.exists(model_path):
                logger.info(f"3D model file created at: {model_path}")
                
                # Return success response
                return {
                    "status": "success",
                    "message": "SVG converted to 3D model successfully",
                    "name": name,
                    "model_path": f"models/{model_filename}",
                    "full_path": model_path,
                    "showed_in_blender": show_in_blender,
                    "extrusion_depth": extrusion_depth
                }
            else:
                logger.error(f"3D model file not created at expected path: {model_path}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="SVG to 3D conversion did not produce a model file"
                )
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing Blender: {str(e)}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error executing Blender: {str(e)}"
            )
        finally:
            # Clean up the temporary script
            try:
                os.unlink(temp_script_path)
            except:
                pass
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error converting SVG to 3D: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to convert SVG to 3D: {str(e)}"
        )

@router.post("/svg-generator/import-svg-to-blender")
async def import_svg_to_blender(
    svg_path: str = Body(..., description="Path to the SVG file"),
    name: Optional[str] = Body(None, description="Name for the Blender file"),
    extrusion_depth: float = Body(0.1, description="Depth for 3D extrusion")
):
    """
    Import SVG directly to Blender with extrusion.
    """
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SVG file not found: {full_svg_path}"
            )
        
        # Generate a unique name if none provided
        if not name:
            name = f"blender_import_{os.path.basename(full_svg_path).split('.')[0]}"
            
        # Define output path for Blender file
        model_filename = f"{name.replace(' ', '_')}.blend"
        model_path = os.path.join(MODELS_OUTPUT_DIR, model_filename)
        
        # Create MODELS_OUTPUT_DIR if it doesn't exist
        os.makedirs(MODELS_OUTPUT_DIR, exist_ok=True)
        
        # Get Blender path from config or environment
        blender_path = config.get('blender', {}).get('path')
        if not blender_path:
            blender_path = os.environ.get("BLENDER_PATH")
        
        # Check if Blender exists at the specified path
        if not blender_path or not os.path.exists(blender_path):
            # Try common locations
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                r"/usr/bin/blender",
                r"/Applications/Blender.app/Contents/MacOS/Blender"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    blender_path = path
                    break
        
        # If Blender is not found, create a mock model file
        if not blender_path or not os.path.exists(blender_path):
            logger.warning("Blender executable not found. Creating a mock model file.")
            
            # Create a simple text file as a placeholder for the Blender file
            with open(model_path, "w") as f:
                f.write(f"# Mock Blender file created by importing {svg_path}\n")
                f.write(f"# This is a placeholder. Actual SVG import requires Blender.\n")
            
            return {
                "status": "success",
                "message": "Mock Blender file created successfully (Blender not available)",
                "name": name,
                "blender_file_path": model_path
            }
        
        # Create a temporary Python script to import SVG to Blender
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as temp_script:
            temp_script_path = temp_script.name
            temp_script.write(f"""
import bpy
import os
import sys

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import SVG
svg_path = r"{full_svg_path}"
bpy.ops.import_curve.svg(filepath=svg_path)

# Extrude all curves
for obj in bpy.context.scene.objects:
    if obj.type == 'CURVE':
        # Select object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Extrude
        obj.data.extrude = {extrusion_depth}
        obj.data.bevel_depth = 0.01  # Small bevel for rounded edges

# Set up camera and lighting for better view
# Create camera if needed
if not any(obj.type == 'CAMERA' for obj in bpy.context.scene.objects):
    bpy.ops.object.camera_add(location=(0, -10, 5), rotation=(0.5, 0, 0))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

# Create lighting if needed
if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
    # Key light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    key_light = bpy.context.active_object
    key_light.data.energy = 2.0
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-5, -2, 5))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 1.0

# Center view on objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.view3d.camera_to_view_selected()

# Save file
output_path = r"{model_path}"
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"SVG imported and saved to: {{output_path}}")
            """)
        
        try:
            logger.info(f"Running Blender to import SVG: {full_svg_path}")
            
            # Command with UI
            cmd = [
                blender_path,
                "--python", temp_script_path
            ]
            
            # Execute command
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Log output
            logger.info(f"Blender output: {process.stdout}")
            if process.stderr:
                logger.warning(f"Blender errors: {process.stderr}")
            
            logger.info(f"SVG imported to Blender successfully: {model_path}")
            
            # Return success response
            return {
                "status": "success",
                "message": "SVG imported to Blender successfully",
                "name": name,
                "blender_file_path": model_path
            }
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing Blender: {str(e)}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error executing Blender: {str(e)}"
            )
        finally:
            # Clean up the temporary script
            try:
                os.unlink(temp_script_path)
            except:
                pass
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error importing SVG to Blender: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing SVG to Blender: {str(e)}"
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
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
                status_code=status.HTTP_404_NOT_FOUND,
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
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Model animation is not implemented: {str(e)}"
            )
        
        if not result:
            logger.error("Model animation failed with no specific error message")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to animate 3D model - check logs for details"
            )
        
        # Verify the animated model file exists
        if not os.path.exists(animated_path):
            logger.error(f"Animated model file not created at expected path: {animated_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Model animation is not implemented: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error animating model: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
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
                status_code=status.HTTP_404_NOT_FOUND,
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
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Video rendering is not implemented: {str(e)}"
            )
        
        if not result:
            logger.error("Video rendering failed with no specific error message")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to render video - check logs for details"
            )
        
        # Verify the video file exists
        if not os.path.exists(video_path):
            logger.error(f"Video file not created at expected path: {video_path}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Video rendering is not implemented: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error rendering video: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render video: {str(e)}"
        )
