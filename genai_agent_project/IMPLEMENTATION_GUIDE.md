# GenAI Agent Implementation Guide

This guide provides instructions for implementing and extending the GenAI Agent for 3D Modeling, Scene Generation, and Animation.

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis

Redis is required for the message bus. You can start it using Docker:

```bash
docker run -d -p 6379:6379 redis
```

Or using the provided helper script:

```bash
python run.py redis
```

### 3. Update Blender Path

Edit `config.yaml` to set the correct path to your Blender installation:

```yaml
services:
  blender:
    path: /path/to/blender  # Update this path
```

### 4. Run the Agent

```bash
python main.py
```

## Project Structure

- `genai_agent/`: Main package
  - `core/`: Core components (Task Manager, Context Manager)
  - `services/`: Services (LLM, Redis, Memory)
  - `tools/`: Tools for different tasks (Blender, SceneX, SVG, etc.)
- `examples/`: Example scripts
- `tests/`: Test cases
- `tools/`: Utility tools
- `config.yaml`: Configuration file
- `main.py`: Entry point
- `run.py`: Helper script

## Implementation Tasks

The following components are already implemented:

- Core infrastructure
- Services (Redis, LLM, Memory)
- Basic tools (Blender, SceneX, SVG)
- Agent orchestration

To complete the implementation, focus on these tasks:

### 1. Integrate Your SceneX Code

Use the provided integration tool:

```bash
python tools/integrate_scenex.py --repo /path/to/scenex/repo
```

Then update the `SceneXTool` class to use your integrated code.

### 2. Connect with Hunyuan-3D

If you want to use Hunyuan-3D for model generation:

1. Implement the `HunyuanTool` class in `genai_agent/tools/hunyuan_tool.py`
2. Update the tool to use your local Hunyuan-3D installation
3. Enable the tool in `config.yaml`

### 3. Add Custom Tools

Create additional tools for your specific needs:

1. Create a new tool class in `genai_agent/tools/`
2. Register the tool in the agent
3. Enable the tool in `config.yaml`

### 4. Enhance LLM Integration

The current implementation uses a basic LLM service. If you have specific LLM requirements:

1. Update the `LLMService` class in `genai_agent/services/llm.py`
2. Add support for your preferred model or API
3. Configure the service in `config.yaml`

### 5. Create Custom UI

Consider adding a web-based UI for easier interaction:

1. Create a simple Flask or FastAPI application
2. Add API endpoints for sending instructions and receiving results
3. Implement a basic frontend for visualization

## Extending the System

### Adding Custom Tools

1. Create a new tool class:

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

### Customizing the Task Manager

If you need to change how tasks are planned and executed:

1. Update the `TaskManager` class in `genai_agent/core/task_manager.py`
2. Modify the `plan_execution` method for customized planning
3. Adjust the `execute_plan` method for different execution strategies

### Adding Advanced Features

Consider adding these advanced features:

1. **Feedback Loop**: Add a mechanism for the agent to learn from user feedback
2. **Pipeline Models**: Create execution pipelines for common operations
3. **Asset Management**: Add a system for managing and reusing 3D assets
4. **Render Queue**: Implement a queue for managing render jobs
5. **Version Control**: Add version control for generated scenes and models

## Testing

Run the tests to verify your implementation:

```bash
python -m unittest discover tests
```

Or using the helper script:

```bash
python run.py test
```

## Documentation

As you extend the system, remember to update the documentation:

1. Add docstrings to your classes and methods
2. Update the README.md files
3. Create examples for new features

## Support

If you encounter issues or have questions, please refer to:

1. The README.md files in each directory
2. The docstrings in the code
3. The example scripts

Happy implementing!
