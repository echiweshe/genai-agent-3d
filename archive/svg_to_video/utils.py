"""
Utility Functions for SVG to Video Pipeline

This module provides utility functions for the SVG to Video pipeline.
"""

import os
import sys
import shutil
import logging
from typing import Optional
from fastapi import UploadFile

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: The path to the directory to ensure exists
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")

def save_uploaded_file(file: UploadFile, destination: str) -> str:
    """
    Save an uploaded file to a destination path.
    
    Args:
        file: The uploaded file
        destination: The destination path
        
    Returns:
        The path to the saved file
    """
    # Ensure the destination directory exists
    ensure_directory_exists(os.path.dirname(destination))
    
    # Save the file
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return destination

def load_dotenv_from_parent() -> None:
    """
    Load environment variables from the .env file in the parent directory.
    """
    from dotenv import load_dotenv
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(parent_dir, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning(f".env file not found at {env_path}")
