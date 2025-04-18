# GenAI Agent Examples

This directory contains examples of how to use the GenAI Agent for various 3D modeling, scene generation, and animation tasks.

## Running the Examples

Before running the examples, make sure you:

1. Install the required dependencies by running `pip install -r ../requirements.txt`
2. Have Redis running locally (typically on port 6379)
3. Have Blender installed and correctly configured in `../config.yaml`

## Available Examples

### 1. Create Simple Scene (`create_simple_scene.py`)

Demonstrates how to create a basic 3D scene with a red cube on a blue plane.

```bash
python create_simple_scene.py
```

### 2. SVG to 3D Conversion (`svg_to_3d.py`)

Shows how to convert SVG content to 3D scenes and add animation.

```bash
python svg_to_3d.py
```

## Creating Your Own Examples

To create additional examples:

1. Import the necessary modules:
   ```python
   from genai_agent.agent import GenAIAgent
   from genai_agent.config import load_config
   ```

2. Initialize the agent with configuration:
   ```python
   config = load_config('../config.yaml')
   agent = GenAIAgent(config)
   ```

3. Process instructions:
   ```python
   result = await agent.process_instruction("Your instruction here")
   ```

4. Clean up resources when done:
   ```python
   await agent.cleanup()
   ```

## Direct Tool Usage

Instead of using the agent to process natural language instructions, you can directly use the tools:

```python
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.scene_generator import SceneGeneratorTool

redis_bus = RedisMessageBus(config.get('services', {}).get('redis', {}))
scene_generator = SceneGeneratorTool(redis_bus, config.get('services', {}).get('blender', {}))

result = await scene_generator.execute({
    'description': 'A scene with mountains and trees',
    'style': 'realistic'
})
```

This approach gives you more direct control over the parameters passed to each tool.
