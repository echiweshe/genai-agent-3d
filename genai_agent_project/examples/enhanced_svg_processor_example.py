"""
Example of using the Enhanced SVG Processor Tool with advanced operations
"""

import os
import asyncio
import yaml
import logging

from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.svg_processor import SVGProcessorTool
from env_loader import get_env, get_config


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Example SVG for testing
EXAMPLE_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <rect x="50" y="50" width="100" height="100" fill="blue" stroke="black" stroke-width="2" />
  <circle cx="100" cy="100" r="40" fill="red" stroke="black" stroke-width="2" />
  <path d="M 30,30 L 170,30 L 100,170 Z" fill="green" stroke="black" stroke-width="2" />
</svg>
"""

async def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize Redis bus
    redis_config = config.get('redis', {})
    redis_bus = RedisMessageBus(redis_config)
    await redis_bus.connect()
    
    try:
        # Initialize the SVG processor tool
        svg_config = config.get('tools', {}).get('svg_processor', {}).get('config', {})
        svg_tool = SVGProcessorTool(redis_bus, svg_config)
        
        # Create output directory
        output_dir = svg_config.get('output_dir', 'output/svg/')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save example SVG to file for testing
        example_svg_path = os.path.join(output_dir, 'example.svg')
        with open(example_svg_path, 'w') as f:
            f.write(EXAMPLE_SVG)
        
        # 1. Analyze the SVG
        logger.info("Analyzing SVG...")
        analyze_result = await svg_tool.execute({
            'svg_file': example_svg_path,
            'operation': 'analyze',
            'name': 'example_analysis'
        })
        
        logger.info(f"Analysis result: {analyze_result.get('status')}")
        logger.info(f"Element counts: {analyze_result.get('element_counts')}")
        logger.info(f"Colors used: {analyze_result.get('colors_used')}")
        
        # 2. Simplify the SVG
        logger.info("\nSimplifying SVG...")
        simplify_result = await svg_tool.execute({
            'svg_file': example_svg_path,
            'operation': 'simplify',
            'name': 'example_simplified',
            'simplify_tolerance': 0.5
        })
        
        logger.info(f"Simplification result: {simplify_result.get('status')}")
        logger.info(f"Points before: {simplify_result.get('points_before')}, Points after: {simplify_result.get('points_after')}")
        logger.info(f"Reduction: {simplify_result.get('point_reduction_percent')}%")
        
        # 3. Remap colors
        logger.info("\nRemapping colors in SVG...")
        color_remap_result = await svg_tool.execute({
            'svg_file': example_svg_path,
            'operation': 'color_remap',
            'name': 'example_recolored',
            'color_map': {
                'blue': 'purple',
                'red': 'orange',
                'green': 'yellow'
            }
        })
        
        logger.info(f"Color remapping result: {color_remap_result.get('status')}")
        logger.info(f"Colors replaced: {color_remap_result.get('colors_replaced')}")
        
        # 4. Extract paths
        logger.info("\nExtracting paths from SVG...")
        paths_result = await svg_tool.execute({
            'svg_file': example_svg_path,
            'operation': 'extract_paths',
            'name': 'example_paths'
        })
        
        logger.info(f"Path extraction result: {paths_result.get('status')}")
        logger.info(f"Number of paths found: {paths_result.get('path_count')}")
        for i, path in enumerate(paths_result.get('paths', [])):
            logger.info(f"Path {i+1} ID: {path.get('id')}")
            logger.info(f"Path {i+1} commands: {path.get('commands')}")
        
        # 5. Convert to 3D model
        logger.info("\nConverting SVG to 3D model...")
        convert_result = await svg_tool.execute({
            'svg_file': example_svg_path,
            'operation': 'convert_to_3d',
            'name': 'example_3d',
            'extrude_depth': 0.2,
            'bevel_resolution': 4,
            'execute_script': False  # Set to True to actually execute the script with Blender
        })
        
        logger.info(f"3D conversion result: {convert_result.get('status')}")
        logger.info(f"Script path: {convert_result.get('script_path')}")
        logger.info(f"Model path: {convert_result.get('model_path')}")
        
        # Return all results
        return {
            'analyze': analyze_result,
            'simplify': simplify_result,
            'color_remap': color_remap_result,
            'paths': paths_result,
            'convert_to_3d': convert_result
        }
    finally:
        # Disconnect from Redis
        await redis_bus.disconnect()

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Print summary of results
    print("\nSVG Processing Results:")
    print("--------------------------")
    for operation, result in results.items():
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message')
        print(f"{operation}: {status} - {message}")
