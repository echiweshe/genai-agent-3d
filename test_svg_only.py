"""
Standalone test script for SVG generation only.

This script tests only the SVG Generator component without any dependencies
on Blender or other 3D components.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import argparse

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to Python path")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_svg_only")

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
        # Create the SVG output directory
        output_dir = output_dir or "output/svg"
        os.makedirs(output_dir, exist_ok=True)
        
        # Import only the necessary modules directly
        from genai_agent.svg_to_video.llm_integrations.llm_factory import get_llm_factory
        from genai_agent.svg_to_video.llm_integrations.claude_direct import get_claude_direct
        
        # Get the LLM factory
        llm_factory = get_llm_factory()
        await llm_factory.initialize()
        
        # Log available providers
        providers = llm_factory.get_providers()
        provider_ids = [p["id"] for p in providers]
        logger.info(f"Available providers: {provider_ids}")
        
        # Check if the specified provider is available
        if provider and provider not in provider_ids:
            logger.warning(f"Provider {provider} is not available. Available providers: {provider_ids}")
            if provider_ids:
                provider = provider_ids[0]
                logger.info(f"Using provider {provider} instead")
            else:
                logger.error("No providers available!")
                return None
        
        # Generate SVG
        logger.info(f"Generating SVG with provider {provider}, diagram type {diagram_type}...")
        logger.info(f"Description: {description}")
        
        svg_content = await llm_factory.generate_svg(
            provider=provider,
            concept=description,
            style=diagram_type,
            temperature=0.4
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
    parser.add_argument("--provider", "-p", type=str, default="claude-direct",
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
