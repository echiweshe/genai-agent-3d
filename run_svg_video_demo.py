"""
SVG to Video Pipeline Demo

This script demonstrates the integrated SVG to Video pipeline
with the modularized structure.
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("svg_video_demo")

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Demonstrate the SVG to Video pipeline")
    parser.add_argument("--description", "-d", type=str,
                        default="A flowchart showing the login process for a web application",
                        help="Description for the SVG diagram")
    parser.add_argument("--output", "-o", type=str,
                        default="output/videos/demo.mp4",
                        help="Path to output video file")
    parser.add_argument("--diagram-type", "-t", type=str,
                        default="flowchart",
                        choices=["flowchart", "network", "sequence"],
                        help="Type of diagram to generate")
    parser.add_argument("--quality", "-q", type=str,
                        default="low",
                        choices=["low", "medium", "high"],
                        help="Rendering quality (low for faster rendering)")
    parser.add_argument("--duration", type=int,
                        default=5,
                        help="Animation duration in seconds")
    
    args = parser.parse_args()
    
    try:
        # Import the pipeline (inside the function to allow for fixing imports first)
        from genai_agent.svg_to_video import SVGToVideoPipeline
        
        # Create pipeline instance
        logger.info("Initializing SVG to Video pipeline...")
        pipeline = SVGToVideoPipeline(debug=True)
        
        # Generate video
        logger.info(f"Generating video from description: {args.description}")
        logger.info(f"Diagram type: {args.diagram_type}")
        logger.info(f"Rendering quality: {args.quality}")
        logger.info(f"Animation duration: {args.duration} seconds")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
        output_files = await pipeline.generate_video_from_description(
            description=args.description,
            diagram_type=args.diagram_type,
            render_quality=args.quality,
            duration=args.duration
        )
        
        # Log the output files
        logger.info("Pipeline completed successfully!")
        logger.info("Generated files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  {file_type}: {file_path}")
        
        # Copy video to requested output path if different
        if output_files["video"] != args.output:
            import shutil
            shutil.copy(output_files["video"], args.output)
            logger.info(f"Video copied to: {args.output}")
        
        return 0
    
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        logger.error("Please run the fix_and_test_svg_to_video.ps1 script first")
        return 1
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
