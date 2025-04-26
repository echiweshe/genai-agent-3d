#!/usr/bin/env python3
"""
Direct Fix for main.py in GenAI Agent 3D

This script directly updates the main.py file in the API server module
to ensure it includes the LLM settings API routes.
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of the file"""
    try:
        backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {str(e)}")
        return False

def find_api_server_main():
    """Find the API server main.py file"""
    # Common locations where the API server main.py might be located
    potential_paths = [
        "genai_agent_project/main.py",
        "genai_agent_project/api/main.py",
        "genai_agent_project/server/main.py",
        "genai_agent_project/api_server/main.py"
    ]
    
    # Search for a FastAPI-based main.py file
    for path in potential_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check if this is a FastAPI file
                if 'from fastapi import' in content or 'import fastapi' in content:
                    logger.info(f"Found API server main.py at: {path}")
                    return path
    
    # If we couldn't find it in common locations, search the entire project
    for root, dirs, files in os.walk("genai_agent_project"):
        if 'main.py' in files:
            path = os.path.join(root, 'main.py')
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check if this is a FastAPI file
                if 'from fastapi import' in content or 'import fastapi' in content:
                    logger.info(f"Found API server main.py at: {path}")
                    return path
    
    logger.error("Could not find the API server main.py file")
    return None

def add_llm_settings_routes(main_path):
    """Add LLM settings routes to main.py"""
    # Read the content
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if "from genai_agent.services.llm_settings_api import add_llm_settings_routes" in content:
        logger.info("main.py is already patched")
        return True
    
    # Look for FastAPI-specific imports
    fastapi_import_idx = content.find("from fastapi import")
    if fastapi_import_idx == -1:
        fastapi_import_idx = content.find("import fastapi")
    
    if fastapi_import_idx == -1:
        logger.error("Could not find FastAPI imports in main.py")
        return False
    
    # Find end of imports
    import_section_end = content.find("\n\n", fastapi_import_idx)
    if import_section_end == -1:
        # If we can't find a clear end to imports, add after the last import
        lines = content.split('\n')
        for i, line in reversed(list(enumerate(lines))):
            if line.startswith('import ') or line.startswith('from '):
                import_section_end = sum(len(l) + 1 for l in lines[:i+1]) - 1
                break
    
    if import_section_end == -1:
        logger.error("Could not determine where to add imports in main.py")
        return False
    
    # Add import
    updated_content = (
        content[:import_section_end] + 
        "\nfrom genai_agent.services.llm_settings_api import add_llm_settings_routes" + 
        content[import_section_end:]
    )
    
    # Find app definition (common patterns)
    app_definition_patterns = [
        "app = FastAPI(",
        "app = fastapi.FastAPI(",
        "app = APIRouter("
    ]
    
    app_definition_idx = -1
    for pattern in app_definition_patterns:
        idx = updated_content.find(pattern)
        if idx != -1:
            app_definition_idx = idx
            break
    
    if app_definition_idx == -1:
        logger.error("Could not find app definition in main.py")
        return False
    
    # Find a good place to add route registration
    route_registration_idx = updated_content.find("@app.get", app_definition_idx)
    if route_registration_idx == -1:
        route_registration_idx = updated_content.find("@app.post", app_definition_idx)
    
    if route_registration_idx == -1:
        # Look for common app setup sections
        for pattern in ["# Add middleware", "# Add routes", "# Routes", "# API routes"]:
            idx = updated_content.find(pattern, app_definition_idx)
            if idx != -1:
                route_registration_idx = idx
                break
    
    if route_registration_idx == -1:
        # If we can't find a good spot, add right after app definition
        route_registration_idx = updated_content.find("\n", app_definition_idx)
        if route_registration_idx == -1:
            route_registration_idx = len(updated_content)
    
    # Add route registration
    final_lines = updated_content.split('\n')
    
    # Convert index to line number
    line_count = 0
    line_num = 0
    for i, line in enumerate(final_lines):
        line_count += len(line) + 1
        if line_count > route_registration_idx:
            line_num = i
            break
    
    # Insert route registration
    final_lines.insert(line_num, "# Register LLM settings API routes")
    final_lines.insert(line_num + 1, "add_llm_settings_routes(app)")
    final_lines.insert(line_num + 2, "")
    
    # Write the updated content
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))
    
    logger.info(f"Successfully patched {main_path}")
    return True

def main():
    """Main function"""
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    logger.info(f"Working in {project_root}")
    
    # Find the API server main.py
    main_path = find_api_server_main()
    if not main_path:
        logger.error("Could not find the API server main.py file")
        return 1
    
    # Backup the file
    if not backup_file(main_path):
        logger.error(f"Failed to backup {main_path}")
        return 1
    
    # Add LLM settings routes
    if add_llm_settings_routes(main_path):
        logger.info(f"Successfully patched {main_path}")
        return 0
    else:
        logger.error(f"Failed to patch {main_path}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
