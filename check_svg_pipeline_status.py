"""
SVG to Video Pipeline Status Checker

This script checks the status of the SVG to Video pipeline and verifies that
all components are working correctly.
"""

import os
import sys
import logging
import importlib
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(ROOT_DIR, "genai_agent_project")

# Add the project directory to sys.path
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

def print_section(title):
    """Print a section title."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def check_directories():
    """Check if all required directories exist."""
    print_section("Checking Directories")
    
    directories = {
        "Main SVG Output": os.path.join(ROOT_DIR, "output", "svg"),
        "SVG to Video - SVG": os.path.join(ROOT_DIR, "output", "svg_to_video", "svg"),
        "SVG to Video - Models": os.path.join(ROOT_DIR, "output", "svg_to_video", "models"),
        "SVG to Video - Animations": os.path.join(ROOT_DIR, "output", "svg_to_video", "animations"),
        "SVG to Video - Videos": os.path.join(ROOT_DIR, "output", "svg_to_video", "videos"),
    }
    
    all_exist = True
    
    for name, path in directories.items():
        if os.path.exists(path):
            if os.path.isdir(path):
                print(f"✅ {name}: {path}")
            else:
                print(f"❌ {name} exists but is a file, not a directory: {path}")
                all_exist = False
        else:
            print(f"❌ {name} does not exist: {path}")
            all_exist = False
    
    return all_exist

def check_module_imports():
    """Check if all required modules can be imported."""
    print_section("Checking Module Imports")
    
    modules = {
        "SVG Generator": "genai_agent.svg_to_video.svg_generator",
        "SVG to 3D Converter": "genai_agent.svg_to_video.svg_to_3d",
        "Animation Generator": "genai_agent.svg_to_video.animation",
        "Video Renderer": "genai_agent.svg_to_video.rendering",
    }
    
    all_imported = True
    
    for name, module_path in modules.items():
        try:
            module = importlib.import_module(module_path)
            print(f"✅ {name} imported successfully")
        except Exception as e:
            print(f"❌ {name} import failed: {str(e)}")
            all_imported = False
    
    return all_imported

def check_svg_to_3d_converter():
    """Check if the SVG to 3D converter is working correctly."""
    print_section("Checking SVG to 3D Converter")
    
    try:
        # Import the SVG to 3D converter
        from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter
        
        # Create an instance with debug mode
        converter = SVGTo3DConverter(debug=True)
        
        print(f"✅ SVGTo3DConverter initialized successfully")
        print(f"✅ SVGTo3DConverter debug parameter working")
        
        return True
    except Exception as e:
        print(f"❌ SVGTo3DConverter test failed: {str(e)}")
        return False

def check_api_keys():
    """Check if API keys are properly configured."""
    print_section("Checking API Keys")
    
    # Check for Anthropic API key
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        print(f"✅ Anthropic API key found")
    else:
        print(f"❌ Anthropic API key not found")
    
    # Check for OpenAI API key
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        print(f"✅ OpenAI API key found")
    else:
        print(f"❌ OpenAI API key not found")
    
    return bool(anthropic_key) or bool(openai_key)

def check_blender_executable():
    """Check if Blender executable is available."""
    print_section("Checking Blender Executable")
    
    # Common Blender executable paths
    blender_paths = [
        "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
        "/usr/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
    ]
    
    blender_found = False
    
    for path in blender_paths:
        if os.path.exists(path):
            print(f"✅ Blender executable found: {path}")
            blender_found = True
            break
    
    if not blender_found:
        print(f"⚠️ Blender executable not found in common locations")
        
        # Try to find it using 'where' command on Windows or 'which' on Unix
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(["where", "blender"], capture_output=True, text=True)
            else:  # Unix-like
                result = subprocess.run(["which", "blender"], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ Blender executable found: {result.stdout.strip()}")
                blender_found = True
        except Exception as e:
            print(f"⚠️ Failed to check for Blender using system commands: {str(e)}")
    
    return blender_found

def count_files():
    """Count the number of files in each output directory."""
    print_section("Checking File Counts")
    
    directories = {
        "SVG Files": os.path.join(ROOT_DIR, "output", "svg_to_video", "svg"),
        "3D Models": os.path.join(ROOT_DIR, "output", "svg_to_video", "models"),
        "Animations": os.path.join(ROOT_DIR, "output", "svg_to_video", "animations"),
        "Videos": os.path.join(ROOT_DIR, "output", "svg_to_video", "videos"),
    }
    
    for name, path in directories.items():
        if os.path.exists(path) and os.path.isdir(path):
            file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            print(f"{name}: {file_count} files")
        else:
            print(f"{name}: Directory not found")

def check_web_ui():
    """Check if the web UI is running and accessible."""
    print_section("Checking Web UI")
    
    import urllib.request
    import urllib.error
    
    # Check backend
    backend_url = "http://localhost:8000/api/status"
    
    try:
        response = urllib.request.urlopen(backend_url)
        if response.status == 200:
            print(f"✅ Backend API is running")
        else:
            print(f"⚠️ Backend API returned status code {response.status}")
    except urllib.error.URLError as e:
        print(f"❌ Backend API is not accessible: {str(e)}")
    
    # Check frontend
    frontend_url = "http://localhost:3000"
    
    try:
        response = urllib.request.urlopen(frontend_url)
        if response.status == 200:
            print(f"✅ Frontend is running")
        else:
            print(f"⚠️ Frontend returned status code {response.status}")
    except urllib.error.URLError as e:
        print(f"❌ Frontend is not accessible: {str(e)}")

def main():
    """Run all checks and report the overall status."""
    print("SVG to Video Pipeline Status Check")
    print(f"Running at: {ROOT_DIR}")
    print(f"Date: {subprocess.check_output('date /t', shell=True).decode('utf-8').strip()}")
    print(f"Time: {subprocess.check_output('time /t', shell=True).decode('utf-8').strip()}")
    
    # Run all checks
    directories_ok = check_directories()
    modules_ok = check_module_imports()
    converter_ok = check_svg_to_3d_converter()
    api_keys_ok = check_api_keys()
    blender_ok = check_blender_executable()
    
    # File counts (informational only)
    count_files()
    
    # Check web UI
    check_web_ui()
    
    # Overall status
    print_section("Overall Status")
    
    status = {
        "Directories": "✅ OK" if directories_ok else "❌ Issues Found",
        "Module Imports": "✅ OK" if modules_ok else "❌ Issues Found",
        "SVG to 3D Converter": "✅ OK" if converter_ok else "❌ Issues Found",
        "API Keys": "✅ OK" if api_keys_ok else "⚠️ Missing Some Keys",
        "Blender Executable": "✅ OK" if blender_ok else "⚠️ Not Found (Optional)",
    }
    
    for name, result in status.items():
        print(f"{name}: {result}")
    
    # Overall result
    critical_issues = not (directories_ok and modules_ok and converter_ok)
    
    if critical_issues:
        print("\n❌ Critical issues found. The SVG to Video pipeline may not work correctly.")
    else:
        print("\n✅ No critical issues found. The SVG to Video pipeline should work correctly.")

if __name__ == "__main__":
    main()
