# SVG to Video Pipeline

This module provides a comprehensive pipeline for converting natural language descriptions to SVG diagrams, 3D models, animations, and finally videos.

## Overview

The SVG to Video pipeline consists of the following stages:

1. **SVG Generation**: Generate SVG diagrams from natural language descriptions using AI
2. **SVG to 3D Conversion**: Convert SVG diagrams to 3D models using Blender
3. **Animation**: Add animation to 3D models
4. **Rendering**: Render animated 3D models to video

## Components

### LLM Integrations

The `llm_integrations` module provides integrations with various LLM providers for SVG generation:

- `claude_direct.py`: Direct integration with Anthropic's Claude API
- `langchain_integrations.py`: Integration with LangChain LLMs
- `redis_llm_service.py`: Integration with Redis-based LLM service
- `llm_factory.py`: Factory pattern for managing LLM integrations

### SVG to 3D

The `svg_to_3d` module contains classes for converting SVG files to 3D models:

- `svg_parser.py`: Parse SVG files into a structured representation
- `svg_to_3d_converter_new.py`: Convert parsed SVG data to 3D models
- Various specialized converters for different SVG elements

### Animation

The `animation.py` module provides functionality to animate 3D models generated from SVGs.

### Rendering

The `rendering.py` module provides functionality to render animated 3D models to video.

## Web UI Integration

The SVG to Video pipeline is integrated into the main GenAI Agent 3D web UI with a dedicated page that allows users to:

1. Generate SVG diagrams from descriptions
2. Convert SVG diagrams to 3D models
3. Animate 3D models
4. Render animations to video

### Backend Integration

The backend integration is implemented in the `svg_generator_routes.py` file, which provides FastAPI routes for:

- `/svg-generator/generate`: Generate SVG diagrams
- `/svg-generator/providers`: Get available LLM providers
- `/svg-generator/diagram-types`: Get available diagram types
- `/svg-generator/capabilities`: Get pipeline capabilities
- `/svg-generator/convert-to-3d`: Convert SVG to 3D model
- `/svg-generator/animate-model`: Animate 3D model
- `/svg-generator/render-video`: Render video from animated model

### Frontend Integration

The frontend integration is implemented in the `SVGToVideoPage.js` component, which provides a user-friendly interface for the entire pipeline.

## Usage

Access the SVG to Video pipeline by selecting it from the navigation sidebar in the GenAI Agent 3D web UI. The interface guides you through each step of the pipeline with clear instructions and visual feedback.

## Dependencies

The SVG to Video pipeline has the following dependencies:

- Blender (for 3D conversion, animation, and rendering)
- Python libraries: FastAPI, asyncio, svg.path, mathutils
- LLM providers (Claude, OpenAI, etc.) for SVG generation
