"""
Script to check if Blender is properly installed and configured.
This helps diagnose issues with the SVG to Video pipeline's Blender integration.
"""
import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_blender_path():
    """Get the path to the Blender executable."""
    # Try to get the path from environment variable
    blender_path = os.environ.get("BLENDER_PATH")
    
    if blender_path and os.path.exists(blender_path):
        return blender_path
    
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
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    return None

def test_blender_execution(blender_path):
    """Test if Blender can be executed."""
    if not blender_path:
        return False, "Blender path not found"
    
    try:
        process = subprocess.run(
            [blender_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if process.returncode == 0:
            return True, process.stdout.strip()
        else:
            return False, f"Blender execution failed with error: {process.stderr}"
    
    except subprocess.TimeoutExpired:
        return False, "Blender execution timed out after 10 seconds"
    except Exception as e:
        return False, f"Error executing Blender: {str(e)}"

def check_environment_variables():
    """Check if necessary environment variables are set."""
    env_vars = {
        "BLENDER_PATH": os.environ.get("BLENDER_PATH")
    }
    
    return env_vars

def check_config_files():
    """Check the configuration files for Blender settings."""
    try:
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        # Check .env file
        env_file = project_root / "genai_agent_project" / ".env"
        env_file_content = None
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_file_content = f.read()
        
        # Check config.yaml
        config_file = project_root / "genai_agent_project" / "config.yaml"
        config_file_content = None
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_file_content = f.read()
        
        return {
            "env_file": {
                "exists": env_file.exists(),
                "path": str(env_file),
                "content": env_file_content
            },
            "config_file": {
                "exists": config_file.exists(),
                "path": str(config_file),
                "content": config_file_content
            }
        }
    except Exception as e:
        return {
            "error": str(e)
        }

def check_output_directories():
    """Check if necessary output directories exist."""
    try:
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        # Define directories to check
        directories = {
            "main_output": project_root / "output",
            "svg_output": project_root / "output" / "svg",
            "svg_to_video_output": project_root / "output" / "svg_to_video",
            "models_output": project_root / "output" / "svg_to_video" / "models",
            "animations_output": project_root / "output" / "svg_to_video" / "animations",
            "videos_output": project_root / "output" / "svg_to_video" / "videos"
        }
        
        # Check each directory
        directory_status = {}
        for name, path in directories.items():
            directory_status[name] = {
                "exists": path.exists(),
                "is_dir": path.is_dir() if path.exists() else False,
                "path": str(path)
            }
        
        return directory_status
    except Exception as e:
        return {
            "error": str(e)
        }

def get_comprehensive_status():
    """Get comprehensive status information about Blender integration."""
    blender_path = get_blender_path()
    blender_executable, blender_version = test_blender_execution(blender_path) if blender_path else (False, None)
    
    return {
        "blender": {
            "available": blender_executable,
            "path": blender_path,
            "version": blender_version
        },
        "environment": check_environment_variables(),
        "config_files": check_config_files(),
        "directories": check_output_directories()
    }

if __name__ == "__main__":
    status = get_comprehensive_status()
    
    # Print status information
    print("\n=== Blender Integration Status ===\n")
    
    if status["blender"]["available"]:
        print(f"✅ Blender is available at: {status['blender']['path']}")
        print(f"Version: {status['blender']['version']}")
    else:
        print("❌ Blender is not available")
        if status["blender"]["path"]:
            print(f"Path exists but execution failed: {status['blender']['path']}")
        else:
            print("Blender path not found")
    
    print("\n=== Environment Variables ===\n")
    
    for name, value in status["environment"].items():
        if value:
            print(f"✅ {name}: {value}")
        else:
            print(f"❌ {name} not set")
    
    print("\n=== Configuration Files ===\n")
    
    for name, info in status["config_files"].items():
        if info.get("exists"):
            print(f"✅ {name} exists at: {info['path']}")
            if "BLENDER_PATH" in info.get("content", ""):
                print(f"   Contains BLENDER_PATH setting")
            else:
                print(f"   Does not contain BLENDER_PATH setting")
        else:
            print(f"❌ {name} not found")
    
    print("\n=== Output Directories ===\n")
    
    for name, info in status["directories"].items():
        if info.get("exists") and info.get("is_dir"):
            print(f"✅ {name} exists at: {info['path']}")
        elif info.get("exists"):
            print(f"⚠️ {name} exists but is not a directory: {info['path']}")
        else:
            print(f"❌ {name} not found: {info['path']}")
