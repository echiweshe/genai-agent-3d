#!/usr/bin/env python3
"""
Ensure Output Directories
-------------------------
This script ensures all output directories are properly set up and linked,
addressing the issue with multiple output directory locations.
"""

import os
import sys
import logging
import platform
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("OutputDirectories")

def ensure_directory_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured directory exists: {directory}")

def create_directory_symlink(source, target):
    """Create a directory symlink from source to target."""
    # Remove existing link or directory if it exists
    if os.path.exists(target):
        if os.path.islink(target):
            os.unlink(target)
            logger.info(f"Removed existing symlink: {target}")
        elif os.path.isdir(target):
            import shutil
            shutil.rmtree(target)
            logger.info(f"Removed existing directory: {target}")
        else:
            os.remove(target)
            logger.info(f"Removed existing file: {target}")
    
    # Create parent directory if needed
    parent_dir = os.path.dirname(target)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    
    # Create the symlink
    system = platform.system()
    
    if system == "Windows":
        # On Windows, use mklink command if running as administrator
        try:
            # First try directory junction for compatibility
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", target, source],
                check=True,
                capture_output=True
            )
            logger.info(f"Created directory junction: {source} -> {target}")
        except subprocess.CalledProcessError:
            # If that fails, try directory symbolic link (requires admin)
            try:
                subprocess.run(
                    ["cmd", "/c", "mklink", "/D", target, source],
                    check=True,
                    capture_output=True
                )
                logger.info(f"Created directory symlink: {source} -> {target}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to create symlink (admin required): {e}")
                return False
    else:
        # On Unix-like systems, use os.symlink
        try:
            os.symlink(source, target, target_is_directory=True)
            logger.info(f"Created directory symlink: {source} -> {target}")
        except Exception as e:
            logger.error(f"Failed to create symlink: {e}")
            return False
    
    return True

def setup_output_directories():
    """Set up and link all output directories."""
    project_root = Path(__file__).parent
    
    # Primary output directory - this will be our canonical location
    primary_output = project_root / "output"
    ensure_directory_exists(primary_output)
    
    # Project output directory
    project_output = project_root / "genai_agent_project" / "output"
    
    # Web backend output directory
    web_output = project_root / "genai_agent_project" / "web" / "backend" / "output"
    
    # Create symlinks
    success = True
    
    if project_output != primary_output:
        if not create_directory_symlink(primary_output, project_output):
            logger.warning(f"Could not link {primary_output} to {project_output}")
            success = False
    
    if web_output != primary_output:
        if not create_directory_symlink(primary_output, web_output):
            logger.warning(f"Could not link {primary_output} to {web_output}")
            success = False
    
    # Update config.yaml to use the correct output directory
    try:
        import yaml
        config_path = project_root / "genai_agent_project" / "config.yaml"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            # Ensure output directory is specified correctly
            config["OUTPUT_DIRECTORY"] = str(primary_output)
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info(f"Updated config to use output directory: {primary_output}")
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        success = False
    
    return success

def main():
    """Main function to set up output directories."""
    logger.info("Setting up output directories...")
    
    success = setup_output_directories()
    
    if success:
        logger.info("Output directories set up successfully")
    else:
        logger.error("Output directory setup completed with errors")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
