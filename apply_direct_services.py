#!/usr/bin/env python3
"""
Apply Direct Services Integration
---------------------------------
This script applies the direct services patch to main.py and ensures all 
necessary core service modules are properly installed.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("DirectServicesSetup")

def ensure_directory_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured directory exists: {directory}")

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.bak"
    
    # Don't overwrite existing backups
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
    else:
        logger.info(f"Backup already exists: {backup_path}")

def apply_main_patch():
    """Apply the direct services patch to main.py."""
    project_root = Path(__file__).parent / "genai_agent_project"
    main_py = project_root / "main.py"
    patch_file = project_root / "main.py.direct_services"
    
    if not main_py.exists():
        logger.error(f"main.py not found at {main_py}")
        return False
    
    if not patch_file.exists():
        logger.error(f"Patch file not found at {patch_file}")
        return False
    
    # Create backup
    backup_file(main_py)
    
    # Copy patch file to main.py
    shutil.copy2(patch_file, main_py)
    logger.info(f"Applied direct services patch to {main_py}")
    
    return True

def ensure_core_services():
    """Ensure all core services directories exist."""
    project_root = Path(__file__).parent / "genai_agent_project"
    core_services_dir = project_root / "genai_agent" / "core" / "services"
    
    # Create directories if they don't exist
    ensure_directory_exists(project_root / "genai_agent" / "core")
    ensure_directory_exists(core_services_dir)
    
    # Check if necessary service files exist
    required_files = [
        core_services_dir / "__init__.py",
        core_services_dir / "service_initialization.py",
        core_services_dir / "llm_service.py",
        core_services_dir / "blender_service.py",
        core_services_dir / "service_integrator.py",
        core_services_dir / "agent_integration.py",
        core_services_dir / "initialize_services.py",
    ]
    
    missing_files = [f for f in required_files if not f.exists()]
    
    if missing_files:
        logger.error(f"Missing required service files: {', '.join(str(f) for f in missing_files)}")
        return False
    
    logger.info("All core service files are present")
    return True

def update_config_for_direct_services():
    """Update config.yaml to enable direct services by default."""
    project_root = Path(__file__).parent / "genai_agent_project"
    config_path = project_root / "config.yaml"
    
    import yaml
    
    if not config_path.exists():
        logger.error(f"Config file not found at {config_path}")
        return False
    
    # Load existing config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    # Check if already configured
    if config.get("USE_DIRECT_SERVICES") == True:
        logger.info("Config already has direct services enabled")
        return True
    
    # Add direct services configuration
    config["USE_DIRECT_SERVICES"] = True
    
    # Also set reasonable timeouts
    if "LLM_TIMEOUT" not in config:
        config["LLM_TIMEOUT"] = 120.0
    
    if "BLENDER_TIMEOUT" not in config:
        config["BLENDER_TIMEOUT"] = 300.0
    
    # Save updated config
    backup_file(config_path)
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    logger.info(f"Updated config at {config_path} to enable direct services")
    return True

def create_run_script():
    """Create a convenience script to run with direct services."""
    project_root = Path(__file__).parent / "genai_agent_project"
    
    # Windows batch script
    bat_script = """@echo off
echo Starting GenAI Agent with direct services...
cd %~dp0
python main.py --direct-services %*
"""
    
    # Linux/Mac shell script
    sh_script = """#!/bin/bash
echo "Starting GenAI Agent with direct services..."
cd "$(dirname "$0")"
python main.py --direct-services "$@"
"""
    
    # Write Windows script
    with open(project_root / "run_direct.bat", 'w') as f:
        f.write(bat_script)
    
    # Write Linux/Mac script
    with open(project_root / "run_direct.sh", 'w') as f:
        f.write(sh_script)
    
    # Make shell script executable on Linux/Mac
    try:
        os.chmod(project_root / "run_direct.sh", 0o755)
    except:
        pass
    
    logger.info("Created convenience run scripts")
    return True

def main():
    """Main function to apply direct services integration."""
    logger.info("Starting direct services integration...")
    
    success = True
    
    # Ensure core services exist
    if not ensure_core_services():
        logger.error("Core services check failed")
        success = False
    
    # Apply main.py patch
    if not apply_main_patch():
        logger.error("Failed to apply main.py patch")
        success = False
    
    # Update config to enable direct services
    if not update_config_for_direct_services():
        logger.error("Failed to update config")
        success = False
    
    # Create convenience run scripts
    if not create_run_script():
        logger.error("Failed to create run scripts")
        success = False
    
    if success:
        logger.info("Direct services integration completed successfully!")
        logger.info("You can now run the agent with direct services using:")
        logger.info("  - Windows: run_direct.bat")
        logger.info("  - Linux/Mac: ./run_direct.sh")
    else:
        logger.error("Direct services integration completed with errors.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
