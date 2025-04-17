"""
Example of using the Enhanced Model Generator Tool with execution capability
"""

import os
import asyncio
import yaml
import logging

from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.model_generator import ModelGeneratorTool
from genai_agent.tools.blender_script import BlenderScriptTool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize Redis bus
    redis_config = config.get('redis', {})
    redis_bus = RedisMessageBus(redis_config)
    await redis_bus.connect()
    
    try:
        # Initialize the Blender script tool
        blender_config = config.get('tools', {}).get('blender_script', {}).get('config', {})
        blender_tool = BlenderScriptTool(redis_bus, blender_config)
        
        # Initialize the model generator tool
        model_config = config.get('tools', {}).get('model_generator', {}).get('config', {})
        model_tool = ModelGeneratorTool(redis_bus, model_config)
        
        # Create output directory
        output_dir = model_config.get('output_dir', 'output/models/')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate and execute a simple mesh model
        logger.info("Generating a simple 3D sculpture model...")
        mesh_result = await model_tool.execute({
            'description': 'A modern abstract sculpture with flowing curves and smooth surfaces',
            'model_type': 'mesh',
            'style': 'modern',
            'name': 'abstract_sculpture',
            'execute': True,  # Actually execute the generated script
            'save_blend': True
        })
        
        logger.info(f"Model generation result: {mesh_result.get('status')}")
        logger.info(f"Model file path: {mesh_result.get('model_path')}")
        
        if mesh_result.get('execution'):
            logger.info(f"Execution status: {mesh_result.get('execution').get('status')}")
        
        # Generate and execute a curve-based model
        logger.info("\nGenerating a curve-based tree model...")
        curve_result = await model_tool.execute({
            'description': 'A stylized tree with curving branches and a broad canopy',
            'model_type': 'curve',
            'style': 'stylized',
            'name': 'stylized_tree',
            'execute': True,
            'save_blend': True
        })
        
        logger.info(f"Model generation result: {curve_result.get('status')}")
        logger.info(f"Model file path: {curve_result.get('model_path')}")
        
        if curve_result.get('execution'):
            logger.info(f"Execution status: {curve_result.get('execution').get('status')}")
        
        # Generate a more complex architectural model
        logger.info("\nGenerating a complex architectural model...")
        architecture_result = await model_tool.execute({
            'description': 'A small modern house with flat roof, large windows, and a minimalist design',
            'model_type': 'mesh',
            'style': 'architectural',
            'name': 'modern_house',
            'execute': True,
            'save_blend': True
        })
        
        logger.info(f"Model generation result: {architecture_result.get('status')}")
        logger.info(f"Model file path: {architecture_result.get('model_path')}")
        
        if architecture_result.get('execution'):
            logger.info(f"Execution status: {architecture_result.get('execution').get('status')}")
        
        return {
            'mesh_model': mesh_result,
            'curve_model': curve_result,
            'architectural_model': architecture_result
        }
    finally:
        # Disconnect from Redis
        await redis_bus.disconnect()

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Print summary of results
    print("\nModel Generation Results:")
    print("--------------------------")
    for model_type, result in results.items():
        status = result.get('status', 'unknown')
        model_path = result.get('model_path', 'N/A')
        exec_status = result.get('execution', {}).get('status', 'not executed')
        print(f"{model_type}: {status} - {model_path} (Execution: {exec_status})")
