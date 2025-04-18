#!/usr/bin/env python3
"""
Main entry point for GenAI Agent
"""

import os
import sys
import logging
import argparse
import asyncio
import yaml
import subprocess
import importlib.util
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from genai_agent.agent import GenAIAgent
from genai_agent.tools.ollama_helper import OllamaHelper
from env_loader import get_env, get_config


def load_config(config_path="config.yaml"):
    """Load configuration from file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

async def agent_shell(config):
    """Interactive shell for agent"""
    agent = GenAIAgent(config)
    print("GenAI Agent Shell - Enter instructions or 'exit' to quit")
    
    while True:
        try:
            instruction = input("\n> ")
            if instruction.lower() in ['exit', 'quit']:
                break
                
            result = await agent.process_instruction(instruction)
            
            # Check if result is string or dict
            if isinstance(result, dict):
                if result.get('status') == 'error':
                    print(f"\nError: {result.get('error', 'Unknown error')}")
                else:
                    print("\nResult:\n")
                    if 'message' in result:
                        print(result['message'])
                    else:
                        import json
                        print(json.dumps(result, indent=2))
            else:
                print("\nResult:\n")
                print(result)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Close agent
    await agent.close()
    print("Exiting shell")

def handle_ollama(args):
    """Handle Ollama-related commands"""
    if args.ollama_command == 'start':
        print("Starting Ollama server...")
        success = OllamaHelper.start_ollama()
        if success:
            print("Ollama server started successfully")
        else:
            print("Failed to start Ollama server")
    
    elif args.ollama_command == 'stop':
        print("Stopping Ollama server...")
        success = OllamaHelper.stop_ollama()
        if success:
            print("Ollama server stopped successfully")
        else:
            print("Failed to stop Ollama server")
    
    elif args.ollama_command == 'list':
        print("Available Ollama models:")
        models = OllamaHelper.list_models()
        if models:
            for model in models:
                size_gb = model.get('size', 0) / (1024 * 1024 * 1024)
                print(f"- {model.get('name')} (Size: {size_gb:.2f} GB)")
        else:
            print("No models found or Ollama server not running")
    
    elif args.ollama_command == 'pull':
        if not args.model:
            print("Error: Model name is required for 'pull' command")
            return
        print(f"Pulling model {args.model}...")
        success = OllamaHelper.pull_model(args.model)
        if success:
            print(f"Successfully pulled model: {args.model}")
        else:
            print(f"Failed to pull model: {args.model}")
    
    elif args.ollama_command == 'details':
        if not args.model:
            print("Error: Model name is required for 'details' command")
            return
        details = OllamaHelper.get_model_details(args.model)
        if details:
            print(f"Details for model {args.model}:")
            for key, value in details.items():
                print(f"- {key}: {value}")
        else:
            print(f"No details found for model {args.model} or Ollama server not running")
    
    else:
        print(f"Unknown Ollama command: {args.ollama_command}")

async def run_command(args):
    """Run a single instruction with the agent"""
    config = load_config(args.config)
    agent = GenAIAgent(config)
    
    try:
        result = await agent.process_instruction(args.instruction)
        
        # Check if result is string or dict
        if isinstance(result, dict):
            if result.get('status') == 'error':
                print(f"Error: {result.get('error', 'Unknown error')}")
            else:
                if 'message' in result:
                    print(result['message'])
                else:
                    import json
                    print(json.dumps(result, indent=2))
        else:
            print(result)
    finally:
        # Close agent
        await agent.close()

def run_examples(args):
    """Run example scripts"""
    examples_dir = os.path.join(project_root, 'examples')
    
    if args.example_name:
        # Run specific example
        example_path = os.path.join(examples_dir, f"{args.example_name}.py")
        if not os.path.exists(example_path):
            print(f"Example not found: {args.example_name}")
            
            # List available examples
            print("\nAvailable examples:")
            for file in os.listdir(examples_dir):
                if file.endswith('.py') and file != '__init__.py':
                    print(f"- {os.path.splitext(file)[0]}")
            
            return
        
        # Run the example
        print(f"Running example: {args.example_name}")
        exec_example(example_path)
    
    else:
        # List available examples
        print("Available examples:")
        for file in os.listdir(examples_dir):
            if file.endswith('.py') and file != '__init__.py':
                print(f"- {os.path.splitext(file)[0]}")
        
        print("\nRun an example with: python run.py examples <example_name>")

def exec_example(example_path):
    """Execute an example script"""
    try:
        # Load the module
        spec = importlib.util.spec_from_file_location("example", example_path)
        example = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(example)
        
        # Run the example
        if hasattr(example, 'main'):
            if asyncio.iscoroutinefunction(example.main):
                asyncio.run(example.main())
            else:
                example.main()
        else:
            print("Example does not have a main() function")
    
    except Exception as e:
        print(f"Error running example: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="GenAI Agent")
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Shell command
    shell_parser = subparsers.add_parser('shell', help='Start interactive shell')
    shell_parser.add_argument('--config', type=str, default='config.yaml', help='Path to configuration file')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run agent with instruction')
    run_parser.add_argument('instruction', type=str, help='Instruction to process')
    run_parser.add_argument('--config', type=str, default='config.yaml', help='Path to configuration file')
    
    # Ollama command
    ollama_parser = subparsers.add_parser('ollama', help='Manage Ollama models')
    ollama_parser.add_argument('ollama_command', choices=['start', 'stop', 'list', 'pull', 'details'], help='Ollama command')
    ollama_parser.add_argument('model', nargs='?', help='Model name for pull/details command')
    
    # Examples command
    examples_parser = subparsers.add_parser('examples', help='Run example scripts')
    examples_parser.add_argument('example_name', nargs='?', help='Name of example to run')
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'shell':
        config = load_config(args.config)
        asyncio.run(agent_shell(config))
    
    elif args.command == 'run':
        asyncio.run(run_command(args))
    
    elif args.command == 'ollama':
        handle_ollama(args)
    
    elif args.command == 'examples':
        run_examples(args)
    
    else:
        # Default to shell if no command specified
        config = load_config('config.yaml')
        asyncio.run(agent_shell(config))

if __name__ == "__main__":
    main()
