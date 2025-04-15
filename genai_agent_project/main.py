#!/usr/bin/env python3
"""
GenAI Agent for 3D Modeling - Main entry point
"""

import asyncio
import argparse
import logging
import yaml
from pathlib import Path

from genai_agent.agent import GenAIAgent
from genai_agent.config import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('genai_agent')

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='GenAI Agent for 3D Modeling')
    parser.add_argument('--config', type=str, default='config.yaml', 
                        help='Path to configuration file')
    parser.add_argument('--instruction', type=str, 
                        help='Instruction to process')
    args = parser.parse_args()
    
    # Load configuration - will search in multiple locations if needed
    config = load_config(args.config)
    
    # Initialize agent
    agent = GenAIAgent(config)
    
    try:
        # Process instruction if provided
        if args.instruction:
            result = await agent.process_instruction(args.instruction)
            print(result)
        else:
            # Interactive mode
            print("GenAI Agent - Interactive Mode")
            print("Type 'exit' to quit")
            
            while True:
                instruction = input(">> ")
                if instruction.lower() == 'exit':
                    break
                    
                result = await agent.process_instruction(instruction)
                print(result)
    finally:
        # Clean up resources
        await agent.cleanup()
    
if __name__ == "__main__":
    asyncio.run(main())
