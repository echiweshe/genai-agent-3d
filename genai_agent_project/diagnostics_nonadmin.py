#!/usr/bin/env python
"""
GenAI Agent 3D - Diagnostic Tool (Non-Admin Version)

This script helps diagnose common issues with the GenAI Agent 3D application,
particularly focusing on file path and directory access problems.
This version doesn't require administrator privileges.
"""

import os
import sys
import platform
import logging
import yaml
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("diagnostics")

def check_directory_exists(path, create=False):
    """Check if a directory exists and optionally create it"""
    if os.path.exists(path):
        if os.path.isdir(path):
            logger.info(f"✓ Directory exists: {path}")
            return True
        else:
            logger.warning(f"✗ Path exists but is not a directory: {path}")
            return False
    else:
        if create:
            try:
                os.makedirs(path, exist_ok=True)
                logger.info(f"✓ Created directory: {path}")
                return True
            except Exception as e:
                logger.error(f"✗ Failed to create directory {path}: {str(e)}")
                return False
        else:
            logger.warning(f"✗ Directory does not exist: {path}")
            return False

def check_reference_dir(main_dir, reference_dir):
    """Check if a reference directory exists and contains the expected README file"""
    if not os.path.exists(reference_dir):
        logger.warning(f"✗ Reference directory does not exist: {reference_dir}")
        return False
    
    readme_path = os.path.join(reference_dir, "README.txt")
    if os.path.exists(readme_path):
        # Check if README contains the correct path
        with open(readme_path, 'r') as f:
            content = f.read()
            if main_dir in content:
                logger.info(f"✓ Reference directory properly set up: {reference_dir}")
                return True
            else:
                logger.warning(f"✗ Reference directory has incorrect README: {reference_dir}")
                return False
    else:
        # No README, check if files exist
        files_match = check_files_match(main_dir, reference_dir)
        if files_match:
            logger.info(f"✓ Reference directory appears to contain correct files: {reference_dir}")
            return True
        else:
            logger.warning(f"✗ Reference directory may not be synchronized: {reference_dir}")
            return False

def check_files_match(dir1, dir2, max_check=5):
    """Check if two directories contain matching files (up to max_check files)"""
    if not (os.path.exists(dir1) and os.path.exists(dir2)):
        return False
    
    # Get a list of files in the first directory
    dir1_files = []
    for root, dirs, files in os.walk(dir1):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), dir1)
            dir1_files.append(rel_path)
            if len(dir1_files) >= max_check:
                break
        if len(dir1_files) >= max_check:
            break
    
    # Check if these files exist in the second directory
    matches = 0
    for rel_path in dir1_files:
        if os.path.exists(os.path.join(dir2, rel_path)):
            matches += 1
    
    # Return true if at least half the files match
    return matches >= min(len(dir1_files) // 2, 1)

def check_file_access(path):
    """Check if a file can be read and written to"""
    if not os.path.exists(path):
        logger.warning(f"✗ File does not exist: {path}")
        return False
    
    try:
        if os.access(path, os.R_OK):
            logger.info(f"✓ File can be read: {path}")
        else:
            logger.warning(f"✗ File cannot be read: {path}")
            return False
        
        if os.access(path, os.W_OK):
            logger.info(f"✓ File can be written to: {path}")
        else:
            logger.warning(f"✗ File cannot be written to: {path}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"✗ Error checking file access for {path}: {str(e)}")
        return False

def check_config(config_path):
    """Check if the config file is valid and has the required paths"""
    if not os.path.exists(config_path):
        logger.warning(f"✗ Config file does not exist: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config:
            logger.warning(f"✗ Config file is empty: {config_path}")
            return False
        
        # Check if paths section exists
        if 'paths' not in config:
            logger.warning(f"✗ Config file missing 'paths' section: {config_path}")
            return False
        
        # Check required paths
        required_paths = [
            'output_dir',
            'models_output_dir',
            'scenes_output_dir',
            'svg_output_dir',
            'diagrams_output_dir'
        ]
        
        missing_paths = []
        for path in required_paths:
            if path not in config['paths']:
                missing_paths.append(path)
        
        if missing_paths:
            logger.warning(f"✗ Config file missing required paths: {', '.join(missing_paths)}")
            return False
        
        logger.info(f"✓ Config file valid: {config_path}")
        return True
    except Exception as e:
        logger.error(f"✗ Error reading config file {config_path}: {str(e)}")
        return False

def run_diagnostics():
    """Run diagnostics for the GenAI Agent 3D application"""
    logger.info("=" * 80)
    logger.info("GenAI Agent 3D - Diagnostics Tool (Non-Admin Version)")
    logger.info("=" * 80)
    
    base_dir = "C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d"
    genai_project_dir = os.path.join(base_dir, "genai_agent_project")
    web_backend_dir = os.path.join(genai_project_dir, "web", "backend")
    web_frontend_dir = os.path.join(genai_project_dir, "web", "frontend")
    
    logger.info("Checking base directories...")
    directories_ok = (
        check_directory_exists(base_dir) and
        check_directory_exists(genai_project_dir) and
        check_directory_exists(web_backend_dir) and
        check_directory_exists(web_frontend_dir)
    )
    
    if not directories_ok:
        logger.error("✗ Base directories check failed.")
        return False
    
    logger.info("\nChecking output directories...")
    output_dir = os.path.join(base_dir, "output")
    output_dirs_ok = (
        check_directory_exists(output_dir, create=True) and
        check_directory_exists(os.path.join(output_dir, "models"), create=True) and
        check_directory_exists(os.path.join(output_dir, "scenes"), create=True) and
        check_directory_exists(os.path.join(output_dir, "svg"), create=True) and
        check_directory_exists(os.path.join(output_dir, "diagrams"), create=True) and
        check_directory_exists(os.path.join(output_dir, "svg_to_video"), create=True)
    )
    
    if not output_dirs_ok:
        logger.warning("✗ Output directories check failed.")
    
    logger.info("\nChecking reference directories...")
    references_ok = (
        check_reference_dir(output_dir, os.path.join(genai_project_dir, "output")) and
        check_reference_dir(output_dir, os.path.join(web_backend_dir, "output")) and
        check_reference_dir(output_dir, os.path.join(web_frontend_dir, "public", "output"))
    )
    
    if not references_ok:
        logger.warning("✗ Reference directories check failed.")
    
    logger.info("\nChecking configuration...")
    config_path = os.path.join(genai_project_dir, "config.yaml")
    config_ok = check_config(config_path)
    
    if not config_ok:
        logger.warning("✗ Configuration check failed.")
    
    # Overall status
    logger.info("\n" + "=" * 80)
    if not (directories_ok and output_dirs_ok and references_ok and config_ok):
        logger.warning("✗ Diagnostics completed with errors.")
        logger.info("Run 'python setup_directory_links_nonadmin.py' to fix issues.")
        logger.info("Then run 'python sync_output_dirs.py' to synchronize files.")
        return False
    else:
        logger.info("✓ All diagnostics passed!")
        return True

def main():
    """Main function"""
    try:
        if not run_diagnostics():
            return 1
        
        logger.info("\nDiagnostics completed successfully.")
        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
