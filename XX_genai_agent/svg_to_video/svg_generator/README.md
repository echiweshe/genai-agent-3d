# SVG Generator

## Overview

The SVG Generator creates SVG diagrams from text descriptions using the project's LLM service. It provides a clean interface for generating SVG content with support for different diagram types.

## Features

- Integration with the project's LLM service via Redis
- Support for multiple diagram types (flowchart, network, sequence)
- Configurable output parameters
- Automatic LLM provider selection
- Retry mechanism for failed generations
- SVG validation and cleaning

## Architecture

The SVG Generator consists of these main components:

1. **LLM Service Integration**: Connects to the project's LLM service via the `LLMServiceManager`
2. **Prompt Templates**: Specialized prompts for different diagram types
3. **SVG Parser**: Extracts and validates SVG content from LLM responses
4. **Output Management**: Saves SVG content to files in the configured output directory

## Usage

```python
from genai_agent.svg_to_video.svg_generator import SVGGenerator

# Initialize the generator
generator = SVGGenerator(debug=True)

# Generate an SVG diagram
svg_content = await generator.generate_svg(
    concept="A flowchart showing user authentication process",
    provider="claude",  # Optional, defaults to the first available provider
    diagram_type="flowchart",  # Optional, can infer from concept
    max_retries=2  # Optional, number of retry attempts
)

# Save the SVG content to a file
svg_path = generator.save_svg(
    svg_content=svg_content,
    filename="authentication_flowchart.svg"  # Optional, generates UUID if not provided
)

# Check available LLM providers
providers = generator.get_available_providers()
print(f"Available providers: {providers}")
```

## Configuration

The SVG Generator can be configured using environment variables:

- `SVG_OUTPUT_DIR`: Directory for generated SVG files (default: "output/svg")

## Integration with LLM Service

The SVG Generator uses the project's `LLMServiceManager` to access language models rather than creating separate connections. This ensures consistent use of language models throughout the project and leverages the existing Redis-based communication system.

## Diagram Types

The generator supports the following diagram types:

1. **Flowchart**: For process flows, workflows, algorithms, etc.
2. **Network**: For network diagrams, system architectures, node graphs, etc.
3. **Sequence**: For sequence diagrams, timing diagrams, etc.
4. **General**: For any other type of diagram (default)

Each diagram type uses a specialized prompt template to guide the LLM in generating the appropriate SVG content.

## Error Handling

The generator includes a retry mechanism for handling failed generations. If a generation fails, it will retry up to the specified number of times before raising an exception. This helps handle intermittent LLM service issues and invalid responses.

## Extending

To add support for a new diagram type:

1. Add a new prompt template in the `_get_prompt_for_diagram_type` method
2. Implement any special handling for the new diagram type

To add support for a new LLM provider:

1. Add the provider to the project's `LLMServiceManager`
2. The SVG Generator will automatically detect the new provider

## Dependencies

- `genai_agent.services.llm.llm_service_manager.LLMServiceManager`: For accessing the project's LLM service
- `asyncio`: For asynchronous operations
- `re`: For SVG content extraction
- `os`, `pathlib`: For file operations
- `uuid`: For generating unique filenames
