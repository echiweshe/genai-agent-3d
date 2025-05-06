# SVG to 3D Conversion Tools

This document describes the various tools available for SVG to 3D conversion in the GenAI Agent 3D project.

## Overview

The SVG to 3D conversion system is a modular collection of tools that convert SVG diagrams to 3D models. The system includes:

1. A comprehensive modular SVG parser and converter
2. Command line tools for single and batch conversion
3. Integration with Blender for viewing and editing the 3D models
4. Web UI integration for the complete SVG to Video pipeline

## Available Tools

### Single SVG Conversion and Viewing

**`convert_and_view_svg.bat`**

This script converts a single SVG file to a 3D model and opens it in Blender for viewing.

Usage:
```
convert_and_view_svg.bat path\to\svg_file.svg
```

Example:
```
convert_and_view_svg.bat output\svg\my_diagram.svg
```

### Batch SVG Conversion

**`batch_convert_svg_to_3d.bat`**

This script converts all SVG files in a directory to 3D models.

Usage:
```
batch_convert_svg_to_3d.bat [input_directory]
```

If no input directory is specified, it defaults to `output\svg`.

Example:
```
batch_convert_svg_to_3d.bat output\diagrams
```

### Module Restoration

**`restore_svg_to_3d_and_restart.bat`**

This script restores the complete modular SVG to 3D converter from the backup location and restarts the backend service.

Usage:
```
restore_svg_to_3d_and_restart.bat
```

### SVG Pipeline Status Check

**`check_svg_pipeline_status.bat`**

This script checks the status of all components in the SVG to Video pipeline.

Usage:
```
check_svg_pipeline_status.bat
```

## Architecture

The SVG to 3D conversion system uses a modular architecture with the following components:

1. **SVG Parser** (`svg_parser.py`) - Parses SVG files and extracts elements
2. **SVG Converter** (`svg_converter_*.py`) - Converts SVG elements to 3D objects
3. **Utilities** (`svg_utils.py`) - Common utility functions
4. **Main Converter Class** (`SVGTo3DConverter`) - Coordinates the conversion process

## Workflow

The typical workflow for SVG to 3D conversion is:

1. Generate SVG diagrams using the web UI or other tools
2. Convert the SVG to a 3D model using the SVG to 3D converter
3. View and optionally edit the 3D model in Blender
4. Use the 3D model in presentations, animations, or videos

## Usage in Python Code

You can also use the SVG to 3D converter in your own Python code:

```python
from genai_agent_project.genai_agent.svg_to_video.svg_to_3d import SVGTo3DConverter

# Create a converter
converter = SVGTo3DConverter(debug=True)

# Convert an SVG file to a 3D model
model_path = converter.convert_svg_to_3d("path/to/svg_file.svg")

print(f"3D model created at: {model_path}")
```

## Troubleshooting

If you encounter issues with the SVG to 3D conversion:

1. Check the logs for specific error messages
2. Ensure Blender is installed and the BLENDER_PATH environment variable is set correctly
3. Verify that the SVG file is valid and contains supported elements
4. Run the `restore_svg_to_3d_and_restart.bat` script to restore the SVG to 3D converter modules

## Credits

The SVG to 3D conversion system was developed as part of the GenAI Agent 3D project. It uses a custom SVG parser and converter with Blender integration for 3D modeling.
