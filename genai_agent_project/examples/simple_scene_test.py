"""
Simple test script for creating a scene with GenAI Agent
"""

import os
import sys
import asyncio
import yaml
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from genai_agent.agent import GenAIAgent

async def main():
    """Test creating a simple scene"""
    print("Testing direct scene creation with GenAI Agent...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check available Ollama models
    print("Checking for available Ollama models...")
    from genai_agent.tools.ollama_helper import OllamaHelper
    
    if OllamaHelper.is_ollama_running():
        models = OllamaHelper.list_models()
        if models:
            print(f"Available models: {[model.get('name') for model in models]}")
            
            # Update config to use an available model
            for model_info in models:
                model_name = model_info.get('name')
                if model_name:
                    config['llm']['model'] = model_name
                    print(f"Using model: {model_name}")
                    break
    
    # Create GenAI Agent
    agent = GenAIAgent(config)
    
    # Clear and specific instruction
    instruction = "Create a scene with a mountain, a forest, and a lake with a small cabin"
    
    print(f"Sending instruction to agent: {instruction}")
    result = await agent.process_instruction(instruction)
    
    print("Result from GenAI Agent:")
    print("="*80)
    print(json.dumps(result, indent=2))
    print("="*80)
    
    # Close agent
    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
