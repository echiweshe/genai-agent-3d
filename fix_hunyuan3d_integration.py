#!/usr/bin/env python3
"""
Fix Hunyuan3D Integration

This script fixes the Hunyuan3D integration in the GenAI Agent 3D project.
It updates the LLM service to correctly handle Hunyuan3D API requests and responses.
"""

import os
import sys
import re
from pathlib import Path
import shutil
import datetime
import json

def main():
    """Main function"""
    # Find the llm.py file
    project_root = Path(__file__).parent.absolute()
    llm_path = project_root / "genai_agent_project" / "genai_agent" / "services" / "llm.py"
    
    # Verify file exists
    if not llm_path.exists():
        print(f"Error: LLM service file not found at {llm_path}")
        return 1
    
    # Backup the original file
    backup_path = llm_path.with_suffix(f".py.bak-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(llm_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Read the file content
    with open(llm_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the _generate_hunyuan3d method
    updated_content = fix_hunyuan3d_method(content)
    
    # Write updated content
    with open(llm_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("\n✅ Successfully updated Hunyuan3D integration!")
    print(f"Updated file: {llm_path}")
    
    # Update the enhanced_env_loader.py file to ensure proper API key loading
    env_loader_path = project_root / "genai_agent_project" / "genai_agent" / "services" / "enhanced_env_loader.py"
    if env_loader_path.exists():
        fix_env_loader(env_loader_path)
    
    # Verify and update .env file
    env_path = project_root / "genai_agent_project" / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if "HUNYUAN3D_API_KEY=" in env_content:
            print("\n✅ Hunyuan3D API key entry exists in the .env file.")
            
            # Ask if the user wants to update the API key
            replace_key = input("Would you like to update the Hunyuan3D API key? (y/n): ").lower() == 'y'
            if replace_key:
                update_api_key(env_path)
        else:
            print("\n❌ Hunyuan3D API key is not set in the .env file.")
            update_api_key(env_path)
    else:
        print(f"\n❌ .env file not found at {env_path}")
        print("Please create the .env file and add your Hunyuan3D API key.")
    
    print("\nCreating guide for obtaining a Hunyuan3D API key...")
    create_hunyuan3d_guide(project_root)
    
    # Ask if the user wants to restart the services
    restart = input("\nWould you like to restart the services now? (y/n): ").lower() == 'y'
    if restart:
        try:
            import subprocess
            subprocess.run([sys.executable, str(project_root / "restart_services.py")], check=True)
            print("\n✅ Services restarted successfully!")
        except Exception as e:
            print(f"\n❌ Failed to restart services: {str(e)}")
            print("Please restart services manually using restart_services.py")
    
    return 0

def fix_hunyuan3d_method(content):
    """Fix the _generate_hunyuan3d method in the LLM service"""
    # Find the _generate_hunyuan3d method
    hunyuan3d_method_pattern = r'async def _generate_hunyuan3d\(.*?\):'
    match = re.search(hunyuan3d_method_pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find _generate_hunyuan3d method. Adding it.")
        # If method not found, add it at the end of the class
        class_end = content.rfind('async def _generate_')
        if class_end == -1:
            print("Could not find the end of the class. Cannot add the method.")
            return content
        
        # Find the end of the last method to insert the new method
        method_end = find_method_end(content, class_end)
        
        # Insert the fixed method after the last method
        fixed_method = '''
    async def _generate_hunyuan3d(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Generate 3D content using Hunyuan3D API via fal.ai"""
        # Try to get API key from environment first, then config
        api_key = get_api_key_for_provider("hunyuan3d") or self.config.get("api_key")
        
        if not api_key:
            error_msg = "Hunyuan3D API key not found. Set HUNYUAN3D_API_KEY environment variable or configure in settings."
            logger.error(error_msg)
            return error_msg
        
        # fal.ai uses a different authentication method
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Key {api_key}"  # Note the format is "Key" not "Bearer"
        }
        
        # Build request body for the Hunyuan3D API on fal.ai
        # See https://fal.ai/models/fal-ai/hunyuan3d/api
        request_body = {
            "prompt": prompt,
            "negative_prompt": parameters.get("negative_prompt", ""),
            "num_inference_steps": parameters.get("num_inference_steps", 30),
            "guidance_scale": parameters.get("guidance_scale", 7.5),
            "width": parameters.get("width", 1024),
            "height": parameters.get("height", 1024),
            "seed": parameters.get("seed", None)
        }
        
        try:
            # Using the correct endpoint for fal.ai
            base_url = self.providers.get("hunyuan3d", {}).get("base_url", "https://api.fal.ai")
            endpoint = f"/models/{model}/infer"
            
            async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for 3D generation
                response = await client.post(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    json=request_body
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Hunyuan3D API response: {data}")
                    
                    # For text response in UI, provide the URLs to the generated content
                    result = "Hunyuan3D Generation Results:\\n\\n"
                    
                    if "images" in data:
                        result += "Generated images:\\n"
                        for i, image_url in enumerate(data["images"], 1):
                            result += f"{i}. {image_url}\\n"
                    
                    if "rendered_frames" in data:
                        result += "\\nRendered frames:\\n"
                        for i, frame in enumerate(data["rendered_frames"], 1):
                            result += f"{i}. {frame}\\n"
                    
                    if "3d_model" in data:
                        result += f"\\n3D Model: {data['3d_model']}\\n"
                    
                    if "mesh_url" in data:
                        result += f"\\nMesh URL: {data['mesh_url']}\\n"
                        
                    return result
                else:
                    error_msg = f"Hunyuan3D API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Error generating content with Hunyuan3D: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
'''
        updated_content = content[:method_end] + fixed_method + content[method_end:]
        return updated_content
    
    # Extract the method body
    method_start = match.start()
    method_end = find_method_end(content, method_start)
    method_body = content[method_start:method_end]
    
    # Add debug logging
    method_body = method_body.replace(
        'if response.status_code == 200:',
        'if response.status_code == 200:\n                    data = response.json()\n                    logger.debug(f"Hunyuan3D API response: {data}")',
        1
    )
    
    # Update endpoint URL
    if 'base_url = self.providers.get("hunyuan3d", {}).get("base_url"' in method_body:
        method_body = re.sub(
            r'base_url = self\.providers\.get\("hunyuan3d", {}\)\.get\("base_url", "[^"]*"\)',
            'base_url = self.providers.get("hunyuan3d", {}).get("base_url", "https://api.fal.ai")',
            method_body
        )
    
    # Replace the old method with the updated one
    updated_content = content[:method_start] + method_body + content[method_end:]
    return updated_content

def find_method_end(content, method_start):
    """Find the end of a method in the content"""
    lines = content[method_start:].split('\n')
    indent_level = len(lines[0]) - len(lines[0].lstrip())
    end_line = 0
    
    for i, line in enumerate(lines[1:], 1):
        if line.strip() and len(line) - len(line.lstrip()) <= indent_level and line.lstrip().startswith(('async def', 'def')):
            end_line = i
            break
    
    if end_line == 0:
        end_line = len(lines)
    
    return method_start + sum(len(line) + 1 for line in lines[:end_line])

def fix_env_loader(env_loader_path):
    """Fix the enhanced_env_loader.py file to ensure proper API key loading"""
    with open(env_loader_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if hunyuan3d is in the provider_env_map
    provider_env_map_pattern = r'provider_env_map\s*=\s*{[^}]*}'
    provider_env_map_match = re.search(provider_env_map_pattern, content, re.DOTALL)
    
    if provider_env_map_match:
        provider_env_map = provider_env_map_match.group(0)
        
        if "'hunyuan3d':" not in provider_env_map and '"hunyuan3d":' not in provider_env_map:
            # Add hunyuan3d to the provider_env_map
            updated_map = provider_env_map.replace(
                '}',
                ",\n        'hunyuan3d': 'HUNYUAN3D_API_KEY'\n    }"
            )
            updated_content = content.replace(provider_env_map, updated_map)
            
            # Write updated content
            with open(env_loader_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"\n✅ Updated enhanced_env_loader.py to include Hunyuan3D API key mapping")
    else:
        print(f"\n❌ Could not find provider_env_map in {env_loader_path}")

def update_api_key(env_path):
    """Update the Hunyuan3D API key in the .env file"""
    print("\nHunyuan3D API Key Setup")
    print("=======================")
    print("You need to provide your Hunyuan3D API key to use Hunyuan3D models.")
    print("For fal.ai, the API key usually starts with 'key-'")
    
    api_key = input("Enter your Hunyuan3D API key: ")
    if not api_key:
        print("No API key provided. Skipping.")
        return
    
    # Read current content
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update or add the API key
    if "HUNYUAN3D_API_KEY=" in content:
        # Replace existing key
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("HUNYUAN3D_API_KEY="):
                lines[i] = f"HUNYUAN3D_API_KEY={api_key}"
                break
            elif line.strip().startswith("# HUNYUAN3D_API_KEY="):
                lines[i] = f"HUNYUAN3D_API_KEY={api_key}"
                break
        
        updated_content = '\n'.join(lines)
    else:
        # Add new key
        if not content.endswith('\n'):
            content += '\n'
        updated_content = content + f"HUNYUAN3D_API_KEY={api_key}\n"
    
    # Write updated content
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("\n✅ Hunyuan3D API key has been successfully updated in the .env file!")

def create_hunyuan3d_guide(project_root):
    """Create a guide for obtaining a Hunyuan3D API key via fal.ai"""
    guide_path = project_root / "HUNYUAN3D_GUIDE.md"
    
    guide_content = """# Hunyuan3D Integration Guide

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
"""
    
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"Created Hunyuan3D guide at {guide_path}")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
