"""
Environment variable checker for SVG to Video pipeline.

This module provides functions to check and set up environment variables.
"""

import os
import logging

logger = logging.getLogger(__name__)

def setup_env_variables():
    """
    Set up the necessary environment variables for the SVG to Video pipeline.
    
    Returns:
        bool: True if all required environment variables are set, False otherwise
    """
    required_vars = {
        "BLENDER_PATH": "Path to Blender executable",
    }
    
    optional_vars = {
        "ANTHROPIC_API_KEY": "API key for Claude (Anthropic)",
        "OPENAI_API_KEY": "API key for OpenAI"
    }
    
    # Check required variables
    missing_required = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_required.append(var)
            logger.warning(f"Missing required environment variable: {var} - {description}")
    
    # Check optional variables
    missing_optional = []
    for var, description in optional_vars.items():
        if not os.environ.get(var):
            missing_optional.append(var)
            logger.warning(f"Missing optional environment variable: {var} - {description}")
    
    # Log status
    if missing_required:
        logger.warning(f"Missing required environment variables: {', '.join(missing_required)}")
    else:
        logger.info("All required environment variables are set")
    
    if missing_optional:
        logger.warning(f"Missing optional environment variables: {', '.join(missing_optional)}")
    else:
        logger.info("All optional environment variables are set")
    
    # Check default paths for Blender
    if "BLENDER_PATH" in missing_required:
        blender_path = find_blender_executable()
        if blender_path:
            os.environ["BLENDER_PATH"] = blender_path
            logger.info(f"Found Blender at {blender_path}")
            missing_required.remove("BLENDER_PATH")
    
    return len(missing_required) == 0

def find_blender_executable():
    """
    Find the Blender executable in common locations.
    
    Returns:
        str: Path to the Blender executable or None if not found
    """
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
            return path
    
    return None

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Test the module
    setup_env_variables()
