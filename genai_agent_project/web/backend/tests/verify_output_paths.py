"""
Verify Output Paths Script

This script checks the output directory structure to make sure SVG files are being saved
to the correct locations for both the test environment and the web UI.
"""

import os
import sys
import logging
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add parent directories to path for imports
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
web_dir = backend_dir.parent
project_dir = web_dir.parent
project_root = project_dir.parent

def load_config():
    """Load the configuration from config.yaml"""
    try:
        config_path = project_dir / "config.yaml"
        logger.info(f"Loading config from: {config_path}")
        
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        return config
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {}

def check_output_paths():
    """Check and display all the various output paths"""
    # Load configuration
    config = load_config()
    
    # Get paths from config
    paths = config.get("paths", {})
    output_dir = paths.get("output_dir", str(project_root / "output"))
    svg_output_dir = paths.get("svg_output_dir", str(Path(output_dir) / "svg"))
    diagrams_output_dir = paths.get("diagrams_output_dir", str(Path(output_dir) / "diagrams"))
    
    # Additional paths used in the project
    project_output_dir = str(project_dir / "output")
    project_svg_output_dir = str(Path(project_output_dir) / "svg")
    
    svg_to_video_dir = str(Path(output_dir) / "svg_to_video")
    svg_to_video_svg_dir = str(Path(svg_to_video_dir) / "svg")
    
    # Display all paths
    logger.info("=== Output Directory Paths ===")
    logger.info(f"Project Root: {project_root}")
    logger.info(f"Project Dir: {project_dir}")
    logger.info(f"Web Dir: {web_dir}")
    logger.info(f"Backend Dir: {backend_dir}")
    logger.info(f"Script Dir: {script_dir}")
    logger.info("")
    logger.info(f"Config Output Dir: {output_dir}")
    logger.info(f"Config SVG Output Dir: {svg_output_dir}")
    logger.info(f"Config Diagrams Output Dir: {diagrams_output_dir}")
    logger.info("")
    logger.info(f"Project Output Dir: {project_output_dir}")
    logger.info(f"Project SVG Output Dir: {project_svg_output_dir}")
    logger.info("")
    logger.info(f"SVG to Video Dir: {svg_to_video_dir}")
    logger.info(f"SVG to Video SVG Dir: {svg_to_video_svg_dir}")
    
    # Check if directories exist
    logger.info("\n=== Directory Existence Check ===")
    for path_name, path in [
        ("Output Dir", output_dir),
        ("SVG Output Dir", svg_output_dir),
        ("Diagrams Output Dir", diagrams_output_dir),
        ("Project Output Dir", project_output_dir),
        ("Project SVG Output Dir", project_svg_output_dir),
        ("SVG to Video Dir", svg_to_video_dir),
        ("SVG to Video SVG Dir", svg_to_video_svg_dir),
    ]:
        exists = os.path.exists(path)
        logger.info(f"{path_name}: {'EXISTS' if exists else 'MISSING'}")
        
        if exists:
            # Check for SVG files
            svg_files = [f for f in os.listdir(path) if f.endswith(".svg")]
            logger.info(f"  - Contains {len(svg_files)} SVG files")
            
            # List the SVG files (up to 5)
            if svg_files:
                for i, svg_file in enumerate(svg_files[:5]):
                    logger.info(f"  - {svg_file}")
                
                if len(svg_files) > 5:
                    logger.info(f"  - ... and {len(svg_files) - 5} more")

def create_test_svg_file():
    """Create a test SVG file in all output directories to verify path configuration"""
    # Load configuration
    config = load_config()
    
    # Get paths from config
    paths = config.get("paths", {})
    output_dir = paths.get("output_dir", str(project_root / "output"))
    svg_output_dir = paths.get("svg_output_dir", str(Path(output_dir) / "svg"))
    diagrams_output_dir = paths.get("diagrams_output_dir", str(Path(output_dir) / "diagrams"))
    
    # Additional paths used in the project
    project_output_dir = str(project_dir / "output")
    project_svg_output_dir = str(Path(project_output_dir) / "svg")
    
    svg_to_video_dir = str(Path(output_dir) / "svg_to_video")
    svg_to_video_svg_dir = str(Path(svg_to_video_dir) / "svg")
    
    # Create all directories if they don't exist
    for path in [
        svg_output_dir,
        diagrams_output_dir,
        project_svg_output_dir,
        svg_to_video_svg_dir
    ]:
        os.makedirs(path, exist_ok=True)
    
    # Create test SVG file
    test_svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <rect width="800" height="600" fill="#f0f0f0" />
  <text x="400" y="300" font-family="Arial" font-size="24" text-anchor="middle" fill="#333">
    Test SVG File - Generated by verification script
  </text>
  <text x="400" y="350" font-family="Arial" font-size="16" text-anchor="middle" fill="#666">
    Created at: %(timestamp)s
  </text>
</svg>"""
    
    # Get current timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create test file
    test_svg_filename = f"test_verify_path_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.svg"
    test_svg = test_svg_content % {"timestamp": timestamp}
    
    logger.info(f"\n=== Creating Test SVG File: {test_svg_filename} ===")
    
    # Write file to all directories
    for path_name, path in [
        ("SVG Output Dir", svg_output_dir),
        ("Diagrams Output Dir", diagrams_output_dir),
        ("Project SVG Output Dir", project_svg_output_dir),
        ("SVG to Video SVG Dir", svg_to_video_svg_dir),
    ]:
        file_path = os.path.join(path, test_svg_filename)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(test_svg)
            logger.info(f"Created test SVG file in {path_name}: {file_path}")
        except Exception as e:
            logger.error(f"Error creating test SVG file in {path_name}: {str(e)}")

if __name__ == "__main__":
    try:
        logger.info("Verifying output paths...")
        check_output_paths()
        
        # Ask if the user wants to create a test SVG file
        response = input("\nDo you want to create a test SVG file in all output directories? (y/n): ")
        if response.lower() == "y":
            create_test_svg_file()
        
        logger.info("\nVerification complete.")
    except Exception as e:
        logger.error(f"Error verifying output paths: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
