import os
import sys
import shutil
import logging
from pathlib import Path
import fileinput
import re

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define paths
PROJECT_ROOT = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d")
MAIN_SVG_PATH = PROJECT_ROOT / "genai_agent" / "svg_to_video"
PROJECT_SVG_PATH = PROJECT_ROOT / "genai_agent_project" / "genai_agent" / "svg_to_video"
TEST_OUTPUT_PATH = PROJECT_ROOT / "genai_agent_project" / "output" / "svg"
WEB_UI_OUTPUT_PATH = PROJECT_ROOT / "output" / "svg_to_video" / "svg"

# Output path to consolidate to
CONSOLIDATED_OUTPUT_PATH = PROJECT_ROOT / "output" / "svg"

def backup_directory(path, backup_suffix="_backup"):
    """Create a backup of a directory."""
    if not os.path.isdir(path):
        logger.warning(f"Cannot backup non-existent directory: {path}")
        return False
    
    backup_path = str(path) + backup_suffix
    if os.path.exists(backup_path):
        logger.warning(f"Backup already exists: {backup_path}")
        # Add timestamp to make it unique
        import time
        backup_path = f"{str(path)}_{int(time.time())}_backup"
    
    try:
        shutil.copytree(path, backup_path)
        logger.info(f"Created backup at: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return False

def update_file_paths(file_path, old_path_pattern, new_path):
    """Update path references in files."""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace paths
        new_content = re.sub(
            r'["\'](?:.*?)(output[\\/]svg_to_video[\\/]svg|genai_agent_project[\\/]output[\\/]svg)["\']', 
            f'"{new_path}"', 
            content
        )
        
        # Write updated content back if changes were made
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"Updated paths in: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating paths in {file_path}: {str(e)}")
        return False

def update_all_file_paths():
    """Update all file paths in the codebase."""
    # Find all Python files in the project
    python_files = []
    for root, dirs, files in os.walk(str(PROJECT_ROOT / "genai_agent_project")):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Update paths in each file
    updated_count = 0
    for file_path in python_files:
        if update_file_paths(file_path, r'output[\\/]svg_to_video[\\/]svg|genai_agent_project[\\/]output[\\/]svg', str(CONSOLIDATED_OUTPUT_PATH)):
            updated_count += 1
    
    logger.info(f"Updated paths in {updated_count} files")
    return updated_count > 0

def copy_files(source_dir, target_dir):
    """Copy files from source to target directory."""
    if not os.path.isdir(source_dir):
        logger.warning(f"Source directory does not exist: {source_dir}")
        return 0
    
    # Check if directories are the same or symlinked
    try:
        source_real = os.path.realpath(source_dir)
        target_real = os.path.realpath(target_dir)
        
        if source_real == target_real:
            logger.info(f"Source and target directories are the same (or symlinked): {source_real}")
            return 0
    except Exception as e:
        logger.warning(f"Error checking real paths: {str(e)}")
    
    os.makedirs(target_dir, exist_ok=True)
    
    copied_count = 0
    skipped_count = 0
    
    for item in os.listdir(source_dir):
        source = os.path.join(source_dir, item)
        target = os.path.join(target_dir, item)
        
        if os.path.isfile(source):
            try:
                if not os.path.exists(target):
                    shutil.copy2(source, target)
                    logger.info(f"Copied {source} to {target}")
                    copied_count += 1
                else:
                    # Files already exist, compare content to avoid unnecessary copies
                    with open(source, 'rb') as f1, open(target, 'rb') as f2:
                        if f1.read() == f2.read():
                            logger.info(f"Skipped identical file: {source}")
                            skipped_count += 1
                        else:
                            # Backup and replace
                            backup = f"{target}.bak"
                            shutil.copy2(target, backup)
                            logger.info(f"Backed up different file to {backup}")
                            shutil.copy2(source, target)
                            logger.info(f"Updated {target}")
                            copied_count += 1
            except shutil.SameFileError:
                logger.info(f"Skipped same file: {source}")
                skipped_count += 1
            except Exception as e:
                logger.error(f"Error copying {source} to {target}: {str(e)}")
    
    logger.info(f"Copied {copied_count} files, skipped {skipped_count} files")
    return copied_count

def update_routes():
    """Update any API routes that reference the old paths."""
    routes_file = PROJECT_ROOT / "genai_agent_project" / "genai_agent" / "svg_to_video" / "svg_generator_routes.py"
    
    if os.path.isfile(routes_file):
        logger.info(f"Updating routes file: {routes_file}")
        return update_file_paths(routes_file, r'output[\\/]svg_to_video[\\/]svg|genai_agent_project[\\/]output[\\/]svg', str(CONSOLIDATED_OUTPUT_PATH))
    else:
        logger.warning(f"Routes file not found: {routes_file}")
        return False

def consolidate_output_directories():
    """Consolidate output directories into a single path."""
    # Check if output directories are already symlinks
    if os.path.islink(str(WEB_UI_OUTPUT_PATH)):
        logger.info(f"Web UI output path is already a symlink pointing to: {os.readlink(str(WEB_UI_OUTPUT_PATH))}")
        web_ui_is_symlink = True
    else:
        web_ui_is_symlink = False
    
    if os.path.islink(str(TEST_OUTPUT_PATH)):
        logger.info(f"Test output path is already a symlink pointing to: {os.readlink(str(TEST_OUTPUT_PATH))}")
        test_is_symlink = True
    else:
        test_is_symlink = False
    
    # Create consolidated output directory
    os.makedirs(CONSOLIDATED_OUTPUT_PATH, exist_ok=True)
    logger.info(f"Created consolidated output directory: {CONSOLIDATED_OUTPUT_PATH}")
    
    # Copy files from directories that are not symlinks
    web_ui_copied = 0
    test_copied = 0
    
    if not web_ui_is_symlink and os.path.isdir(WEB_UI_OUTPUT_PATH):
        web_ui_copied = copy_files(WEB_UI_OUTPUT_PATH, CONSOLIDATED_OUTPUT_PATH)
    
    if not test_is_symlink and os.path.isdir(TEST_OUTPUT_PATH):
        test_copied = copy_files(TEST_OUTPUT_PATH, CONSOLIDATED_OUTPUT_PATH)
    
    logger.info(f"Copied {web_ui_copied} files from Web UI output and {test_copied} files from Test output")
    
    # Only remove directories that are not symlinks and if we copied files
    if web_ui_copied > 0 and not web_ui_is_symlink:
        if backup_directory(WEB_UI_OUTPUT_PATH):
            try:
                shutil.rmtree(WEB_UI_OUTPUT_PATH)
                logger.info(f"Removed old Web UI output directory: {WEB_UI_OUTPUT_PATH}")
            except Exception as e:
                logger.error(f"Failed to remove Web UI output directory: {str(e)}")
    
    if test_copied > 0 and not test_is_symlink:
        if backup_directory(TEST_OUTPUT_PATH):
            try:
                shutil.rmtree(TEST_OUTPUT_PATH)
                logger.info(f"Removed old Test output directory: {TEST_OUTPUT_PATH}")
            except Exception as e:
                logger.error(f"Failed to remove Test output directory: {str(e)}")
    
    return True

def consolidate_code_directories():
    """Consolidate code directories to eliminate duplication."""
    if os.path.isdir(MAIN_SVG_PATH):
        logger.info(f"Duplicate code directory exists: {MAIN_SVG_PATH}")
        
        # Create backup of the directory
        if backup_directory(MAIN_SVG_PATH):
            try:
                # Remove duplicate code directory
                shutil.rmtree(MAIN_SVG_PATH)
                logger.info(f"Removed duplicate code directory: {MAIN_SVG_PATH}")
                return True
            except Exception as e:
                logger.error(f"Failed to remove duplicate code directory: {str(e)}")
                return False
    else:
        logger.info(f"Duplicate code directory not found or already removed: {MAIN_SVG_PATH}")
        return True

def update_main_config():
    """Update main configuration to reference correct paths."""
    config_files = [
        PROJECT_ROOT / "genai_agent_project" / "web" / "backend" / "app" / "main.py",
        PROJECT_ROOT / "genai_agent_project" / "web" / "backend" / "app" / "services" / "svg_service.py"
    ]
    
    updated = False
    for config_file in config_files:
        if os.path.isfile(config_file):
            logger.info(f"Updating config file: {config_file}")
            if update_file_paths(config_file, r'output[\\/]svg_to_video[\\/]svg|genai_agent_project[\\/]output[\\/]svg', str(CONSOLIDATED_OUTPUT_PATH)):
                updated = True
    
    return updated

def check_svg_file_creation():
    """Verify that SVG files can be created in the consolidated output directory."""
    try:
        test_file = CONSOLIDATED_OUTPUT_PATH / "test_consolidation.svg"
        with open(test_file, 'w') as f:
            f.write('<svg width="100" height="100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>')
        
        if os.path.isfile(test_file):
            logger.info(f"Successfully created test SVG file: {test_file}")
            return True
        else:
            logger.error(f"Failed to verify test SVG file creation: {test_file}")
            return False
    except Exception as e:
        logger.error(f"Error during SVG file creation test: {str(e)}")
        return False

def create_path_symlinks():
    """Create symlinks for old paths to ensure backward compatibility."""
    try:
        # Check if the directories already exist as symlinks
        web_ui_is_symlink = os.path.islink(str(WEB_UI_OUTPUT_PATH))
        test_is_symlink = os.path.islink(str(TEST_OUTPUT_PATH))
        
        # Only create parent directories and symlinks if they don't exist
        if not web_ui_is_symlink:
            # If the directory exists but is not a symlink, back it up and remove it
            if os.path.exists(WEB_UI_OUTPUT_PATH):
                if backup_directory(WEB_UI_OUTPUT_PATH):
                    try:
                        shutil.rmtree(WEB_UI_OUTPUT_PATH)
                        logger.info(f"Removed directory to create symlink: {WEB_UI_OUTPUT_PATH}")
                    except Exception as e:
                        logger.error(f"Failed to remove directory: {str(e)}")
                        return False
            
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(WEB_UI_OUTPUT_PATH)
            os.makedirs(parent_dir, exist_ok=True)
            
            # Create the symlink
            os.symlink(CONSOLIDATED_OUTPUT_PATH, WEB_UI_OUTPUT_PATH, target_is_directory=True)
            logger.info(f"Created symlink: {WEB_UI_OUTPUT_PATH} -> {CONSOLIDATED_OUTPUT_PATH}")
        else:
            # Check if the symlink points to the correct target
            current_target = os.readlink(str(WEB_UI_OUTPUT_PATH))
            if os.path.abspath(current_target) != os.path.abspath(CONSOLIDATED_OUTPUT_PATH):
                logger.warning(f"Symlink {WEB_UI_OUTPUT_PATH} points to {current_target} instead of {CONSOLIDATED_OUTPUT_PATH}")
        
        # Handle Test Output Path symlink
        if not test_is_symlink:
            # If the directory exists but is not a symlink, back it up and remove it
            if os.path.exists(TEST_OUTPUT_PATH):
                if backup_directory(TEST_OUTPUT_PATH):
                    try:
                        shutil.rmtree(TEST_OUTPUT_PATH)
                        logger.info(f"Removed directory to create symlink: {TEST_OUTPUT_PATH}")
                    except Exception as e:
                        logger.error(f"Failed to remove directory: {str(e)}")
                        return False
            
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(TEST_OUTPUT_PATH)
            os.makedirs(parent_dir, exist_ok=True)
            
            # Create the symlink
            os.symlink(CONSOLIDATED_OUTPUT_PATH, TEST_OUTPUT_PATH, target_is_directory=True)
            logger.info(f"Created symlink: {TEST_OUTPUT_PATH} -> {CONSOLIDATED_OUTPUT_PATH}")
        else:
            # Check if the symlink points to the correct target
            current_target = os.readlink(str(TEST_OUTPUT_PATH))
            if os.path.abspath(current_target) != os.path.abspath(CONSOLIDATED_OUTPUT_PATH):
                logger.warning(f"Symlink {TEST_OUTPUT_PATH} points to {current_target} instead of {CONSOLIDATED_OUTPUT_PATH}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating symlinks: {str(e)}")
        return False

def consolidate_svg_pipeline():
    """Main function to consolidate the SVG pipeline."""
    logger.info("Starting SVG pipeline consolidation...")
    
    # Step 1: Verify project SVG directory exists
    if not os.path.isdir(PROJECT_SVG_PATH):
        logger.error(f"Project SVG directory not found: {PROJECT_SVG_PATH}")
        return False
    
    # Step 2: Consolidate output directories
    logger.info("Consolidating output directories...")
    consolidate_output_directories()
    
    # Step 3: Update file paths in code
    logger.info("Updating file paths in code...")
    update_all_file_paths()
    
    # Step 4: Update routes
    logger.info("Updating API routes...")
    update_routes()
    
    # Step 5: Update main configuration
    logger.info("Updating main configuration...")
    update_main_config()
    
    # Step 6: Remove duplicate code directory
    logger.info("Consolidating code directories...")
    consolidate_code_directories()
    
    # Step 7: Verify SVG file creation
    logger.info("Verifying SVG file creation in consolidated directory...")
    check_svg_file_creation()
    
    # Step 8: Create symlinks for backward compatibility
    logger.info("Creating symlinks for backward compatibility...")
    create_path_symlinks()
    
    logger.info("SVG pipeline consolidation complete!")
    return True

if __name__ == "__main__":
    # Run the consolidation
    success = consolidate_svg_pipeline()
    if success:
        logger.info("SVG pipeline successfully consolidated!")
    else:
        logger.error("SVG pipeline consolidation failed!")
