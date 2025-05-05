# SVG Generator Implementation

## Overview

The SVG Generator component has been enhanced with multiple LLM integration options to generate SVG diagrams from text descriptions. This implementation allows for flexible LLM selection and can be used independently from the rest of the SVG to Video pipeline.

## Architecture

### Key Components

1. **LLM Integrations**
   - Direct Claude API integration
   - LangChain-based integrations (Claude, OpenAI, Ollama)
   - Redis-based LLM service integration

2. **SVG Generator**
   - Main SVG generation class
   - Handles diagram types and templating
   - Processes LLM responses to extract valid SVG

3. **LLM Factory**
   - Factory pattern for managing different LLM integrations
   - Provides a unified interface for all integrations
   - Handles initialization and provider selection

## Installation

The SVG Generator requires the following dependencies:

- For Claude direct integration:
  - `anthropic` Python package
  - `requests`
  
- For LangChain integration (optional):
  - `langchain`
  - `openai` (for OpenAI integration)
  
- For Redis integration (optional):
  - Redis server
  - `aioredis`

## Usage

### Standalone Testing

Use the standalone test script to test SVG generation without dependencies on Blender:

```bash
python test_svg_only.py --provider claude-direct --diagram-type flowchart \
  --description "Your diagram description" --output-dir output/svg
```

Or use the provided batch file:

```bash
test_claude_svg_only.bat
```

### Programmatic Usage

```python
import asyncio
from genai_agent.svg_to_video.llm_integrations.llm_factory import get_llm_factory

async def generate_svg():
    # Get the LLM factory
    llm_factory = get_llm_factory()
    await llm_factory.initialize()
    
    # Generate SVG
    svg_content = await llm_factory.generate_svg(
        provider="claude-direct",
        concept="A flowchart showing user authentication process",
        style="flowchart",
        temperature=0.4
    )
    
    # Save SVG to file
    with open("output.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print("SVG generated and saved to output.svg")

# Run the example
asyncio.run(generate_svg())
```

### Integration with Full Pipeline

When the necessary dependencies (including Blender's `mathutils`) are available, you can use the full SVG to Video pipeline:

```python
import asyncio
from genai_agent.svg_to_video import SVGToVideoPipeline

async def generate_video():
    # Create and initialize the pipeline
    pipeline = SVGToVideoPipeline(debug=True)
    await pipeline.initialize()
    
    # Generate video from description
    result = await pipeline.generate_video_from_description(
        description="A flowchart showing user authentication process",
        provider="claude-direct",
        diagram_type="flowchart"
    )
    
    print("Generated files:")
    for file_type, file_path in result.items():
        print(f"  {file_type}: {file_path}")

# Run the example (requires Blender dependencies)
asyncio.run(generate_video())
```

## Known Issues and Workarounds

1. **Blender Dependencies**
   - The SVG to 3D converter requires Blender's `mathutils` module
   - Use the standalone SVG generator test without importing the full pipeline to avoid this dependency

2. **LangChain Availability**
   - If LangChain is not installed, only the direct Claude integration will be available
   - The system will log appropriate warnings

3. **Redis LLM Service**
   - This integration requires the main project's Redis setup
   - If not available, use the direct Claude integration instead

## Next Steps

1. **Additional LLM Integrations**
   - Add support for more LLM providers
   - Enhance prompt engineering for better SVG quality

2. **Improved Error Handling**
   - Better handling of API rate limits and timeouts
   - Fallback mechanisms for unavailable providers

3. **Performance Optimizations**
   - Caching for repeated requests
   - Parallel processing for multiple diagrams
