# SVG Generator

## Overview

The SVG Generator module is responsible for converting text descriptions into SVG diagrams using LLM providers like Claude, GPT-4, or Ollama. It leverages prompt engineering and specialized templates to generate diagrams for different use cases.

## Architecture

The SVG Generator consists of the following components:

1. **SVGGenerator Class**: Main class that handles generation requests
2. **LLM Integration**: Connection to LLM providers via the project's EnhancedLLMService
3. **Prompt Templates**: Specialized prompts for different diagram types
4. **SVG Validation**: Ensures generated SVG is valid and well-formed

## Usage

```python
from genai_agent.svg_to_video.svg_generator import SVGGenerator

# Create an SVG Generator instance
svg_generator = SVGGenerator()

# Generate an SVG diagram
description = "A flowchart showing the user authentication process"
svg_content = svg_generator.generate(
    description=description,
    provider="claude",  # or "openai" or "ollama"
    diagram_type="flowchart"  # Optional: specify diagram type
)

# Save the SVG to a file
with open("authentication_flowchart.svg", "w") as f:
    f.write(svg_content)
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: API key for Claude (if using via EnhancedLLMService)
- `OPENAI_API_KEY`: API key for OpenAI (if using via EnhancedLLMService)
- `SVG_OUTPUT_DIR`: Directory for saving generated SVG files (defaults to "output/svg")

## LLM Integration

The SVG Generator uses the project's EnhancedLLMService for all LLM API calls, ensuring consistent handling of:

- Request timeouts
- Error handling
- Rate limiting
- Prompt handling

## Supported Diagram Types

- **Flowchart**: Process flows, decision trees, and workflows
- **Network**: Network infrastructure, system architecture
- **Sequence**: Sequence diagrams for processes and interactions
- **Entity-Relationship**: Database schema and entity relationships
- **Mindmap**: Hierarchical concept maps
- **General**: Generic diagrams when type is not specified

## Templates

The SVG Generator uses different prompt templates based on the diagram type. These templates are located in the `genai_agent/svg_to_video/templates` directory and can be customized to improve generation quality.

## Customization

### Custom Templates

You can create custom templates by adding a file in the templates directory. The template file should include:

1. System prompt for the LLM
2. Example input/output pairs
3. Constraints for SVG generation

### Adding Support for New Diagram Types

To add support for a new diagram type:

1. Create a new template file
2. Update the `_get_template_for_diagram_type` method to include the new type
3. Add appropriate detection logic in the `_detect_diagram_type` method

## Error Handling

The SVG Generator implements several error handling mechanisms:

1. **Timeout Handling**: Configurable timeout for LLM API calls
2. **Retry Logic**: Automatic retry for failed API calls
3. **SVG Validation**: Ensures the generated SVG is well-formed and usable
4. **Fallback Strategies**: If a specific provider fails, can fall back to alternatives

## Performance

For optimal performance:

- Use specific diagram types when possible for better results
- Consider caching common diagrams to reduce API calls
- Use the batch processing mode for multiple diagrams

## Debugging

Set the `debug` parameter to `True` in the SVGGenerator constructor to enable detailed logging of:

- Template selection
- API calls
- SVG validation
- Error handling

## Integration with SVG to 3D Pipeline

The SVG Generator integrates with the SVG to 3D pipeline through:

1. Shared configuration settings
2. Direct pipeline API for end-to-end processing
3. Event hooks for monitoring generation progress
