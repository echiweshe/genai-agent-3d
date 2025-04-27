# Hunyuan3D Integration Guide

## Overview

Hunyuan3D is a powerful 3D model generation system developed by Tencent. In the GenAI Agent 3D project, we integrate with Hunyuan3D through the fal.ai API platform, which provides access to the model.

## Getting a Hunyuan3D API Key

To use Hunyuan3D models via fal.ai, you need to obtain an API key:

1. Visit [fal.ai](https://www.fal.ai/)
2. Create an account or sign in
3. Navigate to the API Keys section in your dashboard
4. Create a new API key
5. Copy the key (it will typically start with `key-`)

## Setting Up Your API Key

After obtaining your fal.ai API key, you can add it to your project:

1. Run the setup script:
   ```bash
   python fix_hunyuan3d_integration.py
   ```
   
   Or:
   
2. Manually edit the `.env` file in the `genai_agent_project` directory:
   ```
   HUNYUAN3D_API_KEY=your_falai_key_here
   ```

## Available Models

The following Hunyuan3D models are available through fal.ai:

- **fal-ai/hunyuan3d/multi-view** - Base model for multi-view 3D generation
- **fal-ai/hunyuan3d/multi-view-hd** - High-definition multi-view 3D generation

## Usage

To generate 3D content with Hunyuan3D:

1. Select "Hunyuan3D" as the provider in the LLM Test interface
2. Choose a model from the dropdown
3. Enter a detailed prompt describing the 3D model you want to create
4. Set any additional parameters (optional)
5. Submit the request

## Parameters

You can customize the generation with the following parameters:

- **negative_prompt**: What the model should avoid generating
- **num_inference_steps**: Higher values (20-50) give better quality but take longer
- **guidance_scale**: How closely to follow the prompt (5-15)
- **width/height**: Output dimensions (default: 1024x1024)
- **seed**: Set a specific seed for reproducible results

## Response Format

The Hunyuan3D API will return:

1. Links to generated images showing the model from different angles
2. A link to download the 3D mesh file
3. Additional metadata about the generation

## API Usage and Costs

Using Hunyuan3D via fal.ai incurs costs based on your usage:

- Each generation typically costs between $0.25 and $0.50
- Higher resolution and more inference steps increase cost
- Check the [fal.ai pricing page](https://www.fal.ai/pricing) for current rates

Monitor your usage through the fal.ai dashboard to avoid unexpected charges.

## Troubleshooting

If you encounter issues with Hunyuan3D generation:

1. **API Key Issues**:
   - Ensure your API key is correct in the `.env` file
   - Check that you have sufficient credits in your fal.ai account

2. **Generation Issues**:
   - Try more specific and detailed prompts
   - Adjust parameters like guidance_scale and inference steps
   - Use negative prompts to avoid unwanted elements

3. **Connection Issues**:
   - Verify internet connectivity
   - Check if fal.ai services are operational

For additional help, refer to the [fal.ai documentation](https://docs.fal.ai/models/hunyuan3d) or open an issue in the project repository.
