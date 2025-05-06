# SVG to 3D Viewer Integration Guide

## Overview

The SVG to 3D Viewer component enhances the SVG to Video Pipeline by providing a seamless way to:

1. Convert SVG diagrams to 3D models
2. View these models directly in Blender
3. Download the 3D models for external use

This integration builds upon the existing SVG to Video Pipeline and adds Blender integration to create a more cohesive workflow between SVG generation and 3D model viewing.

## Components

The integration consists of these main components:

1. **Frontend Components**
   - SVGTo3DViewer - An enhanced React component with Blender viewing capabilities
   - Integration with existing SVGToVideoPage

2. **Backend Components**
   - `blender_routes.py` - API endpoints for Blender integration
   - Enhanced `svg_generator_routes.py` - Integration with Blender routes

3. **Integration Scripts**
   - `apply_svg_to_3d_viewer_and_restart.bat` - Setup and restart script

## Features

### 1. SVG to 3D Conversion

- Convert any SVG diagram to a 3D model with one click
- Status indicators showing conversion progress
- Error handling with clear messages

### 2. Blender Integration

- Automatically detect installed Blender versions
- Open 3D models directly in Blender from the web interface
- Support for multiple Blender versions (3.6+, 4.0+)

### 3. Model Management

- Download 3D models for external use
- View model information and file paths
- Organized file structure in the output directory

## How It Works

### Workflow

1. **Generate SVG**: Create an SVG diagram using the SVG Generator
2. **Select SVG**: Choose a diagram from the Generated Diagrams tab
3. **Convert to 3D**: Navigate to the 3D Conversion tab and click "Convert to 3D Model"
4. **View in Blender**: Click "View in Blender" to open the model directly in Blender

### Technical Implementation

The workflow is implemented through several key components:

- **Frontend React Components**: Handle user interactions and display models/conversion status
- **Backend FastAPI Routes**: Process conversion requests and manage Blender integration
- **Blender Path Detection**: Automatically find Blender installations on the system
- **File Management**: Organize output files in appropriate directories

## Setup and Configuration

### Prerequisites

- Blender installed (version 3.6 or later recommended)
- Node.js and npm for frontend
- Python 3.8+ for backend
- FastAPI and related dependencies

### Configuration

The system looks for Blender in these locations:

1. Environment variable: `BLENDER_PATH`
2. Configuration file: `config.yaml` (blender.path)
3. Common installation directories:
   - Windows: `C:\Program Files\Blender Foundation\Blender x.y\`
   - macOS: `/Applications/Blender x.y/`
   - Linux: `/usr/bin/blender`, `/usr/local/bin/blender`

### Installation

To install the SVG to 3D Viewer integration:

1. Run `apply_svg_to_3d_viewer_and_restart.bat`
2. The script will:
   - Check for Blender installation
   - Create necessary output directories
   - Restart the services

## Usage Guide

### Generating SVGs

1. Navigate to the SVG to Video Pipeline page
2. Enter a description for your diagram in the "Generate SVG" tab
3. Select diagram type and click "Generate SVG"

### Converting to 3D

1. Select your SVG from the "Generated Diagrams" tab
2. Navigate to the "3D Conversion" tab
3. Click "Convert to 3D Model"
4. Wait for the conversion to complete

### Viewing in Blender

1. Once conversion is complete, click "View in Blender"
2. Blender will open with your 3D model loaded
3. You can now manipulate, edit, or render the model in Blender

### Downloading Models

1. After conversion, click "Download Model" to save the 3D model file
2. The file can be opened in Blender or other 3D software

## Troubleshooting

### Common Issues

1. **Blender not found**
   - Ensure Blender is installed
   - Set the `BLENDER_PATH` environment variable
   - Update `config.yaml` with the correct path

2. **Conversion fails**
   - Check the backend logs for specific errors
   - Ensure the SVG is valid and contains convertible elements
   - Verify output directories have write permissions

3. **Blender doesn't open**
   - Check if Blender is properly installed
   - Try opening Blender manually with the model file
   - Check system permissions for launching applications

### Debugging

For detailed debugging:

1. Check backend logs in the console
2. Use the `/blender/debug-paths` endpoint to verify Blender configuration
3. Inspect network requests in the browser developer tools

## Future Enhancements

Planned improvements for the SVG to 3D Viewer:

1. **Enhanced 3D Conversion**
   - Better handling of complex SVG elements
   - Material and texture support
   - Options for extrusion depth and scaling

2. **Blender Integration**
   - Template-based scene creation
   - Custom camera setups
   - Animation presets

3. **User Experience**
   - Real-time 3D preview in the browser
   - Saved model library
   - Conversion settings customization

## Contributing

To contribute to the SVG to 3D Viewer:

1. Understand the existing architecture (see `MASTER_DOCUMENTATION.md`)
2. Follow the code organization patterns
3. Add tests for new functionality
4. Update documentation with changes

## License

This component is part of the GenAI Agent 3D project and follows its licensing.
