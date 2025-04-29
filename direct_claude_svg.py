"""
Direct Claude SVG Generator

This script uses the Anthropic API directly to generate SVG diagrams,
bypassing LangChain to avoid compatibility issues.
"""

import os
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the master .env file
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

# Check if API key is available
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    exit(1)

# Import Anthropic client
try:
    from anthropic import Anthropic
except ImportError:
    print("Anthropic package not installed. Please run: pip install anthropic")
    exit(1)

def generate_svg(concept):
    """
    Generate an SVG diagram using Claude directly.
    
    Args:
        concept: Text description of the diagram to generate
        
    Returns:
        SVG content as a string
    """
    prompt = f"""
    Create an SVG diagram that represents the following concept:
    
    {concept}
    
    Requirements:
    - Use standard SVG elements (rect, circle, path, text, etc.)
    - Include appropriate colors and styling
    - Ensure the diagram is clear and readable
    - Add proper text labels
    - Use viewBox="0 0 800 600" for dimensions
    - Wrap the entire SVG in <svg> tags
    - Do not include any explanation, just the SVG code
    
    SVG Diagram:
    """
    
    # Initialize the client
    client = Anthropic(api_key=api_key)
    
    # Generate response
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract SVG content
    response_text = message.content[0].text
    
    # Extract SVG tags
    if "<svg" in response_text and "</svg>" in response_text:
        svg_match = re.search(r'(<svg.*?</svg>)', response_text, re.DOTALL)
        if svg_match:
            return svg_match.group(1)
        return response_text
    else:
        print("Warning: Generated content does not contain valid SVG tags")
        return response_text

def save_svg(svg_content, output_path):
    """
    Save SVG content to a file.
    
    Args:
        svg_content: SVG content to save
        output_path: Path to save the SVG file
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"SVG saved to {output_path}")

if __name__ == "__main__":
    # Create outputs directory if it doesn't exist
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Get concept from user
    print("Direct Claude SVG Generator")
    print("==========================")
    print("This script generates SVG diagrams using Claude API directly.")
    print()
    
    concept = input("Enter concept description: ")
    if not concept.strip():
        concept = "A flowchart with two boxes connected by an arrow"
        print(f"Using default concept: {concept}")
    
    print("\nGenerating SVG diagram...")
    svg_content = generate_svg(concept)
    
    # Save the SVG
    output_path = output_dir / "direct_claude_svg.svg"
    save_svg(svg_content, output_path)
    
    print("\nSVG content preview:")
    print("--------------------")
    preview_length = min(500, len(svg_content))
    print(f"{svg_content[:preview_length]}...")
    
    print("\nDone! You can find the SVG file at:", output_path)
