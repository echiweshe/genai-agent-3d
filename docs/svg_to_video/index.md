# SVG to Video Pipeline Documentation

## Overview

The SVG to Video pipeline converts text descriptions to SVG diagrams and then to animated 3D videos. This documentation provides details on each component of the pipeline and how they work together.

## Components

1. [SVG Generator](svg_generator.md) - Converts text descriptions to SVG diagrams using LLMs
2. [SVG to 3D Converter](svg_to_3d.md) - Converts SVG diagrams to 3D models
3. [Animation System](animation.md) - Applies animations to 3D models
4. [Video Renderer](rendering.md) - Renders animated 3D scenes to video files

## Integration

The SVG to Video pipeline is fully integrated with the main GenAI Agent 3D project. It uses the project's:

- Environment configuration
- Enhanced LLM Service via Redis
- Shared output directory structure
- Common logging infrastructure

## Using the Pipeline

### Command Line Interface

The pipeline can be run from the command line using the `run_svg_to_video.ps1` script:

```powershell
# Generate an SVG from a description
.\run_svg_to_video.ps1 svg "A flowchart showing user authentication process" output.svg

# Convert an SVG to a video
.\run_svg_to_video.ps1 convert input.svg output.mp4

# Generate a video directly from a description
.\run_svg_to_video.ps1 generate "A network diagram of cloud infrastructure" output.mp4

# List available LLM providers
.\run_svg_to_video.ps1 list-providers
```

### From Python Code

The pipeline can also be used directly from Python code:

```python
from genai_agent.svg_to_video.pipeline_integrated import SVGToVideoPipeline

# Create the pipeline
pipeline = SVGToVideoPipeline(debug=True)

# Generate SVG only
svg_content, svg_path = await pipeline.generate_svg_only(
    description="A flowchart showing user authentication process",
    diagram_type="flowchart"
)

# Convert SVG to video
output_files = await pipeline.convert_svg_to_video(
    svg_path="input.svg",
    animation_type="flowchart",
    render_quality="medium",
    duration=10
)

# Generate video from description
output_files = await pipeline.generate_video_from_description(
    description="A network diagram of cloud infrastructure",
    diagram_type="network",
    animation_type="network",
    render_quality="high",
    duration=15
)
```

## Development

### Running Tests

To run the tests for the SVG to Video pipeline:

```powershell
# Run all SVG to Video tests
.\scripts\test\run_svg_to_video_tests.ps1

# Run tests for a specific module
.\scripts\test\run_svg_to_video_tests.ps1 -Module svg_generator
```

### Adding New Features

To extend the pipeline with new features:

1. For new diagram types: Update the SVG Generator's `_get_prompt_for_diagram_type` method
2. For new animation types: Add a new animation function in the Animation System
3. For new rendering options: Update the VideoRenderer class

## Troubleshooting

Common issues and solutions:

1. **LLM provider not available**: Check that the API keys are properly set in the `.env` file
2. **Blender not found**: Set the `BLENDER_PATH` environment variable to the path of the Blender executable
3. **SVG generation fails**: Try a different LLM provider or simplify the description
4. **Rendering is slow**: Use a lower quality setting or reduce the animation duration
