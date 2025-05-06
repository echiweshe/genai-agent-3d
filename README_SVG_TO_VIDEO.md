# SVG to Video Pipeline for GenAI Agent 3D

## Overview

The SVG to Video Pipeline is a feature within the GenAI Agent 3D project that allows you to:
1. Generate SVG diagrams from text descriptions using AI (Claude, OpenAI, etc.)
2. Convert these SVGs to 3D models
3. Animate the 3D models with various animation types
4. Render the animations to video

This README provides detailed information on setting up and using the pipeline.

## Setup Instructions

### Prerequisites

- **Python 3.8+**: Required for all components
- **Blender 3.5+ or 4.x**: Required for 3D conversion, animation, and rendering
- **API Keys**: Anthropic (Claude) API key for best SVG generation results (OpenAI also supported)

### Installation Steps

1. **Set up Blender**:
   - Install Blender from [blender.org](https://www.blender.org/download/)
   - Run the Blender path update utility:
     ```
     update_blender_path.bat
     ```
   - This will detect your Blender installation and update the configuration files

2. **Set up API Keys**:
   - Open your `.env` file in the `genai_agent_project` directory
   - Add your API keys:
     ```
     ANTHROPIC_API_KEY=your_anthropic_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

3. **Synchronize Directories**:
   - Run the directory synchronization script:
     ```
     sync_svg_directories.bat
     ```
   - This ensures that all necessary directories exist and are properly linked

4. **Restart Services**:
   - Restart the backend service to apply changes:
     ```
     cd genai_agent_project
     python manage_services.py restart backend
     ```

## Testing the Pipeline

To test the SVG to Video pipeline:

1. **Run the test script**:
   ```
   test_svg_pipeline.bat
   ```
   This will:
   - Check the pipeline status
   - Generate a test SVG diagram
   - Convert it to 3D
   - Animate the 3D model
   - Render a test video

2. **Check the test results**:
   - The script will show the status of each step
   - Output files will be saved in the appropriate directories

## Using the Pipeline

### Command Line Interface

To generate a video from the command line:

```
run_svg_to_video_pipeline.bat "Description of your diagram"
```

Follow the interactive prompts to select:
- Diagram type (flowchart, network, sequence, etc.)
- Animation type (simple, rotate, explode, flow, network)
- Video quality (low, medium, high)
- Video duration

### Web UI

To use the SVG to Video pipeline in the web UI:

1. Navigate to the SVG to Video page in the web UI
2. Enter a description for your diagram
3. Select an LLM provider
4. Generate the SVG
5. Convert the SVG to 3D
6. Animate the 3D model
7. Render the animation to video

The web UI also provides a "View in Blender" button to open 3D models directly in Blender.

## Animation Types

The pipeline supports several animation types:

- **Simple**: Basic fade in, rotation, and highlighting
- **Rotate**: Smooth rotation of the model with camera movement
- **Explode**: Elements explode outward from the center
- **Flow**: Sequential animation, ideal for flowcharts
- **Network**: Special animation for network diagrams, with pulse effects

## Troubleshooting

### Blender Integration Issues

If you encounter issues with Blender integration:

1. **Check the Blender path**:
   - Run `update_blender_path.bat` to ensure the correct path is set
   - Make sure Blender can be run from the command line

2. **Debug Blender integration**:
   - Run `debug_blender_integration.py` for detailed diagnostics
   - Check that all required directories exist

3. **Fix directory structure**:
   - Run `sync_svg_directories.bat` to ensure proper directory structure
   - Restart the backend after making changes

### SVG Generation Issues

If SVG generation fails:

1. **Check API keys**:
   - Ensure your Anthropic or OpenAI API key is correctly set in the `.env` file
   - Try the "claude-direct" provider for best results

2. **Check logs**:
   - Review the backend logs for specific error messages
   - Make sure the backend service is running

### 3D Conversion and Rendering Issues

If 3D conversion or rendering fails:

1. **Verify Blender installation**:
   - Make sure Blender is correctly installed
   - Check if Blender can be run directly from the command line

2. **Check for simple diagrams**:
   - Start with simpler diagrams for testing
   - Complex SVGs may be more difficult to convert

## File Locations

- **SVG Files**: `output/svg` and `output/svg_to_video/svg`
- **3D Models**: `output/svg_to_video/models`
- **Animated Models**: `output/svg_to_video/animations`
- **Videos**: `output/svg_to_video/videos`

## Advanced Configuration

Advanced users can modify:

1. **Animation parameters** in: `genai_agent_project/genai_agent/svg_to_video/animation/model_animator.py`
2. **Rendering options** in: `genai_agent_project/genai_agent/svg_to_video/rendering/video_renderer.py`
3. **SVG generation prompts** in: `genai_agent_project/genai_agent/svg_to_video/svg_generator`

## Examples

### Example Diagram Descriptions

Try these example descriptions:

1. **Flowchart**:
   ```
   A flowchart showing the process of online shopping, including 
   steps for browsing products, adding items to cart, checkout 
   process, payment options, and order confirmation.
   ```

2. **Network Diagram**:
   ```
   A network diagram illustrating a secure enterprise network 
   architecture with multiple security zones, including 
   internet-facing DMZ, internal network segments, firewalls, 
   load balancers, web servers, application servers, and database servers.
   ```

3. **Sequence Diagram**:
   ```
   A sequence diagram showing the authentication process for a 
   web application, including the interactions between user, 
   browser, authentication service, user database, and email 
   notification system.
   ```

## Support

If you encounter any issues:

1. Check the documentation and troubleshooting guide
2. Review logs for specific error messages
3. Ensure all prerequisites are correctly installed
4. Try running the fix scripts (`fix_svg_pipeline.bat`, `sync_svg_directories.bat`)

## About This Pipeline

This SVG to Video pipeline is part of the GenAI Agent 3D project, leveraging:
- Claude (Anthropic) and other LLMs for SVG generation
- Blender for 3D conversion, animation, and rendering
- FastAPI and React for the web interface
