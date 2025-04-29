#!/usr/bin/env python
"""
SVG to Video Pipeline CLI

This script provides a command-line interface to the SVG to Video pipeline.
It allows users to generate SVGs, convert them to 3D models, and render videos.
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path

# Add parent directory to sys.path to import genai_agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from genai_agent.svg_to_video.pipeline import SVGToVideoPipeline
from genai_agent.svg_to_video.utils import check_blender_installation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("svg_video_cli")

async def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='SVG to Video Pipeline CLI')
    
    # Add global arguments
    parser.add_argument('--blender-path', help='Path to Blender executable', default='blender')
    parser.add_argument('--script-dir', help='Directory containing Blender scripts', 
                      default=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'genai_agent', 'scripts'))
    parser.add_argument('--output-dir', help='Directory for output files', 
                      default='outputs')
    
    # Add command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Full pipeline command
    pipeline_parser = subparsers.add_parser('generate', help='Generate video from concept')
    pipeline_parser.add_argument('concept', help='Concept description for diagram generation')
    pipeline_parser.add_argument('output', help='Output video file path')
    pipeline_parser.add_argument('--provider', help='LLM provider for SVG generation')
    pipeline_parser.add_argument('--quality', help='Rendering quality (low, medium, high)')
    pipeline_parser.add_argument('--animation-type', help='Animation type (standard, flowchart, network)')
    pipeline_parser.add_argument('--resolution', help='Video resolution (e.g. 1280x720)')
    
    # SVG-only command
    svg_parser = subparsers.add_parser('svg', help='Generate SVG only')
    svg_parser.add_argument('concept', help='Concept description for diagram generation')
    svg_parser.add_argument('output', help='Output SVG file path')
    svg_parser.add_argument('--provider', help='LLM provider for SVG generation')
    
    # Convert existing SVG command
    convert_parser = subparsers.add_parser('convert', help='Convert existing SVG to video')
    convert_parser.add_argument('svg_path', help='Input SVG file path')
    convert_parser.add_argument('output', help='Output video file path')
    convert_parser.add_argument('--quality', help='Rendering quality (low, medium, high)')
    convert_parser.add_argument('--animation-type', help='Animation type (standard, flowchart, network)')
    
    # Check Blender command
    check_parser = subparsers.add_parser('check', help='Check Blender installation')
    check_parser.add_argument('--blender-path', help='Path to Blender executable', default='blender')
    
    # List providers command
    list_parser = subparsers.add_parser('list-providers', help='List available LLM providers')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is specified, show help
    if args.command is None:
        parser.print_help()
        return
    
    # Create configuration
    config = {
        "blender_path": args.blender_path,
        "script_dir": args.script_dir,
        "output_dir": args.output_dir,
        "cleanup_temp": True  # Default to clean up temporary files
    }
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check command
    if args.command == 'check':
        # Check Blender installation
        is_available, version_info = check_blender_installation(args.blender_path)
        if is_available:
            logger.info(f"Blender is available: {version_info}")
        else:
            logger.error(f"Blender is not available: {version_info}")
        return
    
    # Create pipeline
    pipeline = SVGToVideoPipeline(config)
    
    # List providers command
    if args.command == 'list-providers':
        providers = pipeline.get_available_providers()
        if providers:
            logger.info(f"Available LLM providers: {', '.join(providers)}")
        else:
            logger.warning("No LLM providers available. Please check API keys.")
        return
    
    # Generate video from concept
    if args.command == 'generate':
        options = {}
        
        # Add provider if specified
        if args.provider:
            options["provider"] = args.provider
        
        # Add rendering options if specified
        if args.quality:
            options["render_quality"] = args.quality
        
        # Add animation options if specified
        if args.animation_type:
            options["animation_type"] = args.animation_type
        
        # Add resolution if specified
        if args.resolution:
            try:
                width, height = map(int, args.resolution.split('x'))
                options["resolution"] = (width, height)
            except ValueError:
                logger.warning(f"Invalid resolution format: {args.resolution}, using default")
        
        # Process through pipeline
        result = await pipeline.process(args.concept, args.output, options)
        
        if result["status"] == "success":
            logger.info(f"Video generated successfully: {result['output_path']}")
        else:
            logger.error(f"Error generating video: {result.get('error', 'Unknown error')}")
    
    # Generate SVG only
    elif args.command == 'svg':
        provider = args.provider if args.provider else None
        result = await pipeline.generate_svg_only(args.concept, args.output, provider)
        
        if result["status"] == "success":
            logger.info(f"SVG generated successfully: {result.get('output_path', 'No output path specified')}")
        else:
            logger.error(f"Error generating SVG: {result.get('error', 'Unknown error')}")
    
    # Convert existing SVG
    elif args.command == 'convert':
        options = {}
        
        # Add rendering options if specified
        if args.quality:
            options["render_quality"] = args.quality
        
        # Add animation options if specified
        if args.animation_type:
            options["animation_type"] = args.animation_type
        
        result = await pipeline.convert_existing_svg(args.svg_path, args.output, options)
        
        if result["status"] == "success":
            logger.info(f"Video generated successfully: {result['output_path']}")
        else:
            logger.error(f"Error generating video: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())
