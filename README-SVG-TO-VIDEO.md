# SVG to Video Pipeline

## Overview

The SVG to Video pipeline is a component of the GenAI Agent 3D project that converts text descriptions to SVG diagrams and then to animated 3D videos. The pipeline consists of the following stages:

1. **SVG Generation**: Generate an SVG diagram from a text description using various LLM providers (Claude, OpenAI, Ollama)
2. **3D Conversion**: Convert the SVG elements to 3D objects in Blender
3. **Animation**: Apply animations to the 3D objects using the SceneX framework
4. **Video Rendering**: Render the animated 3D scene to a video file

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

This script will:
1. Create a Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies (if Node.js is available)
4. Create a template `.env` file for API keys

### API Keys

The SVG generator requires API keys for the LLM providers. Edit the `.env` file in the root directory and add your API keys:

```
# API Keys for LLM Providers
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
BLENDER_PATH=path_to_blender_executable  # Optional, if Blender is not in PATH
```

## Usage

### Starting the Development Servers

To start both the backend and frontend development servers:

```bash
run_svg_to_video_dev.bat
```

This will:
1. Start the backend server at http://localhost:8000
2. Start the frontend development server at http://localhost:3000

### Starting the Production Server

To build the frontend and start the production server:

```bash
run_svg_to_video_prod.bat
```

This will:
1. Build the frontend if not already built
2. Start the backend server at http://localhost:8000 serving the built frontend

### Using the CLI

The SVG to Video pipeline can also be used from the command line:

```bash
run_svg_cli.bat svg "A flowchart showing user authentication process" output.svg

run_svg_cli.bat convert input.svg output.mp4

run_svg_cli.bat generate "A network diagram showing cloud infrastructure" output.mp4
```

### Testing the Installation

To verify that all components are working correctly:

```bash
test_svg_pipeline.bat
```

This will test:
1. SVG Generator component
2. Blender installation
3. Pipeline module

### API Endpoints

The backend provides the following API endpoints:

- `GET /api/svg-to-video/providers`: Get a list of available LLM providers
- `POST /api/svg-to-video/generate-svg`: Generate an SVG diagram from a concept
- `POST /api/svg-to-video/convert-svg`: Convert an uploaded SVG file to video
- `POST /api/svg-to-video/generate-video`: Generate a video from a concept description
- `GET /api/svg-to-video/task/{task_id}`: Get the status of a video generation task

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

## Architecture

The SVG to Video pipeline is designed with a modular architecture:

1. **SVG Generator**: Uses LangChain to prompt LLMs to create SVG diagrams
2. **SVG to 3D Converter**: Uses Blender Python API to convert SVG elements to 3D objects
3. **Animation System**: Applies animations to 3D objects based on their type and relationships
4. **Video Renderer**: Renders the animated 3D scene to a video file
5. **Pipeline Orchestrator**: Coordinates the entire process and handles errors

## Project Structure

```
genai-agent-3d/
├── genai_agent/
│   ├── svg_to_video/          # Core pipeline components
│   │   ├── svg_generator.py   # SVG generation with LangChain
│   │   ├── svg_to_3d_converter.py # SVG to 3D conversion
│   │   ├── animation_system.py # Animation system
│   │   ├── video_renderer.py  # Video rendering
│   │   ├── pipeline.py        # Pipeline orchestration
│   │   └── utils.py           # Utility functions
│   └── scripts/               # Blender scripts
│       ├── svg_to_3d_blender.py # SVG to 3D conversion script
│       ├── scenex_animation.py  # Animation script
│       └── video_renderer.py    # Rendering script
├── web/
│   ├── frontend/              # React frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   └── svg_generator/ # SVG Generator component
│   │   │   ├── pages/           # Page components
│   │   │   ├── App.jsx          # Main App component
│   │   │   └── index.js         # Entry point
│   └── backend/               # FastAPI backend
│       ├── main.py            # Main application
│       └── requirements.txt   # Python dependencies
├── api/
│   └── routes/
│       └── svg_video_routes.py # API routes for SVG to Video
├── cli/
│   └── svg_video_cli.py        # Command-line interface
├── venv/                      # Python virtual environment
├── outputs/                   # Generated files
├── setup_svg_to_video.bat     # Setup script
├── run_svg_to_video_dev.bat   # Development start script
├── run_svg_to_video_prod.bat  # Production start script
├── run_svg_cli.bat            # CLI runner script
├── test_svg_pipeline.bat      # Test script
└── .env                       # Environment variables
```

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment, you can create it manually:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r web\backend\requirements.txt
```

### Blender Not Found

Make sure Blender is installed and accessible from the command line. You can specify the path to the Blender executable in the `.env` file:

```
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 3.3\blender.exe
```

### LLM Provider Not Available

Check that you have set the required API keys in the `.env` file. You can use the `list-providers` command to see which providers are available:

```bash
run_svg_cli.bat list-providers
```

### Video Rendering Fails

Check that you have enough disk space and that Blender has sufficient resources to render the video. You can try using the `low` quality setting for faster rendering:

```bash
run_svg_cli.bat generate "concept" output.mp4 --quality low
```

### Frontend Build Issues

If you encounter issues building the frontend, you can try:

```bash
cd web\frontend
npm install --force
npm run build
```
