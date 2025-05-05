"""
SVG to Video Pipeline Status Checker

This script checks the status of the SVG to Video pipeline and reports any issues.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path
import requests
import time

# Define colors for console output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a header in blue and bold."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")

def print_status(component, status, message=""):
    """Print a status message with appropriate color."""
    status_color = {
        "OK": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED
    }
    color = status_color.get(status, Colors.END)
    print(f"  {component}: {color}{status}{Colors.END} {message}")

def check_directory(path, required=True):
    """Check if a directory exists and is a directory."""
    if not os.path.exists(path):
        if required:
            return "ERROR", f"Directory not found: {path}"
        else:
            return "WARNING", f"Directory not found: {path}"
    
    if not os.path.isdir(path):
        return "ERROR", f"Path exists but is not a directory: {path}"
    
    return "OK", f"Directory exists: {path}"

def check_file(path, required=True):
    """Check if a file exists and is a file."""
    if not os.path.exists(path):
        if required:
            return "ERROR", f"File not found: {path}"
        else:
            return "WARNING", f"File not found: {path}"
    
    if not os.path.isfile(path):
        return "ERROR", f"Path exists but is not a file: {path}"
    
    return "OK", f"File exists: {path}"

def count_files(directory, extension=None):
    """Count files in a directory with a specific extension."""
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return 0
    
    if extension:
        return len([f for f in os.listdir(directory) if f.endswith(extension)])
    else:
        return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

def check_imports():
    """Check if all required modules can be imported."""
    results = []
    
    # Add the project directory to the path
    project_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project")
    sys.path.insert(0, str(project_dir))
    
    # List of modules to check
    modules = [
        # SVG Generator modules
        ("genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator", "SVG Generator"),
        # LLM Integration modules
        ("genai_agent_project.genai_agent.svg_to_video.llm_integrations.llm_factory", "LLM Factory"),
        ("genai_agent_project.genai_agent.svg_to_video.llm_integrations.claude_direct", "Claude Direct"),
        # SVG to 3D modules
        ("genai_agent_project.genai_agent.svg_to_video.svg_to_3d", "SVG to 3D Converter"),
        # Animation and Rendering modules
        ("genai_agent_project.genai_agent.svg_to_video.animation", "Animation Module"),
        ("genai_agent_project.genai_agent.svg_to_video.rendering", "Rendering Module")
    ]
    
    for module_name, display_name in modules:
        try:
            importlib.import_module(module_name)
            results.append((display_name, "OK", "Successfully imported"))
        except ImportError as e:
            results.append((display_name, "ERROR", f"Import error: {str(e)}"))
        except Exception as e:
            results.append((display_name, "ERROR", f"Error: {str(e)}"))
    
    # Remove the added path
    sys.path.pop(0)
    
    return results

def check_api_keys():
    """Check if API keys are configured properly."""
    results = []
    
    # Check environment variables
    api_keys = {
        "ANTHROPIC_API_KEY": "Anthropic API Key",
        "OPENAI_API_KEY": "OpenAI API Key"
    }
    
    for env_var, display_name in api_keys.items():
        # Check .env file first
        env_file_path = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/.env")
        if os.path.isfile(env_file_path):
            with open(env_file_path, 'r') as f:
                env_content = f.read()
                if f"{env_var}=" in env_content:
                    key_value = env_content.split(f"{env_var}=")[1].split('\n')[0]
                    if key_value and key_value.strip():
                        results.append((display_name, "OK", f"Found in .env file: {key_value[:5]}..."))
                        continue
        
        # Check system environment variables
        if env_var in os.environ and os.environ[env_var]:
            results.append((display_name, "OK", f"Found in system environment: {os.environ[env_var][:5]}..."))
        else:
            results.append((display_name, "WARNING", "Not found or empty"))
    
    return results

def check_blender_setup():
    """Check if Blender is properly configured."""
    results = []
    
    # Check BLENDER_PATH in .env file
    env_file_path = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/.env")
    if os.path.isfile(env_file_path):
        with open(env_file_path, 'r') as f:
            env_content = f.read()
            if "BLENDER_PATH=" in env_content:
                blender_path = env_content.split("BLENDER_PATH=")[1].split('\n')[0]
                if blender_path:
                    # Check if Blender executable exists
                    status, message = check_file(blender_path)
                    results.append(("Blender Executable", status, message))
                else:
                    results.append(("Blender Executable", "WARNING", "BLENDER_PATH is empty in .env file"))
            else:
                results.append(("Blender Executable", "WARNING", "BLENDER_PATH not found in .env file"))
    else:
        results.append(("Blender Executable", "WARNING", ".env file not found"))
    
    # Check mathutils module
    try:
        import mathutils
        results.append(("mathutils Module", "OK", "Successfully imported"))
    except ImportError:
        results.append(("mathutils Module", "WARNING", "Not installed (required for 3D conversion)"))
    
    return results

def check_web_ui_status():
    """Check if the web UI is running and responding."""
    results = []
    
    # Check backend
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            results.append(("Backend API", "OK", "Running at http://localhost:8000"))
        else:
            results.append(("Backend API", "ERROR", f"Returned status code {response.status_code}"))
    except requests.exceptions.ConnectionError:
        results.append(("Backend API", "ERROR", "Not running or not accessible"))
    except Exception as e:
        results.append(("Backend API", "ERROR", f"Error: {str(e)}"))
    
    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            results.append(("Frontend", "OK", "Running at http://localhost:3000"))
        else:
            results.append(("Frontend", "ERROR", f"Returned status code {response.status_code}"))
    except requests.exceptions.ConnectionError:
        results.append(("Frontend", "ERROR", "Not running or not accessible"))
    except Exception as e:
        results.append(("Frontend", "ERROR", f"Error: {str(e)}"))
    
    # Check SVG generator endpoint
    try:
        response = requests.get("http://localhost:8000/svg-generator/health", timeout=5)
        if response.status_code == 200:
            results.append(("SVG Generator API", "OK", "Endpoint is healthy"))
        else:
            results.append(("SVG Generator API", "ERROR", f"Returned status code {response.status_code}"))
    except requests.exceptions.ConnectionError:
        results.append(("SVG Generator API", "ERROR", "Not running or not accessible"))
    except Exception as e:
        results.append(("SVG Generator API", "ERROR", f"Error: {str(e)}"))
    
    # Check available providers
    try:
        response = requests.get("http://localhost:8000/svg-generator/providers", timeout=5)
        if response.status_code == 200:
            providers = response.json()
            if providers and len(providers) > 0:
                results.append(("SVG Generator Providers", "OK", f"Available providers: {', '.join(providers)}"))
            else:
                results.append(("SVG Generator Providers", "WARNING", "No providers available"))
        else:
            results.append(("SVG Generator Providers", "ERROR", f"Returned status code {response.status_code}"))
    except requests.exceptions.ConnectionError:
        results.append(("SVG Generator Providers", "ERROR", "Not running or not accessible"))
    except Exception as e:
        results.append(("SVG Generator Providers", "ERROR", f"Error: {str(e)}"))
    
    return results

def check_directory_structure():
    """Check if the directory structure is correct."""
    results = []
    
    # Define required directories
    directories = [
        # Main output directories
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg", "SVG Output Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/svg", "SVG to Video SVG Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/output/svg", "Test SVG Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/models", "3D Models Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/animations", "Animations Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/videos", "Videos Directory", True),
        
        # Code directories
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/genai_agent/svg_to_video", "SVG to Video Code Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/genai_agent/svg_to_video/svg_generator", "SVG Generator Code Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/genai_agent/svg_to_video/llm_integrations", "LLM Integrations Code Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/genai_agent/svg_to_video/svg_to_3d", "SVG to 3D Code Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/genai_agent/svg_to_video/animation", "Animation Code Directory", True),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/genai_agent/svg_to_video/rendering", "Rendering Code Directory", True),
    ]
    
    for directory, display_name, required in directories:
        status, message = check_directory(directory, required)
        results.append((display_name, status, message))
    
    return results

def check_file_counts():
    """Check the number of files in each directory."""
    results = []
    
    # Define directories to check
    directories = [
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg", "SVG Files", ".svg"),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/models", "3D Models", ".obj"),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/animations", "Animations", ".blend"),
        ("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/videos", "Videos", ".mp4")
    ]
    
    for directory, display_name, extension in directories:
        count = count_files(directory, extension)
        if count > 0:
            results.append((display_name, "OK", f"Found {count} files"))
        else:
            results.append((display_name, "WARNING", f"No {extension} files found"))
    
    return results

def print_results(category, results):
    """Print results for a category."""
    print_header(category)
    for component, status, message in results:
        print_status(component, status, message)

def main():
    """Main function to check the SVG to Video pipeline status."""
    print(f"{Colors.BLUE}{Colors.BOLD}SVG to Video Pipeline Status Checker{Colors.END}")
    print(f"{Colors.BLUE}==============================={Colors.END}")
    print("\nChecking status of the SVG to Video pipeline...\n")
    
    # Check directory structure
    print_results("Directory Structure", check_directory_structure())
    
    # Check imports
    print_results("Module Imports", check_imports())
    
    # Check API keys
    print_results("API Keys", check_api_keys())
    
    # Check Blender setup
    print_results("Blender Setup", check_blender_setup())
    
    # Check file counts
    print_results("File Counts", check_file_counts())
    
    # Check web UI status
    print_results("Web UI Status", check_web_ui_status())
    
    print(f"\n{Colors.BLUE}{Colors.BOLD}Status Check Complete{Colors.END}")
    print(f"{Colors.BLUE}==================={Colors.END}")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
