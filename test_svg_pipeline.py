"""
Test Script for SVG Pipeline in GenAI Agent 3D project.
This script creates a simple SVG and tests the basic file operations
to ensure the consolidated pipeline is working correctly.
"""

import os
import sys
import logging
from pathlib import Path
import shutil
import time

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define paths
PROJECT_ROOT = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d")
CONSOLIDATED_SVG_PATH = PROJECT_ROOT / "output" / "svg"
WEB_UI_SVG_PATH = PROJECT_ROOT / "output" / "svg_to_video" / "svg"
TEST_SVG_PATH = PROJECT_ROOT / "genai_agent_project" / "output" / "svg"

def create_test_svg(file_name="test_svg_pipeline.svg"):
    """Create a test SVG file in the consolidated output directory."""
    test_svg_path = CONSOLIDATED_SVG_PATH / file_name
    
    # Simple SVG content
    svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
    <rect width="400" height="200" fill="#f0f0f0" />
    <text x="50%" y="50%" font-family="Arial" font-size="24" 
          text-anchor="middle" dominant-baseline="middle">
        SVG Pipeline Test - {time.strftime("%Y-%m-%d %H:%M:%S")}
    </text>
    <circle cx="200" cy="120" r="50" fill="blue" opacity="0.5" />
</svg>
"""
    
    try:
        os.makedirs(os.path.dirname(test_svg_path), exist_ok=True)
        with open(test_svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        logger.info(f"Created test SVG file: {test_svg_path}")
        return test_svg_path
    except Exception as e:
        logger.error(f"Error creating test SVG file: {e}")
        return None

def verify_symlinks():
    """Verify that symlinks are correctly set up."""
    # Check if directories exist
    consolidated_exists = os.path.isdir(CONSOLIDATED_SVG_PATH)
    web_ui_exists = os.path.exists(WEB_UI_SVG_PATH)
    test_exists = os.path.exists(TEST_SVG_PATH)
    
    logger.info(f"Consolidated SVG path exists: {consolidated_exists}")
    logger.info(f"Web UI SVG path exists: {web_ui_exists}")
    logger.info(f"Test SVG path exists: {test_exists}")
    
    # Check symlinks
    if web_ui_exists:
        is_symlink = os.path.islink(WEB_UI_SVG_PATH)
        logger.info(f"Web UI SVG path is symlink: {is_symlink}")
        if is_symlink:
            target = os.readlink(WEB_UI_SVG_PATH)
            logger.info(f"Web UI symlink target: {target}")
            correct_target = os.path.abspath(CONSOLIDATED_SVG_PATH) == os.path.abspath(os.path.join(os.path.dirname(WEB_UI_SVG_PATH), target))
            logger.info(f"Web UI symlink target is correct: {correct_target}")
        else:
            logger.warning("Web UI SVG path is not a symlink!")
    
    if test_exists:
        is_symlink = os.path.islink(TEST_SVG_PATH)
        logger.info(f"Test SVG path is symlink: {is_symlink}")
        if is_symlink:
            target = os.readlink(TEST_SVG_PATH)
            logger.info(f"Test symlink target: {target}")
            correct_target = os.path.abspath(CONSOLIDATED_SVG_PATH) == os.path.abspath(os.path.join(os.path.dirname(TEST_SVG_PATH), target))
            logger.info(f"Test symlink target is correct: {correct_target}")
        else:
            logger.warning("Test SVG path is not a symlink!")
    
    return (web_ui_exists and os.path.islink(WEB_UI_SVG_PATH) and 
            test_exists and os.path.islink(TEST_SVG_PATH))

def test_file_visibility():
    """Test that files are visible through the symlinks."""
    # Create a test file
    test_file = create_test_svg()
    if not test_file:
        logger.error("Failed to create test file!")
        return False
    
    # Check visibility through Web UI symlink
    web_ui_file = WEB_UI_SVG_PATH / os.path.basename(test_file)
    web_ui_visibility = os.path.isfile(web_ui_file)
    logger.info(f"Test file visible through Web UI symlink: {web_ui_visibility}")
    
    # Check visibility through Test symlink
    test_file_path = TEST_SVG_PATH / os.path.basename(test_file)
    test_visibility = os.path.isfile(test_file_path)
    logger.info(f"Test file visible through Test symlink: {test_visibility}")
    
    return web_ui_visibility and test_visibility

def verify_code_structure():
    """Verify the SVG code directory structure."""
    # Check project SVG directory
    project_svg_dir = PROJECT_ROOT / "genai_agent_project" / "genai_agent" / "svg_to_video"
    if not os.path.isdir(project_svg_dir):
        logger.error(f"Project SVG directory not found: {project_svg_dir}")
        return False
    
    # Check main SVG directory (should be gone or backed up)
    main_svg_dir = PROJECT_ROOT / "genai_agent" / "svg_to_video"
    if os.path.isdir(main_svg_dir):
        logger.warning(f"Main SVG directory still exists: {main_svg_dir}")
        return False
    
    # Check for essential subdirectories
    essential_dirs = [
        "svg_generator",
        "svg_to_3d",
        "animation",
        "rendering"
    ]
    
    # Check essential files
    essential_files = [
        "animation.py",
        "rendering.py",
        "__init__.py",
        "pipeline_integrated.py"
    ]
    
    all_dirs_exist = True
    for dir_name in essential_dirs:
        dir_path = project_svg_dir / dir_name
        exists = os.path.isdir(dir_path)
        logger.info(f"Directory check: {dir_name}/ - {'EXISTS' if exists else 'MISSING'}")
        all_dirs_exist = all_dirs_exist and exists
    
    all_files_exist = True
    for file_name in essential_files:
        file_path = project_svg_dir / file_name
        exists = os.path.isfile(file_path)
        logger.info(f"File check: {file_name} - {'EXISTS' if exists else 'MISSING'}")
        all_files_exist = all_files_exist and exists
    
    return all_dirs_exist and all_files_exist

def run_tests():
    """Run all tests and generate a report."""
    logger.info("Starting SVG pipeline tests...")
    
    # Test 1: Verify code structure
    logger.info("\n=== Test 1: Code Structure ===")
    code_structure_ok = verify_code_structure()
    
    # Test 2: Verify symlinks
    logger.info("\n=== Test 2: Symlink Setup ===")
    symlinks_ok = verify_symlinks()
    
    # Test 3: File visibility test
    logger.info("\n=== Test 3: File Visibility ===")
    file_visibility_ok = test_file_visibility()
    
    # Test results
    logger.info("\n=== Test Results ===")
    logger.info(f"Code Structure: {'PASS' if code_structure_ok else 'FAIL'}")
    logger.info(f"Symlink Setup: {'PASS' if symlinks_ok else 'FAIL'}")
    logger.info(f"File Visibility: {'PASS' if file_visibility_ok else 'FAIL'}")
    
    overall_success = code_structure_ok and symlinks_ok and file_visibility_ok
    logger.info(f"\nOverall Test Result: {'PASS' if overall_success else 'FAIL'}")
    
    return overall_success

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
