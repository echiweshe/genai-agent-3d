"""
Script to update the Blender path in configuration files.
This helps ensure proper Blender integration with the SVG to Video pipeline.
"""
import os
import sys
import re
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_blender_path():
    """Get the path to the Blender executable."""
    # Default paths to check
    default_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
        r"/usr/bin/blender",
        r"/Applications/Blender.app/Contents/MacOS/Blender"
    ]
    
    # Check each path
    for path in default_paths:
        if os.path.exists(path):
            logger.info(f"Found Blender executable at: {path}")
            # Convert path to use forward slashes to avoid escape problems
            safe_path = path.replace("\\", "/")
            return safe_path
    
    logger.warning("No Blender executable found in default paths")
    
    # Ask the user for a custom path
    custom_path = input("Please enter the path to your Blender executable (or press Enter to skip): ")
    if custom_path and os.path.exists(custom_path):
        logger.info(f"Using custom Blender path: {custom_path}")
        # Convert path to use forward slashes to avoid escape problems
        safe_path = custom_path.replace("\\", "/")
        return safe_path
    elif custom_path:
        logger.warning(f"Custom path does not exist: {custom_path}")
    
    return None

def update_env_file(blender_path):
    """Update the .env file with the Blender path."""
    project_root = Path(os.path.abspath(__file__)).parent
    env_file = project_root / "genai_agent_project" / ".env"
    
    # Check if .env file exists
    if not env_file.exists():
        logger.warning(f".env file not found at: {env_file}")
        # Create .env file
        logger.info("Creating new .env file")
        env_file.parent.mkdir(parents=True, exist_ok=True)
        with open(env_file, 'w') as f:
            f.write(f"# Environment variables for GenAI Agent 3D\n")
            f.write(f"BLENDER_PATH={blender_path}\n")
        logger.info(f"Created .env file with Blender path: {env_file}")
        return True
    
    # Read existing content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check if BLENDER_PATH is already set
    if "BLENDER_PATH=" in content:
        # Update existing BLENDER_PATH using string replacement
        lines = content.splitlines()
        new_lines = []
        
        for line in lines:
            if line.startswith("BLENDER_PATH="):
                new_lines.append(f"BLENDER_PATH={blender_path}")
            else:
                new_lines.append(line)
        
        updated_content = "\n".join(new_lines)
        
        with open(env_file, 'w') as f:
            f.write(updated_content)
        logger.info(f"Updated BLENDER_PATH in .env file: {env_file}")
    else:
        # Add BLENDER_PATH to the end of the file
        with open(env_file, 'a') as f:
            if not content.endswith('\n'):
                f.write('\n')
            f.write(f"BLENDER_PATH={blender_path}\n")
        logger.info(f"Added BLENDER_PATH to .env file: {env_file}")
    
    return True

def update_config_yaml(blender_path):
    """Update the config.yaml file with the Blender path."""
    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML not installed. Cannot update config.yaml")
        return False
    
    project_root = Path(os.path.abspath(__file__)).parent
    config_file = project_root / "genai_agent_project" / "config.yaml"
    
    # Check if config.yaml file exists
    if not config_file.exists():
        logger.warning(f"config.yaml file not found at: {config_file}")
        return False
    
    # Read existing content
    with open(config_file, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error parsing config.yaml: {str(e)}")
            return False
    
    # Update config
    if not config:
        config = {}
    
    if 'blender' not in config:
        config['blender'] = {}
    
    config['blender']['path'] = blender_path
    
    # Write updated config
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    logger.info(f"Updated Blender path in config.yaml: {config_file}")
    return True

def main():
    """Main function."""
    logger.info("Checking for Blender executable...")
    blender_path = get_blender_path()
    
    if not blender_path:
        logger.error("No Blender executable found. Cannot update configuration files.")
        return
    
    # Update .env file
    update_env_file(blender_path)
    
    # Update config.yaml file
    update_config_yaml(blender_path)
    
    logger.info("Configuration files updated successfully.")
    
    # Ask to restart backend
    restart = input("Do you want to restart the backend service? (y/n): ")
    if restart.lower() == 'y':
        try:
            project_root = Path(os.path.abspath(__file__)).parent
            manage_services = project_root / "genai_agent_project" / "manage_services.py"
            
            if manage_services.exists():
                logger.info("Restarting backend service...")
                subprocess.run([sys.executable, str(manage_services), "restart", "backend"])
                logger.info("Backend service restarted.")
            else:
                logger.warning(f"manage_services.py not found at: {manage_services}")
        except Exception as e:
            logger.error(f"Error restarting backend service: {str(e)}")
    
    print("\nUpdate completed. Please ensure that:")
    print("1. The Blender path is correct")
    print("2. The SVG directories are properly synchronized (run sync_svg_directories.bat)")
    print("3. The backend service is restarted")
    print("\nYou can now use the SVG to Video pipeline.")

if __name__ == "__main__":
    main()
