"""
Test script for GenAI Agent with scene generation
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
from genai_agent.tools.scene_generator import SceneGeneratorTool
from genai_agent.services.redis_bus import RedisMessageBus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_direct_scene_generation():
    """Test direct scene generation with SceneGeneratorTool"""
    print("Testing direct scene generation with SceneGeneratorTool...")
    
    # Initialize Redis bus
    redis_bus = RedisMessageBus({'host': 'localhost', 'port': 6379})
    await redis_bus.connect()
    
    # Create scene generator tool
    scene_gen_tool = SceneGeneratorTool(redis_bus, {})
    
    # Create LLM service for the tool to use
    llm_service = LLMService({
        'type': 'local',
        'provider': 'ollama',
        'model': 'deepseek-coder'
    })
    
    # Manually set the LLM service
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
    import json
    print(json.dumps(result, indent=2))
    print("="*80)
    
    # Close Redis connection
    await redis_bus.disconnect()

async def test_agent_scene_generation():
    """Test scene generation through the GenAI Agent"""
    print("Testing scene generation through GenAI Agent...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update config to use Ollama model
    config['llm']['model'] = 'deepseek-coder'
    
    # Create GenAI Agent
    agent = GenAIAgent(config)
    
    # Test instruction
    instruction = "Create a 3D scene with a mountain landscape that has snow on the peaks and a forest at the base"
    
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
    # Test direct scene generation
    await test_direct_scene_generation()
    
    # Test agent scene generation
    await test_agent_scene_generation()

if __name__ == "__main__":
    asyncio.run(main())
