"""
Test direct usage of SceneGeneratorTool
"""

import os
import sys
import asyncio
import yaml
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
    print("Testing direct scene generation with SceneGeneratorTool...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check available models
    if OllamaHelper.is_ollama_running():
        models = OllamaHelper.list_models()
        if models:
            available_model_names = [model.get('name') for model in models]
            print(f"Available models: {available_model_names}")
            
            # Prioritize smaller models
            preferred_models = [
                "llama3:latest",  # First choice
                "llama3.2:latest", 
                "deepseek-coder:latest"
            ]
            
            # Try to find one of our preferred models
            selected_model = None
            for preferred in preferred_models:
                if preferred in available_model_names:
                    selected_model = preferred
                    break
            
            # If no preferred model is found, use the first available
            if not selected_model and available_model_names:
                selected_model = available_model_names[0]
                
            if selected_model:
                config['llm']['model'] = selected_model
                print(f"Using model: {selected_model}")
    else:
        print("Ollama is not running. Starting it...")
        OllamaHelper.start_ollama()
    
    # Initialize Redis bus
    redis_bus = RedisMessageBus(config.get('redis', {}))
    await redis_bus.connect()
    
    # Create LLM service for the tool to use
    llm_service = LLMService(config.get('llm', {}))
    
    # Create scene generator tool
    scene_gen_tool = SceneGeneratorTool(redis_bus, {})
    
    # Manually set the LLM service to bypass service discovery
    scene_gen_tool.llm_service = llm_service
    
    # Test scene generation
    parameters = {
        'description': 'A mountain landscape with snow on the peaks and a forest at the base',
        'style': 'realistic',
        'name': 'MountainScene'
    }
    
    print(f"Generating scene with parameters: {parameters}")
    result = await scene_gen_tool.execute(parameters)
    
    print("Scene generation result:")
    print("="*80)
    print(json.dumps(result, indent=2))
    print("="*80)
    
    # Close Redis connection
    await redis_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
