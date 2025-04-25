# LLM Integration for GenAI Agent 3D

This documentation covers how to use the Language Model (LLM) features in GenAI Agent 3D.

## Overview

GenAI Agent 3D now includes integration with Large Language Models (LLMs) to enhance the 3D model generation process. This integration allows you to:

1. Generate text descriptions and prompts for 3D models
2. Create 3D modeling instructions for Blender
3. Get creative ideas for 3D scenes
4. Enhance model descriptions and metadata

## Getting Started

### Requirements

- **Ollama**: The default LLM provider is Ollama, which runs models locally on your computer.
  - Download and install from [https://ollama.ai/](https://ollama.ai/)
  - Pull a model using `ollama pull llama3.2:latest` or another model of your choice

### Configuration

LLM settings can be configured in two ways:

1. **Via the Settings Page**: Navigate to the Settings page in the web interface to configure the LLM provider and model.

2. **Via Configuration File**: Edit the `config/llm.yaml` file in the project directory.

Example configuration:

```yaml
# LLM Type: local or cloud
type: local

# Provider: ollama, anthropic, openai, etc.
provider: ollama

# Default model to use
model: llama3.2:latest

# Generation parameters
parameters:
  temperature: 0.7
  max_tokens: 2048
```

## Using the LLM Test Page

The LLM Test page allows you to directly interact with the configured language model:

1. Navigate to the "LLM Test" page from the sidebar
2. Select the provider and model from the dropdown menus
3. Enter a prompt in the text area
4. Click "Generate" to get a response from the LLM

Example prompts to try:

- "Create a description for a mountain landscape model"
- "Generate instructions for modeling a science fiction spaceship in Blender"
- "Describe a fantasy castle scene with detailed architectural elements"

## API Endpoints

For developers wanting to integrate with the LLM capabilities programmatically:

### Get Available Providers

- **Endpoint**: `/api/llm/providers`
- **Method**: GET
- **Response**: List of available LLM providers and their models

Example response:
```json
[
  {
    "name": "Ollama",
    "is_local": true,
    "models": [
      {"id": "llama3.2:latest", "name": "Llama 3.2"},
      {"id": "llama3:latest", "name": "Llama 3"}
    ]
  }
]
```

### Generate Text

- **Endpoint**: `/api/llm/generate`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "prompt": "Create a 3D model description for a futuristic city",
    "provider": "ollama",
    "model": "llama3.2:latest",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 2048
    }
  }
  ```
- **Response**: Generated text from the LLM
  ```json
  {
    "text": "The futuristic city features sleek, aerodynamic buildings..."
  }
  ```

## Integrating with 3D Tools

The LLM integration works with the various 3D creation tools in GenAI Agent 3D:

### Model Generator

When using the Model Generator, you can leverage the LLM to:
- Enhance model descriptions
- Generate creative variations of your model ideas
- Create detailed specification documents

### Scene Generator

In the Scene Generator, the LLM can help with:
- Creating rich scene descriptions
- Suggesting scene elements and their arrangements
- Generating atmospheric details and lighting concepts

### Blender Script Generator

When working with Blender scripts, the LLM can:
- Generate Python code for Blender
- Create procedural modeling scripts based on text descriptions
- Help troubleshoot and optimize existing Blender scripts

## Troubleshooting

**Issue**: Cannot connect to Ollama
- Ensure Ollama is running (`ollama serve`)
- Check that the API is accessible at `http://127.0.0.1:11434`

**Issue**: Model not found
- Make sure you've pulled the model with `ollama pull [model-name]`
- Verify the model name matches exactly in the configuration

**Issue**: Slow response times
- For local models, response time depends on your hardware
- Consider using a smaller or more optimized model for faster responses

## Extending with Cloud Providers

While the default setup uses Ollama for local inference, the system is designed to work with cloud providers as well. To configure cloud providers like OpenAI or Anthropic:

1. Edit the `config/llm.yaml` file
2. Update the `provider` field
3. Add your API key in the provider-specific section
4. Restart the application

Example cloud configuration:
```yaml
type: cloud
provider: anthropic
model: claude-3-opus-20240229

providers:
  anthropic:
    api_key: your-api-key-here
```

---

For more information and advanced usage, please refer to the full documentation or contact support.
