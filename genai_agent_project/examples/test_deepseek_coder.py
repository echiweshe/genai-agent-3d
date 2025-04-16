"""
Test script for GenAI Agent with Deepseek-Coder model
"""

import os
import sys
import asyncio
import yaml
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from genai_agent.agent import GenAIAgent
from genai_agent.services.llm import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_direct_llm_generation():
    """Test direct LLM generation with Deepseek-Coder"""
    print("Testing direct LLM generation with Deepseek-Coder...")
    
    # Create LLM service with Deepseek-Coder configuration
    llm_service = LLMService({
        'type': 'local',
        'provider': 'ollama',
        'model': 'deepseek-coder'
    })
    
    # Simple test prompt for Blender code generation
    prompt = "Write a Blender Python script that creates a simple procedural mountainous landscape with snow on the peaks."
    
    print("Sending prompt to Deepseek-Coder...")
    response = await llm_service.generate(prompt)
    
    print("Response from Deepseek-Coder:")
    print("="*80)
    print(response)
    print("="*80)

async def test_agent_instruction():
    """Test GenAI Agent with an instruction"""
    print("Testing GenAI Agent with Deepseek-Coder...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update config to use Deepseek-Coder
    config['llm']['model'] = 'deepseek-coder'
    
    # Create GenAI Agent
    agent = GenAIAgent(config)
    
    # Test instruction
    instruction = "Create a 3D scene with a mountain landscape that has snow on the peaks"
    
    print(f"Sending instruction to GenAI Agent: {instruction}")
    result = await agent.process_instruction(instruction)
    
    print("Result from GenAI Agent:")
    print("="*80)
    import json
    print(json.dumps(result, indent=2))
    print("="*80)
    
    # Close agent
    await agent.close()

async def main():
    """Main entry point"""
    # Test direct LLM generation
    await test_direct_llm_generation()
    
    # Test agent instruction
    await test_agent_instruction()

if __name__ == "__main__":
    asyncio.run(main())
