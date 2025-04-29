"""
SVG to Video CLI

This script provides a command-line interface for the SVG to Video pipeline.
"""

import os
import sys
import argparse
import json

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from genai_agent.svg_to_video.llm_integrations.llm_factory import LLMFactory
from genai_agent.svg_to_video.pipeline import SVGToVideoPipeline
from genai_agent.svg_to_video.utils import ensure_directory_exists

def list_providers():
    """List all available LLM providers."""
    factory = LLMFactory()
    providers = factory.get_providers()
    
    print("Available LLM Providers:")
    print("-----------------------")
    
    for provider in providers:
        status = "✅ Available" if provider.get("available", False) else "❌ Not Available"
        print(f"{provider['name']} ({provider['id']}): {status}")
        
        if provider.get("available", False) and "models" in provider:
            print("  Models:")
            for model in provider["models"]:
                print(f"  - {model['name']} ({model['id']}): {model['description']}")
        
        if not provider.get("available", False) and "error" in provider:
            print(f"  Error: {provider['error']}")
        
        print()

def generate_svg(args):
    """Generate an SVG from a concept using the specified provider."""
    factory = LLMFactory()
    
    try:
        print(f"Generating SVG for concept: '{args.concept}'")
        print(f"Using provider: {args.provider}")
        if args.model:
            print(f"Using model: {args.model}")
        
        svg_content = factory.generate_svg(args.provider, args.concept, args.model, args.style)
        
        # Create output directory if needed
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save SVG
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"SVG saved to: {args.output}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def convert_svg(args):
    """Convert an SVG file to a video."""
    pipeline = SVGToVideoPipeline()
    
    try:
        print(f"Converting SVG: {args.input}")
        print(f"Output video: {args.output}")
        print(f"Animation type: {args.animation_type}")
        print(f"Quality: {args.quality}")
        
        # Create output directory if needed
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Convert SVG to video
        pipeline.convert_svg_to_video(args.input, args.output, args.animation_type, args.quality)
        
        print(f"Video saved to: {args.output}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def generate_video(args):
    """Generate a video from a concept using the specified provider."""
    factory = LLMFactory()
    pipeline = SVGToVideoPipeline()
    
    try:
        print(f"Generating video for concept: '{args.concept}'")
        print(f"Using provider: {args.provider}")
        if args.model:
            print(f"Using model: {args.model}")
        print(f"Animation type: {args.animation_type}")
        print(f"Quality: {args.quality}")
        
        # Create a temporary SVG file
        temp_dir = os.path.join(parent_dir, "outputs", "temp")
        ensure_directory_exists(temp_dir)
        temp_svg = os.path.join(temp_dir, "temp_" + os.path.basename(args.output).replace(".mp4", ".svg"))
        
        # Generate SVG
        print("Step 1: Generating SVG diagram...")
        svg_content = factory.generate_svg(args.provider, args.concept, args.model, args.style)
        
        # Save SVG
        with open(temp_svg, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"SVG saved to temporary file: {temp_svg}")
        
        # Create output directory if needed
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Convert SVG to video
        print("Step 2: Converting SVG to video...")
        pipeline.convert_svg_to_video(temp_svg, args.output, args.animation_type, args.quality)
        
        print(f"Video saved to: {args.output}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="SVG to Video CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List providers command
    list_parser = subparsers.add_parser("list-providers", help="List available LLM providers")
    
    # Generate SVG command
    svg_parser = subparsers.add_parser("svg", help="Generate an SVG from a concept")
    svg_parser.add_argument("concept", help="The concept to visualize as an SVG")
    svg_parser.add_argument("output", help="Path to save the generated SVG file")
    svg_parser.add_argument("--provider", default="claude", help="The LLM provider to use")
    svg_parser.add_argument("--model", help="The specific model to use")
    svg_parser.add_argument("--style", help="Optional style guidelines for the SVG")
    
    # Convert SVG command
    convert_parser = subparsers.add_parser("convert", help="Convert an SVG file to a video")
    convert_parser.add_argument("input", help="Path to the input SVG file")
    convert_parser.add_argument("output", help="Path to save the output video file")
    convert_parser.add_argument("--animation-type", default="standard", choices=["standard", "flowchart", "network"], help="Type of animation to apply")
    convert_parser.add_argument("--quality", default="medium", choices=["low", "medium", "high"], help="Rendering quality")
    
    # Generate video command
    generate_parser = subparsers.add_parser("generate", help="Generate a video from a concept")
    generate_parser.add_argument("concept", help="The concept to visualize as a video")
    generate_parser.add_argument("output", help="Path to save the generated video file")
    generate_parser.add_argument("--provider", default="claude", help="The LLM provider to use for SVG generation")
    generate_parser.add_argument("--model", help="The specific model to use for SVG generation")
    generate_parser.add_argument("--style", help="Optional style guidelines for the SVG")
    generate_parser.add_argument("--animation-type", default="standard", choices=["standard", "flowchart", "network"], help="Type of animation to apply")
    generate_parser.add_argument("--quality", default="medium", choices=["low", "medium", "high"], help="Rendering quality")
    
    args = parser.parse_args()
    
    if args.command == "list-providers":
        return list_providers()
    elif args.command == "svg":
        return generate_svg(args)
    elif args.command == "convert":
        return convert_svg(args)
    elif args.command == "generate":
        return generate_video(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
