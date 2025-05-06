# SVG to 3D Path Configuration Guide

## Overview

This document explains the path configuration for the SVG to 3D conversion feature in the GenAI Agent 3D project. Proper path configuration is essential for the SVG generation, 3D conversion, and Blender integration to work correctly without requiring symbolic links.

## Path Structure

The system uses the following directory structure for SVG to 3D conversion:

```
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/
├── output/
│   ├── svg/                  # SVG files from the main SVG generator
│   ├── diagrams/             # Diagrams (including SVGs) for display in the UI
│   ├── models/               # 3D models converted from SVGs
│   ├── animations/           # Animated 3D models
│   ├── videos/               # Rendered videos from animations
│   ├── svg_to_video/         # Special directory for SVG to Video pipeline
│   │   ├── svg/              # SVG files specific to the pipeline
│   │   └── models/           # 3D models specific to the pipeline
│   └── ... other output directories
```

## Configuration Files

The paths are configured in the following files:

1. **config.yaml**: Main configuration file that defines all output paths
2. **svg_generator_routes.py**: Backend routes that use these paths for file operations
3. **SVGToVideoPage.jsx**: Frontend component that displays and manages SVG diagrams

## Common Issues and Solutions

### 1. SVG to 3D Conversion Button Greyed Out

**Cause**: The frontend isn't finding the selected diagram, or the SVG to 3D conversion capability is not available.

**Solution**:
- Check the backend log to see if `svg_to_3d_available` is set to `true` in the capabilities
- Make sure you've selected a diagram in the "Generated Diagrams" tab before switching to the "3D Conversion" tab
- Verify that the `diagrams` state in the frontend has valid SVG data

### 2. "SVG to 3D conversion requires Blender installation" Warning

**Cause**: The system can't find the Blender executable at the path specified in config.yaml.

**Solution**:
- Verify the Blender path in `config.yaml` under `blender.path`
- Make sure Blender is actually installed at that location
- Check if the `blender_routes.py` is properly importing the Blender path

### 3. Files Saved to Wrong Location

**Cause**: Inconsistent path configuration across different components.

**Solution**:
- Use the `ensure_output_paths.bat` script to create all necessary directories
- Check the logs to see where files are actually being saved
- Verify that all components are using paths from config.yaml

## How Files Move Through the System

1. **SVG Generation**:
   - User submits a text description in the UI
   - Backend generates an SVG using an LLM
   - SVG is saved to both `svg/` and `svg_to_video/svg/` directories
   - SVG also appears in the `diagrams/` directory for UI display

2. **SVG to 3D Conversion**:
   - User selects an SVG and clicks "Convert to 3D"
   - Backend converts the SVG to a 3D model using Blender or other tools
   - Model is saved to both `models/` and `svg_to_video/models/` directories

3. **Blender Viewing**:
   - User clicks "View in Blender"
   - Backend opens the model file in Blender using the path from config.yaml

## Modifying Path Configuration

If you need to change the path configuration:

1. Edit the `paths` section in `config.yaml`
2. Run the `ensure_output_paths.bat` script to create any new directories
3. Restart the services using `restart_services.bat`

## Best Practices

1. **Always use config paths**: Access paths through the config object rather than hardcoding them
2. **Create consistent paths**: Use the same path structure for all components
3. **Log path usage**: Add logging statements when accessing or saving files to help with debugging
4. **Check file existence**: Always verify that files exist before trying to use them

## Troubleshooting

If you encounter path-related issues:

1. Check the backend logs for file path information
2. Verify that all directories exist using `ensure_output_paths.bat`
3. Look for any hardcoded paths in the code that should be using config values instead
4. Make sure the Blender path is correctly set in config.yaml
5. If files exist but aren't being found, check for case sensitivity issues in file paths

By following this guide, you should be able to maintain a consistent path configuration across all components without requiring symbolic links.
