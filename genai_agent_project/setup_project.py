#!/usr/bin/env python3
"""
Setup script for GenAI Agent project structure.
Creates directory structure and initializes base files.
"""

import os
import json
import argparse
import shutil
from pathlib import Path

# Define project structure with directories and files
PROJECT_STRUCTURE = {
    # Core package
    "genai_agent": {
        "__init__.py": "\"\"\"GenAI Agent - 3D scene generation framework\"\"\"\n\n__version__ = '0.1.0'\n",
        
        # Core components
        "agent.py": None,  # Will be populated later
        "config.py": None,  # Will be populated later
        
        # Services
        "services": {
            "__init__.py": "",
            "llm.py": None,  # Will be populated later
            "redis_bus.py": None,  # Will be populated later
            "scene_manager.py": None,  # Will be populated later
            "memory.py": None,  # Will be populated later
            "asset_manager.py": None,  # Will be populated later
        },
        
        # Tools
        "tools": {
            "__init__.py": "",
            "registry.py": None,  # Will be populated later
            "blender_script.py": None,  # Will be populated later
            "scene_generator.py": None,  # Will be populated later
            "model_generator.py": None,  # Will be populated later
            "diagram_generator.py": None,  # Will be populated later
            "svg_processor.py": None,  # Will be populated later
            "ollama_helper.py": None,  # Will be populated later
        },
        
        # Domain models
        "models": {
            "__init__.py": "",
            "scene.py": None,  # Will be populated later
            "task.py": None,  # Will be populated later
            "asset.py": None,  # Will be populated later
        },
        
        # Utilities
        "utils": {
            "__init__.py": "",
            "coordinate.py": None,  # Will be populated later
            "prompts.py": None,  # Will be populated later
            "logging.py": None,  # Will be populated later
        },
    },
    
    # Examples
    "examples": {
        "__init__.py": "",
        "test_llm.py": None,  # Will be populated later
        "test_blender.py": None,  # Will be populated later
        "test_agent.py": None,  # Will be populated later
        "test_deepseek_coder.py": None,  # Will be populated later
    },
    
    # Tests
    "tests": {
        "__init__.py": "",
        "test_agent.py": None,  # Will be populated later
        "test_llm.py": None,  # Will be populated later
        "test_redis.py": None,  # Will be populated later
    },
    
    # Blender addons
    "addons": {
        "README.md": "# Blender Addons\n\nPlace custom Blender addons here.\n",
    },
    
    # Docker configuration
    "docker": {
        "Dockerfile": None,  # Will be populated later
        "docker-compose.yml": None,  # Will be populated later
    },
    
    # Project files
    "README.md": None,  # Will be populated later
    "requirements.txt": None,  # Will be populated later
    "setup.py": None,  # Will be populated later
    "run.py": None,  # Will be populated later
    "config.yaml": None,  # Will be populated later
}

def create_directory_structure(base_path, structure, overwrite=False):
    """Create directory structure and files"""
    for key, value in structure.items():
        path = os.path.join(base_path, key)
        
        if isinstance(value, dict):
            # Create directory
            if not os.path.exists(path):
                print(f"Creating directory: {path}")
                os.makedirs(path)
            create_directory_structure(path, value, overwrite)
        else:
            # Create file
            if value is not None and (overwrite or not os.path.exists(path)):
                print(f"Creating file: {path}")
                with open(path, 'w') as f:
                    f.write(value)
            elif value is None and not os.path.exists(path):
                print(f"Creating empty file: {path}")
                with open(path, 'w') as f:
                    f.write("")

def populate_core_files(base_path):
    """Populate core files with content"""
    print("Populating core files...")
    
    # Configuration file
    config_yaml = """# GenAI Agent Configuration

# General settings
general:
  debug: true
  log_level: info
  
# Redis configuration
redis:
  host: localhost
  port: 6379
  password: null
  db: 0
    
# LLM configuration
llm:
  type: local
  provider: ollama
  model: deepseek-coder  # Default model
  
# Blender configuration
blender:
  path: C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe  # Path to Blender executable
  addons_path: addons/    # Path to custom addons
  
# Tools configuration
tools:
  blender_script:
    module: genai_agent.tools.blender_script
    class: BlenderScriptTool
  
  scene_generator:
    module: genai_agent.tools.scene_generator
    class: SceneGeneratorTool
  
  model_generator:
    module: genai_agent.tools.model_generator
    class: ModelGeneratorTool
  
  diagram_generator:
    module: genai_agent.tools.diagram_generator
    class: DiagramGeneratorTool
  
  svg_processor:
    module: genai_agent.tools.svg_processor
    class: SVGProcessorTool
"""
    with open(os.path.join(base_path, "config.yaml"), 'w') as f:
        f.write(config_yaml)
    
    # README file
    readme_md = """# GenAI Agent - 3D Scene Generation Framework

A framework for AI-driven 3D scene generation, integrating large language models, Blender, and other tools.

## Architecture

The system follows a microservices architecture with the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Interface Layer                      │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                         Agent Core Layer                         │
└───┬─────────────┬─────────────┬─────────────┬─────────────┬─────┘
    │             │             │             │             │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│  LLM   │     │ Tool   │     │ Scene  │     │ Asset  │     │ Memory │
│Service │     │Registry│     │Manager │     │Manager │     │Service │
└───┬───┘     └───┬───┘     └───┬───┘     └───┬───┘     └───┬───┘
    │             │             │             │             │
┌───▼─────────────▼─────────────▼─────────────▼─────────────▼───┐
│                       Redis Message Bus                        │
└───┬─────────────┬─────────────┬─────────────┬─────────────┬───┘
    │             │             │             │             │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│SceneX  │     │Blender │     │Hunyuan │     │Diagram │     │ SVG    │
│Service │     │Service │     │Service │     │Service │     │Service │
└───────┘     └───────┘     └───────┘     └───────┘     └───────┘
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your environment in `config.yaml`
4. Run the application: `python run.py`

## Components

- **Agent Core**: Central orchestration component
- **LLM Service**: Integration with language models
- **Tool Registry**: Framework for tool registration and discovery
- **Redis Message Bus**: Communication backbone between services
- **Scene Manager**: Management of 3D scenes
- **Blender Service**: Integration with Blender

## Usage

```python
from genai_agent.agent import GenAIAgent

# Initialize agent with configuration
agent = GenAIAgent(config)

# Process instruction
result = await agent.process_instruction(
    "Create a scene with a red cube on a blue plane"
)
```

## License

MIT License
"""
    with open(os.path.join(base_path, "README.md"), 'w') as f:
        f.write(readme_md)
    
    # Requirements file
    requirements_txt = """# Core dependencies
aiohttp>=3.8.5
pyyaml>=6.0
redis>=4.6.0
requests>=2.31.0
tqdm>=4.66.1

# Development dependencies
black>=23.7.0
flake8>=6.1.0
pytest>=7.4.0
pytest-asyncio>=0.21.1

# Optional dependencies
mermaid-cli>=0.1.3  # For diagram generation
svglib>=1.5.1       # For SVG processing
"""
    with open(os.path.join(base_path, "requirements.txt"), 'w') as f:
        f.write(requirements_txt)
    
    # Run script
    run_py = """#!/usr/bin/env python3
\"\"\"
Main entry point for GenAI Agent
\"\"\"

import os
import sys
import logging
import argparse
import asyncio
import yaml
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from genai_agent.agent import GenAIAgent
from env_loader import get_env, get_config


def load_config(config_path="config.yaml"):
    \"\"\"Load configuration from file\"\"\"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

async def agent_shell(config):
    \"\"\"Interactive shell for agent\"\"\"
    agent = GenAIAgent(config)
    print("GenAI Agent Shell - Enter instructions or 'exit' to quit")
    
    while True:
        try:
            instruction = input("\\n> ")
            if instruction.lower() in ['exit', 'quit']:
                break
                
            result = await agent.process_instruction(instruction)
            print("\\nResult:\\n")
            print(result)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("Exiting shell")

def handle_ollama(args):
    \"\"\"Handle Ollama-related commands\"\"\"
    if args.ollama_command == 'start':
        print("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"])
        print("Ollama server started")
    elif args.ollama_command == 'pull':
        if not args.model:
            print("Error: Model name is required for 'pull' command")
            return
        print(f"Pulling model {args.model}...")
        subprocess.run(["ollama", "pull", args.model])
    elif args.ollama_command == 'list':
        print("Available models:")
        subprocess.run(["ollama", "list"])
    else:
        print(f"Unknown Ollama command: {args.ollama_command}")

def main():
    \"\"\"Main entry point\"\"\"
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
    ollama_parser.add_argument('ollama_command', choices=['start', 'pull', 'list'], help='Ollama command')
    ollama_parser.add_argument('model', nargs='?', help='Model name for pull command')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handle commands
    if args.command == 'shell':
        config = load_config(args.config)
        asyncio.run(agent_shell(config))
    elif args.command == 'run':
        config = load_config(args.config)
        agent = GenAIAgent(config)
        result = asyncio.run(agent.process_instruction(args.instruction))
        print(result)
    elif args.command == 'ollama':
        handle_ollama(args)
    else:
        # Default to shell if no command specified
        config = load_config('config.yaml')
        asyncio.run(agent_shell(config))

if __name__ == "__main__":
    main()
"""
    with open(os.path.join(base_path, "run.py"), 'w') as f:
        f.write(run_py)

def main():
    parser = argparse.ArgumentParser(description="Setup GenAI Agent project structure")
    parser.add_argument("--path", type=str, default=".", help="Base path for project")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()
    
    # Create directory structure
    create_directory_structure(args.path, PROJECT_STRUCTURE, args.overwrite)
    
    # Populate core files
    populate_core_files(args.path)
    
    print("\nProject structure created successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Update config.yaml with your environment settings")
    print("3. Run the application: python run.py")

if __name__ == "__main__":
    main()
