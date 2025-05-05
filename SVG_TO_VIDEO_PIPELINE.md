# SVG to Video Pipeline

## Overview

The SVG to Video Pipeline is a feature within the GenAI Agent 3D project that allows users to generate SVG diagrams from text descriptions using LLM providers (Claude, OpenAI, etc.), convert these SVGs to 3D models, animate them, and render them as videos.

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| SVG Generation | ✅ Working | Successfully integrated with Claude Direct API |
| SVG to 3D Conversion | ⚠️ Requires Setup | Requires Blender installation and proper mathutils module |
| Animation | ⚠️ Requires Setup | Requires Blender installation |
| Rendering | ⚠️ Requires Setup | Requires Blender installation |

## Architecture

The pipeline consists of several components:

1. **SVG Generator**: Uses LLM providers to convert text descriptions into SVG diagrams
2. **SVG to 3D Converter**: Converts SVG diagrams to 3D models using Blender
3. **Animation Module**: Adds animations to the 3D models
4. **Rendering Module**: Renders the animated models to video

## Directory Structure

```
genai-agent-3d/
├── output/
│   ├── svg/                     # Main SVG output directory
│   └── svg_to_video/
│       ├── animations/          # Animations output directory
│       ├── models/              # 3D models output directory
│       ├── svg/                 # SVG files for the pipeline
│       └── videos/              # Rendered videos output directory
└── genai_agent_project/
    └── genai_agent/
        └── svg_to_video/        # Core code for the pipeline
            ├── animation/       # Animation module
            ├── llm_integrations/ # LLM provider integrations
            ├── rendering/       # Rendering module
            ├── svg_generator/   # SVG generation module
            └── svg_to_3d/       # SVG to 3D conversion module
```

## Configuration

The pipeline uses the following configuration:

1. **Environment Variables** (.env file):
   - `BLENDER_PATH`: Path to the Blender executable (e.g., `C:/Program Files/Blender Foundation/Blender 4.2/blender.exe`)
   - `ANTHROPIC_API_KEY`: API key for Claude (Anthropic)
   - `OPENAI_API_KEY`: API key for OpenAI

2. **Config File** (config.yaml):
   - Output directories
   - LLM provider settings
   - Pipeline configurations

## Web UI Integration

The SVG to Video pipeline is integrated into the web UI with the following endpoints:

- `/svg-generator/generate`: Generate an SVG based on a text description
- `/svg-generator/convert-to-3d`: Convert an SVG to a 3D model
- `/svg-generator/animate-model`: Animate a 3D model
- `/svg-generator/render-video`: Render an animated model to video
- `/svg-generator/providers`: Get available LLM providers
- `/svg-generator/health`: Check the health of the SVG generator

## LLM Provider Integration

The pipeline supports multiple LLM providers for SVG generation:

- **Claude Direct**: Using the Anthropic API directly
- **OpenAI**: Using the OpenAI API
- **Ollama**: Using the local Ollama service
- **Mock**: For testing without API usage

## Setup Requirements

To fully utilize the SVG to Video pipeline, you need:

1. **Blender Installation**: Required for SVG to 3D conversion, animation, and rendering
2. **API Keys**: Anthropic (Claude) and/or OpenAI API keys
3. **Python Dependencies**: Required for SVG generation and 3D conversion

## Usage Instructions

### Generating SVGs

1. Navigate to the SVG to Video page in the web UI
2. Select a provider (Claude Direct recommended)
3. Enter a text description for your diagram
4. Click "Generate SVG"

### Converting to 3D (When Available)

1. After generating an SVG, select it
2. Click "Convert to 3D"
3. Configure conversion parameters if needed
4. Click "Convert"

### Adding Animation (When Available)

1. After converting to 3D, select the model
2. Click "Animate"
3. Select animation type and parameters
4. Click "Apply Animation"

### Rendering to Video (When Available)

1. After adding animation, select the animated model
2. Click "Render"
3. Configure rendering parameters
4. Click "Render to Video"

## Recent Fixes and Improvements

- Fixed directory structure issues with SVG output
- Fixed SVG generator integration with Claude Direct API
- Created stub implementations for mathutils and ModelAnimator
- Fixed the Claude provider 'count_tokens' error
- Added synchronization scripts for SVG directories
- Added comprehensive documentation

## Future Work

- Complete integration with Blender for 3D conversion
- Implement full animation capabilities
- Enhance rendering options and quality
- Add more diagram types and templates
- Improve error handling and user feedback
