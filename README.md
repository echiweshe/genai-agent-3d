# GenAI Agent 3D

A comprehensive 3D content generation system powered by AI for creating models, scenes, diagrams, and animations that can be used in training materials, presentations, and educational content.

## Overview

GenAI Agent 3D combines the power of Large Language Models (LLMs) with Blender and other 3D tools to automate the creation of 3D content. It provides a web-based interface for generating and managing 3D assets, with support for various LLM providers including local options (Ollama) and cloud-based services (OpenAI, Claude).

The system is designed to streamline the process of creating visual content for educational purposes, with a focus on technical topics such as GenAI, Cloud, AWS, Networking, and more.

## Key Features

- **3D Model Generation**: Create 3D models from text descriptions
- **Scene Creation**: Generate complete 3D scenes for visualization
- **Diagram Generation**: Create technical diagrams and visualizations
- **Blender Integration**: Seamless integration with Blender for rendering and animation
- **Multi-LLM Support**: Use Ollama (local), OpenAI, Claude, or Hunyuan3D
- **Web Interface**: Easy-to-use web-based UI for all operations
- **Microservices Architecture**: Scalable and modular design

## Getting Started

### Prerequisites

- Python 3.9+ with pip
- Node.js 16+ with npm
- Redis server
- Blender 4.0+ (with Python support)
- Ollama (optional, for local LLM)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/genai-agent-3d.git
   cd genai-agent-3d
   ```

2. Set up the Python environment:
   ```bash
   cd genai_agent_project
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd web/frontend
   npm install
   ```

4. Configure your API keys:
   ```bash
   # Use the setup script
   python ../../setup_api_keys.py
   
   # Or manually create/edit .env file in genai_agent_project directory
   ```

5. Start the services:
   ```bash
   cd ../..  # Return to genai_agent_project
   python manage_services.py start all
   ```

6. Access the web interface:
   Open your browser and navigate to `http://localhost:3000`

### Configuration

The system can be configured through the `config.yaml` file in the `genai_agent_project` directory. API keys and environment-specific settings should be placed in the `.env` file.

#### API Keys

To use cloud-based LLM providers, you'll need to set up API keys:

- **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/)
- **Claude (Anthropic)**: Get your API key from [Anthropic Console](https://console.anthropic.com/)
- **Hunyuan3D (fal.ai)**: Get your API key from [fal.ai Dashboard](https://fal.ai/dashboard/keys)

Use the `setup_api_keys.py` script to configure these keys, or add them manually to your `.env` file.

#### Blender Configuration

Ensure Blender is correctly installed and the path is specified in your `.env` file:

```
BLENDER_PATH=/path/to/blender/executable
```

## Usage Guide

### LLM Testing

The LLM Tester allows you to experiment with different LLM providers:

1. Navigate to the "LLM Test" page in the web interface
2. Select a provider (Ollama, OpenAI, Claude, Hunyuan3D)
3. Choose a model
4. Enter a prompt and click "Generate"

For best results with 3D content generation:
- Use OpenAI (GPT-4) or Claude for complex 3D descriptions
- Use specific, detailed prompts that describe the 3D object's appearance
- Include material properties, dimensions, and contextual details

### 3D Model Generation

To generate a 3D model:

1. Navigate to the "Models" page
2. Click "Create New Model"
3. Enter a detailed description of the model
4. Select the LLM provider and model to use
5. Click "Generate Model"
6. Once generated, you can view and open the model in Blender

Example prompt for a model:
```
Create a detailed 3D model of a modern desk with a computer, lamp, and coffee mug. The desk should have a sleek design with metal legs and a wooden top. The computer should be a laptop with the screen open. The lamp should be an adjustable desk lamp. The coffee mug should be placed to the right of the laptop.
```

### Scene Generation

To create a complete 3D scene:

1. Navigate to the "Scene Editor" page
2. Click "Create New Scene"
3. Enter a description of the scene, including objects, lighting, and camera
4. Select the LLM provider and model
5. Click "Generate Scene"
6. Once generated, you can preview and open the scene in Blender

Example prompt for a scene:
```
Create a 3D scene of a network operations center with multiple monitors showing network diagrams, servers in racks, and technicians working at workstations. Include appropriate lighting to highlight the technical equipment. Position the camera to show an overview of the entire room from a slightly elevated angle.
```

### Diagram Generation

To create technical diagrams:

1. Navigate to the "Diagrams" page
2. Click "Create New Diagram"
3. Enter a description of the diagram, specifying the technical concept
4. Select the LLM provider (Claude recommended for SVG generation)
5. Click "Generate Diagram"
6. The generated SVG can be viewed, downloaded, or further processed

Example prompt for a diagram:
```
Create a technical diagram showing the AWS architecture for a three-tier web application with a VPC, public and private subnets, an Application Load Balancer, an Auto Scaling Group with EC2 instances, an RDS database, and connections to S3 and CloudFront. Label all components clearly and show the data flow between them.
```

### Blender Scripts

To browse and execute Blender scripts:

1. Navigate to the "Blender Scripts" page
2. Browse the available scripts or generate a new one
3. To generate a new script, enter a description of what the script should do
4. Review the generated script
5. Click "Execute in Blender" to run the script with the configured Blender installation

Example prompt for a Blender script:
```
Create a Python script for Blender that generates a procedural city block with buildings of varying heights, streets, sidewalks, and street lights. The buildings should have simple window textures and the streets should have road markings.
```

## Advanced Features

### PowerPoint Integration (Coming Soon)

Future versions will include features for:
- Converting 3D scenes to PowerPoint slides
- Exporting animations as PowerPoint presentations
- Creating animated slide decks from 3D content

### Animation System - SceneX (Planned)

A powerful animation system based on Manim's coordinate system will enable:
- Precise object placement and camera alignment
- Rich animations (fade in/out, transitions, morphing)
- Advanced API for complex animation sequences

### SVG Processing Workflow (In Development)

The planned SVG workflow will include:
1. Generate SVG diagrams with Claude
2. Process SVGs to extract individual elements
3. Convert elements to 3D models
4. Create animations from the elements
5. Combine with slides for final presentations

## Architecture

GenAI Agent 3D follows a microservices architecture with these main components:

- **Frontend**: React-based web UI
- **Backend API**: FastAPI service
- **LLM Service**: Handles various LLM providers
- **Agent**: Orchestrates tools and workflows
- **Redis Message Bus**: Facilitates communication
- **Tool Registry**: Manages available tools
- **External Integrations**: Blender, Hunyuan3D, etc.

For a detailed architecture overview, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Troubleshooting

### LLM Connection Issues

- **Ollama**: Ensure Ollama is running locally
- **OpenAI/Claude**: Verify API keys and internet connection
- **Hunyuan3D**: Check fal.ai API key and account status

### Output Directory Issues

If generated files aren't appearing in the web interface:
1. Check that the symbolic links are correctly set up
2. Verify file permissions
3. Restart all services: `python manage_services.py restart all`

### Blender Integration Problems

- Verify Blender path in `.env`
- Ensure Blender has necessary permissions
- Check Blender's Python version compatibility

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Blender Foundation for Blender
- The Manim Community for animation concepts
- All contributors and testers
