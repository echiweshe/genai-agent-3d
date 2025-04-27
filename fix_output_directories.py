#!/usr/bin/env python3
"""
Fix Output Directory Linking Issues

This script fixes the output directory linking issues in the GenAI Agent 3D project.
It ensures all output directories exist and creates proper symbolic links.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
import platform
import ctypes
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # For Unix systems, check if the effective user ID is 0 (root)
            return os.geteuid() == 0
    except:
        return False

def needs_admin():
    """Check if admin privileges are needed for this operation"""
    # On Windows, creating symbolic links typically requires admin privileges
    # On Unix systems, it depends on the user's permissions
    return platform.system() == 'Windows' and not is_admin()

def restart_as_admin():
    """Restart the script with administrator privileges"""
    if platform.system() == 'Windows':
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    else:
        logger.error("Please run this script with sudo on Unix systems if you encounter permission issues.")
        sys.exit(1)

def ensure_output_directories(project_root):
    """Ensure all output directories exist"""
    logger.info("Ensuring output directories exist...")
    
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Create standard output directories
    subdirs = [
        "models",
        "scenes",
        "diagrams",
        "svg",
        "blendergpt",
        "hunyuan",
        "trellis",
        "temp"
    ]
    
    for subdir in subdirs:
        subdir_path = output_dir / subdir
        subdir_path.mkdir(exist_ok=True)
        logger.info(f"Ensured directory exists: {subdir_path}")
    
    return output_dir

def create_symlinks(project_root, output_dir):
    """Create symbolic links for output directories"""
    logger.info("Creating symbolic links...")
    
    # Directories to link in the frontend/public directory
    frontend_dirs = [
        "models",
        "scenes",
        "diagrams",
        "svg"
    ]
    
    frontend_public_dir = project_root / "genai_agent_project" / "web" / "frontend" / "public"
    
    # Make sure the frontend/public directory exists
    if not frontend_public_dir.exists():
        logger.warning(f"Frontend public directory does not exist: {frontend_public_dir}")
        logger.info("Creating frontend public directory...")
        frontend_public_dir.mkdir(exist_ok=True, parents=True)
    
    # Create symbolic links in the frontend/public directory
    success = True
    for subdir in frontend_dirs:
        target_path = output_dir / subdir
        link_path = frontend_public_dir / subdir
        
        try:
            # Check if the link already exists and points to the correct target
            if link_path.exists():
                if link_path.is_symlink() and link_path.resolve() == target_path.resolve():
                    logger.info(f"Symbolic link already exists and is correct: {link_path} -> {target_path}")
                    continue
                
                # Remove existing link or directory
                if link_path.is_symlink():
                    logger.info(f"Removing existing symbolic link: {link_path}")
                    link_path.unlink()
                else:
                    logger.info(f"Removing existing directory: {link_path}")
                    shutil.rmtree(link_path)
            
            # Create the symbolic link
            logger.info(f"Creating symbolic link: {link_path} -> {target_path}")
            link_path.symlink_to(target_path, target_is_directory=True)
            logger.info(f"Successfully created symbolic link: {link_path} -> {target_path}")
            
        except OSError as e:
            logger.error(f"Failed to create symbolic link {link_path} -> {target_path}: {str(e)}")
            if "privilege" in str(e).lower() or "permission" in str(e).lower():
                logger.error("This operation requires administrator privileges.")
                success = False
            else:
                success = False
    
    return success

def create_alternative_links(project_root, output_dir):
    """Create alternative links (copies) if symbolic links fail"""
    logger.info("Creating alternative directory copies...")
    
    # Directories to copy to the frontend/public directory
    frontend_dirs = [
        "models",
        "scenes",
        "diagrams",
        "svg"
    ]
    
    frontend_public_dir = project_root / "genai_agent_project" / "web" / "frontend" / "public"
    
    # Create directory copies
    for subdir in frontend_dirs:
        target_path = output_dir / subdir
        copy_path = frontend_public_dir / subdir
        
        try:
            # Remove existing directory if it exists
            if copy_path.exists():
                if copy_path.is_dir() and not copy_path.is_symlink():
                    logger.info(f"Removing existing directory: {copy_path}")
                    shutil.rmtree(copy_path)
                else:
                    logger.info(f"Removing existing link: {copy_path}")
                    copy_path.unlink()
            
            # Create the directory
            logger.info(f"Creating directory: {copy_path}")
            copy_path.mkdir(exist_ok=True)
            
            # Create a README explaining this is a copy
            readme_path = copy_path / "README.txt"
            with open(readme_path, 'w') as f:
                f.write(f"""This directory is a copy of {target_path}.
It was created because symbolic links could not be established.
Files generated in the output directory will need to be manually copied here for preview.
""")
            
            logger.info(f"Created directory and README: {copy_path}")
            
        except OSError as e:
            logger.error(f"Failed to create directory {copy_path}: {str(e)}")
    
    logger.warning("Using directory copies instead of symbolic links.")
    logger.warning("You will need to manually copy files from the output directory to these directories for preview.")

def check_links(project_root):
    """Check if the symbolic links are working correctly"""
    logger.info("Checking symbolic links...")
    
    frontend_public_dir = project_root / "genai_agent_project" / "web" / "frontend" / "public"
    output_dir = project_root / "output"
    
    # Directories to check
    frontend_dirs = [
        "models",
        "scenes",
        "diagrams",
        "svg"
    ]
    
    all_links_ok = True
    for subdir in frontend_dirs:
        link_path = frontend_public_dir / subdir
        target_path = output_dir / subdir
        
        if not link_path.exists():
            logger.error(f"Link does not exist: {link_path}")
            all_links_ok = False
            continue
        
        if not link_path.is_symlink():
            logger.warning(f"Not a symbolic link (directory copy): {link_path}")
            continue
        
        # Check if the link points to the correct target
        try:
            resolved_path = link_path.resolve()
            if resolved_path != target_path.resolve():
                logger.error(f"Link points to wrong target: {link_path} -> {resolved_path} (expected {target_path})")
                all_links_ok = False
            else:
                logger.info(f"Link is correct: {link_path} -> {target_path}")
        except Exception as e:
            logger.error(f"Error checking link {link_path}: {str(e)}")
            all_links_ok = False
    
    return all_links_ok

def create_test_files(project_root):
    """Create test files in the output directories to verify access"""
    logger.info("Creating test files...")
    
    output_dir = project_root / "output"
    
    # Directories to test
    test_dirs = [
        "models",
        "scenes",
        "diagrams",
        "svg"
    ]
    
    # Create a test file in each directory
    for subdir in test_dirs:
        test_file_path = output_dir / subdir / "test_file.txt"
        
        try:
            with open(test_file_path, 'w') as f:
                f.write(f"Test file created at {test_file_path} on {datetime.datetime.now().isoformat()}")
            
            logger.info(f"Created test file: {test_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to create test file {test_file_path}: {str(e)}")

def update_config(project_root, output_dir):
    """Update configuration files to use the correct output paths"""
    logger.info("Updating configuration files...")
    
    # Update .env file
    env_path = project_root / "genai_agent_project" / ".env"
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Update output directory paths
            output_dir_str = str(output_dir).replace('\\', '/')
            
            # Update OUTPUT_DIR
            content = re.sub(
                r'OUTPUT_DIR=.*',
                f'OUTPUT_DIR={output_dir_str}',
                content
            )
            
            # Update subdirectory paths
            for subdir in ["BLENDERGPT", "DIAGRAMS", "HUNYUAN", "MODELS", "SCENES", "SVG", "TRELLIS"]:
                content = re.sub(
                    f'{subdir}_OUTPUT_DIR=.*',
                    f'{subdir}_OUTPUT_DIR={output_dir_str}/{subdir.lower()}',
                    content
                )
            
            with open(env_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Updated .env file: {env_path}")
        except Exception as e:
            logger.error(f"Failed to update .env file: {str(e)}")
    
    # Update config.yaml if it exists
    config_path = project_root / "genai_agent_project" / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update output directory paths
            output_dir_str = str(output_dir).replace('\\', '/')
            
            if 'paths' not in config:
                config['paths'] = {}
            
            config['paths']['output_dir'] = output_dir_str
            
            # Update subdirectory paths
            subdirs = {
                "blendergpt_output_dir": f"{output_dir_str}/blendergpt",
                "diagrams_output_dir": f"{output_dir_str}/diagrams",
                "hunyuan_output_dir": f"{output_dir_str}/hunyuan",
                "models_output_dir": f"{output_dir_str}/models",
                "scenes_output_dir": f"{output_dir_str}/scenes",
                "svg_output_dir": f"{output_dir_str}/svg",
                "trellis_output_dir": f"{output_dir_str}/trellis"
            }
            
            for key, value in subdirs.items():
                config['paths'][key] = value
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info(f"Updated config.yaml file: {config_path}")
        except Exception as e:
            logger.error(f"Failed to update config.yaml file: {str(e)}")

def main():
    """Main function"""
    import datetime
    import re
    
    # Get project root
    project_root = Path(__file__).parent.absolute()
    
    print("===========================================")
    print("  Fix Output Directory Linking - GenAI Agent 3D")
    print("===========================================")
    print(f"Project root: {project_root}")
    
    # Check if admin privileges are needed
    if needs_admin():
        logger.warning("Creating symbolic links on Windows requires administrator privileges.")
        response = input("Would you like to restart this script with administrator privileges? (y/n): ").lower()
        if response == 'y':
            restart_as_admin()
        else:
            logger.warning("Continuing without administrator privileges. Symbolic links may fail.")
    
    # Ensure output directories exist
    output_dir = ensure_output_directories(project_root)
    
    # Try to create symbolic links
    symlinks_success = create_symlinks(project_root, output_dir)
    
    # If symbolic links failed, create directory copies as an alternative
    if not symlinks_success:
        create_alternative_links(project_root, output_dir)
    
    # Check if the links are working correctly
    links_ok = check_links(project_root)
    
    # Create test files in the output directories
    create_test_files(project_root)
    
    # Update configuration files
    update_config(project_root, output_dir)
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Output directories created: {output_dir}")
    print(f"Symbolic links created: {'Success' if symlinks_success else 'Failed'}")
    print(f"Link verification: {'Passed' if links_ok else 'Failed'}")
    
    if not symlinks_success or not links_ok:
        print("\n⚠️ Some operations failed. This may affect content preview in the web interface.")
        print("Manual intervention may be required to ensure proper file access.")
    else:
        print("\n✅ Output directory linking has been fixed successfully!")
    
    # Provide instructions for restarting services
    print("\nTo apply these changes, restart the services:")
    print("python restart_services.py")
    
    return 0 if symlinks_success and links_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
