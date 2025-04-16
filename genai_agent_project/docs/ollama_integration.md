# Ollama Integration Guide

This guide explains how to set up and use Ollama with the GenAI Agent for 3D Modeling, Scene Generation, and Animation.

## What is Ollama?

[Ollama](https://ollama.com/) is a lightweight framework for running large language models locally on your computer. It enables you to use powerful AI models without sending data to external APIs, offering both privacy and cost benefits.

## Setting Up Ollama

The GenAI Agent includes built-in tools to help you install, set up, and manage Ollama.

### 1. Installation

To install Ollama:

```bash
python run.py ollama install
```

This will download and install Ollama for your operating system. On Windows, it will be installed to your local AppData folder.

> Note: On Linux or macOS, the script will direct you to the official Ollama website for installation instructions.

### 2. Starting the Ollama Server

Once installed, you can start the Ollama server:

```bash
python run.py ollama start
```

This will launch the Ollama server in the background, making it accessible at `localhost:11434`.

### 3. Installing Models

Ollama can run various language models. The GenAI Agent works well with the Llama 3 models. To download one:

```bash
python run.py ollama pull llama3
```

You can also try other models like:
- `llama3:8b` - Smaller, faster Llama 3 model
- `llama3:70b` - Larger, more capable Llama 3 model (requires more RAM)
- `mistral` - Mistral 7B model
- `gemma:2b` - Lightweight Gemma model
- `deepseek-coder:16b` - Coding-focused model excellent for Blender scripting

### 4. Checking Available Models

To see what models you have installed:

```bash
python run.py ollama list
```

### 5. Testing a Model

To test a model with a sample prompt:

```bash
python run.py ollama test llama3 --prompt "Write a description of a 3D scene with a mountain landscape"
```

## Configuring the GenAI Agent to Use Ollama

The GenAI Agent is pre-configured to use Ollama as its default LLM provider. The configuration is in `config.yaml`:

```yaml
services:
  llm:
    type: local
    provider: ollama
    model: llama3  # Change this to match your installed model
```

### Changing the Model

To use a different model, update the `model` parameter in the config to match the name of an installed model.

## Using Deepseek-Coder for 3D Modeling

The Deepseek-Coder model (especially the 16B variant) is an excellent choice for Blender scripting and 3D modeling tasks. It excels at generating precise Python code with proper Blender API usage.

### Setting Up Deepseek-Coder

1. Pull the model:
   ```bash
   python run.py ollama pull deepseek-coder:16b
   ```

2. Update your configuration in `config.yaml`:
   ```yaml
   services:
     llm:
       type: local
       provider: ollama
       model: deepseek-coder:16b
   ```

3. Test the model:
   ```bash
   python examples/test_deepseek_coder.py
   ```

### Optimizing Prompts for Deepseek-Coder

The GenAI Agent automatically optimizes prompts for Deepseek-Coder, but when calling it directly, consider using prompts that:

- Clearly specify the Blender version if relevant
- Provide context about the desired outcome  
- Ask for comments in the code
- Request specific API usage patterns if needed

Example effective prompt:
```
Generate Blender 3.x Python code to create a procedural mountainous landscape with snow on the peaks.
Include comments explaining the key techniques used. The terrain should have varying heights with
random distribution, and snow should only appear above a certain height threshold.
```

### System Requirements

The deepseek-coder:16b model requires:
- At least a 16GB RAM system (24GB+ recommended)
- 10GB of disk space for the model
- A GPU is helpful but not required

If you experience out-of-memory issues, consider using the smaller variant:  
```bash
python run.py ollama pull deepseek-coder:6.7b
```

And update your config.yaml accordingly:
```yaml
services:
  llm:
    model: deepseek-coder:6.7b
```

## Automatic Ollama Integration

The GenAI Agent will automatically:

1. Check if Ollama is running when it starts
2. Attempt to start Ollama if it's not running
3. Fall back to simulated responses for development if Ollama can't be started

## Using Ollama in Your Code

If you want to interact with Ollama directly in your code:

```python
from genai_agent.services.llm import LLMService

# Initialize LLM service with Ollama configuration
llm_service = LLMService({
    'type': 'local',
    'provider': 'ollama',
    'model': 'llama3'
})

# Generate text
response = await llm_service.generate("Describe a 3D scene with mountains")
print(response)
```

## Troubleshooting

### Ollama Not Starting

If Ollama doesn't start automatically:

1. Check if it's installed: `python run.py ollama check`
2. Try starting it manually: `ollama serve`
3. Check for error messages in the console

### Model Not Found

If you get a "model not found" error:

1. Check available models: `python run.py ollama list`
2. Pull the required model: `python run.py ollama pull <model_name>`
3. Ensure the model name in `config.yaml` matches an installed model

### Performance Issues

If Ollama is running slowly or crashing:

1. Try a smaller model (like `llama3:8b` instead of `llama3`)
2. Close other resource-intensive applications
3. Check your computer meets the minimum requirements (4GB+ RAM for smaller models, 16GB+ for larger models)

## Advanced Configuration

Ollama supports many advanced configuration options through model tags and parameters. For more information, visit the [Ollama documentation](https://github.com/ollama/ollama/blob/main/docs/api.md).
