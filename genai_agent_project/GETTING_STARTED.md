# Getting Started with GenAI Agent

This guide will help you get up and running with the GenAI Agent for 3D scene generation.

## Quick Start

### 1. Install Dependencies

First, make sure you have all the required dependencies installed:

```bash
pip install -r requirements.txt
```

### 2. Set Up Ollama

Install Ollama from [ollama.ai](https://ollama.ai) for local LLM support.

Start the Ollama server:

```bash
python run.py ollama start
```

Pull the required models:

```bash
python run.py ollama pull deepseek-coder
```

### 3. Configure Blender Path

Edit `config.yaml` to set the correct path to your Blender installation:

```yaml
blender:
  path: C:\Program Files\Blender Foundation\Blender 4.2\blender.exe  # Adjust this path
```

### 4. Start the Interactive Shell

```bash
python run.py shell
```

### 5. Try These Example Instructions

```
> Create a scene with a red cube on a blue plane
```

```
> Generate a 3D model of a mountain landscape with snow
```

```
> Create a scene with three buildings and a road
```

## Running Examples

The project includes several examples to help you understand how to use different components:

```bash
# List available examples
python run.py examples

# Run a specific example
python run.py examples test_scene_generation
```

## Architecture Overview

The GenAI Agent is built on a modular, service-oriented architecture:

1. **Agent Core** - Coordinates all activities and processes user instructions
2. **LLM Service** - Handles communication with language models
3. **Tool Registry** - Manages the available tools
4. **Redis Message Bus** - Provides communication between services
5. **Scene Manager** - Manages 3D scenes
6. **Asset Manager** - Manages 3D assets and resources
7. **Memory Service** - Provides persistent storage for agent memory

## Customizing the Agent

### Adding a New Tool

To add a new tool, create a new tool class that inherits from `Tool`:

```python
from genai_agent.tools.registry import Tool

class MyNewTool(Tool):
    def __init__(self, redis_bus, config):
        super().__init__(
            name="my_new_tool",
            description="Description of what my tool does"
        )
        self.redis_bus = redis_bus
        self.config = config
    
    async def execute(self, parameters):
        # Tool implementation goes here
        return {"status": "success", "message": "Tool executed successfully"}
```

Then add it to the configuration in `config.yaml`:

```yaml
tools:
  my_new_tool:
    module: genai_agent.tools.my_new_tool
    class: MyNewTool
    config:
      # Tool-specific configuration
```

### Using a Different LLM

To use a different LLM, update the `llm` section in `config.yaml`:

```yaml
llm:
  type: local
  provider: ollama
  model: llama3  # Change to your preferred model
```

For API-based models:

```yaml
llm:
  type: api
  provider: openai
  model: gpt-4
  api_key: your_api_key_here
```

## Common Operations

### Generate a 3D Scene

```python
from genai_agent.agent import GenAIAgent
import yaml
import asyncio
import json

async def generate_scene():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize agent
    agent = GenAIAgent(config)
    
    # Process instruction
    result = await agent.process_instruction(
        "Create a scene with a mountain and a lake"
    )
    
    # Print the result
    print(json.dumps(result, indent=2))
    
    # Close agent
    await agent.close()

if __name__ == "__main__":
    asyncio.run(generate_scene())
```

### Create a 3D Model

```python
from genai_agent.tools.model_generator import ModelGeneratorTool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.llm import LLMService
import asyncio
import json

async def generate_model():
    # Initialize Redis bus
    redis_bus = RedisMessageBus({'host': 'localhost', 'port': 6379})
    await redis_bus.connect()
    
    # Create model generator tool
    model_gen_tool = ModelGeneratorTool(redis_bus, {})
    
    # Create LLM service for the tool to use
    llm_service = LLMService({
        'type': 'local',
        'provider': 'ollama',
        'model': 'deepseek-coder'
    })
    
    # Manually set the LLM service
    model_gen_tool.llm_service = llm_service
    
    # Generate model
    result = await model_gen_tool.execute({
        'description': 'A procedural pine tree with detailed bark and needles',
        'model_type': 'mesh',
        'style': 'realistic',
        'name': 'PineTree'
    })
    
    # Print the result
    print(json.dumps(result, indent=2))
    
    # Close Redis connection
    await redis_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(generate_model())
```

## Troubleshooting

### Redis Connection Issues

If you encounter Redis connection issues:

1. Make sure Redis server is running:
   - Windows: Start Redis server manually or via Windows Service
   - Linux/Mac: `redis-server`

2. Update Redis configuration in `config.yaml`:
   ```yaml
   redis:
     host: localhost
     port: 6379
     password: null  # Set if your Redis server requires authentication
     db: 0
   ```

3. Test Redis connection:
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   print(r.ping())  # Should return True
   ```

### Ollama Issues

If you have issues with Ollama:

1. Check if Ollama is running:
   ```bash
   python run.py ollama list
   ```

2. Make sure you have the required models:
   ```bash
   python run.py ollama pull deepseek-coder
   ```

3. Check model details:
   ```bash
   python run.py ollama details deepseek-coder
   ```

4. If the model name doesn't match, update it in `config.yaml`.

### Blender Issues

1. Verify Blender installation path in `config.yaml`.

2. Test Blender execution manually:
   ```bash
   "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --version
   ```

3. Check if Blender can run Python scripts:
   ```bash
   "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python-expr "import bpy; print('Blender Python works!')"
   ```

## Advanced Usage

### Working with SVG Files

```python
from genai_agent.tools.svg_processor import SVGProcessorTool
from genai_agent.services.redis_bus import RedisMessageBus
import asyncio
import json

async def process_svg():
    # Initialize Redis bus
    redis_bus = RedisMessageBus({'host': 'localhost', 'port': 6379})
    await redis_bus.connect()
    
    # Create SVG processor tool
    svg_tool = SVGProcessorTool(redis_bus, {})
    
    # SVG content (simple circle)
    svg_content = """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="red" />
    </svg>"""
    
    # Process SVG
    result = await svg_tool.execute({
        'svg_content': svg_content,
        'operation': 'analyze',
        'name': 'SimpleCircle'
    })
    
    # Print the result
    print(json.dumps(result, indent=2))
    
    # Close Redis connection
    await redis_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(process_svg())
```

### Managing Assets

```python
from genai_agent.services.asset_manager import AssetManager
from genai_agent.services.redis_bus import RedisMessageBus
import asyncio
import json
import os

async def manage_assets():
    # Initialize Redis bus
    redis_bus = RedisMessageBus({'host': 'localhost', 'port': 6379})
    await redis_bus.connect()
    
    # Create asset manager
    asset_manager = AssetManager(redis_bus, {})
    
    # Create a simple test file
    test_file = "test_asset.txt"
    with open(test_file, "w") as f:
        f.write("This is a test asset")
    
    # Store asset
    asset_id = await asset_manager.store_asset(
        test_file,
        {"description": "Simple test asset"}
    )
    
    # Get asset metadata
    metadata = await asset_manager.get_asset_metadata(asset_id)
    print("Asset metadata:", json.dumps(metadata, indent=2))
    
    # List all assets
    assets = await asset_manager.list_assets()
    print(f"Found {len(assets)} assets")
    
    # Clean up test file
    os.remove(test_file)
    
    # Close Redis connection
    await redis_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(manage_assets())
```

## Best Practices

1. **Work with Complex Instructions**:
   Break complex instructions into simpler tasks using the agent's planning capabilities.

2. **Handling Large Scenes**:
   For large scenes, create it in parts and then combine them.

3. **Script Organization**:
   Keep Blender scripts modular and organized for better maintenance.

4. **Memory Management**:
   Use the Memory Service for persistent data that needs to be accessed across sessions.

5. **Error Handling**:
   Always check the status of tool execution results and handle errors appropriately.

## Next Steps

As you get more familiar with the GenAI Agent, consider the following advanced topics:

1. Creating custom tools for specific 3D modeling tasks
2. Integrating with other 3D software beyond Blender
3. Extending the agent with machine learning capabilities for better scene understanding
4. Contributing to the project by adding new features or fixing bugs

For more details, refer to the full documentation in the `docs` directory.
