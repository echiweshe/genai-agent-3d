"""
Example script to convert SVG to 3D using the GenAI Agent
"""

import os
import sys
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from genai_agent.agent import GenAIAgent
from genai_agent.config import load_config
from genai_agent.tools.svg_processor import SVGProcessorTool
from genai_agent.services.redis_bus import RedisMessageBus

# Sample SVG content
SAMPLE_SVG = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="30" height="30" />
  <circle cx="70" cy="20" r="15" />
  <rect x="10" y="60" width="80" height="20" />
</svg>
"""

async def main():
    """
    Main function to demonstrate the SVG Processor
    """
    # Load configuration - use absolute path
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    config = load_config(config_path)
    
    # Initialize agent
    agent = GenAIAgent(config)
    
    try:
        # Process instruction through agent
        print("Converting SVG to 3D using the agent...")
        result = await agent.process_instruction(
            f"Convert this SVG to 3D and extrude it by 0.5 units: {SAMPLE_SVG}"
        )
        
        # Display agent result
        print("\nAgent Result:")
        print(f"Tasks executed: {result.get('tasks_executed', 0)}")
        print(f"Tasks succeeded: {result.get('tasks_succeeded', 0)}")
        print(f"Tasks failed: {result.get('tasks_failed', 0)}")
        
        # Direct use of SVG Processor Tool
        print("\nDirect use of SVG Processor Tool...")
        
        # Initialize Redis Bus and SVG Processor
        redis_bus = RedisMessageBus(config.get('services', {}).get('redis', {}))
        svg_processor = SVGProcessorTool(redis_bus, config.get('services', {}).get('blender', {}))
        
        # Execute SVG Processor directly
        svg_result = await svg_processor.execute({
            'svg_content': SAMPLE_SVG,
            'extrude_depth': 0.5,
            'animation': {
                'frame_end': 120,
                'objects': [
                    {
                        'object_index': 0,
                        'keyframes': {
                            '1': (0, 0, 0),
                            '60': (0, 0, 5),
                            '120': (0, 0, 0)
                        }
                    }
                ]
            }
        })
        
        # Display SVG Processor result
        print("\nSVG Processor Result:")
        print(f"Status: {svg_result.get('status', 'unknown')}")
        if 'objects_created' in svg_result:
            print(f"Objects created: {svg_result.get('objects_created', 0)}")
        if 'object_names' in svg_result:
            print(f"Object names: {svg_result.get('object_names', [])}")
    finally:
        # Clean up resources
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
