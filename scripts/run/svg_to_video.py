"""
SVG to Video Pipeline Runner

This script provides a command-line interface for the SVG to Video pipeline.
It supports generating SVGs, converting SVGs to 3D models, and creating videos.
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, "output", "logs", "svg_to_video.log"))
    ]
)

logger = logging.getLogger("svg_to_video")

# Import the pipeline
from genai_agent.svg_to_video.pipeline_integrated import SVGToVideoPipeline

async def generate_svg(description, output_path, provider=None, diagram_type=None):
    """Generate an SVG from a description."""
    try:
        logger.info(f"Generating SVG from description: {description[:50]}...")
        
        # Create the pipeline
        pipeline = SVGToVideoPipeline(debug=True)
        
        # Generate the SVG
        svg_content, svg_path = await pipeline.generate_svg_only(
            description=description,
            provider=provider,
            diagram_type=diagram_type
        )
        
        # If output path is provided, copy the SVG to that location
        if output_path:
            import shutil
            shutil.copy(svg_path, output_path)
            logger.info(f"SVG copied to: {output_path}")
        
        logger.info(f"SVG generated successfully: {svg_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error generating SVG: {str(e)}")
        return False

async def convert_svg(svg_path, output_path, animation_type=None, render_quality="medium", duration=10):
    """Convert an SVG to a video."""
    try:
        logger.info(f"Converting SVG to video: {svg_path}")
        
        # Create the pipeline
        pipeline = SVGToVideoPipeline(debug=True)
        
        # Convert the SVG to video
        output_files = await pipeline.convert_svg_to_video(
            svg_path=svg_path,
            animation_type=animation_type,
            render_quality=render_quality,
            duration=duration
        )
        
        # If output path is provided, copy the video to that location
        if output_path and "video" in output_files:
            import shutil
            shutil.copy(output_files["video"], output_path)
            logger.info(f"Video copied to: {output_path}")
        
        logger.info(f"SVG converted successfully:")
        logger.info(f"  Model: {output_files.get('model', 'N/A')}")
        logger.info(f"  Animation: {output_files.get('animation', 'N/A')}")
        logger.info(f"  Video: {output_files.get('video', 'N/A')}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error converting SVG to video: {str(e)}")
        return False

async def generate_video(description, output_path, provider=None, diagram_type=None, 
                         animation_type=None, render_quality="medium", duration=10):
    """Generate a video from a description."""
    try:
        logger.info(f"Generating video from description: {description[:50]}...")
        
        # Create the pipeline
        pipeline = SVGToVideoPipeline(debug=True)
        
        # Generate the video
        output_files = await pipeline.generate_video_from_description(
            description=description,
            provider=provider,
            diagram_type=diagram_type,
            animation_type=animation_type,
            render_quality=render_quality,
            duration=duration
        )
        
        # If output path is provided, copy the video to that location
        if output_path and "video" in output_files:
            import shutil
            shutil.copy(output_files["video"], output_path)
            logger.info(f"Video copied to: {output_path}")
        
        logger.info(f"Video generated successfully:")
        logger.info(f"  SVG: {output_files.get('svg', 'N/A')}")
        logger.info(f"  Model: {output_files.get('model', 'N/A')}")
        logger.info(f"  Animation: {output_files.get('animation', 'N/A')}")
        logger.info(f"  Video: {output_files.get('video', 'N/A')}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        return False

async def list_providers():
    """List available LLM providers."""
    try:
        # Create the pipeline
        pipeline = SVGToVideoPipeline(debug=True)
        
        # Get available providers
        providers = pipeline.svg_generator.get_available_providers()
        
        logger.info("Available LLM providers:")
        for provider in providers:
            logger.info(f"  - {provider}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error listing providers: {str(e)}")
        return False

def main():
    """Main entry point."""
    # Create parser
    parser = argparse.ArgumentParser(description="SVG to Video Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # SVG generation command
    svg_parser = subparsers.add_parser("svg", help="Generate an SVG from a description")
    svg_parser.add_argument("description", help="Text description of the diagram")
    svg_parser.add_argument("output", help="Output file path")
    svg_parser.add_argument("--provider", help="LLM provider to use")
    svg_parser.add_argument("--type", dest="diagram_type", help="Type of diagram to generate")
    
    # Video conversion command
    convert_parser = subparsers.add_parser("convert", help="Convert an SVG to a video")
    convert_parser.add_argument("input", help="Input SVG file path")
    convert_parser.add_argument("output", help="Output video file path")
    convert_parser.add_argument("--animation", dest="animation_type", help="Type of animation to apply")
    convert_parser.add_argument("--quality", dest="render_quality", default="medium", 
                                choices=["low", "medium", "high"], help="Rendering quality")
    convert_parser.add_argument("--duration", type=int, default=10, help="Animation duration in seconds")
    
    # Video generation command
    generate_parser = subparsers.add_parser("generate", help="Generate a video from a description")
    generate_parser.add_argument("description", help="Text description of the diagram")
    generate_parser.add_argument("output", help="Output video file path")
    generate_parser.add_argument("--provider", help="LLM provider to use")
    generate_parser.add_argument("--diagram-type", help="Type of diagram to generate")
    generate_parser.add_argument("--animation-type", help="Type of animation to apply")
    generate_parser.add_argument("--quality", dest="render_quality", default="medium", 
                                 choices=["low", "medium", "high"], help="Rendering quality")
    generate_parser.add_argument("--duration", type=int, default=10, help="Animation duration in seconds")
    
    # List providers command
    list_parser = subparsers.add_parser("list-providers", help="List available LLM providers")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create output directories if they don't exist
    os.makedirs(os.path.join(project_root, "output", "logs"), exist_ok=True)
    
    # Run the appropriate command
    if args.command == "svg":
        result = asyncio.run(generate_svg(
            description=args.description,
            output_path=args.output,
            provider=args.provider,
            diagram_type=args.diagram_type
        ))
    elif args.command == "convert":
        result = asyncio.run(convert_svg(
            svg_path=args.input,
            output_path=args.output,
            animation_type=args.animation_type,
            render_quality=args.render_quality,
            duration=args.duration
        ))
    elif args.command == "generate":
        result = asyncio.run(generate_video(
            description=args.description,
            output_path=args.output,
            provider=args.provider,
            diagram_type=args.diagram_type,
            animation_type=args.animation_type,
            render_quality=args.render_quality,
            duration=args.duration
        ))
    elif args.command == "list-providers":
        result = asyncio.run(list_providers())
    else:
        parser.print_help()
        return 1
    
    # Return appropriate exit code
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
