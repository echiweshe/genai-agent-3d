#!/usr/bin/env python
"""
Automated Setup Integrations Script for GenAI Agent 3D

This script automatically clones and sets up the required third-party integrations:
- BlenderGPT (https://github.com/gd3kr/BlenderGPT)
- Hunyuan-3D 2.0 (https://github.com/Tencent/Hunyuan3D-2)
- TRELLIS (https://github.com/microsoft/TRELLIS)
- Ollama (already configured but verified)

No user input is required. The script will:
1. Check prerequisites
2. Create the integration directories
3. Clone the repositories
4. Set up each integration
5. Update the config.yaml file with the correct paths
"""

import os
import sys
import subprocess
import shutil
import yaml
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("setup_integrations")

# Project root directory (parent of genai_agent_project)
PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__))).parent
INTEGRATIONS_DIR = PROJECT_ROOT / "integrations"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")

# Repository URLs
REPOS = {
    "blendergpt": "https://github.com/gd3kr/BlenderGPT.git",
    "hunyuan3d": "https://github.com/Tencent/Hunyuan3D-2.git",
    "trellis": "https://github.com/microsoft/TRELLIS.git"
}

def check_prerequisites():
    """Check that all required tools are installed."""
    logger.info("Checking prerequisites...")
    
    # Check git
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        logger.info("✅ Git is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("❌ Git is not installed or not in PATH")
        return False
    
    # Check python
    try:
        subprocess.run([sys.executable, "--version"], check=True, capture_output=True)
        logger.info(f"✅ Python is installed: {sys.version.split()[0]}")
    except subprocess.SubprocessError:
        logger.error("❌ Python check failed")
        return False
    
    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        logger.info("✅ Pip is installed")
    except subprocess.SubprocessError:
        logger.error("❌ Pip is not installed")
        return False
    
    # Check npm for frontend dependencies
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        logger.info("✅ NPM is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("⚠️ NPM is not installed - might be needed for some integrations")
    
    # Check if config.yaml exists
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"❌ Config file not found at {CONFIG_FILE}")
        return False
    
    return True

def create_directories():
    """Create necessary directories for integrations."""
    logger.info("Creating integration directories...")
    os.makedirs(INTEGRATIONS_DIR, exist_ok=True)
    logger.info(f"✅ Created integrations directory at {INTEGRATIONS_DIR}")
    return True

def clone_repository(repo_name):
    """Clone a repository to the integrations directory."""
    repo_url = REPOS[repo_name]
    target_dir = INTEGRATIONS_DIR / repo_name
    
    # Remove directory if it exists
    if os.path.exists(target_dir):
        logger.info(f"Removing existing directory: {target_dir}")
        shutil.rmtree(target_dir)
    
    logger.info(f"Cloning {repo_name} from {repo_url}...")
    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_dir)], 
            check=True, 
            capture_output=True
        )
        logger.info(f"✅ Successfully cloned {repo_name}")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"❌ Failed to clone {repo_name}: {e}")
        logger.error(f"STDOUT: {e.stdout.decode() if hasattr(e, 'stdout') and e.stdout else 'N/A'}")
        logger.error(f"STDERR: {e.stderr.decode() if hasattr(e, 'stderr') and e.stderr else 'N/A'}")
        return False

def setup_blendergpt():
    """Set up BlenderGPT integration."""
    repo_dir = INTEGRATIONS_DIR / "blendergpt"
    
    if not os.path.exists(repo_dir):
        logger.error(f"❌ BlenderGPT directory not found at {repo_dir}")
        return False
    
    logger.info("Setting up BlenderGPT...")
    
    # Install requirements
    requirements_file = repo_dir / "requirements.txt"
    if os.path.exists(requirements_file):
        logger.info("Installing BlenderGPT requirements...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True
            )
            logger.info("✅ Installed BlenderGPT requirements")
        except subprocess.SubprocessError as e:
            logger.error(f"❌ Failed to install BlenderGPT requirements: {e}")
            logger.warning("Continuing anyway...")
    
    # Create a simple adapter config file
    adapter_config = {
        "blendergpt_path": str(repo_dir),
        "adapter_version": "1.0.0"
    }
    
    with open(repo_dir / "adapter_config.json", "w") as f:
        import json
        json.dump(adapter_config, f, indent=2)
    
    logger.info("✅ BlenderGPT setup completed")
    return True

def setup_hunyuan3d():
    """Set up Hunyuan-3D integration."""
    repo_dir = INTEGRATIONS_DIR / "hunyuan3d"
    
    if not os.path.exists(repo_dir):
        logger.error(f"❌ Hunyuan-3D directory not found at {repo_dir}")
        return False
    
    logger.info("Setting up Hunyuan-3D...")
    
    # Install requirements if present
    requirements_file = repo_dir / "requirements.txt"
    if os.path.exists(requirements_file):
        logger.info("Installing Hunyuan-3D requirements...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True
            )
            logger.info("✅ Installed Hunyuan-3D requirements")
        except subprocess.SubprocessError as e:
            logger.error(f"❌ Failed to install Hunyuan-3D requirements: {e}")
            logger.warning("Continuing anyway...")
    
    # Create adapter config file
    adapter_config = {
        "hunyuan3d_path": str(repo_dir),
        "adapter_version": "1.0.0"
    }
    
    with open(repo_dir / "adapter_config.json", "w") as f:
        import json
        json.dump(adapter_config, f, indent=2)
    
    logger.info("✅ Hunyuan-3D setup completed")
    return True

def setup_trellis():
    """Set up TRELLIS integration."""
    repo_dir = INTEGRATIONS_DIR / "trellis"
    
    if not os.path.exists(repo_dir):
        logger.error(f"❌ TRELLIS directory not found at {repo_dir}")
        return False
    
    logger.info("Setting up TRELLIS...")
    
    # Install requirements if present
    requirements_file = repo_dir / "requirements.txt"
    if os.path.exists(requirements_file):
        logger.info("Installing TRELLIS requirements...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True
            )
            logger.info("✅ Installed TRELLIS requirements")
        except subprocess.SubprocessError as e:
            logger.error(f"❌ Failed to install TRELLIS requirements: {e}")
            logger.warning("Continuing anyway...")
    
    # Create adapter config file
    adapter_config = {
        "trellis_path": str(repo_dir),
        "adapter_version": "1.0.0"
    }
    
    with open(repo_dir / "adapter_config.json", "w") as f:
        import json
        json.dump(adapter_config, f, indent=2)
    
    logger.info("✅ TRELLIS setup completed")
    return True

def check_ollama():
    """Verify Ollama installation."""
    logger.info("Checking Ollama installation...")
    
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            check=True, 
            capture_output=True,
            text=True
        )
        logger.info("✅ Ollama is installed and running")
        logger.info(f"Available models: {result.stdout.strip()}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.error(f"❌ Ollama check failed: {e}")
        logger.error("Please install Ollama from https://github.com/ollama/ollama")
        return False

def update_config():
    """Update config.yaml with integration paths."""
    logger.info(f"Updating configuration file: {CONFIG_FILE}")
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update integration paths
        if 'integrations' not in config:
            config['integrations'] = {}
        
        config['integrations']['blendergpt'] = {
            'path': str(INTEGRATIONS_DIR / "blendergpt")
        }
        config['integrations']['hunyuan3d'] = {
            'path': str(INTEGRATIONS_DIR / "hunyuan3d")
        }
        config['integrations']['trellis'] = {
            'path': str(INTEGRATIONS_DIR / "trellis")
        }
        
        # Backup the original config
        backup_file = f"{CONFIG_FILE}.bak"
        shutil.copy2(CONFIG_FILE, backup_file)
        logger.info(f"Created backup of config file at {backup_file}")
        
        # Write updated config
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info("✅ Configuration file updated")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to update config file: {e}")
        return False

def main():
    """Main function to run the setup process."""
    logger.info("===== GenAI Agent 3D - Automated Integrations Setup =====")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Integrations directory: {INTEGRATIONS_DIR}")
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Failed prerequisite checks. Exiting.")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        logger.error("Failed to create directories. Exiting.")
        sys.exit(1)
    
    # Clone repositories
    success = True
    for repo_name in REPOS:
        if not clone_repository(repo_name):
            logger.error(f"Failed to clone {repo_name}")
            success = False
    
    if not success:
        logger.error("Some repositories failed to clone.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Setup each integration
    setup_blendergpt()
    setup_hunyuan3d()
    setup_trellis()
    check_ollama()
    
    # Update config
    update_config()
    
    logger.info("===== Integrations Setup Complete =====")
    logger.info(f"BlenderGPT: {INTEGRATIONS_DIR / 'blendergpt'}")
    logger.info(f"Hunyuan-3D: {INTEGRATIONS_DIR / 'hunyuan3d'}")
    logger.info(f"TRELLIS: {INTEGRATIONS_DIR / 'trellis'}")
    logger.info("To test the setup, run: python run.py examples integrations_example")

if __name__ == "__main__":
    main()