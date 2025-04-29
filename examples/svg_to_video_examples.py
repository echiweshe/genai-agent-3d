"""
SVG to Video Pipeline Examples

This script demonstrates how to use the SVG to Video pipeline from Python code.
It includes examples for each stage of the pipeline.
"""

import os
import asyncio
import json
from pathlib import Path

# Add parent directory to path to import genai_agent modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from genai_agent.svg_to_video.pipeline import SVGToVideoPipeline
from genai_agent.svg_to_video.utils import check_blender_installation

# Load configuration
def load_config():
    config_path = Path(__file__).parent.parent / "config" / "svg_video_config.json"
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {}

# Example 1: Generate SVG only
async def example_generate_svg():
    """Example of generating an SVG diagram."""
    print("\n=== Example 1: Generate SVG Only ===")
    
    config = load_config()
    pipeline = SVGToVideoPipeline(config)
    
    # Concept description
    concept = "A flowchart showing user authentication process with login, validation, and access control steps"
    
    # Generate SVG
    print(f"Generating SVG for concept: '{concept}'")
    
    output_path = os.path.join(config.get("output_dir", "outputs"), "example_flowchart.svg")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    result = await pipeline.generate_svg_only(concept, output_path)
    
    if result["status"] == "success":
        print(f"SVG generated successfully: {result['output_path']}")
        
        # Print SVG statistics (e.g., size)
        if os.path.exists(result['output_path']):
            file_size = os.path.getsize(result['output_path']) / 1024  # Size in KB
            print(f"SVG file size: {file_size:.2f} KB")
    else:
        print(f"Error generating SVG: {result.get('error', 'Unknown error')}")

# Example 2: Convert SVG to 3D model
async def example_svg_to_3d():
    """Example of converting an SVG to a 3D model."""
    print("\n=== Example 2: Convert SVG to 3D ===")
    
    config = load_config()
    pipeline = SVGToVideoPipeline(config)
    
    # Check if we have an SVG from the previous example
    svg_path = os.path.join(config.get("output_dir", "outputs"), "example_flowchart.svg")
    
    if not os.path.exists(svg_path):
        print(f"SVG file not found: {svg_path}")
        print("Please run example_generate_svg() first")
        return
    
    # Output path for 3D model
    output_path = os.path.join(config.get("output_dir", "outputs"), "example_flowchart.blend")
    
    print(f"Converting SVG to 3D model: {svg_path}")
    
    # Convert SVG to 3D
    result = await pipeline.convert_svg_to_3d_only(svg_path, output_path)
    
    if result["status"] == "success":
        print(f"3D model generated successfully: {result['output_path']}")
    else:
        print(f"Error converting SVG to 3D: {result.get('error', 'Unknown error')}")

# Example 3: Full pipeline from concept to video
async def example_full_pipeline():
    """Example of the full pipeline from concept to video."""
    print("\n=== Example 3: Full Pipeline (Concept to Video) ===")
    
    config = load_config()
    pipeline = SVGToVideoPipeline(config)
    
    # Concept description
    concept = "A network diagram showing a secure cloud architecture with VPC, subnets, EC2 instances, and a database"
    
    # Output path for video
    output_path = os.path.join(config.get("output_dir", "outputs"), "example_network.mp4")
    
    # Set options
    options = {
        "provider": "claude",  # or any available provider
        "render_quality": "medium",
        "animation_type": "network",
        "resolution": (1280, 720)
    }
    
    print(f"Generating video for concept: '{concept}'")
    print(f"Using options: {options}")
    
    # Process through pipeline
    result = await pipeline.process(concept, output_path, options)
    
    if result["status"] == "success":
        print(f"Video generated successfully: {result['output_path']}")
    else:
        print(f"Error generating video: {result.get('error', 'Unknown error')}")

# Example 4: Convert existing SVG to video
async def example_convert_existing_svg():
    """Example of converting an existing SVG to video."""
    print("\n=== Example 4: Convert Existing SVG to Video ===")
    
    config = load_config()
    pipeline = SVGToVideoPipeline(config)
    
    # Check if we have an SVG from a previous example
    svg_path = os.path.join(config.get("output_dir", "outputs"), "example_flowchart.svg")
    
    if not os.path.exists(svg_path):
        print(f"SVG file not found: {svg_path}")
        print("Please run example_generate_svg() first")
        return
    
    # Output path for video
    output_path = os.path.join(config.get("output_dir", "outputs"), "example_flowchart_video.mp4")
    
    # Set options
    options = {
        "render_quality": "medium",
        "animation_type": "flowchart"
    }
    
    print(f"Converting SVG to video: {svg_path}")
    print(f"Using options: {options}")
    
    # Convert existing SVG to video
    result = await pipeline.convert_existing_svg(svg_path, output_path, options)
    
    if result["status"] == "success":
        print(f"Video generated successfully: {result['output_path']}")
    else:
        print(f"Error generating video: {result.get('error', 'Unknown error')}")

# Run all examples
async def run_all_examples():
    """Run all examples."""
    # First, check Blender installation
    is_available, version_info = check_blender_installation()
    
    if not is_available:
        print(f"Warning: Blender is not available or accessible: {version_info}")
        print("The examples that require Blender will fail.")
    else:
        print(f"Blender is available: {version_info}")
    
    try:
        # Example 1: Generate SVG
        await example_generate_svg()
        
        # Example 2: Convert SVG to 3D
        await example_svg_to_3d()
        
        # Example 3: Full pipeline
        await example_full_pipeline()
        
        # Example 4: Convert existing SVG
        await example_convert_existing_svg()
        
    except Exception as e:
        print(f"Error running examples: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_examples())
