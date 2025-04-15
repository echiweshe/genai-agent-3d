# GenAI Agent for 3D Modeling, Scene Generation, and Animation

This project implements a modular AI agent architecture for 3D modeling, scene generation, and animation using Blender. It integrates various tools including SceneX, SVG processing, and more into a unified system controlled through natural language instructions, powered by local LLMs via Ollama.

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
│SceneX  │     │Blender │     │Ollama  │     │Diagram │     │ SVG    │
│Service │     │Service │     │Service │     │Service │     │Service │
└───────┘     └───────┘     └───────┘     └───────┘     └───────┘
```

## LLM Integration with Ollama

The GenAI Agent uses Ollama for local LLM support, which provides several advantages:

- **Privacy**: All processing happens locally on your machine
- **No API costs**: No need for subscription to cloud LLM services
- **Offline operation**: Works without internet connection once models are downloaded

### Using the LLM Service

The LLM Service is automatically configured to use Ollama as its local provider. You can adjust settings in the `config.yaml` file:

```yaml
services:
  llm:
    type: local
    provider: ollama
    model: llama3  # Change to your preferred model
```

You can test the LLM directly from the command line:

```bash
python run.py ollama test llama3 --prompt "Generate a description for a mountain landscape scene"
```

For more details on Ollama integration, see the [Ollama Integration Guide](docs/ollama_integration.md).

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Install and set up Ollama (optional but recommended):

```bash
# Install Ollama
python run.py ollama install

# Start Ollama server
python run.py ollama start

# Download a language model
python run.py ollama pull llama3
```

For more details, see the [Ollama Integration Guide](docs/ollama_integration.md).

3. Make sure you have Blender installed and update the path in `config.yaml`.

4. Start Redis (required for the message bus):

```bash
# Using the helper script
python run.py redis

# Or using Docker directly
docker run -d -p 6379:6379 redis
```

## Usage

### Command Line Mode

Process a single instruction:

```bash
python main.py --instruction "Create a scene with a red cube on a plane"
```

### Interactive Mode

Start an interactive session:

```bash
python main.py
```

Then type instructions at the prompt:

```
>> Create a scene with a blue sphere and a green cube
>> Animate the sphere rotating around the cube
>> exit
```

## Project Structure

- `genai_agent/`: Main package
  - `core/`: Core components (Task Manager, Context Manager)
  - `services/`: Services (LLM, Redis, Memory)
  - `tools/`: Tools for different tasks (Blender, SceneX, SVG, etc.)
- `config.yaml`: Configuration file
- `main.py`: Entry point

## Extending the System

### Adding Custom Tools

1. Create a new tool class in `genai_agent/tools/`:

```python
from genai_agent.tools.registry import Tool

class MyCustomTool(Tool):
    def __init__(self, redis_bus, config):
        super().__init__(name="my_custom_tool", description="Description of what it does")
        self.redis_bus = redis_bus
        self.config = config
        
    async def execute(self, parameters):
        # Implement your tool functionality
        return {"status": "success", "result": "Tool executed"}
```

2. Enable the tool in `config.yaml`:

```yaml
tools:
  enabled:
    - blender_script
    - scene_generator
    - my_custom_tool
```

## Integrating with SceneX

The SceneXTool provides a simplified implementation that mimics your existing SceneX functionality. To fully integrate your SceneX code:

1. Update the `_generate_scenex_script` method in `genai_agent/tools/scenex_tool.py`
2. Import your existing SceneX libraries
3. Adapt the SceneX coordinate system to work with the Blender environment

## License

This project is licensed under the MIT License.
