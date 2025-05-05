# Video Rendering Component

## Overview

This document details the implementation of the Video Rendering component, which takes animated 3D scenes and renders them to high-quality video files. The component leverages Blender's rendering capabilities to produce professional-looking outputs with configurable quality settings.

## Implementation Details

### Video Renderer Class

```python
# video_renderer.py
import bpy
import os
import sys

class VideoRenderer:
    """Render a Blender animation to video."""
    
    def __init__(self, blend_file):
        """Initialize with a blend file path."""
        self.blend_file = blend_file
        
        # Open the Blender file
        bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    def setup_render_settings(self, resolution=(1920, 1080), fps=30, quality='medium'):
        """Configure render settings."""
        scene = bpy.context.scene
        
        # Set resolution
        scene.render.resolution_x = resolution[0]
        scene.render.resolution_y = resolution[1]
        scene.render.resolution_percentage = 100
        
        # Set frame rate
        scene.render.fps = fps
        
        # Set output format
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        
        # Set quality based on preset
        if quality == 'high':
            scene.render.ffmpeg.constant_rate_factor = 'HIGH'
            scene.render.use_motion_blur = True
            scene.eevee.use_bloom = True
            scene.eevee.use_ssr = True
            scene.eevee.use_gtao = True
            scene.eevee.taa_render_samples = 64
        elif quality == 'medium':
            scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
            scene.render.use_motion_blur = False
            scene.eevee.use_bloom = True
            scene.eevee.use_ssr = False
            scene.eevee.use_gtao = True
            scene.eevee.taa_render_samples = 32
        else:  # low
            scene.render.ffmpeg.constant_rate_factor = 'LOW'
            scene.render.use_motion_blur = False
            scene.eevee.use_bloom = False
            scene.eevee.use_ssr = False
            scene.eevee.use_gtao = False
            scene.eevee.taa_render_samples = 16
        
        # Set render engine to EEVEE for faster rendering
        scene.render.engine = 'BLENDER_EEVEE'
    
    def render(self, output_path, frame_start=None, frame_end=None):
        """Render the animation to video."""
        scene = bpy.context.scene
        
        # Set frame range if specified
        if frame_start is not None:
            scene.frame_start = frame_start
        if frame_end is not None:
            scene.frame_end = frame_end
        
        # Set output path
        scene.render.filepath = output_path
        
        # Render animation
        bpy.ops.render.render(animation=True)
        
        return output_path

# For command-line execution from Blender
if __name__ == "__main__":
    # Get args after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    if len(argv) >= 2:
        blend_file = argv[0]
        output_path = argv[1]
        
        # Optional quality parameter
        quality = 'medium'
        if len(argv) >= 3:
            quality = argv[2]
        
        renderer = VideoRenderer(blend_file)
        renderer.setup_render_settings(quality=quality)
        renderer.render(output_path)
```

### Enhanced Render Settings

For more control over rendering quality and output, we can extend the renderer with additional settings:

```python
# enhanced_renderer.py
import bpy
import os
import sys
import json

class EnhancedVideoRenderer:
    """Enhanced renderer with additional options for video output."""
    
    def __init__(self, blend_file):
        """Initialize with a blend file path."""
        self.blend_file = blend_file
        
        # Open the Blender file
        bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    def setup_render_settings(self, config=None):
        """Configure render settings with a configuration dictionary."""
        config = config or {}
        scene = bpy.context.scene
        
        # Resolution
        resolution = config.get('resolution', (1920, 1080))
        scene.render.resolution_x = resolution[0]
        scene.render.resolution_y = resolution[1]
        scene.render.resolution_percentage = config.get('resolution_percentage', 100)
        
        # Frame rate
        scene.render.fps = config.get('fps', 30)
        
        # Frame range
        frame_start = config.get('frame_start')
        if frame_start is not None:
            scene.frame_start = frame_start
            
        frame_end = config.get('frame_end')
        if frame_end is not None:
            scene.frame_end = frame_end
        
        # Output format
        scene.render.image_settings.file_format = config.get('file_format', 'FFMPEG')
        
        if scene.render.image_settings.file_format == 'FFMPEG':
            # Video format settings
            scene.render.ffmpeg.format = config.get('video_format', 'MPEG4')
            scene.render.ffmpeg.codec = config.get('video_codec', 'H264')
            scene.render.ffmpeg.constant_rate_factor = config.get('quality', 'MEDIUM')
            scene.render.ffmpeg.ffmpeg_preset = config.get('preset', 'GOOD')
            
            # Audio settings if needed
            if config.get('audio_codec'):
                scene.render.ffmpeg.audio_codec = config.get('audio_codec')
        
        # Render engine
        engine = config.get('engine', 'BLENDER_EEVEE')
        scene.render.engine = engine
        
        # Engine-specific settings
        if engine == 'BLENDER_EEVEE':
            # EEVEE settings
            scene.eevee.use_bloom = config.get('bloom', False)
            scene.eevee.use_ssr = config.get('screen_space_reflections', False)
            scene.eevee.use_gtao = config.get('ambient_occlusion', True)
            scene.eevee.taa_render_samples = config.get('samples', 32)
            scene.eevee.use_soft_shadows = config.get('soft_shadows', True)
        elif engine == 'CYCLES':
            # Cycles settings
            scene.cycles.samples = config.get('samples', 128)
            scene.cycles.use_denoising = config.get('denoising', True)
            scene.cycles.film_exposure = config.get('exposure', 1.0)
        
        # Motion blur
        scene.render.use_motion_blur = config.get('motion_blur', False)
        
        # Color management
        scene.view_settings.view_transform = config.get('view_transform', 'Filmic')
        scene.view_settings.look = config.get('look', 'None')
        
        return self
    
    def add_text_overlay(self, text, position='BOTTOM', font_size=32, color=(1, 1, 1, 1)):
        """Add text overlay to the video (like a title or watermark)."""
        # Create a new text object
        bpy.ops.object.text_add()
        text_obj = bpy.context.object
        text_obj.data.body = text
        
        # Set text properties
        text_obj.data.size = font_size / 100  # Convert to Blender units
        
        # Position the text
        if position == 'TOP':
            text_obj.location = (0, 0.8, 0)
        elif position == 'BOTTOM':
            text_obj.location = (0, -0.8, 0)
        elif position == 'CENTER':
            text_obj.location = (0, 0, 0)
        
        # Create material for text
        mat = bpy.data.materials.new(name="TextOverlayMaterial")
        mat.use_nodes = True
        
        # Set material color
        principled = mat.node_tree.nodes["Principled BSDF"]
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Emission"].default_value = color
        principled.inputs["Emission Strength"].default_value = 1.0
        
        # Assign material
        text_obj.data.materials.append(mat)
        
        # Make sure text faces the camera
        constraint = text_obj.constraints.new(type='TRACK_TO')
        constraint.target = bpy.context.scene.camera
        constraint.track_axis = 'TRACK_Z'
        constraint.up_axis = 'UP_Y'
        
        return text_obj
    
    def render(self, output_path):
        """Render the animation to video."""
        scene = bpy.context.scene
        
        # Set output path
        scene.render.filepath = output_path
        
        # Render animation
        bpy.ops.render.render(animation=True)
        
        return output_path
```

### Render Configuration Files

To make rendering more flexible, we can use configuration files to define render settings:

```json
// render_config_high.json
{
  "resolution": [1920, 1080],
  "fps": 30,
  "engine": "BLENDER_EEVEE",
  "quality": "HIGH",
  "bloom": true,
  "screen_space_reflections": true,
  "ambient_occlusion": true,
  "samples": 64,
  "motion_blur": true,
  "soft_shadows": true,
  "view_transform": "Filmic",
  "look": "High Contrast"
}
```

```json
// render_config_medium.json
{
  "resolution": [1280, 720],
  "fps": 30,
  "engine": "BLENDER_EEVEE",
  "quality": "MEDIUM",
  "bloom": true,
  "screen_space_reflections": false,
  "ambient_occlusion": true,
  "samples": 32,
  "motion_blur": false,
  "soft_shadows": true,
  "view_transform": "Filmic",
  "look": "None"
}
```

```json
// render_config_low.json
{
  "resolution": [854, 480],
  "fps": 30,
  "engine": "BLENDER_EEVEE",
  "quality": "LOW",
  "bloom": false,
  "screen_space_reflections": false,
  "ambient_occlusion": false,
  "samples": 16,
  "motion_blur": false,
  "soft_shadows": false,
  "view_transform": "Standard",
  "look": "None"
}
```

### Command-Line Usage with Configuration

```python
# render_with_config.py
import bpy
import os
import sys
import json
from enhanced_renderer import EnhancedVideoRenderer

# For command-line execution from Blender
if __name__ == "__main__":
    # Get args after '--'
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    if len(argv) >= 2:
        blend_file = argv[0]
        output_path = argv[1]
        
        # Optional config file
        config = {}
        if len(argv) >= 3 and os.path.exists(argv[2]):
            with open(argv[2], 'r') as f:
                config = json.load(f)
        
        # Create and configure renderer
        renderer = EnhancedVideoRenderer(blend_file)
        renderer.setup_render_settings(config)
        
        # Add title if specified
        if 'title' in config:
            renderer.add_text_overlay(
                config['title'],
                position=config.get('title_position', 'TOP'),
                font_size=config.get('title_size', 32),
                color=config.get('title_color', (1, 1, 1, 1))
            )
        
        # Render
        renderer.render(output_path)
```

## Command-Line Usage

Basic usage:

```bash
blender --background --python video_renderer.py -- input.blend output.mp4 medium
```

With configuration file:

```bash
blender --background --python render_with_config.py -- input.blend output.mp4 render_config_high.json
```

## Implementation Notes

### Render Engines

The implementation supports two render engines:

1. **EEVEE**: A real-time render engine that provides good quality with fast render times
2. **Cycles**: A ray-tracing render engine that provides photo-realistic quality but with longer render times

For our SVG to Video pipeline, EEVEE is recommended for its speed while still providing good quality.

### Quality Presets

The implementation provides three quality presets:

1. **High**: Full HD resolution, high sample count, all effects enabled
2. **Medium**: HD resolution, medium sample count, some effects enabled
3. **Low**: SD resolution, low sample count, minimal effects

These presets balance quality and render time for different use cases.

### Output Formats

The primary output format is MP4 with H.264 encoding, which provides a good balance of quality and file size. Other supported formats include:

1. **WebM**: For web delivery
2. **GIF**: For simple animations
3. **Image Sequence**: For further processing or editing

### Performance Considerations

Rendering is computationally intensive. Some performance considerations:

1. **GPU Acceleration**: Enable GPU rendering when available
2. **Sample Count**: Lower sample counts render faster but with more noise
3. **Resolution**: Lower resolutions render faster
4. **Effects**: Disable complex effects (SSR, bloom, motion blur) for faster rendering

## Dependencies

- Blender 3.0+ with Python support
- FFmpeg (included with Blender)

## Testing

### Manual Testing

1. Test with different quality presets
2. Verify output video quality and file size
3. Test with different animation types
4. Check rendering time for performance optimization

### Automated Testing

```python
# test_video_renderer.py
import subprocess
import os
import unittest
import json

class TestVideoRenderer(unittest.TestCase):
    def test_basic_rendering(self):
        # Test file paths
        blend_path = "test_animation.blend"
        output_path = "test_output.mp4"
        
        # Run the rendering script
        result = subprocess.run([
            "blender", "--background", "--python", "video_renderer.py", "--",
            blend_path, output_path, "low"  # Use low quality for faster tests
        ], capture_output=True)
        
        # Check if the process succeeded
        self.assertEqual(result.returncode, 0)
        
        # Check if the output file exists
        self.assertTrue(os.path.exists(output_path))
        
        # Check if the file size is reasonable (not empty)
        self.assertGreater(os.path.getsize(output_path), 1000)
        
        # Clean up
        os.remove(output_path)
    
    def test_rendering_with_config(self):
        # Test file paths
        blend_path = "test_animation.blend"
        output_path = "test_config_output.mp4"
        config_path = "test_config.json"
        
        # Create a test config
        config = {
            "resolution": [640, 360],
            "fps": 15,
            "engine": "BLENDER_EEVEE",
            "quality": "LOW",
            "samples": 8,
            "title": "Test Video"
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        # Run the rendering script
        result = subprocess.run([
            "blender", "--background", "--python", "render_with_config.py", "--",
            blend_path, output_path, config_path
        ], capture_output=True)
        
        # Check if the process succeeded
        self.assertEqual(result.returncode, 0)
        
        # Check if the output file exists
        self.assertTrue(os.path.exists(output_path))
        
        # Clean up
        os.remove(output_path)
        os.remove(config_path)

if __name__ == "__main__":
    unittest.main()
```

## Known Limitations

1. Limited to Blender's rendering capabilities
2. No support for external renderers
3. Basic text overlay support (no complex compositions)
4. No audio support in the initial implementation

## Next Steps

1. Add support for audio tracks and narration
2. Implement more advanced text and graphic overlays
3. Add support for rendering to different output formats
4. Optimize rendering performance with GPU acceleration
5. Implement a render farm system for distributed rendering
6. Integrate with the pipeline orchestration component