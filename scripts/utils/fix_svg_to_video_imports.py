"""
Fix SVG to Video Imports

This script fixes import issues in the SVG to Video pipeline.
It updates the import paths to use the modularized structure.
"""

import os
import sys
import importlib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("fix_svg_to_video_imports")

def fix_imports():
    """Fix import issues in the SVG to Video pipeline."""
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    logger.info(f"Project root: {project_root}")
    
    # Add project root to Python path if not there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"Added {project_root} to Python path")
    
    # Force reload of modules to clear cache
    logger.info("Reloading modules...")
    
    # First, try to clear modules from cache
    modules_to_clear = []
    for name in list(sys.modules.keys()):
        if 'svg_to_video' in name or 'svg_to_3d' in name:
            modules_to_clear.append(name)
    
    for name in modules_to_clear:
        if name in sys.modules:
            del sys.modules[name]
            logger.info(f"Removed {name} from sys.modules cache")
    
    # Now try to import the modules in the correct order
    try:
        # Import SVG Generator
        logger.info("Importing SVG Generator...")
        from genai_agent.svg_to_video.svg_generator import SVGGenerator
        logger.info("SVG Generator imported successfully")
        
        # Import SVG to 3D Converter
        logger.info("Importing SVG to 3D Converter...")
        from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter
        logger.info("SVG to 3D Converter imported successfully")
        
        # Import Animation System
        logger.info("Importing Animation System...")
        from genai_agent.svg_to_video.animation import AnimationSystem
        logger.info("Animation System imported successfully")
        
        # Import Video Renderer
        logger.info("Importing Video Renderer...")
        from genai_agent.svg_to_video.rendering import VideoRenderer
        logger.info("Video Renderer imported successfully")
        
        # Import Pipeline
        logger.info("Importing Pipeline...")
        from genai_agent.svg_to_video.pipeline_integrated import SVGToVideoPipeline
        logger.info("Pipeline imported successfully")
        
        logger.info("All imports successful!")
        return True
    
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Failed to import modules")
        return False
    
    except IndentationError as e:
        logger.error(f"Indentation error: {str(e)}")
        logger.error("There is an indentation error in one of the modules")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error("Failed to fix imports")
        return False

if __name__ == "__main__":
    success = fix_imports()
    sys.exit(0 if success else 1)
