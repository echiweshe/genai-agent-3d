#!/usr/bin/env python3
"""
Helper script to run the GenAI Agent with various commands
"""

import os
import sys
import argparse
import subprocess
import asyncio

def start_redis():
    """Start Redis using Docker if available"""
    try:
        # Check if Redis is already running
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", "name=genai-redis"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("Redis is already running")
            return True
        
        # Start Redis
        print("Starting Redis...")
        result = subprocess.run(
            ["docker", "run", "-d", "--name", "genai-redis", "-p", "6379:6379", "redis"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Redis started successfully")
            return True
        else:
            print(f"Failed to start Redis: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error starting Redis: {str(e)}")
        print("Please make sure Docker is installed and running")
        return False

def manage_ollama(command, args=None):
    """Manage Ollama using the helper script"""
    ollama_script = os.path.join(os.path.dirname(__file__), "tools", "ollama_helper.py")
    
    if command == "start":
        subprocess.run([sys.executable, ollama_script, "start"])
    elif command == "install":
        subprocess.run([sys.executable, ollama_script, "install"])
    elif command == "pull":
        if not args or not args.model:
            print("Error: Model name is required for 'ollama pull' command")
            return
        subprocess.run([sys.executable, ollama_script, "pull", args.model])
    elif command == "list":
        subprocess.run([sys.executable, ollama_script, "list"])
    elif command == "test":
        if not args or not args.model:
            print("Error: Model name is required for 'ollama test' command")
            return
            
        prompt = args.prompt if args and args.prompt else "Hello, world!"
        subprocess.run([sys.executable, ollama_script, "test", args.model, "--prompt", prompt])
    else:
        # Just run the script with no args to see status
        subprocess.run([sys.executable, ollama_script])

def run_agent(command, args):
    """Run the GenAI Agent with the specified command"""
    if command == "interactive":
        # Run in interactive mode
        subprocess.run(["python", "main.py"])
    elif command == "instruction":
        # Run with a specific instruction
        if not args.instruction:
            print("Error: Instruction is required for 'instruction' command")
            return
        
        subprocess.run(["python", "main.py", "--instruction", args.instruction])
    elif command == "example":
        # Run a specific example
        if not args.example:
            print("Error: Example name is required for 'example' command")
            return
        
        example_path = os.path.join("examples", f"{args.example}.py")
        if not os.path.exists(example_path):
            print(f"Error: Example '{args.example}' not found")
            return
        
        subprocess.run(["python", example_path])
    elif command == "test":
        # Run tests
        subprocess.run(["python", "-m", "unittest", "discover", "tests"])
    elif command.startswith("ollama"):
        # Handle Ollama commands
        ollama_command = command.replace("ollama_", "")
        manage_ollama(ollama_command, args)
    else:
        print(f"Unknown command: {command}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run the GenAI Agent')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Run in interactive mode')
    
    # Instruction mode
    instruction_parser = subparsers.add_parser('instruction', help='Run with a specific instruction')
    instruction_parser.add_argument('--instruction', type=str, help='Instruction to process')
    
    # Example mode
    example_parser = subparsers.add_parser('example', help='Run a specific example')
    example_parser.add_argument('--example', type=str, help='Example name to run (without .py)')
    
    # Test mode
    test_parser = subparsers.add_parser('test', help='Run tests')
    
    # Redis mode
    redis_parser = subparsers.add_parser('redis', help='Start Redis')
    
    # Ollama commands
    ollama_parser = subparsers.add_parser('ollama', help='Manage Ollama')
    ollama_subparsers = ollama_parser.add_subparsers(dest='ollama_command', help='Ollama command')
    
    # Ollama install
    ollama_install_parser = ollama_subparsers.add_parser('install', help='Install Ollama')
    
    # Ollama start
    ollama_start_parser = ollama_subparsers.add_parser('start', help='Start Ollama server')
    
    # Ollama list
    ollama_list_parser = ollama_subparsers.add_parser('list', help='List available models')
    
    # Ollama pull
    ollama_pull_parser = ollama_subparsers.add_parser('pull', help='Pull a model')
    ollama_pull_parser.add_argument('model', type=str, help='Model name to pull')
    
    # Ollama test
    ollama_test_parser = ollama_subparsers.add_parser('test', help='Test a model')
    ollama_test_parser.add_argument('model', type=str, help='Model name to test')
    ollama_test_parser.add_argument('--prompt', type=str, default='Hello, world!', help='Test prompt')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'redis':
        start_redis()
    elif args.command == 'ollama':
        if not args.ollama_command:
            # Just show Ollama status
            manage_ollama(None)
        else:
            manage_ollama(args.ollama_command, args)
    else:
        run_agent(args.command, args)

if __name__ == "__main__":
    main()
