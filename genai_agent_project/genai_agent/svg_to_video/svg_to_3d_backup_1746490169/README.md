# SVG to 3D Converter

## Overview

The SVG to 3D Converter transforms SVG elements into 3D objects using Blender's Python API. It supports a wide range of SVG elements and attributes, converting them into equivalent 3D representations.

## Features

- Support for basic shapes (rectangles, circles, ellipses)
- Support for paths and polylines
- Support for groups and transforms
- Material handling for fills, strokes, and opacity
- Scene setup with camera and lighting
- Modular architecture for easy extension

## Architecture

The SVG to 3D converter follows a modular architecture:

```
svg_to_3d/
├── __init__.py                   # Package initialization
├── svg_parser.py                 # SVG file parsing
├── svg_parser_elements.py        # SVG element parsing
├── svg_parser_paths.py           # SVG path parsing
├── svg_converter.py              # Base converter class
├── svg_converter_create.py       # Object creation methods
├── svg_converter_group.py        # Group handling methods
├── svg_converter_materials.py    # Material creation methods
├── svg_converter_path.py         # Path conversion methods
├── svg_converter_scene.py        # Scene setup methods
├── svg_to_3d_converter_new.py    # Main converter class
└── svg_utils.py                  # Utility functions
```

Each module handles a specific aspect of the conversion process, making the code more maintainable and easier to extend.

## Usage

```python
from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter

# Initialize the converter
converter = SVGTo3DConverter(
    extrude_depth=0.1,  # Depth for 3D extrusion
    scale_factor=0.01,  # Scale factor for conversion
    debug=True  # Enable debug logging
)

# Convert an SVG file to a 3D model
result = await converter.convert_svg_to_3d(
    svg_path="input.svg",
    output_path="output.blend"
)

# Check the result
if result:
    print("Conversion successful!")
else:
    print("Conversion failed!")
```

## SVG Element Support

The converter supports the following SVG elements:

1. **Basic Shapes**:
   - `<rect>`: Rectangles, including rounded corners
   - `<circle>`: Circles
   - `<ellipse>`: Ellipses
   - `<line>`: Lines
   - `<polyline>`: Polylines
   - `<polygon>`: Polygons

2. **Advanced Elements**:
   - `<path>`: Paths with various commands (M, L, H, V, C, S, Q, T, A, Z)
   - `<g>`: Groups with nested elements
   - `<text>`: Text elements

3. **Attributes**:
   - `fill`: Fill color
   - `stroke`: Stroke color
   - `stroke-width`: Stroke width
   - `opacity`: Overall opacity
   - `fill-opacity`: Fill opacity
   - `stroke-opacity`: Stroke opacity
   - `transform`: Transformations (translate, rotate, scale, matrix)

## Material System

The converter includes a sophisticated material system that handles:

1. **Fill Materials**: For filled shapes
2. **Stroke Materials**: For stroked shapes
3. **Transparency**: Using Blender's material blend modes
4. **Material Caching**: To improve performance

## Transform Handling

The converter supports SVG transform attributes:

1. **translate**: Move elements
2. **rotate**: Rotate elements
3. **scale**: Scale elements
4. **matrix**: Apply custom transformation matrices

## Scene Setup

The converter sets up a complete Blender scene:

1. **Camera**: Properly positioned to view the entire scene
2. **Lighting**: Three-point lighting system
3. **World Settings**: Background color and environment settings
4. **Viewport Configuration**: Material preview mode

## Known Limitations

1. **Complex Gradients**: Limited support for gradient fills
2. **Filters**: No support for SVG filters
3. **Animations**: No support for SVG animations (SMIL)
4. **Custom Fonts**: Limited support for text with custom fonts

## Extending

To add support for new SVG elements:

1. Add parsing logic in `svg_parser_elements.py`
2. Add conversion logic in a new or existing converter module
3. Register the new element handler in `svg_converter.py`

## Dependencies

- `bpy`: Blender Python API
- `mathutils`: Blender's math utilities
- `xml.dom.minidom`: For SVG parsing
- `re`: For regular expressions
- `math`: For mathematical operations
