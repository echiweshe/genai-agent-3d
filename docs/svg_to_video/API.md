# SVG to Video Pipeline: API Reference

## SVGToVideoPipeline

Main class that integrates all components and provides a unified interface.

### Initialization

```python
pipeline = SVGToVideoPipeline(debug=False)
```

Parameters:
- `debug` (bool): Enable debug logging

### Methods

#### `generate_video_from_description`

Generate a video from a text description.

```python
output_files = await pipeline.generate_video_from_description(
    description="A flowchart showing login process",
    provider=None,
    diagram_type="flowchart",
    animation_type=None,
    render_quality="medium",
    duration=10
)
```

Parameters:
- `description` (str): Text description of the diagram
- `provider` (str, optional): LLM provider to use (defaults to project default)
- `diagram_type` (str, optional): Type of diagram ("flowchart", "network", "sequence")
- `animation_type` (str, optional): Type of animation (detected automatically if None)
- `render_quality` (str): Rendering quality ("low", "medium", "high")
- `duration` (int): Animation duration in seconds

Returns:
- Dictionary with paths to generated files:
  ```
  {
      "svg": path to SVG file,
      "model": path to 3D model file,
      "animation": path to animated model file,
      "video": path to rendered video file
  }
  ```

#### `generate_svg_only`

Generate only an SVG diagram from a text description.

```python
svg_content, svg_path = await pipeline.generate_svg_only(
    description="A network diagram",
    provider=None,
    diagram_type="network"
)
```

Parameters:
- `description` (str): Text description of the diagram
- `provider` (str, optional): LLM provider to use
- `diagram_type` (str, optional): Type of diagram

Returns:
- Tuple of (svg_content, svg_path)

#### `convert_svg_to_video`

Convert an existing SVG file to a video.

```python
output_files = await pipeline.convert_svg_to_video(
    svg_path="input.svg",
    animation_type=None,
    render_quality="medium",
    duration=10
)
```

Parameters:
- `svg_path` (str): Path to SVG file
- `animation_type` (str, optional): Type of animation
- `render_quality` (str): Rendering quality
- `duration` (int): Animation duration in seconds

Returns:
- Dictionary with paths to generated files

## SVGGenerator

Class for generating SVG diagrams from text descriptions.

### Initialization

```python
generator = SVGGenerator(debug=False)
```

Parameters:
- `debug` (bool): Enable debug logging

### Methods

#### `generate_svg`

Generate an SVG diagram from a text description.

```python
svg_content = await generator.generate_svg(
    concept="A flowchart showing login process",
    provider=None,
    diagram_type="flowchart",
    max_retries=2
)
```

Parameters:
- `concept` (str): Text description of the diagram
- `provider` (str, optional): LLM provider to use
- `diagram_type` (str, optional): Type of diagram
- `max_retries` (int): Maximum retry attempts

Returns:
- SVG content as a string

#### `save_svg`

Save SVG content to a file.

```python
svg_path = generator.save_svg(
    svg_content="<svg>...</svg>",
    filename=None
)
```

Parameters:
- `svg_content` (str): SVG content to save
- `filename` (str, optional): Filename to use (generates UUID if not provided)

Returns:
- Path to the saved SVG file

#### `get_available_providers`

Get list of available LLM providers.

```python
providers = generator.get_available_providers()
```

Returns:
- List of provider names

## SVGTo3DConverter

Class for converting SVG to 3D models.

### Initialization

```python
converter = SVGTo3DConverter(
    extrude_depth=0.1,
    scale_factor=0.01,
    debug=False
)
```

Parameters:
- `extrude_depth` (float): Depth for 3D extrusion
- `scale_factor` (float): Scale factor for conversion
- `debug` (bool): Enable debug logging

### Methods

#### `convert`

Convert SVG data to a 3D model.

```python
result = converter.convert(svg_data)
```

Parameters:
- `svg_data` (dict): Dictionary with:
  - `elements`: List of SVG elements
  - `width`: SVG width
  - `height`: SVG height

Returns:
- `True` if successful, `False` otherwise

#### `convert_svg_to_3d`

Convert an SVG file to a 3D model.

```python
result = await converter.convert_svg_to_3d(
    svg_path="input.svg",
    output_path="output.blend"
)
```

Parameters:
- `svg_path` (str): Path to input SVG file
- `output_path` (str): Path to output Blender file

Returns:
- `True` if successful, `False` otherwise

## AnimationSystem

Class for adding animations to 3D models.

### Initialization

```python
animation_system = AnimationSystem(debug=False)
```

Parameters:
- `debug` (bool): Enable debug logging

### Methods

#### `animate_model`

Animate a 3D model using Blender.

```python
result = await animation_system.animate_model(
    model_path="input.blend",
    output_path="animated.blend",
    animation_type="standard",
    duration=10
)
```

Parameters:
- `model_path` (str): Path to input 3D model file
- `output_path` (str): Path to save animated model file
- `animation_type` (str): Type of animation ("standard", "flowchart", "network", "sequence")
- `duration` (int): Animation duration in seconds

Returns:
- `True` if successful, `False` otherwise

## VideoRenderer

Class for rendering animated 3D scenes to video.

### Initialization

```python
renderer = VideoRenderer(
    debug=False,
    quality="medium",
    output_format="mp4"
)
```

Parameters:
- `debug` (bool): Enable debug logging
- `quality` (str): Default rendering quality
- `output_format` (str): Default output format

### Methods

#### `render_video`

Render an animated 3D scene to video.

```python
result = await renderer.render_video(
    animation_path="animated.blend",
    output_path="output.mp4",
    quality="medium",
    resolution=(1280, 720),
    fps=30,
    samples=64
)
```

Parameters:
- `animation_path` (str): Path to input animated Blender file
- `output_path` (str): Path to save video file
- `quality` (str, optional): Rendering quality
- `resolution` (tuple, optional): Output resolution as (width, height)
- `fps` (int, optional): Frames per second
- `samples` (int, optional): Number of render samples

Returns:
- `True` if successful, `False` otherwise

## Error Handling

All asynchronous methods in the API can throw exceptions that should be handled appropriately:

1. **`ImportError`**: Thrown when a required module is not available
2. **`RuntimeError`**: Thrown when an operation fails during execution
3. **`ValueError`**: Thrown when invalid parameters are provided
4. **`FileNotFoundError`**: Thrown when a required file is not found

Example error handling:

```python
try:
    result = await pipeline.generate_video_from_description(
        description="A flowchart showing login process"
    )
    # Process successful result
except ImportError as e:
    # Handle missing module
    print(f"Missing module: {e}")
except RuntimeError as e:
    # Handle runtime error
    print(f"Runtime error: {e}")
except ValueError as e:
    # Handle invalid parameter
    print(f"Invalid parameter: {e}")
except Exception as e:
    # Handle unexpected error
    print(f"Unexpected error: {e}")
```

## Environment Variables

The API uses the following environment variables:

- `SVG_OUTPUT_DIR`: Directory for generated SVG files (default: "output/svg")
- `MODEL_OUTPUT_DIR`: Directory for 3D model files (default: "output/models")
- `ANIMATION_OUTPUT_DIR`: Directory for animation files (default: "output/animations")
- `VIDEO_OUTPUT_DIR`: Directory for rendered videos (default: "output/videos")
- `BLENDER_PATH`: Path to Blender executable (default: "blender")

You can set these variables in your environment or in a `.env` file.
