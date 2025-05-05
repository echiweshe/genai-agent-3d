"""
Test script for the SVG generator.
This script tests the SVG generator with Claude and OpenAI LLMs.
"""

import os
import sys
import time
from pathlib import Path

# Add project directory to path
project_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project")
sys.path.insert(0, str(project_dir))

# Import SVG generator
try:
    from genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator import generate_svg
    print("Successfully imported SVG generator")
except ImportError as e:
    print(f"Error importing SVG generator: {e}")
    sys.exit(1)

# Define output directory
output_dir = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg")
os.makedirs(output_dir, exist_ok=True)

# Test with Claude
def test_with_claude():
    print("\nTesting SVG generator with Claude...")
    output_file = output_dir / f"claude_test_flowchart_{int(time.time())}.svg"
    
    try:
        result = generate_svg(
            prompt="Create a flowchart showing the process of making coffee",
            diagram_type="flowchart",
            output_file=str(output_file),
            provider="claude"  # Use Claude provider
        )
        
        if result and os.path.isfile(output_file):
            print(f"Success! SVG generated at: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return True
        else:
            print("Failed to generate SVG with Claude")
            return False
    except Exception as e:
        print(f"Error generating SVG with Claude: {e}")
        return False

# Test with OpenAI
def test_with_openai():
    print("\nTesting SVG generator with OpenAI...")
    output_file = output_dir / f"openai_test_flowchart_{int(time.time())}.svg"
    
    try:
        result = generate_svg(
            prompt="Create a flowchart showing the process of making coffee",
            diagram_type="flowchart",
            output_file=str(output_file),
            provider="openai"  # Use OpenAI provider
        )
        
        if result and os.path.isfile(output_file):
            print(f"Success! SVG generated at: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return True
        else:
            print("Failed to generate SVG with OpenAI")
            return False
    except Exception as e:
        print(f"Error generating SVG with OpenAI: {e}")
        return False

# Test with mock provider as fallback
def test_with_mock():
    print("\nTesting SVG generator with mock provider...")
    output_file = output_dir / f"mock_test_flowchart_{int(time.time())}.svg"
    
    try:
        result = generate_svg(
            prompt="Create a flowchart showing the process of making coffee",
            diagram_type="flowchart",
            output_file=str(output_file),
            provider="mock"  # Use mock provider
        )
        
        if result and os.path.isfile(output_file):
            print(f"Success! SVG generated at: {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
            return True
        else:
            print("Failed to generate SVG with mock provider")
            return False
    except Exception as e:
        print(f"Error generating SVG with mock provider: {e}")
        return False

if __name__ == "__main__":
    print("SVG Generator Test")
    print("=================")
    
    # Run tests
    claude_success = test_with_claude()
    openai_success = test_with_openai()
    mock_success = test_with_mock()
    
    # Print summary
    print("\nTest Summary:")
    print(f"Claude: {'SUCCESS' if claude_success else 'FAILED'}")
    print(f"OpenAI: {'SUCCESS' if openai_success else 'FAILED'}")
    print(f"Mock: {'SUCCESS' if mock_success else 'FAILED'}")
    
    # Overall result
    if claude_success or openai_success:
        print("\nSVG generator is working with at least one LLM provider!")
        sys.exit(0)
    elif mock_success:
        print("\nSVG generator is working with mock provider only.")
        print("Check your LLM provider configurations.")
        sys.exit(1)
    else:
        print("\nSVG generator is not working with any provider.")
        print("Please check the logs for errors.")
        sys.exit(1)
