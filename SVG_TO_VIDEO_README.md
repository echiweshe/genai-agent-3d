# SVG to Video Pipeline Integration

This document describes the integration of the SVG to Video pipeline into the GenAI Agent 3D project.

## Overview

The SVG to Video pipeline is a comprehensive workflow that allows users to:

1. Generate SVG diagrams from natural language descriptions using LLMs
2. Convert these SVGs to 3D models
3. Animate the 3D models
4. Render the animations to video

The pipeline is integrated into the main web UI with a dedicated page that guides users through each step of the process.

## Architecture

The SVG to Video pipeline consists of the following components:

- **LLM Integrations**: Connects to various LLM providers (Claude, OpenAI, etc.) for SVG generation
- **SVG to 3D Conversion**: Converts SVG diagrams to 3D models using Blender
- **Animation**: Adds animations to 3D models
- **Rendering**: Renders animated 3D models to video

## Directory Structure

```
genai_agent/svg_to_video/
├── __init__.py
├── animation.py               # Animation module
├── pipeline_integrated.py     # Complete pipeline integration
├── README.md                  # Documentation
├── rendering.py               # Video rendering module
├── llm_integrations/          # LLM provider integrations
│   ├── __init__.py
│   ├── claude_direct.py       # Direct integration with Claude API
│   ├── langchain_integrations.py  # LangChain integrations
│   ├── llm_factory.py         # Factory for managing LLM providers
│   └── redis_llm_service.py   # Integration with Redis LLM service
└── svg_to_3d/                 # SVG to 3D conversion
    ├── __init__.py
    ├── svg_converter.py       # SVG conversion utilities
    ├── svg_parser.py          # SVG parsing utilities
    └── svg_to_3d_converter_new.py  # Main converter
```

## Installation

To make the SVG to Video pipeline available in the GenAI Agent 3D web UI:

1. Run the `copy_svg_to_video_module.bat` script to copy the module from the main project to the genai_agent_project structure.
2. Restart the services with `python manage_services.py restart all`.

## Usage

1. Navigate to the "SVG to Video" page in the web UI.
2. Enter a description for the diagram you want to generate.
3. Select a diagram type and LLM provider.
4. Click "Generate SVG" to create the diagram.
5. Follow the steps to convert the SVG to 3D, animate it, and render it to video.

## API Endpoints

The SVG to Video pipeline exposes the following API endpoints:

- `GET /svg-generator/health`: Check the health of the SVG generator API
- `GET /svg-generator/providers`: Get available LLM providers
- `GET /svg-generator/diagram-types`: Get available diagram types
- `GET /svg-generator/capabilities`: Get pipeline capabilities
- `POST /svg-generator/generate`: Generate an SVG diagram
- `POST /svg-generator/convert-to-3d`: Convert an SVG to a 3D model
- `POST /svg-generator/animate-model`: Animate a 3D model
- `POST /svg-generator/render-video`: Render a video from an animated model

## Troubleshooting

If you encounter any issues:

1. Check the server logs for error messages.
2. Ensure that all required modules are installed.
3. Try running the copy_svg_to_video_module.bat script to update the module files.
4. Check the browser console for any frontend errors.

## Dependencies

- Blender: Required for 3D conversion, animation, and rendering
- LLM providers: At least one LLM provider must be available for SVG generation
- Python libraries: FastAPI, aiohttp, svg.path, etc.

## Development

To modify the SVG to Video pipeline:

1. Make changes to the original files in `genai_agent/svg_to_video/`.
2. Run the `copy_svg_to_video_module.bat` script to update the files in the genai_agent_project structure.
3. Restart the services to apply the changes.

## Future Enhancements

Planned enhancements for the SVG to Video pipeline:

1. Add more animation options
2. Improve 3D model generation quality
3. Add support for custom rendering settings
4. Implement batch processing for multiple SVGs
5. Add audio narration generation for videos
