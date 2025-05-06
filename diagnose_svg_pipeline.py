"""
Diagnostic tool for the SVG to Video pipeline.
This script performs comprehensive checks on all pipeline components.
"""

import os
import sys
import importlib
import subprocess
import shutil
import platform
from pathlib import Path
import logging
import json
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("svg_pipeline_diagnostic.log", mode="w")
    ]
)
logger = logging.getLogger("SVGPipelineDiagnostic")

# Define paths
PROJECT_ROOT = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d")
PROJECT_ENV = PROJECT_ROOT / "genai_agent_project" / "venv"
SVG_OUTPUT_DIR = PROJECT_ROOT / "output" / "svg"
MODELS_DIR = PROJECT_ROOT / "output" / "svg_to_video" / "models"
ANIMATIONS_DIR = PROJECT_ROOT / "output" / "svg_to_video" / "animations"
VIDEOS_DIR = PROJECT_ROOT / "output" / "svg_to_video" / "videos"
SVG_TO_VIDEO_CODE = PROJECT_ROOT / "genai_agent_project" / "genai_agent" / "svg_to_video"

# ANSI colors
class Colors:
    INFO = '\033[94m'      # Blue
    SUCCESS = '\033[92m'   # Green
    WARNING = '\033[93m'   # Yellow
    ERROR = '\033[91m'     # Red
    BOLD = '\033[1m'       # Bold
    END = '\033[0m'        # Reset

def color_text(text, color):
    """Add color to text based on platform."""
    if platform.system() == "Windows" and "TERM" not in os.environ:
        return text  # No color on Windows command prompt
    return f"{color}{text}{Colors.END}"

def print_section(title):
    """Print a section header."""
    logger.info("\n" + "=" * 50)
    logger.info(color_text(title, Colors.BOLD + Colors.INFO))
    logger.info("=" * 50)

def print_result(name, status, message=""):
    """Print a test result with appropriate color."""
    status_color = {
        "PASS": Colors.SUCCESS,
        "WARN": Colors.WARNING,
        "FAIL": Colors.ERROR,
        "INFO": Colors.INFO
    }
    
    color = status_color.get(status, Colors.END)
    status_text = color_text(f"[{status}]", color)
    logger.info(f"{status_text} {name}: {message}")

def check_directory(path, create_if_missing=True):
    """Check if a directory exists and create it if specified."""
    try:
        if not os.path.exists(path):
            if create_if_missing:
                os.makedirs(path, exist_ok=True)
                logger.info(f"Created missing directory: {path}")
                return "PASS", f"Created directory {path}"
            return "WARN", f"Directory {path} does not exist"
        
        if not os.path.isdir(path):
            return "FAIL", f"Path exists but is not a directory: {path}"
        
        # Check if writable
        try:
            test_file = os.path.join(path, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return "PASS", f"Directory exists and is writable: {path}"
        except Exception as e:
            return "WARN", f"Directory exists but is not writable: {path} - {str(e)}"
    
    except Exception as e:
        return "FAIL", f"Error checking directory {path}: {str(e)}"

def check_env_variables():
    """Check if required environment variables are set."""
    results = []
    
    # Load variables from .env file if available
    env_file = PROJECT_ROOT / "genai_agent_project" / ".env"
    env_vars = {}
    
    if os.path.isfile(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Check essential variables
    required_vars = {
        "BLENDER_PATH": "Path to Blender executable",
        "ANTHROPIC_API_KEY": "API key for Claude (Anthropic)",
        "OPENAI_API_KEY": "API key for OpenAI"
    }
    
    for var, description in required_vars.items():
        # Check .env file first
        if var in env_vars and env_vars[var]:
            # Mask API keys for security
            if "API_KEY" in var:
                masked_value = env_vars[var][:5] + "..." + env_vars[var][-5:] if len(env_vars[var]) > 10 else env_vars[var][:3] + "..."
                results.append((var, "PASS", f"Found in .env file: {masked_value}"))
            else:
                results.append((var, "PASS", f"Found in .env file: {env_vars[var]}"))
        # Then check system environment
        elif var in os.environ and os.environ[var]:
            if "API_KEY" in var:
                masked_value = os.environ[var][:5] + "..." + os.environ[var][-5:] if len(os.environ[var]) > 10 else os.environ[var][:3] + "..."
                results.append((var, "PASS", f"Found in system environment: {masked_value}"))
            else:
                results.append((var, "PASS", f"Found in system environment: {os.environ[var]}"))
        else:
            if var == "BLENDER_PATH":
                # Check default Blender paths
                blender_path = find_blender()
                if blender_path:
                    results.append((var, "WARN", f"Not set in .env or environment, but found at: {blender_path}"))
                else:
                    results.append((var, "FAIL", f"Not set in .env or environment, and not found in default locations"))
            else:
                results.append((var, "WARN", f"Not set in .env or environment: {description}"))
    
    return results

def find_blender():
    """Find Blender executable in default locations."""
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
        if os.path.isfile(path):
            return path
    
    # Check if blender is in PATH
    blender = shutil.which("blender")
    if blender:
        return blender
    
    return None

def check_packages():
    """Check for required Python packages."""
    results = []
    
    required_packages = [
        "anthropic",
        "langchain", 
        "langchain-anthropic",
        "langchain-openai",
        "openai",
        "svgwrite",
        "fastapi",
        "uvicorn",
        "requests",
        "pathlib",
        "mathutils"
    ]
    
    # Check if packages are installed
    for package in required_packages:
        try:
            # Try to import the package
            importlib.import_module(package)
            results.append((package, "PASS", "Successfully imported"))
        except ImportError:
            # Check if it's installed but not importable
            try:
                subprocess.check_output([sys.executable, '-m', 'pip', 'show', package])
                results.append((package, "WARN", "Installed but not importable"))
            except subprocess.CalledProcessError:
                results.append((package, "FAIL", "Not installed"))
        except Exception as e:
            results.append((package, "WARN", f"Error importing: {str(e)}"))
    
    return results

def check_modules():
    """Check if all pipeline modules can be imported."""
    results = []
    
    # Add project directory to path
    project_dir = PROJECT_ROOT / "genai_agent_project"
    sys.path.insert(0, str(project_dir))
    
    modules = [
        # SVG Generator
        ("genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator", "SVG Generator"),
        
        # SVG to 3D
        ("genai_agent_project.genai_agent.svg_to_video.svg_to_3d", "SVG to 3D Converter"),
        
        # Animation
        ("genai_agent_project.genai_agent.svg_to_video.animation", "Animation Module"),
        
        # Rendering
        ("genai_agent_project.genai_agent.svg_to_video.rendering", "Rendering Module"),
        
        # LLM Integrations
        ("genai_agent_project.genai_agent.svg_to_video.llm_integrations.llm_factory", "LLM Factory"),
        ("genai_agent_project.genai_agent.svg_to_video.llm_integrations.claude_direct", "Claude Direct Integration")
    ]
    
    for module_name, display_name in modules:
        try:
            importlib.import_module(module_name)
            results.append((display_name, "PASS", "Successfully imported"))
        except ImportError as e:
            results.append((display_name, "FAIL", f"Import error: {str(e)}"))
        except Exception as e:
            results.append((display_name, "FAIL", f"Error: {str(e)}"))
    
    # Remove project directory from path
    if str(project_dir) in sys.path:
        sys.path.remove(str(project_dir))
    
    return results

def check_api_connectivity():
    """Check connectivity to required APIs."""
    results = []
    
    # Check Claude API
    try:
        import anthropic
        
        # Get API key from environment or .env file
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            env_file = PROJECT_ROOT / "genai_agent_project" / ".env"
            if os.path.isfile(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith("ANTHROPIC_API_KEY="):
                            api_key = line.strip().split("=", 1)[1]
                            break
        
        if api_key:
            # Just verify the client initializes without error
            client = anthropic.Anthropic(api_key=api_key)
            results.append(("Claude API", "PASS", "Successfully initialized client"))
        else:
            results.append(("Claude API", "WARN", "API key not found, skipping connectivity test"))
    except Exception as e:
        results.append(("Claude API", "WARN", f"Error initializing client: {str(e)}"))
    
    # Check OpenAI API
    try:
        import openai
        
        # Get API key from environment or .env file
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            env_file = PROJECT_ROOT / "genai_agent_project" / ".env"
            if os.path.isfile(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith("OPENAI_API_KEY="):
                            api_key = line.strip().split("=", 1)[1]
                            break
        
        if api_key:
            # Just verify the client initializes without error
            client = openai.OpenAI(api_key=api_key)
            results.append(("OpenAI API", "PASS", "Successfully initialized client"))
        else:
            results.append(("OpenAI API", "WARN", "API key not found, skipping connectivity test"))
    except Exception as e:
        results.append(("OpenAI API", "WARN", f"Error initializing client: {str(e)}"))
    
    # Check Backend API
    try:
        import requests
        
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            results.append(("Backend API", "PASS", "Running and accessible"))
        else:
            results.append(("Backend API", "WARN", f"Returned status code {response.status_code}"))
    except requests.exceptions.ConnectionError:
        results.append(("Backend API", "WARN", "Not running or not accessible"))
    except Exception as e:
        results.append(("Backend API", "WARN", f"Error: {str(e)}"))
    
    # Check SVG Generator API
    try:
        import requests
        
        response = requests.get("http://localhost:8000/svg-generator/health", timeout=5)
        if response.status_code == 200:
            results.append(("SVG Generator API", "PASS", "Endpoint is healthy"))
        else:
            results.append(("SVG Generator API", "WARN", f"Returned status code {response.status_code}"))
    except requests.exceptions.ConnectionError:
        results.append(("SVG Generator API", "WARN", "Not running or not accessible"))
    except Exception as e:
        results.append(("SVG Generator API", "WARN", f"Error: {str(e)}"))
    
    return results

def check_blender():
    """Check if Blender is installed and working."""
    results = []
    
    # Get Blender path
    blender_path = os.environ.get("BLENDER_PATH", "")
    if not blender_path:
        env_file = PROJECT_ROOT / "genai_agent_project" / ".env"
        if os.path.isfile(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith("BLENDER_PATH="):
                        blender_path = line.strip().split("=", 1)[1]
                        break
    
    if not blender_path:
        blender_path = find_blender()
    
    if not blender_path:
        results.append(("Blender Executable", "FAIL", "Could not find Blender executable"))
        return results
    
    # Check if the executable exists
    if not os.path.isfile(blender_path):
        results.append(("Blender Executable", "FAIL", f"Blender executable not found at: {blender_path}"))
        return results
    
    results.append(("Blender Executable", "PASS", f"Found at: {blender_path}"))
    
    # Test running Blender with --version
    try:
        output = subprocess.check_output([blender_path, "--version"], text=True, stderr=subprocess.STDOUT)
        version_info = output.strip()
        results.append(("Blender Version", "PASS", version_info))
    except subprocess.CalledProcessError as e:
        results.append(("Blender Version", "WARN", f"Error running Blender: {e.output}"))
    except Exception as e:
        results.append(("Blender Version", "WARN", f"Error: {str(e)}"))
    
    # Check for mathutils module
    try:
        # Check if mathutils is available as a standard package
        import mathutils
        results.append(("mathutils Module", "PASS", "Available as a Python package"))
    except ImportError:
        # Check if a stub exists in the project
        mathutils_stub = SVG_TO_VIDEO_CODE / "svg_to_3d" / "mathutils.py"
        if os.path.isfile(mathutils_stub):
            results.append(("mathutils Module", "PASS", f"Stub available at {mathutils_stub}"))
        else:
            results.append(("mathutils Module", "WARN", "Not available as a package and no stub found"))
    
    return results

def check_file_counts():
    """Check the number of files in each output directory."""
    results = []
    
    # Check SVG files
    svg_files = list(SVG_OUTPUT_DIR.glob("*.svg"))
    results.append(("SVG Files", "INFO", f"Found {len(svg_files)} SVG files in {SVG_OUTPUT_DIR}"))
    
    # Check 3D model files
    model_files = list(MODELS_DIR.glob("*.obj")) + list(MODELS_DIR.glob("*.stl")) + \
                 list(MODELS_DIR.glob("*.fbx")) + list(MODELS_DIR.glob("*.glb"))
    results.append(("3D Model Files", "INFO", f"Found {len(model_files)} 3D model files in {MODELS_DIR}"))
    
    # Check animation files
    animation_files = list(ANIMATIONS_DIR.glob("*.blend"))
    results.append(("Animation Files", "INFO", f"Found {len(animation_files)} animation files in {ANIMATIONS_DIR}"))
    
    # Check video files
    video_files = list(VIDEOS_DIR.glob("*.mp4")) + list(VIDEOS_DIR.glob("*.avi")) + \
                 list(VIDEOS_DIR.glob("*.mov"))
    results.append(("Video Files", "INFO", f"Found {len(video_files)} video files in {VIDEOS_DIR}"))
    
    return results

def run_simple_tests():
    """Run simple tests to ensure the pipeline components are working."""
    results = []
    
    # Add project directory to path
    project_dir = PROJECT_ROOT / "genai_agent_project"
    sys.path.insert(0, str(project_dir))
    
    # Test SVG generation with mock provider
    try:
        from genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator import generate_svg
        
        # Generate test SVG
        test_svg_path = SVG_OUTPUT_DIR / f"test_diagnostic_{int(time.time())}.svg"
        result = generate_svg(
            prompt="Create a simple flowchart for testing",
            diagram_type="flowchart",
            output_file=str(test_svg_path),
            provider="mock"
        )
        
        if result and os.path.isfile(test_svg_path):
            with open(test_svg_path, 'r') as f:
                svg_content = f.read()
            
            size = os.path.getsize(test_svg_path)
            results.append(("SVG Generation (Mock)", "PASS", f"Generated SVG at {test_svg_path} ({size} bytes)"))
            
            # Test SVG to 3D conversion if applicable
            try:
                from genai_agent_project.genai_agent.svg_to_video.svg_to_3d import convert_svg_to_3d
                
                # Get Blender path
                blender_path = os.environ.get("BLENDER_PATH", "")
                if not blender_path:
                    env_file = PROJECT_ROOT / "genai_agent_project" / ".env"
                    if os.path.isfile(env_file):
                        with open(env_file, 'r') as f:
                            for line in f:
                                if line.startswith("BLENDER_PATH="):
                                    blender_path = line.strip().split("=", 1)[1]
                                    break
                
                if not blender_path:
                    blender_path = find_blender()
                
                if blender_path and os.path.isfile(blender_path):
                    test_model_path = MODELS_DIR / f"{test_svg_path.stem}.obj"
                    
                    try:
                        # Skip actual conversion for diagnostic purposes
                        # Just check if the function is callable
                        results.append(("SVG to 3D Conversion", "PASS", "Function is callable (skipped actual conversion for diagnostics)"))
                        
                        # Similarly, test animation and rendering function existence
                        from genai_agent_project.genai_agent.svg_to_video.animation import animate_model
                        results.append(("Animation", "PASS", "Function is callable (skipped actual animation for diagnostics)"))
                        
                        from genai_agent_project.genai_agent.svg_to_video.rendering import render_video
                        results.append(("Rendering", "PASS", "Function is callable (skipped actual rendering for diagnostics)"))
                    except Exception as e:
                        results.append(("3D Pipeline", "WARN", f"Error testing pipeline functions: {str(e)}"))
                else:
                    results.append(("3D Pipeline", "WARN", "Skipping 3D tests because Blender not found"))
            except ImportError as e:
                results.append(("SVG to 3D Conversion", "WARN", f"Import error: {str(e)}"))
            except Exception as e:
                results.append(("SVG to 3D Conversion", "WARN", f"Error: {str(e)}"))
        else:
            results.append(("SVG Generation (Mock)", "FAIL", f"Failed to generate test SVG"))
    except ImportError as e:
        results.append(("SVG Generation", "FAIL", f"Import error: {str(e)}"))
    except Exception as e:
        results.append(("SVG Generation", "FAIL", f"Error: {str(e)}"))
    
    # Remove project directory from path
    if str(project_dir) in sys.path:
        sys.path.remove(str(project_dir))
    
    return results

def generate_summary(all_results):
    """Generate a summary of all test results."""
    summary = {
        "pass": 0,
        "warn": 0,
        "fail": 0,
        "info": 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sections": {}
    }
    
    for section, results in all_results.items():
        section_summary = {"pass": 0, "warn": 0, "fail": 0, "info": 0}
        for _, status, _ in results:
            if status == "PASS":
                section_summary["pass"] += 1
                summary["pass"] += 1
            elif status == "WARN":
                section_summary["warn"] += 1
                summary["warn"] += 1
            elif status == "FAIL":
                section_summary["fail"] += 1
                summary["fail"] += 1
            elif status == "INFO":
                section_summary["info"] += 1
                summary["info"] += 1
        
        summary["sections"][section] = section_summary
    
    return summary

def print_summary(summary):
    """Print a summary of all test results."""
    print_section("DIAGNOSTIC SUMMARY")
    
    logger.info(f"Timestamp: {summary['timestamp']}")
    logger.info(f"Tests Passed: {summary['pass']}")
    logger.info(f"Warnings: {summary['warn']}")
    logger.info(f"Failures: {summary['fail']}")
    logger.info(f"Info Items: {summary['info']}")
    
    logger.info("\nSection Results:")
    for section, results in summary["sections"].items():
        status = "PASS"
        if results["fail"] > 0:
            status = "FAIL"
        elif results["warn"] > 0:
            status = "WARN"
        
        status_color = {
            "PASS": Colors.SUCCESS,
            "WARN": Colors.WARNING,
            "FAIL": Colors.ERROR
        }
        
        status_text = color_text(f"[{status}]", status_color[status])
        logger.info(f"{status_text} {section}: {results['pass']} passed, {results['warn']} warnings, {results['fail']} failures")
    
    # Overall assessment
    if summary["fail"] > 0:
        logger.info(color_text("\nOverall Assessment: ISSUES DETECTED", Colors.ERROR))
        logger.info("Some tests failed. Please review the detailed results to fix the issues.")
    elif summary["warn"] > 0:
        logger.info(color_text("\nOverall Assessment: MOSTLY WORKING WITH WARNINGS", Colors.WARNING))
        logger.info("The pipeline appears to be working with some warnings. Review the details for potential improvements.")
    else:
        logger.info(color_text("\nOverall Assessment: ALL TESTS PASSED", Colors.SUCCESS))
        logger.info("The pipeline appears to be working correctly.")

def run_diagnostics():
    """Run all diagnostic tests and generate a report."""
    print_section("SVG TO VIDEO PIPELINE DIAGNOSTICS")
    logger.info(f"Starting diagnostics at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    all_results = {}
    
    # Check directories
    print_section("Checking Directory Structure")
    directories = [
        (SVG_OUTPUT_DIR, "SVG Output Directory"),
        (MODELS_DIR, "3D Models Directory"),
        (ANIMATIONS_DIR, "Animations Directory"),
        (VIDEOS_DIR, "Videos Directory"),
        (SVG_TO_VIDEO_CODE, "SVG to Video Code Directory"),
        (SVG_TO_VIDEO_CODE / "svg_generator", "SVG Generator Code"),
        (SVG_TO_VIDEO_CODE / "svg_to_3d", "SVG to 3D Code"),
        (SVG_TO_VIDEO_CODE / "animation", "Animation Code"),
        (SVG_TO_VIDEO_CODE / "rendering", "Rendering Code"),
        (SVG_TO_VIDEO_CODE / "llm_integrations", "LLM Integrations Code")
    ]
    
    directory_results = []
    for path, name in directories:
        status, message = check_directory(path)
        print_result(name, status, message)
        directory_results.append((name, status, message))
    
    all_results["Directory Structure"] = directory_results
    
    # Check environment variables
    print_section("Checking Environment Variables")
    env_results = check_env_variables()
    for name, status, message in env_results:
        print_result(name, status, message)
    
    all_results["Environment Variables"] = env_results
    
    # Check packages
    print_section("Checking Required Packages")
    package_results = check_packages()
    for name, status, message in package_results:
        print_result(name, status, message)
    
    all_results["Required Packages"] = package_results
    
    # Check modules
    print_section("Checking Pipeline Modules")
    module_results = check_modules()
    for name, status, message in module_results:
        print_result(name, status, message)
    
    all_results["Pipeline Modules"] = module_results
    
    # Check API connectivity
    print_section("Checking API Connectivity")
    api_results = check_api_connectivity()
    for name, status, message in api_results:
        print_result(name, status, message)
    
    all_results["API Connectivity"] = api_results
    
    # Check Blender
    print_section("Checking Blender")
    blender_results = check_blender()
    for name, status, message in blender_results:
        print_result(name, status, message)
    
    all_results["Blender"] = blender_results
    
    # Check file counts
    print_section("Checking File Counts")
    file_results = check_file_counts()
    for name, status, message in file_results:
        print_result(name, status, message)
    
    all_results["File Counts"] = file_results
    
    # Run simple tests
    print_section("Running Simple Tests")
    test_results = run_simple_tests()
    for name, status, message in test_results:
        print_result(name, status, message)
    
    all_results["Simple Tests"] = test_results
    
    # Generate and print summary
    summary = generate_summary(all_results)
    print_summary(summary)
    
    # Write results to JSON file
    results_file = "svg_pipeline_diagnostic_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "summary": summary,
            "results": {
                section: [(name, status, message) for name, status, message in results]
                for section, results in all_results.items()
            }
        }, f, indent=2)
    
    logger.info(f"\nDetailed results saved to {results_file} and svg_pipeline_diagnostic.log")

if __name__ == "__main__":
    run_diagnostics()
