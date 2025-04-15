# Getting Started with GenAI Agent

This guide will help you quickly get started with the GenAI Agent for 3D Modeling, Scene Generation, and Animation.

## Prerequisites

- Python 3.8+ installed
- Blender 2.8+ installed 
- Docker (optional, for Redis)
- 8GB+ RAM for running local LLM models

## Quick Start Guide

### 1. Clone/Setup the Repository

Make sure you have the project files in a directory:

```bash
cd genai_agent_project
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and Setup Ollama (for LLM support)

```bash
# Install Ollama
python run.py ollama install

# Start Ollama server
python run.py ollama start

# Download a language model (small model for testing)
python run.py ollama pull llama3:8b
```

Note: If you have a powerful machine, you can try larger models like `llama3` (default) or `llama3:70b` for better quality results.

### 4. Configure Blender Path

Edit `config.yaml` to set the correct path to your Blender installation:

```yaml
services:
  blender:
    path: C:\Path\To\Your\Blender\blender.exe  # Update this
```

### 5. Start Redis for Message Bus

```bash
# Using the helper script (requires Docker)
python run.py redis

# Or if you have Redis installed locally, start it manually
```

### 6. Test the System with a Simple Example

```bash
# Run a simple example
python examples/create_simple_scene.py

# Or try interactive mode
python main.py
```

In interactive mode, try the following instructions:

```
>> Create a simple scene with a red cube on a blue plane
>> Create a mountain landscape with trees
>> Create a scene with a sphere orbiting a cube
```

## Testing Ollama Directly

You can test if your Ollama setup is working correctly by running:

```bash
python run.py ollama test llama3:8b --prompt "Describe a 3D scene with mountains and a lake"
```

This should return a descriptive response about a 3D scene.

## Common Issues

### Ollama Not Starting

If Ollama doesn't start:
- Check if it's installed by running `ollama --version` in your terminal
- Try starting it manually with `ollama serve`
- Make sure no other process is using port 11434

### Redis Connection Issues

If you see Redis connection errors:
- Make sure Docker is running (if using Docker)
- Check if Redis is running with `docker ps | grep redis`
- Try starting Redis manually with `docker run -d -p 6379:6379 redis`

### Blender Not Found

If Blender isn't launching:
- Double-check the path in `config.yaml`
- Make sure you're using the correct path to the Blender executable
- Try running Blender manually to ensure it works

## Next Steps

Once you have the basic system working:

1. Try more complex instructions to test the capabilities
2. Explore the example scripts in the `examples/` directory
3. Customize the `config.yaml` file to adjust behavior
4. Read the [Ollama Integration Guide](ollama_integration.md) for advanced LLM options
5. Consider integrating your existing SceneX code using the provided tools

For more detailed information, refer to the main [README.md](../README.md) and other documentation in the `docs/` directory.
