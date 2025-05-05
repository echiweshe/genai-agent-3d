# Video Renderer

## Overview

The Video Renderer handles the rendering of animated 3D scenes to video files. It configures Blender's render settings and produces high-quality video output with customizable parameters.

## Features

- Multiple quality presets (low, medium, high)
- Configurable output formats (MP4, WebM)
- Resolution and frame rate settings
- Render samples and quality controls
- Progress tracking and logging
- Integration with Blender's render system

## Architecture

The Video Renderer consists of these main components:

1. **Quality Presets**: Predefined settings for different rendering quality levels
2. **Render Script Generator**: Creates Blender Python scripts for rendering
3. **Render Process Management**: Handles Blender subprocess execution
4. **Output Configuration**: Manages output format, resolution, and other settings

## Usage

```python
from genai_agent.svg_to_video.rendering import VideoRenderer

# Initialize the renderer
renderer = VideoRenderer(
    debug=True,
    quality="medium",  # Default quality
    output_format="mp4"  # Default output format
)

# Render a video
result = await renderer.render_video(
    animation_path="animated.blend",
    output_path="output.mp4",
    quality="high",  # Override default quality
    resolution=(1920, 1080),  # Custom resolution
    fps=30,  # Frames per second
    samples=128  # Render samples (higher for better quality)
)

# Check the result
if result:
    print("Rendering successful!")
else:
    print("Rendering failed!")
```

## Quality Presets

The renderer includes three quality presets:

1. **Low**: Fast rendering with basic quality
   - Resolution: 640x480
   - Samples: 32
   - Features: Basic lighting, no motion blur

2. **Medium**: Balanced rendering with good quality
   - Resolution: 1280x720
   - Samples: 64
   - Features: Improved lighting, basic effects

3. **High**: Detailed rendering with excellent quality
   - Resolution: 1920x1080
   - Samples: 128
   - Features: Advanced lighting, motion blur, high-quality effects

## Render Engine

The renderer uses Blender's Cycles render engine for high-quality output. This provides:

1. **Physically-Based Rendering**: Realistic lighting and materials
2. **GPU Acceleration**: Utilizes GPU for faster rendering when available
3. **Advanced Effects**: Supports depth of field, motion blur, and other effects

## Output Formats

The renderer supports the following output formats:

1. **MP4 (H.264)**: Standard video format with good compression
2. **WebM (VP9)**: Open format with good quality and compression

## Render Script

The renderer generates a Blender Python script that:

1. Configures render settings based on the specified quality
2. Sets up output format and resolution
3. Configures the render engine and samples
4. Sets frames per second and animation range
5. Executes the rendering process
6. Saves the output to the specified file

## Error Handling

The renderer includes robust error handling:

1. **Process Monitoring**: Tracks Blender process status
2. **Timeout Management**: Handles long-running renders
3. **Output Validation**: Ensures the output file exists and is valid
4. **Logging**: Detailed logs for debugging rendering issues

## Extending

To add a new quality preset:

1. Add the preset definition in the `render_video` method
2. Update the render script generation to handle the new preset

To add a new output format:

1. Add format handling in the `_ensure_render_script_exists` method
2. Update the render script to configure the new format

## Dependencies

- `bpy`: Blender Python API
- `asyncio`: For asynchronous operations
- `os`, `pathlib`: For file operations
- `subprocess`: For running Blender as a subprocess
