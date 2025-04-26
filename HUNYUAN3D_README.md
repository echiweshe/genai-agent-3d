# Hunyuan3D Integration for GenAI Agent 3D

This guide explains how to set up and use the Hunyuan3D integration with GenAI Agent 3D.

## Overview

Hunyuan3D is a powerful 3D AI generation model that can be used to generate 3D models, scenes, and animations based on text prompts. The GenAI Agent 3D project supports Hunyuan3D as one of its LLM providers, allowing you to leverage Hunyuan3D's capabilities alongside other models like Claude and GPT.

## Setup Instructions

### 1. Obtain Hunyuan3D API Key

To use Hunyuan3D, you'll need an API key:

1. Visit the Hunyuan3D website and create an account
2. Navigate to the API section of your account dashboard
3. Generate a new API key
4. Copy the API key for the next step

### 2. Set Up Hunyuan3D in GenAI Agent 3D

You can set up Hunyuan3D using the provided script:

```bash
python setup_hunyuan3d.py
```

This script will:
- Configure your Hunyuan3D API key
- Set up the integration directory structure
- Provide further setup instructions

Alternatively, you can manually:

1. Edit the `.env` file in the `genai_agent_project` directory
2. Add your API key: `HUNYUAN3D_API_KEY=your_api_key_here`
3. Create an `integrations/hunyuan3d` directory if it doesn't exist

### 3. Test Your Hunyuan3D API Key

You can verify your API key is working correctly by running:

```bash
python test_api_keys.py
```

This will test all configured API keys, including Hunyuan3D.

## Using Hunyuan3D in GenAI Agent 3D

Once configured, you can use Hunyuan3D as an LLM provider in the following ways:

### Web Interface

1. Open the GenAI Agent 3D web interface (http://localhost:3000)
2. Go to Settings > LLM Settings
3. Select "Hunyuan3D" as the provider
4. Choose your preferred model (e.g., "hunyuan-3d-base" or "hunyuan-3d-pro")
5. Apply settings

### API

You can also specify Hunyuan3D when making API requests:

```json
{
  "instruction": "Your instruction here",
  "provider": "hunyuan3d",
  "model": "hunyuan-3d-base",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

## Troubleshooting

### API Key Issues

If you experience issues with your Hunyuan3D API key:

1. Verify the key is correct and active in your Hunyuan3D dashboard
2. Run `python test_api_keys.py` to check for specific errors
3. Check application logs for detailed error messages
4. Ensure the key is properly formatted in the .env file

### Integration Issues

If the Hunyuan3D integration isn't working:

1. Make sure you've restarted all services after configuration:
   ```bash
   python genai_agent_project/manage_services.py restart all
   ```
2. Check that the integration directory exists at `genai_agent_project/integrations/hunyuan3d`
3. Verify that the `HUNYUAN3D_PATH` is correctly set in your `.env` file

## Additional Resources

- [Hunyuan3D API Documentation](https://docs.hunyuan3d.ai/)
- [GenAI Agent 3D Documentation](https://github.com/your-organization/genai-agent-3d)
