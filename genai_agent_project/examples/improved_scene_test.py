"""
Improved test script for creating a scene directly with SceneGeneratorTool
Includes error handling and model selection logic
"""

import os
import sys
import asyncio
import yaml
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.llm import LLMService
from genai_agent.tools.scene_generator import SceneGeneratorTool
from genai_agent.tools.ollama_helper import OllamaHelper
from env_loader import get_env, get_config


async def main():
    """Test direct scene generation with SceneGeneratorTool"""
    print("Testing improved direct scene generation with SceneGeneratorTool...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check if Ollama is running, start if needed
    if not OllamaHelper.is_ollama_running():
        print("Ollama is not running. Starting it...")
        OllamaHelper.start_ollama()
        # Wait a moment for it to start
        await asyncio.sleep(5)
    
    # Check available models
    print("Checking for available Ollama models...")
    models = OllamaHelper.list_models()
    
    if models:
        available_model_names = [model.get('name') for model in models]
        print(f"Available models: {available_model_names}")
        
        # ✅ Prioritize lighter and known-working models
        preferred_models = [
            "deepseek-coder:latest",    # ✅ First choice (smallest & most stable)
            "llama3.2:latest",          # Second choice (2.0 GB)
            "llama3:latest",            # Third choice (4.7 GB)
            "deepseek-coder-v2:latest"  # Largest fallback (8.9 GB)
        ]
        
        # Try to find the best available model from our preferred list
        selected_model = None
        for model in preferred_models:
            if model in available_model_names:
                selected_model = model
                break
                
        # If found a model, update the config
        if selected_model:
            print(f"Using model: {selected_model}")
            config['llm']['model'] = selected_model
    else:
        print("No models found or Ollama server not responding correctly")
    
    # Initialize Redis bus with a longer timeout
    redis_config = config.get('redis', {})
    redis_bus = RedisMessageBus(redis_config)
    
    # Connect with retry logic
    for attempt in range(3):
        try:
            connect_result = await redis_bus.connect()
            if connect_result:
                print("Connected to Redis successfully")
                break
        except Exception as e:
            print(f"Redis connection attempt {attempt+1} failed: {str(e)}")
            await asyncio.sleep(1)
    
    try:
        # Create scene generator tool
        scene_gen_tool = SceneGeneratorTool(redis_bus, {})
        
        # Create LLM service for the tool to use
        llm_service = LLMService(config.get('llm', {}))
        
        # Manually set the LLM service to bypass service discovery
        scene_gen_tool.llm_service = llm_service
        
        # Test scene generation with a simple scene
        scene_description = "A mountain landscape with snow on the peaks and a forest at the base"
        
        print(f"Generating scene with description: {scene_description}")
        result = await scene_gen_tool.execute({
            'description': scene_description,
            'style': 'realistic',
            'name': 'MountainScene'
        })
        
        print("\nScene generation result:")
        print("="*80)
        print(json.dumps(result, indent=2))
        print("="*80)
        
        # If successful, try a more complex scene
        if result.get('status') == 'success':
            print("\nNow trying a more complex scene...")
            complex_result = await scene_gen_tool.execute({
                'description': "A futuristic cityscape with tall buildings, flying vehicles, and a central plaza with a fountain",
                'style': 'sci-fi',
                'name': 'FutureCity'
            })
            
            print("\nComplex scene generation result:")
            print("="*80)
            print(json.dumps(complex_result, indent=2))
            print("="*80)
    except Exception as e:
        print(f"Error during scene generation: {str(e)}")
        import traceback
        print(traceback.format_exc())
    finally:
        # Close Redis connection
        try:
            await redis_bus.disconnect()
            print("Disconnected from Redis")
        except Exception as e:
            print(f"Error disconnecting from Redis: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
