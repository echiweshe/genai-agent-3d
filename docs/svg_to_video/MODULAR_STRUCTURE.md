# SVG to Video Pipeline: Modular Structure

## Overview

The SVG to Video pipeline has been reorganized into a modular structure to improve maintainability, facilitate future enhancements, and follow best practices for Python project organization. This document explains the modular structure and how to use it.

## Directory Structure

The pipeline is now organized as follows:

```
genai-agent-3d/
├── genai_agent/
│   └── svg_to_video/            # Main pipeline package
│       ├── svg_generator/       # SVG generation module
│       │   ├── svg_generator.py # Main SVG generator class
│       │   └── __init__.py      # Module initialization
│       ├── svg_to_3d/           # SVG to 3D conversion module
│       │   ├── svg_converter.py # Base converter class
│       │   ├── svg_parser.py    # SVG parsing functions
│       │   ├── svg_converter_*.py # Specialized converter modules
│       │   └── __init__.py      # Module initialization
│       ├── animation/           # Animation module
│       │   ├── animation_system.py # Animation system
│       │   └── __init__.py      # Module initialization
│       ├── rendering/           # Rendering module
│       │   ├── video_renderer.py # Video renderer
│       │   └── __init__.py      # Module initialization
│       ├── pipeline_integrated.py # Integrated pipeline
│       └── __init__.py          # Package initialization
├── scripts/
│   ├── run/                    # Run scripts
│   │   └── run_svg_to_video.ps1 # Main run script
│   ├── test/                   # Test scripts
│   │   └── run_svg_to_video_tests.ps1 # Test script
│   └── utils/                  # Utility scripts
│       └── fix_and_test_svg_to_video.ps1 # Fix script
├── tests/
│   └── svg_to_video/           # Test suite
│       ├── svg_generator/      # SVG generator tests
│       ├── svg_to_3d/          # SVG to 3D converter tests
│       ├── animation/          # Animation tests
│       ├── rendering/          # Rendering tests
│       └── pipeline/           # Pipeline tests
├── output/                     # Output directory
│   ├── svg/                    # Generated SVG files
│   ├── models/                 # 3D model files
│   ├── animations/             # Animation files
│   └── videos/                 # Rendered videos
└── docs/
    └── svg_to_video/           # Documentation
        ├── svg_generator.md    # SVG generator documentation
        ├── svg_to_3d.md        # SVG to 3D converter documentation
        ├── animation.md        # Animation system documentation
        ├── rendering.md        # Rendering documentation
        └── index.md            # Main documentation
```

## Key Components

### 1. SVG Generator

The SVG Generator module handles the generation of SVG diagrams from text descriptions using LLMs (Claude, GPT-4, etc.) through the project's EnhancedLLMService.

Key features:
- Integration with the project's LLM service via Redis
- Support for different diagram types (flowchart, network, etc.)
- Customizable prompts for different diagram types
- SVG validation and cleaning

### 2. SVG to 3D Converter

The SVG to 3D Converter module transforms SVG diagrams into 3D models using Blender.

Key features:
- Modular architecture with separate components for different SVG elements
- Proper material handling for fills and strokes
- Support for complex SVG elements (paths, text, etc.)
- Scene setup with camera and lighting

### 3. Animation System

The Animation System adds animations to 3D models based on the diagram type.

Key features:
- Support for different animation types (standard, flowchart, network, sequence)
- Automatic detection of diagram type from content
- Customizable animation parameters (duration, etc.)
- Integration with Blender's animation system

### 4. Video Renderer

The Video Renderer renders animated 3D scenes to video files.

Key features:
- Support for different quality presets (low, medium, high)
- Configurable output formats and resolutions
- Optimized rendering settings for different use cases
- Integration with Blender's rendering system

### 5. Integrated Pipeline

The Integrated Pipeline connects all components to provide a seamless experience.

Key features:
- End-to-end processing from text description to video
- Support for partial processing (SVG only, SVG to video, etc.)
- Consistent error handling and logging
- Integration with the project's output directory structure

## Usage

### Command Line Interface

The SVG to Video pipeline can be used from the command line using the following scripts:

```powershell
# Generate an SVG from a description
.\run_svg_to_video.ps1 svg "A flowchart showing user authentication process" output.svg

# Convert an SVG to a video
.\run_svg_to_video.ps1 convert input.svg output.mp4

# Generate a video directly from a description
.\run_svg_to_video.ps1 generate "A network diagram of cloud infrastructure" output.mp4

# Run a demo of the pipeline
.\run_svg_video_demo.ps1

# Run the demo with custom parameters
.\run_svg_video_demo.ps1 --description "A flowchart showing the login process" --quality low --duration 5
```

### Python API

The SVG to Video pipeline can also be used programmatically:

```python
from genai_agent.svg_to_video import SVGToVideoPipeline

# Create a pipeline instance
pipeline = SVGToVideoPipeline(debug=True)

# Generate an SVG only
svg_content, svg_path = await pipeline.generate_svg_only(
    description="A flowchart showing user authentication process",
    diagram_type="flowchart"
)

# Convert an SVG to a video
output_files = await pipeline.convert_svg_to_video(
    svg_path="input.svg",
    animation_type="flowchart",
    render_quality="medium",
    duration=10
)

# Generate a video from a description
output_files = await pipeline.generate_video_from_description(
    description="A network diagram of cloud infrastructure",
    diagram_type="network",
    animation_type="network",
    render_quality="high",
    duration=15
)
```

## Troubleshooting

If you encounter import errors or other issues with the SVG to Video pipeline, run the fix script:

```powershell
.\scripts\utils\fix_and_test_svg_to_video.ps1
```

This script will:
1. Fix import issues caused by module reorganization
2. Test the pipeline to ensure it's working properly
3. Create a test script that demonstrates how to use the pipeline

For more detailed information about each component, refer to the individual documentation files in the `docs/svg_to_video/` directory.

## Future Enhancements

The modular structure allows for easier enhancements:

1. **SVG Generator**: Add support for more diagram types and LLM providers
2. **SVG to 3D Converter**: Add support for more SVG features (gradients, patterns, etc.)
3. **Animation System**: Add more animation types and effects, especially using the Scenex system
4. **Video Renderer**: Add more output formats and rendering options
5. **Pipeline**: Add more customization options and integration points
