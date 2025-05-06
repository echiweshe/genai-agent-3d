"""
Test script for SVG to 3D conversion.
This script tests the SVG to 3D conversion functionality.
"""

import os
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project")
sys.path.insert(0, str(project_dir))

# Import SVG to 3D module
try:
    from genai_agent_project.genai_agent.svg_to_video.svg_to_3d import convert_svg_to_3d, get_supported_formats, get_conversion_options
    print("Successfully imported SVG to 3D module")
except ImportError as e:
    print(f"Error importing SVG to 3D module: {e}")
    sys.exit(1)

# Define paths
project_root = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d")
svg_dir = project_root / "output" / "svg"
models_dir = project_root / "output" / "svg_to_video" / "models"

def list_svg_files():
    """List available SVG files."""
    if not svg_dir.exists():
        print(f"SVG directory not found: {svg_dir}")
        return []
    
    svg_files = list(svg_dir.glob("*.svg"))
    return svg_files

def test_svg_to_3d_conversion(svg_path, output_format="obj"):
    """Test SVG to 3D conversion with a specific SVG file."""
    print(f"\nTesting SVG to 3D conversion with: {svg_path}")
    
    # Create models directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    # Generate output file path
    output_file = models_dir / f"{svg_path.stem}.{output_format}"
    
    try:
        # Convert SVG to 3D
        result = convert_svg_to_3d(
            svg_path=str(svg_path),
            output_file=str(output_file),
            extrude_height=10.0,
            scale_factor=1.0
        )
        
        if result and os.path.isfile(result):
            print(f"Success! 3D model generated at: {result}")
            print(f"File size: {os.path.getsize(result)} bytes")
            return True
        else:
            print("Failed to convert SVG to 3D")
            return False
    except Exception as e:
        print(f"Error converting SVG to 3D: {e}")
        return False

def main():
    """Main function to test SVG to 3D conversion."""
    print("SVG to 3D Conversion Test")
    print("========================")
    
    # Get supported formats
    supported_formats = get_supported_formats()
    print(f"Supported output formats: {', '.join(supported_formats)}")
    
    # Get conversion options
    options = get_conversion_options()
    print(f"Available conversion options: {', '.join(options.keys())}")
    
    # List available SVG files
    svg_files = list_svg_files()
    if not svg_files:
        print("No SVG files found to test conversion.")
        return False
    
    print(f"\nFound {len(svg_files)} SVG files:")
    for i, file in enumerate(svg_files):
        print(f"{i+1}. {file.name}")
    
    # Select an SVG file to test
    if len(svg_files) == 1:
        svg_file = svg_files[0]
    else:
        while True:
            try:
                choice = input("\nEnter the number of the SVG file to convert (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return False
                
                index = int(choice) - 1
                if 0 <= index < len(svg_files):
                    svg_file = svg_files[index]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(svg_files)}")
            except ValueError:
                print("Please enter a valid number")
    
    # Select output format
    while True:
        format_choice = input(f"\nEnter output format ({', '.join(supported_formats)}): ")
        if format_choice.lower() in supported_formats:
            break
        else:
            print(f"Please enter a supported format: {', '.join(supported_formats)}")
    
    # Test the conversion
    success = test_svg_to_3d_conversion(svg_file, format_choice)
    
    if success:
        print("\nSVG to 3D conversion test PASSED!")
    else:
        print("\nSVG to 3D conversion test FAILED!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
