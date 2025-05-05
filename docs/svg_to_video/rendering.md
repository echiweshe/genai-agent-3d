# Video Rendering

## Overview

The Video Rendering module is responsible for converting animated 3D scenes into high-quality videos. It handles rendering settings, quality optimization, and output format configuration to produce professional-looking videos from Blender scenes.

## Architecture

The Video Rendering module consists of the following components:

1. **Render Manager**: Manages the rendering process and settings
2. **Quality Configurator**: Configures rendering quality presets
3. **Output Handler**: Manages video output format and file handling
4. **Render Queue**: Handles batch rendering of multiple scenes

## Usage

```python
from genai_agent.svg_to_video.rendering import VideoRenderer

# Create a renderer instance
renderer = VideoRenderer(
    quality="medium",  # Rendering quality preset (low, medium, high)
    output_format="mp4",  # Output video format
    resolution=(1920, 1080),  # Video resolution
    debug=True  # Enable debug logging
)

# Render an animated scene to video
input_blend = "path/to/animated.blend"
output_video = "path/to/output.mp4"

result = renderer.render(
    input_file=input_blend,
    output_file=output_video,
    frame_range=(1, 240),  # Start and end frames
    fps=30  # Frames per second
)

if result:
    print(f"Successfully rendered {input_blend} to {output_video}")
else:
    print("Rendering failed")
```

## Render Manager

The Render Manager handles:

- Setting up the rendering environment
- Configuring render engine settings (Cycles, EEVEE, etc.)
- Managing rendering processes
- Monitoring rendering progress
- Error handling during rendering

## Quality Configurator

The Quality Configurator provides:

- Predefined quality presets (low, medium, high)
- Custom quality configuration
- Balance between quality and rendering speed
- Adaptive quality based on scene complexity

### Quality Presets

#### Low Quality
- Fast rendering with minimal effects
- Lower sample counts
- Simplified lighting
- Basic materials
- Optimized for previews and testing

#### Medium Quality
- Balanced quality and performance
- Moderate sample counts
- Standard lighting and shadows
- Full material features
- Suitable for most production purposes

#### High Quality
- Maximum quality with advanced effects
- High sample counts
- Advanced lighting and shadows
- Full material features with enhanced effects
- Final production quality

## Output Handler

The Output Handler manages:

- Video format configuration (MP4, WebM, etc.)
- Codec selection and settings
- Audio integration (if applicable)
- File naming and organization
- Metadata management

### Supported Output Formats

- **MP4**: Using H.264 codec (most compatible)
- **WebM**: Using VP9 codec (web optimized)
- **MKV**: Using various codecs (high quality)
- **Image Sequence**: PNG or JPEG sequences for post-processing

## Render Queue

The Render Queue provides:

- Batch rendering of multiple scenes
- Priority-based rendering
- Resource allocation for parallel rendering
- Job management and status tracking

## Blender Integration

The Video Rendering module integrates with Blender through:

1. Python scripting using the Blender Python API (bpy)
2. Configuring rendering settings programmatically
3. Using Blender's command-line rendering capabilities
4. Post-processing rendered frames into video

## Advanced Features

### Post-Processing

The module supports various post-processing options:

- Color grading and correction
- Compositing effects
- Text overlays and captions
- Transitions between scenes

### Distributed Rendering

For large projects, the module supports:

- Rendering across multiple machines
- Frame distribution for parallel processing
- Render farming integration
- Progress synchronization

### Adaptive Rendering

The module includes adaptive rendering features:

- Automatic quality adjustment based on scene complexity
- Noise reduction for faster rendering
- Detail enhancement for important elements
- Render region optimization

## Performance Optimization

For optimal rendering performance:

- Use the appropriate quality preset for your needs
- Consider using EEVEE for faster rendering when appropriate
- Enable denoising for faster rendering with fewer samples
- Use simplified materials for background elements
- Enable persistent data for faster batch rendering

## Troubleshooting

### Common Issues

1. **Slow Rendering**
   
   **Symptom**: Rendering takes much longer than expected
   
   **Solution**: Reduce quality settings, simplify scene, use GPU rendering if available

2. **Quality Issues**

   **Symptom**: Output video has noise, artifacts, or quality problems
   
   **Solution**: Increase sample count, check lighting and materials, enable denoising

3. **Crashes During Rendering**

   **Symptom**: Blender crashes during rendering
   
   **Solution**: Render in smaller frame batches, reduce memory usage, update GPU drivers

4. **Output Format Problems**

   **Symptom**: Output video has compatibility issues or excessive file size
   
   **Solution**: Change output format or codec settings, adjust bitrate

## Integration with Pipeline

The Video Rendering module integrates with the full SVG to Video pipeline:

1. Receives animated 3D scenes from the Animation System
2. Applies final rendering settings based on project requirements
3. Outputs the final video files to the specified directory
4. Reports rendering status and statistics back to the pipeline orchestrator
