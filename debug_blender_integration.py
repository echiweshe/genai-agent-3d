"""
Debug and test Blender integration for the SVG to Video pipeline.
"""
import os
import sys
import subprocess
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler('blender_integration_debug.log')
                    ])
logger = logging.getLogger(__name__)

def check_blender_installation():
    """Check if Blender is installed and available."""
    # Check environment variable
    blender_path = os.environ.get("BLENDER_PATH")
    env_var_set = blender_path is not None
    
    logger.info(f"BLENDER_PATH environment variable: {'SET' if env_var_set else 'NOT SET'}")
    if env_var_set:
        logger.info(f"BLENDER_PATH value: {blender_path}")
        if os.path.exists(blender_path):
            logger.info(f"✅ Blender executable exists at: {blender_path}")
        else:
            logger.error(f"❌ Blender executable NOT found at: {blender_path}")
    
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
    
    logger.info("Checking default Blender paths...")
    found_paths = []
    
    for path in default_paths:
        if os.path.exists(path):
            found_paths.append(path)
            logger.info(f"✅ Blender found at: {path}")
        else:
            logger.info(f"❌ Blender not found at: {path}")
    
    if not found_paths and not (env_var_set and os.path.exists(blender_path)):
        logger.error("Blender not found in any of the default locations or environment variable.")
        return None
    
    # Use the environment variable path if set and exists, otherwise use the first found path
    selected_path = blender_path if env_var_set and os.path.exists(blender_path) else (found_paths[0] if found_paths else None)
    
    if selected_path:
        logger.info(f"Selected Blender path: {selected_path}")
        return selected_path
    else:
        logger.error("No valid Blender path found.")
        return None

def test_blender_execution(blender_path):
    """Test if Blender can be executed."""
    if not blender_path:
        logger.error("Cannot test Blender execution: No Blender path provided.")
        return False
    
    logger.info(f"Testing Blender execution with: {blender_path} --version")
    
    try:
        process = subprocess.run([blender_path, "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
        
        if process.returncode == 0:
            logger.info(f"✅ Blender executed successfully")
            logger.info(f"Blender version output:\n{process.stdout}")
            return True
        else:
            logger.error(f"❌ Blender execution failed with return code: {process.returncode}")
            logger.error(f"Error output:\n{process.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        logger.error("❌ Blender execution timed out after 10 seconds")
        return False
    except Exception as e:
        logger.error(f"❌ Error executing Blender: {str(e)}")
        return False

def check_python_modules():
    """Check if required Python modules are available."""
    try:
        import mathutils
        logger.info("✅ mathutils module is available")
        return True
    except ImportError:
        logger.warning("❌ mathutils module not found. Checking for stub implementation...")
        
        # Check for stub implementation
        svg_to_3d_dir = os.path.join("genai_agent_project", "genai_agent", "svg_to_video", "svg_to_3d")
        if os.path.exists(os.path.join(svg_to_3d_dir, "mathutils.py")):
            logger.info("✅ mathutils stub implementation found")
            
            # Try to import the stub
            sys.path.insert(0, os.path.abspath(svg_to_3d_dir))
            try:
                import mathutils
                logger.info("✅ mathutils stub module imported successfully")
                return True
            except ImportError as e:
                logger.error(f"❌ Failed to import mathutils stub: {str(e)}")
                return False
            finally:
                if svg_to_3d_dir in sys.path:
                    sys.path.remove(svg_to_3d_dir)
        else:
            logger.error("❌ mathutils module not found and no stub implementation available")
            return False

def check_env_file():
    """Check if .env file exists and contains BLENDER_PATH."""
    env_file_path = os.path.join("genai_agent_project", ".env")
    
    if not os.path.exists(env_file_path):
        logger.error(f"❌ .env file not found at: {env_file_path}")
        return False
    
    logger.info(f"✅ .env file found at: {env_file_path}")
    
    # Check if BLENDER_PATH is in the .env file
    with open(env_file_path, 'r') as f:
        content = f.read()
    
    if "BLENDER_PATH" in content:
        logger.info("✅ BLENDER_PATH is defined in .env file")
        
        # Extract the BLENDER_PATH value
        import re
        match = re.search(r'BLENDER_PATH\s*=\s*(.*)', content)
        if match:
            path = match.group(1).strip()
            logger.info(f"BLENDER_PATH value in .env file: {path}")
            
            if os.path.exists(path):
                logger.info(f"✅ Path in .env file exists")
            else:
                logger.error(f"❌ Path in .env file does not exist: {path}")
        
        return True
    else:
        logger.warning("❌ BLENDER_PATH is not defined in .env file")
        return False

def check_config_yaml():
    """Check if config.yaml file exists and contains Blender configuration."""
    config_file_path = os.path.join("genai_agent_project", "config.yaml")
    
    if not os.path.exists(config_file_path):
        logger.error(f"❌ config.yaml file not found at: {config_file_path}")
        return False
    
    logger.info(f"✅ config.yaml file found at: {config_file_path}")
    
    # Check if Blender configuration is in the config.yaml file
    try:
        import yaml
        with open(config_file_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if config and "blender" in config:
            logger.info("✅ Blender configuration found in config.yaml")
            logger.info(f"Blender configuration: {json.dumps(config['blender'], indent=2)}")
            return True
        else:
            logger.warning("❌ Blender configuration not found in config.yaml")
            return False
    except Exception as e:
        logger.error(f"❌ Error reading config.yaml: {str(e)}")
        return False

def check_output_directories():
    """Check if output directories for SVG to Video pipeline exist."""
    base_output_dir = os.path.join("output")
    svg_output_dir = os.path.join(base_output_dir, "svg")
    svg_to_video_dir = os.path.join(base_output_dir, "svg_to_video")
    models_dir = os.path.join(svg_to_video_dir, "models")
    animations_dir = os.path.join(svg_to_video_dir, "animations")
    videos_dir = os.path.join(svg_to_video_dir, "videos")
    
    directories = [
        base_output_dir,
        svg_output_dir,
        svg_to_video_dir,
        models_dir,
        animations_dir,
        videos_dir
    ]
    
    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            if os.path.isdir(directory):
                logger.info(f"✅ Directory exists: {directory}")
            else:
                logger.error(f"❌ Path exists but is not a directory: {directory}")
                all_exist = False
        else:
            logger.error(f"❌ Directory does not exist: {directory}")
            all_exist = False
    
    return all_exist

def fix_common_issues():
    """Try to fix common issues with the SVG to Video pipeline."""
    logger.info("Attempting to fix common issues...")
    
    # 1. Create output directories if they don't exist
    base_output_dir = os.path.join("output")
    svg_output_dir = os.path.join(base_output_dir, "svg")
    svg_to_video_dir = os.path.join(base_output_dir, "svg_to_video")
    models_dir = os.path.join(svg_to_video_dir, "models")
    animations_dir = os.path.join(svg_to_video_dir, "animations")
    videos_dir = os.path.join(svg_to_video_dir, "videos")
    
    directories = [
        base_output_dir,
        svg_output_dir,
        svg_to_video_dir,
        models_dir,
        animations_dir,
        videos_dir
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Created directory: {directory}")
        elif not os.path.isdir(directory):
            # Rename the file and create the directory
            try:
                backup_path = f"{directory}_backup"
                os.rename(directory, backup_path)
                logger.info(f"✅ Renamed file to: {backup_path}")
                os.makedirs(directory, exist_ok=True)
                logger.info(f"✅ Created directory: {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to fix directory issue for {directory}: {str(e)}")
    
    # 2. Run the directory sync script if it exists
    sync_script_path = "sync_svg_directories.py"
    if os.path.exists(sync_script_path):
        logger.info(f"Running directory sync script: {sync_script_path}")
        try:
            subprocess.run([sys.executable, sync_script_path], check=True)
            logger.info("✅ Successfully ran directory sync script")
        except Exception as e:
            logger.error(f"❌ Failed to run directory sync script: {str(e)}")
    else:
        logger.warning(f"❌ Directory sync script not found: {sync_script_path}")
    
    # 3. Check and update .env file if needed
    env_file_path = os.path.join("genai_agent_project", ".env")
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            content = f.read()
        
        if "BLENDER_PATH" not in content:
            logger.info("Adding BLENDER_PATH to .env file")
            
            # Find the best Blender path
            blender_path = check_blender_installation()
            if blender_path:
                with open(env_file_path, 'a') as f:
                    f.write(f"\n# Added by debug script\nBLENDER_PATH={blender_path}\n")
                logger.info(f"✅ Added BLENDER_PATH={blender_path} to .env file")
            else:
                logger.error("❌ Could not find Blender path to add to .env file")
    else:
        logger.warning(f"❌ .env file not found, cannot update: {env_file_path}")
    
    logger.info("Fix attempts completed")

def main():
    """Main function to debug Blender integration."""
    logger.info("="*80)
    logger.info("SVG to Video Pipeline - Blender Integration Debug Tool")
    logger.info("="*80)
    
    # 1. Check Blender installation
    logger.info("\n1. Checking Blender installation...")
    blender_path = check_blender_installation()
    
    # 2. Test Blender execution
    logger.info("\n2. Testing Blender execution...")
    if blender_path:
        test_blender_execution(blender_path)
    else:
        logger.error("Skipping Blender execution test: No Blender path found")
    
    # 3. Check Python modules
    logger.info("\n3. Checking required Python modules...")
    check_python_modules()
    
    # 4. Check .env file
    logger.info("\n4. Checking .env file...")
    check_env_file()
    
    # 5. Check config.yaml
    logger.info("\n5. Checking config.yaml...")
    check_config_yaml()
    
    # 6. Check output directories
    logger.info("\n6. Checking output directories...")
    check_output_directories()
    
    # 7. Offer to fix common issues
    logger.info("\n7. Fix common issues?")
    choice = input("Would you like to attempt to fix common issues? (y/n): ")
    if choice.lower() == 'y':
        fix_common_issues()
    
    logger.info("\nDebug process completed. See the log file for details: blender_integration_debug.log")

if __name__ == "__main__":
    main()
