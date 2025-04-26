#!/usr/bin/env python3
"""
Patch main.py to include LLM settings API

This script adds the necessary code to main.py to include the LLM settings API.
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

def patch_main_py():
    """Patch main.py to include LLM settings API"""
    main_path = Path("genai_agent_project/main.py")
    
    if not main_path.exists():
        logger.error(f"Main file {main_path} not found")
        return False
    
    # Backup the file
    if not backup_file(main_path):
        return False
    
    # Read the file
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if "from genai_agent.services.llm_settings_api import add_llm_settings_routes" in content:
        logger.info("main.py is already patched")
        return True
    
    # Find import section
    import_section = content.find("# Application imports")
    if import_section == -1:
        import_section = content.find("import logging")
    
    if import_section == -1:
        logger.error("Could not find import section in main.py")
        return False
    
    # Find next section after imports
    next_section = content.find("# Initialize", import_section)
    if next_section == -1:
        next_section = content.find("# Application", import_section)
    
    if next_section == -1:
        logger.error("Could not find section after imports in main.py")
        return False
    
    # Add our import
    new_content = (
        content[:next_section] + 
        "from genai_agent.services.llm_settings_api import add_llm_settings_routes\n" + 
        content[next_section:]
    )
    
    # Find where routes are added
    routes_section = new_content.find("# Register API routes")
    if routes_section == -1:
        routes_section = new_content.find("# Add API routers")
    
    if routes_section == -1:
        # Try to find where app is created
        app_section = new_content.find("app = FastAPI(")
        if app_section != -1:
            # Find next section after app creation
            end_of_app_setup = new_content.find("\n\n", app_section)
            if end_of_app_setup != -1:
                routes_section = end_of_app_setup
    
    if routes_section == -1:
        logger.error("Could not find where to add routes in main.py")
        return False
    
    # Add our route
    line_end = new_content.find("\n", routes_section)
    if line_end == -1:
        line_end = len(new_content)
    
    final_content = (
        new_content[:line_end] + 
        "\n\n# Register LLM settings API routes\nadd_llm_settings_routes(app)\n" + 
        new_content[line_end:]
    )
    
    # Write the updated content
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    logger.info(f"Successfully patched {main_path}")
    return True

def main():
    """Main function"""
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    logger.info(f"Working in {project_root}")
    
    # Patch main.py
    if patch_main_py():
        logger.info("Patch applied successfully")
        return 0
    else:
        logger.error("Failed to apply patch")
        return 1

if __name__ == "__main__":
    sys.exit(main())
