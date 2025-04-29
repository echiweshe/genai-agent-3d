"""
SVG to Video Utilities

This module provides utility functions for the SVG to Video pipeline.
"""

import re
import os
import logging
import tempfile
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

def validate_svg(svg_content: str) -> Tuple[bool, str]:
    """
    Validate SVG content for security and correctness.
    
    Args:
        svg_content: SVG content to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Check for basic SVG structure
    if not svg_content.strip().startswith("<svg") or "</svg>" not in svg_content:
        return False, "Invalid SVG structure: missing <svg> tags"
    
    try:
        # Check for script tags (security risk)
        if re.search(r'<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>', svg_content, re.IGNORECASE):
            return False, "SVG contains script elements, which are not allowed"
        
        # Check for external references (security risk)
        if re.search(r'href\s*=\s*["\'](?:https?:|data:|javascript:)', svg_content, re.IGNORECASE):
            return False, "SVG contains external references, which are not allowed"
        
        # SVG seems valid and safe
        return True, "SVG is valid"
        
    except Exception as e:
        logger.error(f"Error validating SVG: {str(e)}")
        return False, f"Error validating SVG: {str(e)}"

def create_temp_file(content: str, suffix: str = ".svg") -> str:
    """
    Create a temporary file with the given content.
    
    Args:
        content: Content to write to the file
        suffix: File suffix
        
    Returns:
        Path to the temporary file
    """
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return temp_path
    except Exception as e:
        # Clean up if an error occurs
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

def check_blender_installation(blender_path: str = "blender") -> Tuple[bool, str]:
    """
    Check if Blender is installed and available.
    
    Args:
        blender_path: Path to the Blender executable
        
    Returns:
        Tuple of (is_available, version_info)
    """
    import subprocess
    
    try:
        result = subprocess.run(
            [blender_path, "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            version_info = result.stdout.strip()
            return True, version_info
        else:
            return False, f"Blender returned error code: {result.returncode}"
    
    except FileNotFoundError:
        return False, f"Blender executable not found at: {blender_path}"
    except subprocess.TimeoutExpired:
        return False, "Checking Blender version timed out"
    except Exception as e:
        return False, f"Error checking Blender installation: {str(e)}"

def ensure_directory_exists(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to check/create
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")
