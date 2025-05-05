# SVG to Video Pipeline

## Overview

The SVG to Video pipeline is a component of the GenAI Agent 3D project that converts text descriptions to SVG diagrams and then to animated 3D videos. The pipeline leverages AI-powered diagram generation, Blender for 3D conversion, and custom animation techniques to create engaging visualizations.

## Features

- **AI-Powered SVG Generation**: Create SVG diagrams from text descriptions using Claude or OpenAI
- **3D Conversion**: Transform SVG elements into 3D objects using Blender
- **Smart Animation**: Apply context-aware animations based on diagram type
- **High-Quality Rendering**: Produce professional video output with customizable settings
- **Multi-Mode Operation**: Run in development, production, or simple mode
- **Comprehensive API**: Full API for integration with other systems
- **User-Friendly Interface**: Web interface for diagram generation and video creation

## Installation

### Prerequisites

- Python 3.9+
- Blender 3.0+ (must be accessible from the command line)
- Node.js 14+ (for the frontend)

### Initial Setup

Run the setup script to create a virtual environment and install all dependencies:

```bash
setup_svg_to_video.bat
```

### API Keys

The SVG generator requires API keys for the LLM providers. Edit the `.env` file in the root directory and add your API keys:

```
# API Keys for LLM Providers
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
BLENDER_PATH=path_to_blender_executable  # Optional, if Blender is not in PATH
```

## Usage

### Unified Run Script

```powershell
# Start in development mode (separate backend and frontend)
.\run_svg_to_video.ps1 -Dev

# Start in simple mode (simplified server)
.\run_svg_to_video.ps1 -Simple

# Start in production mode (built frontend served by backend)
.\run_svg_to_video.ps1 -Production
```

### Kill Script

To stop all running servers:

```powershell
.\kill_servers.ps1
```

### Command Line Interface

The SVG to Video pipeline can also be used from the command line:

```bash
# List available providers
.\run_svg_cli.bat list-providers

# Generate an SVG from a text description
.\run_svg_cli.bat svg "A flowchart showing user authentication process" output.svg

# Convert an existing SVG to video
.\run_svg_cli.bat convert input.svg output.mp4

# Generate a video directly from a concept
.\run_svg_cli.bat generate "A network diagram showing cloud infrastructure" output.mp4
```

## Architecture

### Components

1. **SVG Generator**: Creates SVG diagrams from text descriptions using LLM providers
2. **SVG to 3D Converter**: Transforms SVG elements into 3D objects using Blender
3. **Animation System**: Applies animations to 3D objects based on diagram type
4. **Video Renderer**: Renders the animated 3D scene to a video file
5. **Pipeline Orchestrator**: Coordinates the entire process and handles errors

### API Endpoints

- `GET /api/svg-to-video/providers`: Get available LLM providers
- `GET /api/svg-to-video/generate-svg`: Generate SVG from text description
- `POST /api/svg-to-video/generate-svg`: Generate SVG (form or JSON body)
- `POST /api/svg-to-video/convert-svg`: Convert SVG to video
- `POST /api/svg-to-video/generate-video`: Generate video from text description
- `GET /api/svg-to-video/task/{task_id}`: Get task status
- `GET /api/svg-to-video/download/{file_id}`: Download generated files

## Development Status

- **SVG Generation**: ✅ Working in development and simple mode
- **3D Conversion**: 🔄 Basic implementation, needs testing
- **Animation System**: 🔄 Basic implementation, needs testing
- **Video Rendering**: 🔄 Basic implementation, needs testing
- **Pipeline Orchestration**: 🔄 Basic implementation, needs enhancement

## Development Workflow

1. Run `.\kill_servers.ps1` to ensure no lingering processes
2. Start the server in the desired mode (Development/Simple/Production)
3. Access the web interface at the provided URL
4. Create SVG diagrams and convert them to videos
5. Check logs for any issues or errors

## Project Structure

```
genai-agent-3d/
├── api/
│   └── routes/
│       └── svg_video_routes.py    # API endpoint definitions
├── cli/
│   └── svg_video_cli.py           # Command-line interface
├── config/
│   └── ports.json                 # Port configuration for services
├── docs/
│   └── svg_to_video/              # Documentation for SVG to Video pipeline
│       ├── svg_generator.md       # SVG Generator documentation
│       ├── svg_to_3d.md           # SVG to 3D Converter documentation
│       ├── animation.md           # Animation System documentation
│       └── rendering.md           # Video Rendering documentation
├── genai_agent/
│   ├── scripts/                   # Blender scripts
│   │   ├── svg_to_3d_blender.py   # SVG to 3D conversion script
│   │   ├── scenex_animation.py    # Animation script
│   │   └── video_renderer.py      # Rendering script
│   └── svg_to_video/              # Core pipeline components
│       ├── llm_integrations/      # LLM providers integration
│       │   ├── claude_direct.py   # Direct Claude API integration
│       │   ├── llm_factory.py     # Factory for LLM providers
│       │   └── __init__.py        # Package initialization
│       ├── svg_generator/         # SVG generation module
│       ├── svg_to_3d/             # SVG to 3D conversion module
│       ├── animation/             # Animation system module
│       ├── rendering/             # Video rendering module
│       ├── pipeline.py            # Pipeline orchestration
│       └── __init__.py            # Package initialization
├── output/                        # Generated files directory
│   ├── svg/                       # Generated SVG files
│   ├── models/                    # 3D model files
│   ├── animations/                # Animation files 
│   └── videos/                    # Rendered videos
├── scripts/                       # Scripts directory
│   ├── setup/                     # Setup scripts
│   ├── run/                       # Run scripts
│   └── test/                      # Test scripts
├── tests/                         # Test suite
│   └── svg_to_video/              # Tests for SVG to Video pipeline
│       ├── svg_generator/         # Tests for SVG Generator
│       ├── svg_to_3d/             # Tests for SVG to 3D Converter
│       ├── animation/             # Tests for Animation System
│       └── rendering/             # Tests for Video Rendering
├── .env.template                  # Environment variables template
└── README.md                      # Main project documentation
```

## Customization

### Animation Types

The pipeline supports different animation types:

- `standard`: General purpose animation sequence
- `flowchart`: Animation optimized for flowcharts with sequential highlighting
- `network`: Animation optimized for network diagrams with pulse effects

### Rendering Quality

The video renderer supports different quality settings:

- `low`: Fast rendering with minimal effects
- `medium`: Balanced quality and performance
- `high`: High quality rendering with advanced effects

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   
   **Symptom**: Error message about address already in use
   
   **Solution**: Run `.\kill_servers.ps1` to free up ports, or check if another application is using the required ports

2. **API Keys Missing**

   **Symptom**: Provider not available or authentication errors
   
   **Solution**: Ensure API keys are correctly set in the `.env` file

3. **Blender Not Found**

   **Symptom**: SVG to 3D conversion fails with "Blender not found" error
   
   **Solution**: Install Blender and set the path in the `.env` file, or add Blender to your system PATH

4. **Frontend Build Issues**

   **Symptom**: Production mode fails to start or shows errors
   
   **Solution**: Check Node.js installation, reinstall dependencies with `npm install` in the frontend directory

### Logs

Check the following locations for logs:

- Terminal window running the backend server
- Browser console for frontend errors
- Application logs in the `logs` directory

## Next Steps

For the next phase of development, focus on:

1. Testing and enhancing the SVG to 3D conversion with Blender
2. Implementing more sophisticated animations based on diagram type
3. Improving the video rendering quality and performance
4. Enhancing the frontend interface with better user feedback

See the individual documentation files for each component for more detailed information.
