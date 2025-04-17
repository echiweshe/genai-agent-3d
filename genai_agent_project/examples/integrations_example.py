"""
Example of using external tool integrations
"""

import os
import asyncio
import yaml
import logging
import argparse

from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.blender_gpt_tool import BlenderGPTTool
from genai_agent.tools.hunyuan_3d_tool import Hunyuan3DTool
from genai_agent.tools.trellis_tool import TrellisTool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_blendergpt_example(redis_bus, config):
    """Run BlenderGPT example"""
    logger.info("Running BlenderGPT example...")
    
    # Initialize the BlenderGPT tool
    tool_config = config.get('tools', {}).get('blender_gpt', {}).get('config', {})
    blendergpt_tool = BlenderGPTTool(redis_bus, tool_config)
    
    # Check if the tool is available
    if not blendergpt_tool.blender_gpt.is_available:
        logger.warning("BlenderGPT is not available. Make sure it's installed and the paths are correct in the config file.")
        return
    
    # Generate a simple scene from natural language
    logger.info("Generating a simple scene from natural language...")
    result = await blendergpt_tool.execute({
        'operation': 'generate_script',
        'prompt': 'Create a simple scene with a red cube on a blue plane, add proper lighting and camera',
        'execute': True  # Actually execute the script
    })
    
    logger.info(f"Generation result: {result.get('status')}")
    
    if result.get('status') == 'success':
        logger.info(f"Script generated and saved to: {result.get('script_path')}")
        
        if result.get('execution', {}).get('status') == 'success':
            logger.info("Script executed successfully")
        else:
            logger.warning(f"Script execution failed: {result.get('execution', {}).get('error')}")
    else:
        logger.error(f"Failed to generate script: {result.get('error')}")
    
    return result

async def run_hunyuan3d_example(redis_bus, config):
    """Run Hunyuan-3D example"""
    logger.info("Running Hunyuan-3D example...")
    
    # Initialize the Hunyuan-3D tool
    tool_config = config.get('tools', {}).get('hunyuan_3d', {}).get('config', {})
    hunyuan_tool = Hunyuan3DTool(redis_bus, tool_config)
    
    # Check if the tool is available
    if not hunyuan_tool.hunyuan_3d.is_available:
        logger.warning("Hunyuan-3D is not available. Make sure it's installed and the paths are correct in the config file.")
        return
    
    # Generate a 3D model from text
    logger.info("Generating a 3D model from text...")
    result = await hunyuan_tool.execute({
        'operation': 'generate_model',
        'prompt': 'A modern chair with a sleek design',
        'format': 'obj',
        'name': 'modern_chair',
        'resolution': 256,
        'steps': 50
    })
    
    logger.info(f"Generation result: {result.get('status')}")
    
    if result.get('status') == 'success':
        logger.info(f"Model generated and saved to: {result.get('model_path')}")
    else:
        logger.error(f"Failed to generate model: {result.get('error')}")
    
    return result

async def run_trellis_example(redis_bus, config):
    """Run TRELLIS example"""
    logger.info("Running TRELLIS example...")
    
    # Initialize the TRELLIS tool
    tool_config = config.get('tools', {}).get('trellis', {}).get('config', {})
    trellis_tool = TrellisTool(redis_bus, tool_config)
    
    # Check if the tool is available
    if not trellis_tool.trellis.is_available:
        logger.warning("TRELLIS is not available. Make sure it's installed and the paths are correct in the config file.")
        return
    
    # Perform spatial reasoning
    logger.info("Performing spatial reasoning...")
    result = await trellis_tool.spatial_reasoning({
        'scene_description': 'A room with a table in the center. On the table, there is a red cube to the left of a blue sphere. Behind the sphere is a green pyramid.',
        'question': 'What is the relationship between the cube and the pyramid?',
        'max_steps': 3
    })
    
    logger.info(f"Reasoning result: {result.get('status')}")
    
    if result.get('status') == 'success':
        logger.info(f"Conclusion: {result.get('conclusion')}")
        logger.info(f"Result saved to: {result.get('file_path')}")
    else:
        logger.error(f"Failed to perform reasoning: {result.get('error')}")
    
    # Generate a plan for 3D scene creation
    logger.info("\nGenerating a plan for 3D scene creation...")
    plan_result = await trellis_tool.execute({
        'operation': 'plan',
        'goal': 'Create a 3D scene of a forest with a small cabin and a river',
        'constraints': [
            'The scene should be realistic',
            'The lighting should create a sunset atmosphere',
            'The cabin should be made of wood'
        ],
        'resources': [
            'Blender 3D software',
            'Tree models',
            'Water shader'
        ],
        'max_depth': 3
    })
    
    logger.info(f"Planning result: {plan_result.get('status')}")
    
    if plan_result.get('status') == 'success':
        logger.info(f"Plan with {len(plan_result.get('plan', []))} steps generated")
        logger.info(f"Result saved to: {plan_result.get('file_path')}")
    else:
        logger.error(f"Failed to generate plan: {plan_result.get('error')}")
    
    return result, plan_result

async def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Run integration examples')
    parser.add_argument('--blendergpt', action='store_true', help='Run BlenderGPT example')
    parser.add_argument('--hunyuan', action='store_true', help='Run Hunyuan-3D example')
    parser.add_argument('--trellis', action='store_true', help='Run TRELLIS example')
    parser.add_argument('--all', action='store_true', help='Run all examples')
    args = parser.parse_args()
    
    run_all = args.all or not (args.blendergpt or args.hunyuan or args.trellis)
    
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize Redis bus
    redis_config = config.get('redis', {})
    redis_bus = RedisMessageBus(redis_config)
    await redis_bus.connect()
    
    try:
        results = {}
        
        # Run selected examples
        if run_all or args.blendergpt:
            results['blendergpt'] = await run_blendergpt_example(redis_bus, config)
        
        if run_all or args.hunyuan:
            results['hunyuan'] = await run_hunyuan3d_example(redis_bus, config)
        
        if run_all or args.trellis:
            results['trellis'] = await run_trellis_example(redis_bus, config)
        
        return results
    finally:
        # Disconnect from Redis
        await redis_bus.disconnect()

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Print summary
    print("\nIntegration Examples Results:")
    print("============================")
    
    for integration, result in results.items():
        if result:
            if isinstance(result, tuple):
                # Multiple results (trellis)
                print(f"{integration.upper()}: {result[0].get('status')} / {result[1].get('status')}")
            else:
                print(f"{integration.upper()}: {result.get('status')}")
        else:
            print(f"{integration.upper()}: Not available")
