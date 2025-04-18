"""
Example of using the Diagram Generator Tool
"""

import os
import asyncio
import yaml
import logging

from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.diagram_generator import DiagramGeneratorTool
from env_loader import get_env, get_config


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
        # Initialize the diagram generator tool
        diagram_tool_config = config.get('tools', {}).get('diagram_generator', {}).get('config', {})
        diagram_tool = DiagramGeneratorTool(redis_bus, diagram_tool_config)
        
        # Create output directory if it doesn't exist
        output_dir = diagram_tool_config.get('output_dir', 'output/diagrams/')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a flowchart diagram
        flowchart_result = await diagram_tool.execute({
            'description': 'A flowchart showing the process of creating a 3D model from an SVG file',
            'diagram_type': 'flowchart',
            'format': 'mermaid',
            'name': 'svg_to_3d_flowchart'
        })
        
        logger.info(f"Flowchart generated: {flowchart_result.get('file_path')}")
        logger.info(f"Diagram code: \n{flowchart_result.get('code')}")
        
        # Generate a hierarchy diagram
        hierarchy_result = await diagram_tool.execute({
            'description': 'A scene hierarchy showing a typical 3D scene with camera, lights, and objects',
            'diagram_type': 'hierarchy',
            'format': 'mermaid',
            'name': 'scene_hierarchy'
        })
        
        logger.info(f"Hierarchy diagram generated: {hierarchy_result.get('file_path')}")
        logger.info(f"Diagram code: \n{hierarchy_result.get('code')}")
        
        # Generate a UML class diagram
        uml_result = await diagram_tool.execute({
            'description': 'UML class diagram for the core components of the GenAI agent system including Agent, SceneManager, and Tools',
            'diagram_type': 'uml',
            'format': 'mermaid',
            'name': 'agent_uml'
        })
        
        logger.info(f"UML diagram generated: {uml_result.get('file_path')}")
        logger.info(f"Diagram code: \n{uml_result.get('code')}")
        
        # Generate an SVG diagram (more complex)
        svg_result = await diagram_tool.execute({
            'description': 'A simple diagram of a house with a roof, door, and windows',
            'diagram_type': 'scene_layout',
            'format': 'svg',
            'name': 'house_layout'
        })
        
        logger.info(f"SVG diagram generated: {svg_result.get('file_path')}")
        
        return {
            'flowchart': flowchart_result,
            'hierarchy': hierarchy_result,
            'uml': uml_result,
            'svg': svg_result
        }
    finally:
        # Disconnect from Redis
        await redis_bus.disconnect()

if __name__ == "__main__":
    results = asyncio.run(main())
    
    # Print summary of results
    print("\nDiagram Generation Results:")
    print("--------------------------")
    for diagram_type, result in results.items():
        status = result.get('status', 'unknown')
        file_path = result.get('file_path', 'N/A')
        print(f"{diagram_type.capitalize()}: {status} - {file_path}")
