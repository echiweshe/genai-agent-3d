# SVG to 3D Converter

## Overview

The SVG to 3D Converter module transforms SVG diagrams into three-dimensional models using Blender. It parses SVG elements, converts them to 3D geometry, applies materials, and prepares the scene for animation and rendering.

## Architecture

The SVG to 3D Converter consists of the following components:

1. **SVG Parser**: Parses SVG files into a structured representation
2. **SVG Converter**: Converts SVG elements to 3D objects
3. **Material Handler**: Creates and applies materials to 3D objects
4. **Scene Manager**: Sets up the 3D scene with camera, lighting, and environment

## Usage

```python
from genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter

# Create a converter instance
converter = SVGTo3DConverter(
    extrude_depth=0.1,  # Depth of extrusion for 3D objects
    scale_factor=0.01,  # Scale factor for converting SVG to Blender units
    debug=True          # Enable debug logging
)

# Convert an SVG file to 3D
input_svg = "path/to/input.svg"
output_blend = "path/to/output.blend"
result = converter.convert_file(input_svg, output_blend)

if result:
    print(f"Successfully converted {input_svg} to {output_blend}")
else:
    print("Conversion failed")
```

## SVG Parser

The SVG Parser handles:

- Reading SVG files
- Parsing SVG elements (rect, circle, ellipse, path, etc.)
- Extracting style information (fill, stroke, opacity, etc.)
- Transforming coordinates to Blender's coordinate system

### Supported SVG Elements

- Basic shapes: `<rect>`, `<circle>`, `<ellipse>`, `<line>`, `<polyline>`, `<polygon>`
- Complex paths: `<path>` with various commands (M, L, C, Q, A, etc.)
- Text elements: `<text>` (basic support)
- Groups: `<g>` with transformations
- SVG attributes: fill, stroke, opacity, transform, etc.

## SVG Converter

The SVG Converter includes modules for:

- Converting SVG rectangles to 3D objects
- Converting SVG circles and ellipses to 3D objects
- Converting SVG paths to 3D objects
- Converting SVG text to 3D objects
- Handling SVG groups and transformations

## Material Handler

The Material Handler manages:

- Creating materials based on SVG styles
- Handling color, opacity, and other visual properties
- Applying materials to 3D objects
- Supporting both fill and stroke styles

### Material Features

- Fill colors and opacity
- Stroke colors, widths, and opacity
- Simple gradients (linear and radial)
- Transparent materials

## Scene Manager

The Scene Manager handles:

- Setting up the camera for optimal viewing
- Creating appropriate lighting
- Configuring the environment
- Preparing the scene for animation and rendering

## Integration with Blender

The SVG to 3D Converter integrates with Blender through:

1. Python scripting using the Blender Python API (bpy)
2. Running the converter inside Blender's Python environment
3. Saving the result as a Blender file (.blend) that can be loaded for further editing

## Customization

### Extrusion Settings

The converter supports customization of the extrusion:

- **extrude_depth**: Controls how "thick" the 3D objects will be
- **extrude_mode**: Controls how the extrusion is performed (Normal, Freestyle, etc.)

### Material Settings

Material appearance can be customized:

- **material_type**: Controls the shader type (Principled BSDF, Diffuse, etc.)
- **use_nodes**: Enables node-based materials for advanced effects
- **transparency_mode**: Controls how transparency is handled

### Scene Settings

Scene parameters can be adjusted:

- **camera_type**: Controls the camera projection (Perspective, Orthographic)
- **lighting_setup**: Controls the lighting arrangement (Studio, 3-Point, etc.)
- **background_color**: Sets the environment background color

## Troubleshooting

### Common Issues

1. **Missing SVG Elements**
   
   **Symptom**: Some elements from the SVG are missing in the 3D output
   
   **Solution**: Check if the elements use unsupported features or have invalid data

2. **Material Issues**

   **Symptom**: Materials have wrong colors or transparency doesn't work
   
   **Solution**: Check the material settings and SVG style attributes

3. **Scale Problems**

   **Symptom**: Objects are too small, too large, or disproportionate
   
   **Solution**: Adjust the scale_factor parameter or check the SVG viewBox attribute

4. **Performance Issues**

   **Symptom**: Conversion is slow or crashes with large SVGs
   
   **Solution**: Simplify complex paths, use lower polygon counts, or split the SVG into parts

## Development

### Adding Support for New SVG Features

To add support for new SVG features:

1. Update the SVG Parser to recognize and extract the feature
2. Add corresponding conversion logic in the SVG Converter
3. Update the Material Handler if new style attributes are involved
4. Test with sample SVGs that use the feature

### Performance Optimization

For better performance:

- Use simplified SVGs with fewer path points
- Optimize path conversion algorithms
- Use instancing for repeated elements
- Implement level-of-detail techniques for complex scenes
