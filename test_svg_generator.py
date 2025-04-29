"""
Test script for the SVG Generator component.

This script tests the SVG Generator component in isolation to verify it works properly.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the main project .env file
env_path = Path(__file__).parent / "genai_agent_project" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from {env_path}")
else:
    # Fall back to local .env file if it exists
    local_env = Path(__file__).parent / ".env"
    if local_env.exists():
        load_dotenv(dotenv_path=local_env)
        print(f"Loaded environment variables from {local_env}")
    else:
        print("No .env file found! API keys may not be available.")

# Add the project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Import the SVG Generator
from genai_agent.svg_to_video.svg_generator import SVGGenerator

async def test_svg_generator():
    """Test the SVG Generator component."""
    print("Testing SVG Generator...")
    
    # Create an instance of the SVG Generator
    generator = SVGGenerator()
    
    # Check available providers
    providers = generator.get_available_providers()
    print(f"Available providers: {providers}")
    
    if not providers:
        print("No LLM providers available. Please check your API keys.")
        print("Current environment variables:")
        print(f"ANTHROPIC_API_KEY: {'Set' if os.environ.get('ANTHROPIC_API_KEY') else 'Not set'}")
        print(f"OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set'}")
        return
    
    # Get the first available provider
    provider = providers[0]
    print(f"Using provider: {provider}")
    
    # Test generating an SVG
    concept = "A simple flowchart with two boxes connected by an arrow"
    print(f"Generating SVG for concept: {concept}")
    
    try:
        svg_content = await generator.generate_svg(concept, provider=provider)
        
        # Save the SVG to a file
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_svg.svg"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"SVG generated successfully and saved to {output_path}")
        print(f"SVG content (preview):\n{svg_content[:500]}...")
        
    except Exception as e:
        print(f"Error generating SVG: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_svg_generator())
