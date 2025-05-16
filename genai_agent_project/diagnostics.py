#!/usr/bin/env python
"""
GenAI Agent 3D - Diagnostic and Repair Tool

This script helps diagnose and repair common issues with the GenAI Agent 3D application,
particularly focusing on file path and directory access problems.
"""

import os
import sys
import platform
import logging
import subprocess
import yaml
import shutil
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("diagnostics")

def is_admin():
    """Check if script is running with admin/root privileges"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

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

def check_symlink(source, target):
    """Check if a symbolic link exists and points to the correct location"""
    if not os.path.exists(source):
        logger.warning(f"✗ Source directory does not exist: {source}")
        return False
        
    if os.path.exists(target):
        if os.path.islink(target) or (platform.system() == "Windows" and os.path.isdir(target) and not os.path.samefile(target, target)):
            # Get the actual target of the link
            try:
                if platform.system() == "Windows":
                    # On Windows, use the dir command to check junction target
                    import subprocess
                    result = subprocess.run(["dir", target, "/AL"], shell=True, capture_output=True, text=True)
                    for line in result.stdout.split("\n"):
                        if "[" in line and "]" in line:
                            actual_target = line.split("[")[1].split("]")[0]
                            break
                    else:
                        actual_target = "Unknown"
                else:
                    actual_target = os.readlink(target)
                
                if os.path.abspath(actual_target) == os.path.abspath(source):
                    logger.info(f"✓ Link exists and points to correct location: {target} -> {source}")
                    return True
                else:
                    logger.warning(f"✗ Link exists but points to wrong location: {target} -> {actual_target} (should be {source})")
                    return False
            except Exception as e:
                logger.error(f"✗ Error checking link target: {str(e)}")
                return False
        else:
            logger.warning(f"✗ Path exists but is not a link: {target}")
            return False
    else:
        logger.warning(f"✗ Link does not exist: {target}")
        return False

def create_symlink(source, target):
    """Create a symbolic link or directory junction"""
    if os.path.exists(target):
        logger.info(f"Removing existing link/directory: {target}")
        try:
            if os.path.islink(target) or os.path.isdir(target) and platform.system() == "Windows":
                # On Windows, rmdir removes both directories and junctions
                os.rmdir(target)
            else:
                # For regular files or Linux/Mac symlinks
                os.unlink(target)
        except Exception as e:
            logger.error(f"Error removing {target}: {str(e)}")
            return False
    
    try:
        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(target)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        if platform.system() == "Windows":
            # Use directory junction on Windows
            subprocess.run(["mklink", "/J", target, source], shell=True, check=True)
            logger.info(f"✓ Created directory junction: {target} -> {source}")
        else:
            # Use symbolic link on Linux/Mac
            os.symlink(source, target, target_is_directory=True)
            logger.info(f"✓ Created symbolic link: {target} -> {source}")
        return True
    except Exception as e:
        logger.error(f"✗ Error creating link from {source} to {target}: {str(e)}")
        return False

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

def fix_configuration(base_dir):
    """Fix configuration issues"""
    output_dir = os.path.join(base_dir, "output")
    genai_project_dir = os.path.join(base_dir, "genai_agent_project")
    web_backend_dir = os.path.join(genai_project_dir, "web", "backend")
    web_frontend_dir = os.path.join(genai_project_dir, "web", "frontend")
    
    # Ensure output directories exist
    subdirs = [
        "models", "scenes", "svg", "diagrams", "svg_to_video",
        os.path.join("svg_to_video", "svg"), os.path.join("svg_to_video", "models"),
        "blendergpt", "hunyuan", "trellis"
    ]
    
    os.makedirs(output_dir, exist_ok=True)
    for subdir in subdirs:
        subdir_path = os.path.join(output_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)
    
    # Update config.yaml
    config_path = os.path.join(genai_project_dir, "config.yaml")
    config_backup_path = os.path.join(genai_project_dir, "config.backup.yaml")
    
    try:
        # Make a backup of the current config
        if os.path.exists(config_path):
            shutil.copy2(config_path, config_backup_path)
            logger.info(f"✓ Created backup of config file: {config_backup_path}")
        
        # Load current config or create a new one
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        
        # Ensure paths section exists
        if 'paths' not in config:
            config['paths'] = {}
        
        # Update paths
        paths_config = config['paths']
        paths_config['output_dir'] = output_dir
        paths_config['models_output_dir'] = os.path.join(output_dir, "models")
        paths_config['scenes_output_dir'] = os.path.join(output_dir, "scenes")
        paths_config['svg_output_dir'] = os.path.join(output_dir, "svg")
        paths_config['diagrams_output_dir'] = os.path.join(output_dir, "diagrams")
        paths_config['svg_to_video_dir'] = os.path.join(output_dir, "svg_to_video")
        paths_config['svg_to_video_svg_dir'] = os.path.join(output_dir, "svg_to_video", "svg")
        paths_config['svg_to_video_models_dir'] = os.path.join(output_dir, "svg_to_video", "models")
        paths_config['blendergpt_output_dir'] = os.path.join(output_dir, "blendergpt")
        paths_config['hunyuan_output_dir'] = os.path.join(output_dir, "hunyuan")
        paths_config['trellis_output_dir'] = os.path.join(output_dir, "trellis")
        
        # Write updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"✓ Updated config file: {config_path}")
        return True
    except Exception as e:
        logger.error(f"✗ Error updating config file: {str(e)}")
        return False

def create_symbolic_links(base_dir):
    """Create symbolic links for directory access"""
    output_dir = os.path.join(base_dir, "output")
    genai_project_dir = os.path.join(base_dir, "genai_agent_project")
    web_backend_dir = os.path.join(genai_project_dir, "web", "backend")
    web_frontend_dir = os.path.join(genai_project_dir, "web", "frontend")
    
    # Define links to create
    links = [
        (output_dir, os.path.join(genai_project_dir, "output")),
        (output_dir, os.path.join(web_backend_dir, "output")),
        (output_dir, os.path.join(web_frontend_dir, "public", "output"))
    ]
    
    success = True
    for source, target in links:
        if not create_symlink(source, target):
            success = False
    
    return success

def run_diagnostics():
    """Run diagnostics for the GenAI Agent 3D application"""
    logger.info("=" * 80)
    logger.info("GenAI Agent 3D - Diagnostics Tool")
    logger.info("=" * 80)
    
    base_dir = "C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d" if platform.system() == "Windows" else "/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d"
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
    
    logger.info("\nChecking symbolic links...")
    links_ok = (
        check_symlink(output_dir, os.path.join(genai_project_dir, "output")) and
        check_symlink(output_dir, os.path.join(web_backend_dir, "output")) and
        check_symlink(output_dir, os.path.join(web_frontend_dir, "public", "output"))
    )
    
    if not links_ok:
        logger.warning("✗ Symbolic links check failed.")
    
    logger.info("\nChecking configuration...")
    config_path = os.path.join(genai_project_dir, "config.yaml")
    config_ok = check_config(config_path)
    
    if not config_ok:
        logger.warning("✗ Configuration check failed.")
    
    # Overall status
    logger.info("\n" + "=" * 80)
    if not (directories_ok and output_dirs_ok and links_ok and config_ok):
        logger.warning("✗ Diagnostics completed with errors. Run with --fix to attempt automatic repairs.")
        return False
    else:
        logger.info("✓ All diagnostics passed!")
        return True

def fix_issues():
    """Fix common issues"""
    logger.info("=" * 80)
    logger.info("GenAI Agent 3D - Automatic Repair Tool")
    logger.info("=" * 80)
    
    base_dir = "C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d" if platform.system() == "Windows" else "/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d"
    
    logger.info("\nFixing configuration...")
    config_ok = fix_configuration(base_dir)
    
    logger.info("\nCreating symbolic links...")
    links_ok = create_symbolic_links(base_dir)
    
    # Overall status
    logger.info("\n" + "=" * 80)
    if not (config_ok and links_ok):
        logger.warning("✗ Some repairs failed. Please check the logs and try again.")
        return False
    else:
        logger.info("✓ All repairs completed successfully!")
        return True

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="GenAI Agent 3D - Diagnostic and Repair Tool")
    parser.add_argument("--fix", action="store_true", help="Fix common issues")
    args = parser.parse_args()
    
    if not is_admin() and args.fix:
        logger.error("This script must be run with administrator/root privileges to fix issues.")
        if platform.system() == "Windows":
            logger.info("Please run as administrator.")
        else:
            logger.info("Please run with sudo.")
        return 1
    
    try:
        if args.fix:
            success = fix_issues()
            
            # Run diagnostics after fixing to verify
            logger.info("\nRunning diagnostics to verify repairs...")
            diagnostics_ok = run_diagnostics()
            
            if not (success and diagnostics_ok):
                logger.warning("✗ Some issues could not be repaired automatically.")
                return 1
        else:
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
