# SVG to Video Pipeline Integration Guide

## Overview

The SVG to Video pipeline is now fully integrated into the GenAI Agent 3D project. This guide provides information about the integration, new features, and how to use the pipeline.

## Features

### SVG Generation
- Generate SVG diagrams using AI from text descriptions
- Support for multiple LLM providers including Claude Direct API, OpenAI, and local Ollama
- Various diagram types supported: flowcharts, network diagrams, sequence diagrams, and more
- Full integration with the web UI

### SVG to 3D Conversion
- Convert SVG diagrams to 3D models using Blender
- Customizable extrusion, scale, and other 3D parameters
- Support for various output formats (OBJ, STL, FBX, GLTF/GLB, X3D)
- Blender integration with "View in Blender" capability

### Animation System
- Basic animation of 3D models
- Different animation types for various diagram types
- Animation preview in Blender

### Video Rendering
- Render animated 3D models to video
- Customizable quality settings
- Output in common video formats

## Directory Structure

The SVG to Video pipeline uses the following directory structure:

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
            ├── scripts/         # Helper scripts
            ├── svg_generator/   # SVG generation module
            └── svg_to_3d/       # SVG to 3D conversion module
```

## New Blender Integration

The pipeline now includes enhanced Blender integration:

1. **View in Blender Button**: Open your 3D models and animated models directly in Blender from the web UI
2. **Blender Path Detection**: Automatic detection of Blender installation with user-friendly error messages
3. **Debugging Tools**: Advanced tools to diagnose Blender integration issues
4. **Cross-Platform Support**: Works on Windows, Mac, and Linux

## Setup Requirements

To fully utilize the SVG to Video pipeline, you need:

1. **Blender Installation**: Required for SVG to 3D conversion, animation, and rendering
   - Recommended: Blender 3.5 or higher
   - Set the `BLENDER_PATH` environment variable in the `.env` file
   - Example: `BLENDER_PATH=C:/Program Files/Blender Foundation/Blender 4.2/blender.exe`

2. **API Keys**: For LLM providers
   - Anthropic (Claude) API key for best SVG generation results
   - OpenAI API key as an alternative

3. **Directory Setup**: Run the `sync_svg_directories.bat` script to ensure proper directory structure
   - Creates required directories
   - Sets up symbolic links when possible
   - Synchronizes content between directories

## Usage Guide

### Generating SVGs

1. Navigate to the SVG to Video page in the web UI
2. Enter a detailed description of the diagram you want to create
3. Select the diagram type (flowchart, network diagram, etc.)
4. Choose an LLM provider (Claude Direct recommended)
5. Click "Generate SVG"

### Converting to 3D

1. After generating an SVG, proceed to the "SVG to 3D" step
2. Review your SVG diagram
3. Click "Convert to 3D"
4. Once converted, you can use the "View in Blender" button to open the 3D model in Blender

### Animating Models

1. After converting to 3D, proceed to the "Animation" step
2. Click "Animate Model" to add basic animations
3. Use the "View in Blender" button to preview the animation in Blender

### Rendering to Video

1. After adding animation, proceed to the "Rendering" step
2. Click "Render Video" to render the animated model to video
3. Once complete, you can view or download the video

## Troubleshooting

### Directory Structure Issues

If you encounter issues with file paths or missing directories:

1. Run the `fix_svg_pipeline.bat` script
2. This will fix directory structure issues and synchronize all SVG directories

### Blender Integration Issues

If Blender integration is not working:

1. Ensure Blender is installed and the path is correct in the `.env` file
2. Click the "Debug Blender Issues" button on the SVG to Video page
3. Check the console for detailed debug information
4. Make sure Blender can be run from the command line

### SVG to 3D Conversion Failures

If conversion from SVG to 3D fails:

1. Check if Blender is properly installed
2. Ensure the SVG file is valid and not too complex
3. Try using a simpler SVG diagram
4. Check logs for specific error messages

## Advanced Configuration

Advanced users can modify the configuration in:

1. `.env` file for environment variables
2. `config.yaml` for application configuration

Key configuration options:

- `BLENDER_PATH`: Path to the Blender executable
- `SVG_OUTPUT_DIR`: Directory for generated SVGs
- `MODELS_OUTPUT_DIR`: Directory for 3D models
- `ANIMATIONS_OUTPUT_DIR`: Directory for animated models
- `VIDEOS_OUTPUT_DIR`: Directory for rendered videos

## Future Enhancements

Planned future enhancements for the SVG to Video pipeline:

1. More advanced animation options
2. Material and texture customization
3. Voiceover generation for videos
4. Additional diagram types and templates
5. Integration with presentation software

## Credits

This SVG to Video pipeline is part of the GenAI Agent 3D project, leveraging:

- Claude (Anthropic) API for SVG generation
- Blender for 3D conversion and animation
- FastAPI and React for the web interface
