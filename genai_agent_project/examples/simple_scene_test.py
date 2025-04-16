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
            available_model_names = [model.get('name') for model in models]
            print(f"Available models: {available_model_names}")
            
            # ✅ Prioritize lighter and known-working models
            preferred_models = [
                "deepseek-coder:latest",        # ✅ First choice (smallest & most stable)
                "llama3.2:latest",              # Second choice (2.0 GB)
                "llama3:latest",                # Third choice (4.7 GB)
                "deepseek-coder-v2:latest",     # Largest fallback (8.9 GB)
            ]

            # Pick the first available model from preferred list
            for model in preferred_models:
                if model in available_model_names:
                    selected_model = model
                    print(f"Using model: {selected_model}")
                    break
            else:
                selected_model = available_model_names[0]
                print(f"Using fallback model: {selected_model}")

            
            # If no preferred model is found, use the first available
            if not selected_model and available_model_names:
                selected_model = available_model_names[0]
                
            if selected_model:
                config['llm']['model'] = selected_model
                print(f"Using model: {selected_model}")
    
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
