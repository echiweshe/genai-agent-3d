"""
Example script to create a simple scene using the GenAI Agent
"""

import os
import sys
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from genai_agent.agent import GenAIAgent
from genai_agent.config import load_config

async def main():
    """
    Main function to demonstrate the GenAI Agent
    """
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    config = load_config(config_path)
    
    # Initialize agent
    agent = GenAIAgent(config)
    
    try:
        # Process instruction
        print("Creating a simple scene with a cube on a plane...")
        result = await agent.process_instruction(
            "Create a simple scene with a red cube on a blue plane"
        )
        
        # Display result
        print("\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Tasks executed: {result.get('tasks_executed', 0)}")
        print(f"Tasks succeeded: {result.get('tasks_succeeded', 0)}")
        print(f"Tasks failed: {result.get('tasks_failed', 0)}")
        
        # Show individual task results
        print("\nTask results:")
        for i, task_result in enumerate(result.get('results', [])):
            print(f"Task {i+1}: {task_result.get('task', 'Unknown task')}")
            print(f"  Status: {task_result.get('status', 'unknown')}")
            if task_result.get('status') == 'error':
                print(f"  Error: {task_result.get('error', 'Unknown error')}")
            else:
                # Show limited result info
                task_data = task_result.get('result', {})
                if isinstance(task_data, dict):
                    print(f"  Output: Success")
                    if 'objects_created' in task_data:
                        print(f"  Objects created: {task_data.get('objects_created', 0)}")
                    if 'camera_position' in task_data:
                        print(f"  Camera position: {task_data.get('camera_position', [])}")
                else:
                    print(f"  Output: {task_data}")
    finally:
        # Clean up resources
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
