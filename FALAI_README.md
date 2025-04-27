# fal.ai Hunyuan3D Integration Guide

This guide explains how to integrate fal.ai's Hunyuan3D models with GenAI Agent 3D.

## About Hunyuan3D on fal.ai

Hunyuan3D is a powerful 3D generation model available through fal.ai's platform. It can generate 3D assets from text prompts, which can be imported into Blender and other 3D tools.

Website: [fal.ai/models/fal-ai/hunyuan3d](https://fal.ai/models/fal-ai/hunyuan3d/v2/multi-view/api)

## Setting Up Your fal.ai API Key

### Option 1: Use the Setup Script (Recommended)

Run the setup script:

```bash
# On Windows
setup_falai_key.bat

# OR on any platform
python setup_falai_key.py
```

This will:
1. Guide you through getting a fal.ai API key
2. Save the key to your environment configuration
3. Offer to restart services to apply the changes

### Option 2: Manual Setup

1. Get an API key from [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)
2. Open `genai_agent_project/.env`
3. Add the line: `HUNYUAN3D_API_KEY=your_fal_ai_key_here`
4. Save the file
5. Restart services: `python genai_agent_project/manage_services.py restart all`

## Using Hunyuan3D in GenAI Agent 3D

Once you've set up your API key, you can use Hunyuan3D in the LLM Tester:

1. From the LLM Tester tab, select "Hunyuan3D" as the provider
2. Choose a model:
   - "Hunyuan-3D Base" (standard quality)
   - "Hunyuan-3D HD" (higher quality)
3. Enter a prompt describing the 3D model you want to generate
   - Example: "A detailed 3D model of a futuristic spaceship"
4. Click "Generate"

The response will include links to:
- Generated images (previews of the 3D model)
- The 3D model file (typically in GLB format)
- Mesh URL for direct download

## Advanced Parameters

You can use advanced parameters for Hunyuan3D by editing the default parameters:

- `negative_prompt`: Things you don't want in the generated model
- `num_inference_steps`: Number of steps for generation (higher = more detail, but slower)
- `guidance_scale`: How closely to follow the prompt (higher = more literal)
- `width` and `height`: Resolution of generated images
- `seed`: For reproducible results

## Importing Generated 3D Models to Blender

To use the generated 3D models in Blender:

1. Copy the "Mesh URL" link from the Hunyuan3D response
2. In Blender, go to File > Import > glTF 2.0 (.glb/.gltf)
3. Paste the URL in the file browser or download the file first and then import it

## Troubleshooting

If you encounter issues with Hunyuan3D:

- **"API key not found" error**: Run `setup_falai_key.py` to set up your key
- **Request timeouts**: 3D generation can take time, especially for HD models
- **Quality issues**: Try adjusting the prompt or using negative prompts
- **Authentication errors**: Your key might be invalid; generate a new one

## Limitations

- The free tier of fal.ai may have usage limits
- Generation can take 30-60 seconds or more, especially for complex models
- Quality varies based on the prompt and parameters

## Further Resources

- [fal.ai Hunyuan3D Documentation](https://fal.ai/models/fal-ai/hunyuan3d/v2/multi-view/api)
- [Prompt Engineering for 3D Models](https://fal.ai/blog/hunyuan-3d)
