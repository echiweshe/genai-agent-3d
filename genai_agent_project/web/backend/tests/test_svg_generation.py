"""
Test script for SVG generation with Claude Direct
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import environment checker
from env_checker import setup_env_variables

# Test SVG generation with Claude Direct
async def test_svg_generation():
    """Test SVG generation with Claude Direct"""
    try:
        # Setup environment variables
        setup_env_variables()
        
        # Check ANTHROPIC_API_KEY
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            logger.error("ANTHROPIC_API_KEY not set")
            return False
        
        logger.info(f"Using ANTHROPIC_API_KEY: {anthropic_api_key[:8]}...")
        
        # Import LLM factory and Claude Direct
        sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))
        
        # Import SVG Generator
        from genai_agent.svg_to_video.llm_integrations.llm_factory import get_llm_factory
        from genai_agent.svg_to_video.llm_integrations.claude_direct import get_claude_direct
        
        # Get LLM factory
        llm_factory = get_llm_factory()
        await llm_factory.initialize()
        
        # Get Claude Direct
        claude_direct = get_claude_direct()
        if not claude_direct:
            logger.error("Claude Direct not available")
            return False
        
        # Set model to Claude 3 Opus
        claude_direct.set_model("claude-3-opus-20240229")
        
        # Test SVG generation
        logger.info("Testing SVG generation with Claude Direct...")
        svg_content = await claude_direct.generate_svg_async(
            concept="A simple flowchart showing the steps to make coffee",
            style="flowchart",
            temperature=0.4
        )
        
        # Check SVG content
        if not svg_content:
            logger.error("SVG content is empty")
            return False
        
        if not svg_content.startswith("<svg"):
            logger.error(f"Invalid SVG content: {svg_content[:100]}...")
            return False
        
        logger.info(f"SVG content generated successfully (first 100 chars): {svg_content[:100]}...")
        
        # Save SVG to file
        output_dir = Path(__file__).parent.parent.parent.parent / "output" / "svg"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        output_file = output_dir / "test_coffee_flowchart.svg"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        logger.info(f"SVG saved to: {output_file}")
        
        # Test SVG generation with LLM factory
        logger.info("Testing SVG generation with LLM factory...")
        svg_content = await llm_factory.generate_svg(
            provider="claude-direct",
            concept="A simple network diagram showing a home network setup",
            style="network",
            temperature=0.4
        )
        
        # Check SVG content
        if not svg_content:
            logger.error("SVG content is empty")
            return False
        
        if not svg_content.startswith("<svg"):
            logger.error(f"Invalid SVG content: {svg_content[:100]}...")
            return False
        
        logger.info(f"SVG content generated successfully (first 100 chars): {svg_content[:100]}...")
        
        # Save SVG to file
        output_file = output_dir / "test_network_diagram.svg"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        logger.info(f"SVG saved to: {output_file}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing SVG generation: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_svg_generation())
    
    if result:
        logger.info("SVG generation test passed")
        sys.exit(0)
    else:
        logger.error("SVG generation test failed")
        sys.exit(1)
