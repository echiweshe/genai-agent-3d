#!/usr/bin/env python3
"""
Script to clean up duplicate files and optimize the project structure
"""

import os
import shutil
import logging
from env_loader import get_env, get_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Files to delete
files_to_delete = [
    "genai_agent/services/llm copy.py",
    "genai_agent/tools/ollama_helper copy.py",
    "genai_agent/tools/scene_generator copy.py",
    "genai_agent/tools/scene_generator copy 2.py"
]

def main():
    """Main cleanup function"""
    # Get the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Project root: {project_root}")
    
    # Delete unnecessary files
    for file_path in files_to_delete:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                logger.info(f"Deleted: {file_path}")
            except OSError as e:
                logger.error(f"Error deleting {file_path}: {e}")
        else:
            logger.warning(f"File not found: {file_path}")
    
    # Clean pycache directories
    for root, dirs, files in os.walk(project_root):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                    logger.info(f"Removed __pycache__ directory: {pycache_path}")
                except OSError as e:
                    logger.error(f"Error removing __pycache__ directory {pycache_path}: {e}")
    
    logger.info("Cleanup completed successfully!")

if __name__ == "__main__":
    main()
