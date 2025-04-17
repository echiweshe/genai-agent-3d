# External Tool Integrations

This document provides information about the external tools that can be integrated with GenAI Agent 3D, how to set them up, and how to use them.

## Overview

GenAI Agent 3D can integrate with several powerful open-source tools to enhance its capabilities:

1. **BlenderGPT**: Natural language interface for Blender 3D
2. **Hunyuan-3D**: High-quality text-to-3D model generation
3. **TRELLIS**: Advanced reasoning and planning framework
4. **Ollama**: Local large language model execution (included by default)

These integrations are optional and require separate installation of the respective tools. GenAI Agent 3D provides adapter interfaces and configuration utilities to make the integration process as seamless as possible.

## Installation Requirements

### BlenderGPT

- GitHub Repository: [https://github.com/gd3kr/BlenderGPT](https://github.com/gd3kr/BlenderGPT)
- Requirements:
  - Blender 4.x installed
  - OpenAI API key or compatible API (for using GPT models)
  - Python dependencies as specified in BlenderGPT's requirements

### Hunyuan-3D

- GitHub Repository: [https://github.com/Tencent/Hunyuan3D-2](https://github.com/Tencent/Hunyuan3D-2)
- Requirements:
  - CUDA-compatible GPU (recommended)
  - PyTorch with CUDA support
  - Python dependencies as specified in Hunyuan-3D's requirements

### TRELLIS

- GitHub Repository: [https://github.com/microsoft/TRELLIS](https://github.com/microsoft/TRELLIS)
- Requirements:
  - Python 3.10+ 
  - API key for language models (if using API-based models)
  - Python dependencies as specified in TRELLIS's requirements

## Setting Up Integrations

GenAI Agent 3D provides a setup utility to help you configure the integrations. 

### Using the Setup Utility

```bash
# Set up BlenderGPT integration
python setup_integrations.py blendergpt --blendergpt-path "C:/path/to/BlenderGPT" --blender-path "C:/Program Files/Blender Foundation/Blender 4.2/blender.exe" --api-key "your-api-key"

# Set up Hunyuan-3D integration
python setup_integrations.py hunyuan3d --hunyuan-path "C:/path/to/Hunyuan3D-2" --use-gpu

# Set up TRELLIS integration
python setup_integrations.py trellis --trellis-path "C:/path/to/TRELLIS" --api-key "your-api-key"
```

### Manual Configuration

You can also manually edit the `config.yaml` file to configure the integrations:

1. Set `enabled: true` for the integration in both the `integrations` and `tools` sections
2. Provide the correct paths and configuration parameters
3. Make sure the dependencies are installed and accessible

## Using the Integrations

Once set up, you can use the integrations through their respective tools:

### BlenderGPT Tool

```python
from genai_agent.tools.blender_gpt_tool import BlenderGPTTool

# Initialize the tool
blendergpt_tool = BlenderGPTTool(redis_bus, config)

# Generate a Blender script from natural language
result = await blendergpt_tool.execute({
    'operation': 'generate_script',
    'prompt': 'Create a realistic landscape with mountains and a lake',
    'execute': True  # Actually execute the script
})
```

### Hunyuan-3D Tool

```python
from genai_agent.tools.hunyuan_3d_tool import Hunyuan3DTool

# Initialize the tool
hunyuan_tool = Hunyuan3DTool(redis_bus, config)

# Generate a 3D model from text
result = await hunyuan_tool.execute({
    'operation': 'generate_model',
    'prompt': 'A modern chair with a sleek design',
    'format': 'obj',
    'name': 'modern_chair'
})
```

### TRELLIS Tool

```python
from genai_agent.tools.trellis_tool import TrellisTool

# Initialize the tool
trellis_tool = TrellisTool(redis_bus, config)

# Perform spatial reasoning
result = await trellis_tool.spatial_reasoning({
    'scene_description': 'A room with a table in the center. On the table, there is a red cube to the left of a blue sphere.',
    'question': 'What is the relationship between the cube and the sphere?'
})
```

## Example

We have included a comprehensive example script in `examples/integrations_example.py` that demonstrates how to use all of the integrations:

```bash
# Run all examples
python examples/integrations_example.py

# Run specific integration examples
python examples/integrations_example.py --blendergpt
python examples/integrations_example.py --hunyuan
python examples/integrations_example.py --trellis
```

## Fallback Mechanisms

GenAI Agent 3D is designed to work gracefully even if the external integrations are not available:

1. Each tool checks for the availability of its integration and will report errors if it's not available
2. The core functionality of GenAI Agent 3D works independently of these integrations
3. When using the agent, it will automatically choose appropriate tools based on what's available

## Troubleshooting

### Common Issues

1. **Integration not found**: Make sure the path provided in the configuration is correct and the tool is properly installed
2. **API key issues**: Check that you've provided a valid API key for services that require it
3. **GPU not available**: If you're using Hunyuan-3D with `use_gpu: true`, make sure CUDA is available
4. **Import errors**: Ensure that all dependencies for the external tools are installed

### Checking Integration Status

You can check the status of the integrations by running:

```python
# Check BlenderGPT status
from genai_agent.integrations.blender_gpt import BlenderGPTIntegration
integration = BlenderGPTIntegration(config)
print(integration.get_status())

# Similarly for other integrations
```

## Advanced Configuration

For advanced configuration options, please refer to the documentation of the respective external tools:

- [BlenderGPT Documentation](https://github.com/gd3kr/BlenderGPT)
- [Hunyuan-3D Documentation](https://github.com/Tencent/Hunyuan3D-2)
- [TRELLIS Documentation](https://github.com/microsoft/TRELLIS)
