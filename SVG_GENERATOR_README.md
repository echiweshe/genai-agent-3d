# SVG Generator Restoration and Integration

## Overview

This guide explains how to restore and integrate the SVG Generator module in the GenAI Agent 3D project. The SVG Generator allows users to create SVG diagrams from text descriptions using LLM providers such as Claude and OpenAI, and then convert these SVGs to 3D models, animate them, and render them as videos.

## Current Status

The SVG Generator was previously working from the following path:
```
C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent\svg_to_video
```

A backup of this directory has been created at:
```
C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\XX_genai_agent\svg_to_video
```

We need to restore this code to the main project path:
```
C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\genai_agent\svg_to_video
```

## Restoration Process

The `restore_svg_generator.ps1` script automates the process of restoring the SVG Generator from the backup location to the main project path. Here's what it does:

1. Creates a backup of the current SVG Generator code (if any)
2. Copies the working SVG Generator code from the backup location to the main project path
3. Updates import statements in the Python files to reflect the new location
4. Creates a test script to verify the SVG Generator works with Claude and OpenAI LLMs
5. Creates a web UI integration script to add routes to the web UI backend

## Web UI Integration

The SVG Generator can be integrated into the web UI with the following components:

1. **API Routes**: The `svg_generator_routes.py` file defines routes for:
   - Generating SVGs from text descriptions
   - Converting SVGs to 3D models
   - Animating 3D models
   - Rendering videos

2. **Service**: The `svg_generator_service.py` file provides:
   - Methods to get a list of SVG files
   - Methods to delete SVG files

3. **Main Application**: The main.py file is updated to include the SVG Generator routes

## Usage

### Restoring and Testing

1. Run the restoration script:
   ```
   powershell -ExecutionPolicy Bypass -File restore_svg_generator.ps1
   ```

2. Test the SVG Generator:
   ```
   python test_svg_generator.py
   ```

3. Integrate with the web UI:
   ```
   python integrate_svg_to_web_ui.py
   ```

Alternatively, you can run all steps at once using the batch script:
```
restore_and_test_svg_generator.bat
```

### Using the SVG Generator

After restoration and integration, you can use the SVG Generator in the following ways:

1. **From Python code**:
   ```python
   from genai_agent_project.genai_agent.svg_to_video.svg_generator.svg_generator import generate_svg
   
   result = generate_svg(
       prompt="Create a flowchart showing the process of making coffee",
       diagram_type="flowchart",
       output_file="coffee_flowchart.svg",
       provider="claude"  # or "openai" or "mock"
   )
   ```

2. **From the Web UI**:
   - Navigate to the SVG Generator page in the web UI
   - Enter a text description
   - Select a diagram type and LLM provider
   - Click "Generate SVG"
   - Optionally convert to 3D, animate, and render as video

3. **From the API**:
   ```
   POST /svg-generator/generate-svg
   {
       "prompt": "Create a flowchart showing the process of making coffee",
       "diagram_type": "flowchart",
       "provider": "claude"
   }
   ```

## Output Directories

All SVG files are stored in the consolidated output directory:
```
C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg
```

Other output files are stored in:
- 3D models: `output\svg_to_video\models`
- Animations: `output\svg_to_video\animations`
- Videos: `output\svg_to_video\videos`

## Troubleshooting

If you encounter issues:

1. **SVG Generation Fails**:
   - Check if the LLM provider is configured correctly
   - Try using the "mock" provider as a fallback
   - Check the logs for error messages

2. **Web UI Integration Fails**:
   - Verify that the routes are added to main.py
   - Check if the service files are in the correct location
   - Restart the web UI server

3. **3D Conversion/Animation/Rendering Fails**:
   - Verify that the required dependencies are installed
   - Check if the modules are imported correctly
   - Look for specific error messages in the logs

## Contributing

When making changes to the SVG Generator:

1. Always make a backup before modifying the code
2. Update the import statements if necessary
3. Test with multiple LLM providers
4. Update the documentation if you add new features

## License

This code is part of the GenAI Agent 3D project and follows the same licensing terms.
