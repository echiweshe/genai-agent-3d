# SVG to 3D Conversion Component

## Overview

This document details the implementation of the SVG to 3D Conversion component, which transforms SVG diagrams into 3D Blender scenes using the Blender Python API.

## Implementation Details

### SVG to 3D Conversion Script

```python
# svg_to_3d_blender.py
import bpy
import os
import sys
import xml.etree.ElementTree as ET
import mathutils

def clean_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def parse_svg(svg_path):
    """Parse SVG file and extract elements."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    # Extract viewBox dimensions
    if 'viewBox' in root.attrib:
        viewBox = root.attrib['viewBox'].split()
        width = float(viewBox[2])
        height = float(viewBox[3])
    else:
        width = 800
        height = 600
    
    elements = []
    
    # Process all elements
    for elem in root.findall('.//*'):
        if elem.tag.endswith('rect'):
            # Process rectangle
            x = float(elem.attrib.get('x', 0))
            y = float(elem.attrib.get('y', 0))
            w = float(elem.attrib.get('width', 0))
            h = float(elem.attrib.get('height', 0))
            fill = elem.attrib.get('fill', '#CCCCCC')
            
            elements.append({
                'type': 'rect',
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'fill': fill
            })
        
        elif elem.tag.endswith('circle'):
            # Process circle
            cx = float(elem.attrib.get('cx', 0))
            cy = float(elem.attrib.get('cy', 0))
            r = float(elem.attrib.get('r', 0))
            fill = elem.attrib.get('fill', '#CCCCCC')
            
            elements.append({
                'type': 'circle',
                'cx': cx,
                'cy': cy,
                'r': r,
                'fill': fill
            })
        
        elif elem.tag.endswith('line'):
            # Process line
            x1 = float(elem.attrib.get('x1', 0))
            y1 = float(elem.attrib.get('y1', 0))
            x2 = float(elem.attrib.get('x2', 0))
            y2 = float(elem.attrib.get('y2', 0))
            stroke = elem.attrib.get('stroke', '#000000')
            
            elements.append({
                'type': 'line',
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'stroke': stroke
            })
        
        elif elem.tag.endswith('text'):
            # Process text
            x = float(elem.attrib.get('x', 0))
            y = float(elem.attrib.get('y', 0))
            text_content = elem.text or ""
            fill = elem.attrib.get('fill', '#000000')
            
            elements.append({
                'type': 'text',
                'x': x,
                'y': y,
                'text': text_content,
                'fill': fill
            })
        
        # Add other SVG element types as needed (path, polyline, etc.)
        
    return elements, width, height

def create_3d_object(element, max_width, max_height):
    """Convert an SVG element to a 3D Blender object."""
    if element['type'] == 'rect':
        # Create a cube for rectangle
        x = (element['x'] - max_width/2) * 0.01  # Scale and center
        y = (max_height/2 - element['y']) * 0.01  # Scale, center, and flip Y
        
        width = element['width'] * 0.01
        height = element['height'] * 0.01
        depth = 0.1  # Fixed depth for now
        
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x + width/2, y - height/2, 0)
        )
        obj = bpy.context.active_object
        obj.scale = (width, height, depth)
        
        # Create material
        material = bpy.data.materials.new(name="Material")
        material.use_nodes = True
        
        # Set color based on fill
        if 'fill' in element:
            # Convert hex color to RGB
            fill = element['fill'].lstrip('#')
            if len(fill) == 6:
                rgb = tuple(int(fill[i:i+2], 16)/255 for i in (0, 2, 4))
                material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
        
        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
    elif element['type'] == 'circle':
        # Create a cylinder for circle
        cx = (element['cx'] - max_width/2) * 0.01
        cy = (max_height/2 - element['cy']) * 0.01
        r = element['r'] * 0.01
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=r,
            depth=0.1,
            location=(cx, cy, 0)
        )
        obj = bpy.context.active_object
        
        # Create material
        material = bpy.data.materials.new(name="Material")
        material.use_nodes = True
        
        # Set color based on fill
        if 'fill' in element:
            fill = element['fill'].lstrip('#')
            if len(fill) == 6:
                rgb = tuple(int(fill[i:i+2], 16)/255 for i in (0, 2, 4))
                material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
        
        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
    elif element['type'] == 'line':
        # Create a line/cylinder for connecting elements
        x1 = (element['x1'] - max_width/2) * 0.01
        y1 = (max_height/2 - element['y1']) * 0.01
        x2 = (element['x2'] - max_width/2) * 0.01
        y2 = (max_height/2 - element['y2']) * 0.01
        
        # Calculate center point and length
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Calculate direction vector
        direction = mathutils.Vector((x2 - x1, y2 - y1, 0))
        length = direction.length
        
        # Create cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.02,  # Thin line
            depth=length,
            location=(center_x, center_y, 0)
        )
        obj = bpy.context.active_object
        
        # Align cylinder with line direction
        if length > 0:
            direction.normalize()
            # Get the default cylinder orientation (z-axis)
            up_vector = mathutils.Vector((0, 0, 1))
            # Calculate rotation quaternion
            quaternion = up_vector.rotation_difference(direction)
            obj.rotation_euler = quaternion.to_euler()
        
        # Create material for the line
        material = bpy.data.materials.new(name="LineMaterial")
        material.use_nodes = True
        
        # Set color based on stroke
        if 'stroke' in element:
            stroke = element['stroke'].lstrip('#')
            if len(stroke) == 6:
                rgb = tuple(int(stroke[i:i+2], 16)/255 for i in (0, 2, 4))
                material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
        
        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    
    elif element['type'] == 'text':
        # Create 3D text
        x = (element['x'] - max_width/2) * 0.01
        y = (max_height/2 - element['y']) * 0.01
        
        # Create text object
        bpy.ops.object.text_add(location=(x, y, 0.1))  # Slightly raised above other elements
        text_obj = bpy.context.active_object
        text_obj.data.body = element['text']
        
        # Set text properties
        text_obj.data.size = 0.15
        text_obj.data.extrude = 0.02  # Give some depth to the text
        
        # Create material
        material = bpy.data.materials.new(name="TextMaterial")
        material.use_nodes = True
        
        # Set color based on fill
        if 'fill' in element:
            fill = element['fill'].lstrip('#')
            if len(fill) == 6:
                rgb = tuple(int(fill[i:i+2], 16)/255 for i in (0, 2, 4))
                material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
        
        # Assign material
        if text_obj.data.materials:
            text_obj.data.materials[0] = material
        else:
            text_obj.data.materials.append(material)

def setup_camera_and_lighting():
    """Set up camera and lighting for the scene."""
    # Add camera
    bpy.ops.object.camera_add(location=(0, -5, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.0, 0, 0)
    
    # Make this the active camera
    bpy.context.scene.camera = camera
    
    # Add lighting
    bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    
    # Add ambient light
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    area = bpy.context.active_object
    area.data.energy = 3.0
    area.scale = (10, 10, 1)

def convert_svg_to_3d(svg_path, output_path):
    """Convert an SVG file to a 3D Blender scene."""
    # Clean the scene
    clean_scene()
    
    # Parse SVG
    elements, width, height = parse_svg(svg_path)
    
    # Create 3D objects for each element
    for element in elements:
        create_3d_object(element, width, height)
    
    # Setup camera and lighting
    setup_camera_and_lighting()
    
    # Save the file
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    
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
        svg_path = argv[0]
        output_path = argv[1]
        convert_svg_to_3d(svg_path, output_path)
```

## Command-Line Usage

To use this script with Blender directly from the command line:

```bash
blender --background --python svg_to_3d_blender.py -- input.svg output.blend
```

## Implementation Notes

### Supported SVG Elements

The current implementation supports the following SVG elements:

1. **Rectangle (`<rect>`)**: Converted to 3D cubes
2. **Circle (`<circle>`)**: Converted to 3D cylinders
3. **Line (`<line>`)**: Converted to thin cylinders
4. **Text (`<text>`)**: Converted to 3D extruded text

Future versions could add support for:
- Paths (`<path>`)
- Polylines (`<polyline>`)
- Polygons (`<polygon>`)
- Ellipses (`<ellipse>`)
- Groups (`<g>`)

### Scaling and Positioning

The implementation handles scaling and positioning with the following approach:

1. Reads SVG viewBox dimensions to understand the original scale
2. Centers the diagram in 3D space
3. Scales SVG coordinates (typically in pixels) to Blender units (0.01 units per pixel)
4. Flips Y coordinates (SVG has Y increasing downward, Blender has Y increasing upward)

### Materials and Colors

Each SVG element is assigned a material based on its fill or stroke color:

1. Converts hex colors to RGB values
2. Uses Blender's material nodes to apply colors
3. Sets up basic properties like metallic, roughness, etc.

### Scene Setup

The script also sets up a basic 3D scene with:

1. A camera positioned to view the entire diagram
2. Key lighting (sun light) for main illumination
3. Fill lighting (area light) for softer illumination

## Dependencies

- Blender 3.0+ with Python support
- Python libraries:
  - `xml.etree.ElementTree` (standard library)
  - `mathutils` (included with Blender)

## Testing

### Manual Testing

1. Start with simple SVG files containing basic shapes
2. Test with increasingly complex SVG diagrams
3. Verify proper positioning, scaling, and coloring
4. Check if text is legible and properly positioned

### Automated Testing

Since this component runs inside Blender, automated testing requires running Blender in headless mode:

```python
# test_svg_to_3d.py
import subprocess
import os
import unittest

class TestSVGTo3D(unittest.TestCase):
    def test_conversion(self):
        # Test file paths
        svg_path = "test_diagram.svg"
        blend_path = "test_output.blend"
        
        # Create a simple test SVG
        with open(svg_path, "w") as f:
            f.write('''
            <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
              <rect x="100" y="100" width="200" height="100" fill="#FF0000"/>
              <circle cx="400" cy="300" r="50" fill="#0000FF"/>
            </svg>
            ''')
        
        # Run the conversion script
        result = subprocess.run([
            "blender", "--background", "--python", "svg_to_3d_blender.py", "--",
            svg_path, blend_path
        ], capture_output=True)
        
        # Check if the process succeeded
        self.assertEqual(result.returncode, 0)
        
        # Check if the output file exists
        self.assertTrue(os.path.exists(blend_path))
        
        # Clean up
        os.remove(svg_path)
        os.remove(blend_path)

if __name__ == "__main__":
    unittest.main()
```

## Known Limitations

1. Limited SVG element support (currently only basic shapes)
2. No support for SVG gradients or patterns
3. No support for SVG animations
4. Text positioning might not be pixel-perfect

## Next Steps

1. Implement support for additional SVG elements
2. Add advanced material handling for different visual styles
3. Improve text handling and positioning
4. Add support for SVG groups and hierarchy
5. Create utilities for batch conversion
6. Integrate with animation system component