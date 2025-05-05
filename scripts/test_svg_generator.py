"""
Test script for the SVG Generator with real LLM integration.

This script tests the SVG Generator component with actual LLM integrations
like Claude, OpenAI, or Redis-based LLM services.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import argparse

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to Python path")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_svg_generator")

async def test_svg_generator(description, provider=None, diagram_type=None, output_dir=None):
    """
    Test the SVG Generator with the given parameters.
    
    Args:
        description: Text description for the SVG
        provider: LLM provider to use
        diagram_type: Type of diagram
        output_dir: Directory to save the output
    """
    try:
        # Import the SVG Generator
        from genai_agent.svg_to_video.svg_generator import SVGGenerator
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            os.environ["SVG_OUTPUT_DIR"] = output_dir
        
        # Create SVG Generator instance
        logger.info("Creating SVG Generator instance...")
        svg_generator = SVGGenerator(debug=True)
        
        # Initialize the generator
        logger.info("Initializing SVG Generator...")
        await svg_generator.initialize()
        
        # Log available providers
        providers = svg_generator.get_available_providers()
        logger.info(f"Available providers: {providers}")
        
        # Check if the specified provider is available
        if provider and provider not in providers:
            logger.warning(f"Provider {provider} is not available. Available providers: {providers}")
            if providers:
                provider = providers[0]
                logger.info(f"Using provider {provider} instead")
            else:
                logger.error("No providers available!")
                return
        
        # Generate SVG
        logger.info(f"Generating SVG with provider {provider}, diagram type {diagram_type}...")
        logger.info(f"Description: {description}")
        
        svg_content = await svg_generator.generate_svg(
            concept=description,
            provider=provider,
            diagram_type=diagram_type
        )
        
        # Save SVG
        if output_dir:
            # Generate filename based on provider and diagram type
            filename_parts = []
            if provider:
                filename_parts.append(provider.replace("-", "_"))
            if diagram_type:
                filename_parts.append(diagram_type)
            filename_parts.append("test")
            
            filename = "_".join(filename_parts) + ".svg"
            output_path = os.path.join(output_dir, filename)
            
            # Save SVG to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            logger.info(f"SVG saved to {output_path}")
        
        # Print sample of the SVG content
        svg_preview = svg_content[:500] + "..." if len(svg_content) > 500 else svg_content
        logger.info(f"SVG content preview:\n{svg_preview}")
        
        return svg_content
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the SVG Generator component.")
    parser.add_argument("--description", "-d", type=str, required=True,
                       help="Text description for the SVG")
    parser.add_argument("--provider", "-p", type=str, default=None,
                       help="LLM provider to use")
    parser.add_argument("--diagram-type", "-t", type=str, default=None,
                       help="Type of diagram (flowchart, network, etc.)")
    parser.add_argument("--output-dir", "-o", type=str, default="output/svg",
                       help="Directory to save the output")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Run the test
    result = asyncio.run(test_svg_generator(
        description=args.description,
        provider=args.provider,
        diagram_type=args.diagram_type,
        output_dir=args.output_dir
    ))
    
    # Exit with appropriate status
    sys.exit(0 if result else 1)
