"""
Verify No Mock Implementations Script

This script checks the SVG to Video pipeline to ensure that all mock implementations
have been removed and proper error handling is in place.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(project_root))

def check_module_for_mocks(module_path, module_name):
    """
    Check a module for mock implementations or fallbacks
    """
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Checking {module_name} for mock implementations...")
        
        # Look for indicators of mock implementations
        mock_indicators = [
            "# TODO: Implement",
            "# For now",
            "mock",
            "Mock",
            "fallback",
            "Fallback",
            "placeholder",
            "Placeholder",
            "simulate",
            "Simulate",
            "await asyncio.sleep(",
            "shutil.copy",
            "create a basic SVG"
        ]
        
        # Check for each indicator
        found_mocks = False
        for indicator in mock_indicators:
            if indicator in content:
                line_num = 1
                for line in content.split('\n'):
                    if indicator in line:
                        logger.warning(f"Potential mock found in {module_name} (line {line_num}): {line.strip()}")
                        found_mocks = True
                    line_num += 1
        
        if not found_mocks:
            logger.info(f"No mocks found in {module_name}")
            return True
        else:
            logger.error(f"Mock implementations found in {module_name}")
            return False
    
    except Exception as e:
        logger.error(f"Error checking {module_name}: {str(e)}")
        return False

def check_svg_to_video_pipeline():
    """
    Check the SVG to Video pipeline for mock implementations
    """
    try:
        module_checks = [
            (os.path.join(project_root, "genai_agent", "svg_to_video", "llm_integrations", "claude_direct.py"), "Claude Direct"),
            (os.path.join(project_root, "genai_agent", "svg_to_video", "animation.py"), "Animation"),
            (os.path.join(project_root, "genai_agent", "svg_to_video", "rendering.py"), "Rendering"),
            (os.path.join(project_root, "genai_agent_project", "web", "backend", "routes", "svg_generator_routes.py"), "SVG Generator Routes")
        ]
        
        all_clean = True
        for module_path, module_name in module_checks:
            if os.path.exists(module_path):
                if not check_module_for_mocks(module_path, module_name):
                    all_clean = False
            else:
                logger.warning(f"Module not found: {module_path}")
        
        return all_clean
    
    except Exception as e:
        logger.error(f"Error checking SVG to Video pipeline: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        logger.info("Verifying that all mock implementations have been removed...")
        
        if check_svg_to_video_pipeline():
            logger.info("All modules appear to be free of mock implementations")
            sys.exit(0)
        else:
            logger.error("Mock implementations found in one or more modules")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error verifying no mocks: {str(e)}")
        sys.exit(1)
