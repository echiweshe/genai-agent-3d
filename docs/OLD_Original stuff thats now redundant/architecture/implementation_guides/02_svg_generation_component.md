# SVG Generation Component

## Overview

This document details the implementation of the SVG Generation component, which uses LangChain to prompt various LLM providers to create SVG diagrams based on text descriptions.

## Implementation Details

### Core SVG Generator Class

```python
# langchain_svg_generator.py
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

class SVGGenerator:
    """Generate SVG diagrams using LangChain and various LLM providers."""
    
    def __init__(self):
        # Initialize LLM providers
        self.providers = {
            "openai": ChatOpenAI(temperature=0.7),
            "claude": ChatAnthropic(),
            "ollama": ChatOllama(model="llama3")
        }
        
        # Base prompts for SVG generation
        self.svg_prompt_template = """
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
    
    async def generate_svg(self, concept, provider="claude", max_retries=2):
        """Generate an SVG diagram based on a concept description."""
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        llm = self.providers[provider]
        prompt = self.svg_prompt_template.format(concept=concept)
        
        # Try to generate with retries
        for attempt in range(max_retries + 1):
            try:
                messages = [HumanMessage(content=prompt)]
                response = await llm.agenerate([messages])
                
                # Extract SVG content
                svg_text = response.generations[0][0].text
                
                # Validate it's proper SVG
                if "<svg" in svg_text and "</svg>" in svg_text:
                    # Extract just the SVG tags
                    import re
                    svg_match = re.search(r'(<svg.*?</svg>)', svg_text, re.DOTALL)
                    if svg_match:
                        return svg_match.group(1)
                    return svg_text
                else:
                    if attempt < max_retries:
                        continue
                    raise ValueError("Generated content is not valid SVG")
                
            except Exception as e:
                if attempt < max_retries:
                    continue
                raise
        
        raise RuntimeError("Failed to generate valid SVG after multiple attempts")
```

### Usage Example

```python
# Example usage of the SVG Generator
import asyncio
import os

async def generate_diagram(concept, provider="claude", output_file=None):
    """Generate an SVG diagram and optionally save to file."""
    generator = SVGGenerator()
    
    try:
        svg_content = await generator.generate_svg(concept, provider=provider)
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"SVG saved to {output_file}")
        
        return svg_content
    
    except Exception as e:
        print(f"Error generating SVG: {str(e)}")
        return None

# Example execution
if __name__ == "__main__":
    concept = "A microservices architecture with an API Gateway, three services, and a database"
    output_file = "microservices_diagram.svg"
    
    svg_content = asyncio.run(generate_diagram(concept, output_file=output_file))
```

## Implementation Notes

### Key Features

1. **Multiple LLM Provider Support**:
   - OpenAI (GPT models)
   - Anthropic (Claude models)
   - Ollama (local models like Llama)

2. **Robustness**:
   - Retry mechanism for failed attempts
   - SVG validation to ensure proper output
   - Error handling for different failure modes

3. **Customization**:
   - Configurable prompts for different diagram types
   - Temperature and other generation parameters can be adjusted

### Prompt Engineering

The prompt is designed to guide the LLM to produce valid SVG code with proper elements and structure. Key aspects of the prompt include:

- Clear instructions for SVG element usage
- Specification of viewBox dimensions
- Requirements for labels and styling
- Direction to only output SVG code (no explanations)

### Potential Enhancements

1. **Specialized Diagram Types**:
   - Add prompt templates for specific diagram types (flowcharts, architecture diagrams, etc.)
   - Implement style guidance for consistent look and feel

2. **SVG Post-Processing**:
   - Add methods to clean up and optimize generated SVG
   - Implement size/dimension normalization

3. **Provider-Specific Parameters**:
   - Fine-tune prompts for different LLM providers
   - Adjust generation parameters for optimal results

## Dependencies

- LangChain (`pip install langchain`)
- Provider-specific packages:
  - `pip install openai` for OpenAI support
  - `pip install anthropic` for Claude support
  - Ollama server for local models

## Testing

### Unit Test Example

```python
# test_svg_generator.py
import unittest
import asyncio
from langchain_svg_generator import SVGGenerator

class TestSVGGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = SVGGenerator()
        
    def test_generate_svg(self):
        concept = "A simple flowchart with two boxes connected by an arrow"
        
        # Run the async function in the test
        svg_content = asyncio.run(self.generator.generate_svg(concept))
        
        # Check that the output is valid SVG
        self.assertIn("<svg", svg_content)
        self.assertIn("</svg>", svg_content)
        self.assertIn("viewBox", svg_content)
        
    def test_invalid_provider(self):
        concept = "A diagram"
        
        with self.assertRaises(ValueError):
            asyncio.run(self.generator.generate_svg(concept, provider="invalid_provider"))

if __name__ == "__main__":
    unittest.main()
```

## Next Steps

1. Implement the base SVG generator class
2. Create unit tests to validate functionality
3. Experiment with different prompts for optimal SVG generation
4. Add support for custom diagram types and styles
5. Integrate with the next step in the pipeline (SVG to 3D Conversion)