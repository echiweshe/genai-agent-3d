# SVG to Video Pipeline

## Overview

The SVG to Video pipeline is a component of the GenAI Agent 3D project that converts text descriptions to SVG diagrams and then to animated 3D videos. This component uses AI-powered SVG generation through direct Claude API integration, providing faster and more reliable results compared to the previous LangChain implementation.

## Features

- **Direct Claude API Integration**: Generates high-quality SVG diagrams directly through Anthropic's Claude API
- **Multiple LLM Provider Support**: Compatible with Claude, OpenAI, and other LLM providers
- **SVG to 3D Conversion**: Transforms SVG elements into 3D objects in Blender
- **Animation System**: Applies professional animations based on diagram type
- **Video Rendering**: Creates high-quality animated videos with customizable settings
- **User-friendly Web Interface**: Simple interface for creating diagrams and videos
- **API Endpoints**: Comprehensive REST API for integration with other systems
- **CLI Support**: Command-line interface for batch processing and automation

## Architecture

The SVG to Video pipeline follows a modular architecture with the following components:

1. **SVG Generation**: Uses direct API integration with Claude to create detailed SVG diagrams
2. **SVG to 3D Conversion**: Leverages Blender's Python API to transform SVG elements into 3D objects
3. **Animation System**: Applies animations based on the type of diagram (flowchart, network diagram, etc.)
4. **Video Rendering**: Renders the animated 3D scene into a video file
5. **Pipeline Orchestration**: Coordinates the entire process and handles error recovery

## Installation

### Prerequisites

- Python 3.9+
- Blender 3.0+ (with command-line access)
- Node.js 14+ (for the frontend)
- Anthropic API key (for Claude)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/genai-agent-3d.git
   cd genai-agent-3d
   ```

2. Run the setup script:
   ```bash
   setup_svg_to_video.bat  # Windows
   # OR
   ./setup_svg_to_video.ps1  # PowerShell
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   OPENAI_API_KEY=your_openai_api_key
   BLENDER_PATH=path_to_blender_executable  # Optional, if not in PATH
   ```

## Usage

### Development Mode

To start the development servers:

```bash
run_svg_to_video_dev.ps1
```

This will:
- Start the backend server on port 8001
- Start the frontend development server on port 3001

### Production Mode

To run in production mode:

```bash
run_svg_to_video_prod.ps1
```

This will:
- Build the frontend
- Start the backend server serving the built frontend

### Simple Mode

For a simplified development setup:

```bash
run_simple_dev.ps1
```

### Command Line Interface

The SVG to Video pipeline can also be used from the command line:

```bash
# List available providers
run_svg_cli.bat list-providers

# Generate an SVG diagram
run_svg_cli.bat svg "A flowchart showing user authentication process" output.svg

# Convert an existing SVG to video
run_svg_cli.bat convert input.svg output.mp4

# Generate a video directly from a concept
run_svg_cli.bat generate "A network diagram showing cloud infrastructure" output.mp4
```

## API Endpoints

The backend provides the following API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check endpoint |
| `/api/svg-to-video/providers` | GET | Get a list of available LLM providers |
| `/api/svg-to-video/generate-svg` | GET/POST | Generate an SVG diagram from a concept |
| `/api/svg-to-video/convert-svg` | POST | Convert an uploaded SVG file to video |
| `/api/svg-to-video/task/{task_id}` | GET | Get the status of a video generation task |

## Configuration

The SVG to Video pipeline uses the following configuration files:

- `config/ports.json`: Defines port assignments for different services
- `.env`: Contains API keys and environment-specific settings

## Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| Main Backend | 8000 | The primary backend API server |
| SVG to Video Backend | 8001 | Backend for the SVG to Video pipeline |
| Web Backend | 8002 | Backend for the web interface |
| Web Frontend | 3000 | Frontend for the main web interface |
| SVG to Video Frontend | 3001 | Frontend for the SVG to Video pipeline |

This port configuration ensures that multiple services can run simultaneously without conflicts.

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure your `.env` file contains valid API keys
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

2. **Blender Not Found**: Either add Blender to your PATH or specify the path in your `.env` file
   ```
   BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 3.3\blender.exe
   ```

3. **Port Conflicts**: If you encounter port conflicts, run the `kill_servers.ps1` script to free up ports

4. **SVG Generation Fails**: Check the logs for API errors. The most common cause is an invalid or expired API key

### Logs

Log files are located in the `logs` directory. Check these logs for detailed error information.

## Development Notes

### Architecture Overview

The direct Claude integration provides several advantages over the previous LangChain approach:

1. **Simplified Architecture**: Eliminates unnecessary abstraction layers
2. **Lower Latency**: Direct API calls reduce response time
3. **Better Error Handling**: More specific error messages from the API
4. **Reduced Dependencies**: Fewer external libraries required

### Future Enhancements

- Advanced animation presets for specific diagram types
- Support for additional 3D engines beyond Blender
- Integration with more LLM providers
- Real-time collaborative editing of diagrams

## Contributors

This component was developed by the GenAI Agent 3D team.

## License

[Your License Information]
