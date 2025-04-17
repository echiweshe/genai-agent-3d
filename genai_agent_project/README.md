# GenAI Agent - 3D Scene Generation Framework

A framework for AI-driven 3D scene generation, integrating large language models with Blender and other 3D tools.

## Architecture

The system follows a microservices architecture with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Interface Layer                      │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                         Agent Core Layer                         │
└───┬─────────────┬─────────────┬─────────────┬─────────────┬─────┘
    │             │             │             │             │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│  LLM   │     │ Tool   │     │ Scene  │     │ Asset  │     │ Memory │
│Service │     │Registry│     │Manager │     │Manager │     │Service │
└───┬───┘     └───┬───┘     └───┬───┘     └───┬───┘     └───┬───┘
    │             │             │             │             │
┌───▼─────────────▼─────────────▼─────────────▼─────────────▼───┐
│                       Redis Message Bus                        │
└───┬─────────────┬─────────────┬─────────────┬─────────────┬───┘
    │             │             │             │             │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│SceneX  │     │Blender │     │Model  │     │Diagram │     │ SVG    │
│Service │     │Service │     │Service│     │Service │     │Service │
└───────┘     └───────┘     └───────┘     └───────┘     └───────┘
```

## Installation

### Prerequisites

- Python 3.10+
- Redis server (optional, for message bus)
- Blender 4.x installed
- Ollama (for local LLM support)

### Setup

1. Clone the repository:

```
git clone https://github.com/yourusername/genai-agent-3d.git
cd genai-agent-3d
```

2. Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Configure the application by editing `config.yaml` to match your environment.

### Ollama Setup (Local LLMs)

1. Install Ollama from [ollama.ai](https://ollama.ai).
2. Start the Ollama server:

```
python run.py ollama start
```

3. Pull the required models:

```
python run.py ollama pull deepseek-coder
```

## Usage

### Interactive Shell

Start the interactive shell to work with the agent:

```
python run.py shell
```

This will launch a prompt where you can enter instructions, such as:

```
> Create a simple scene with a red cube on a blue plane
```

### Running Scripts

You can run a specific instruction without the interactive shell:

```
python run.py run "Create a scene with a mountain landscape"
```

### Running Examples

To see available examples:

```
python run.py examples
```

To run a specific example:

```
python run.py examples test_deepseek_coder
```

## Core Components

### Agent Core

The central orchestration component that coordinates services and tools. It processes user instructions by:

1. Analyzing the instruction to determine the task
2. Planning the task execution using available tools
3. Executing the plan and coordinating between services

### LLM Service

Provides integration with language models, with support for:

- Local models via Ollama (deepseek-coder, llama3, etc.)
- API-based models (OpenAI, Anthropic)

### Tool Registry

Manages the available tools and their discovery. Current tools include:

- **Blender Script Tool**: Executes Python scripts in Blender
- **Scene Generator Tool**: Creates 3D scenes from descriptions
- **Model Generator Tool**: Generates 3D models from descriptions
- **SVG Processor Tool**: Processes SVG files and converts them to 3D models

### Scene Manager

Manages the creation, modification, and retrieval of 3D scenes. Features include:

- Scene creation and storage
- Object management
- Export to various formats

### Asset Manager

Handles storage, retrieval, and metadata for 3D assets like models, textures, and materials.

### Memory Service

Provides persistent storage for agent memory, including conversation history and scene history.

## Examples

### Creating a Simple Scene

```python
from genai_agent.agent import GenAIAgent
import yaml
import asyncio

async def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
  
    # Initialize agent
    agent = GenAIAgent(config)
  
    # Process instruction
    result = await agent.process_instruction(
        "Create a scene with a red cube on a blue plane"
    )
  
    print(result)
  
    # Close agent
    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Working with Blender

```python
from genai_agent.tools.blender_script import BlenderScriptTool
from genai_agent.services.redis_bus import RedisMessageBus
import asyncio

async def main():
    # Initialize Redis bus
    redis_bus = RedisMessageBus({'host': 'localhost', 'port': 6379})
    await redis_bus.connect()
  
    # Initialize Blender script tool
    blender_tool = BlenderScriptTool(
        redis_bus,
        {'blender_path': 'C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe'}
    )
  
    # Execute Blender script
    result = await blender_tool.execute({
        'script': """
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
        """
    })
  
    print(result)
  
    # Close Redis connection
    await redis_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Ollama Issues

If you encounter issues with Ollama models:

1. Check available models:

```
python run.py ollama list
```

2. If a model is not found, pull it:

```
python run.py ollama pull deepseek-coder
```

3. Check model details:

```
python run.py ollama details deepseek-coder
```

### Blender Issues

Ensure the Blender path in `config.yaml` is correct for your system. On Windows, use double backslashes or forward slashes in the path.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
