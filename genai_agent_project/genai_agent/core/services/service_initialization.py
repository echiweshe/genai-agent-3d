"""
Service Initialization Module
----------------------------
Handles direct initialization of critical services to ensure reliability
and provides a unified configuration management system.
"""

import os
import sys
import yaml
import logging
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("ServiceInitialization")

class ServiceRegistry:
    """Registry for managing critical service instances and their configuration."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.service_instances = {}
            self.config = self._load_unified_config()
            self.project_root = self._find_project_root()
            self._initialized = True
            
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Register a service instance in the registry."""
        self.service_instances[service_name] = service_instance
        logger.info(f"Registered service: {service_name}")
    
    def get_service(self, service_name: str) -> Any:
        """Get a service instance from the registry."""
        if service_name not in self.service_instances:
            logger.warning(f"Service {service_name} not found in registry")
            return None
        return self.service_instances[service_name]
    
    def list_services(self) -> List[str]:
        """List all registered services."""
        return list(self.service_instances.keys())
    
    def _find_project_root(self) -> Path:
        """Find the root directory of the project."""
        # Start with the current directory and search upward
        current_dir = Path(__file__).resolve().parent
        
        while current_dir.name:
            # Check if this is the project root by looking for key files
            if (current_dir / "config.yaml").exists() or (current_dir / ".env").exists():
                return current_dir
            
            # Check if this is the genai_agent_project directory
            if current_dir.name == "genai_agent_project":
                return current_dir
                
            # Move up one directory
            parent = current_dir.parent
            if parent == current_dir:  # Root of the filesystem
                break
            current_dir = parent
        
        # If we couldn't find a likely project root, use the current working directory
        logger.warning("Could not definitively find project root, using current directory")
        return Path(os.getcwd())
    
    def _load_unified_config(self) -> Dict[str, Any]:
        """
        Load and unify configuration from both .env and config.yaml.
        Environment variables take precedence over config.yaml values.
        """
        config = {}
        
        # Try to find .env and config.yaml in the current directory or parent directories
        for file_path in self._find_config_files():
            if file_path.name == ".env":
                logger.info(f"Loading environment variables from {file_path}")
                load_dotenv(file_path)
                # Add environment variables to config
                for key, value in os.environ.items():
                    config[key] = value
            
            elif file_path.name.endswith(".yaml") or file_path.name.endswith(".yml"):
                logger.info(f"Loading configuration from {file_path}")
                try:
                    with open(file_path, 'r') as yaml_file:
                        yaml_config = yaml.safe_load(yaml_file)
                        if yaml_config:
                            # Only override config values that aren't already set by environment variables
                            for key, value in yaml_config.items():
                                if key not in config:
                                    config[key] = value
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {str(e)}")
        
        logger.info(f"Unified configuration loaded with {len(config)} keys")
        return config
    
    def _find_config_files(self) -> List[Path]:
        """Find .env and config.yaml files in current and parent directories."""
        config_files = []
        current_dir = Path.cwd()
        
        # Check current directory and up to 3 parent directories
        for _ in range(4):
            env_file = current_dir / ".env"
            if env_file.exists():
                config_files.append(env_file)
            
            # Check for YAML files
            for yaml_file in current_dir.glob("*.yaml"):
                config_files.append(yaml_file)
            for yaml_file in current_dir.glob("*.yml"):
                config_files.append(yaml_file)
            
            # Move up one directory
            parent = current_dir.parent
            if parent == current_dir:  # Root of the filesystem
                break
            current_dir = parent
        
        return config_files
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key with fallback to default."""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value and update relevant files if needed."""
        self.config[key] = value
        
        # Update environment variable
        os.environ[key] = str(value)
        
        # Find config.yaml and update it if the key exists there
        current_dir = Path.cwd()
        for _ in range(4):  # Check current and up to 3 parent directories
            config_path = current_dir / "config.yaml"
            if config_path.exists():
                try:
                    # Load existing config
                    with open(config_path, 'r') as file:
                        yaml_config = yaml.safe_load(file) or {}
                    
                    # Update value if key exists
                    if key in yaml_config:
                        yaml_config[key] = value
                        
                        # Write back to file
                        with open(config_path, 'w') as file:
                            yaml.dump(yaml_config, file, default_flow_style=False)
                        
                        logger.info(f"Updated {key} in config.yaml")
                except Exception as e:
                    logger.error(f"Error updating config.yaml: {str(e)}")
                
                break
            
            # Move up one directory
            parent = current_dir.parent
            if parent == current_dir:  # Root of the filesystem
                break
            current_dir = parent
    
    def resolve_path(self, path: str) -> str:
        """Resolve a path relative to the project root."""
        if os.path.isabs(path):
            return path
        return str(self.project_root / path)

    def get_output_directory(self) -> str:
        """Get standardized output directory path."""
        # First check if output directory is specified in config
        output_dir = self.get_config("OUTPUT_DIRECTORY")
        
        if not output_dir:
            # Default to project_root/output
            output_dir = str(self.project_root / "output")
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Using output directory: {output_dir}")
        return output_dir
    
    def initialize_essential_services(self) -> None:
        """Initialize essential services required for the application to function."""
        from genai_agent.core.services.llm_service import LLMService
        from genai_agent.core.services.blender_service import BlenderService
        
        # Initialize and register LLM Service
        llm_service = LLMService()
        self.register_service("llm", llm_service)
        
        # Initialize and register Blender Service
        blender_service = BlenderService()
        self.register_service("blender", blender_service)
        
        logger.info("Essential services initialized")

# Global registry instance
registry = ServiceRegistry()

def get_registry() -> ServiceRegistry:
    """Get the global service registry instance."""
    return registry

def get_service(service_name: str) -> Any:
    """Get a service from the global registry."""
    return registry.get_service(service_name)

def initialize_services() -> ServiceRegistry:
    """Initialize all essential services and return the registry."""
    registry.initialize_essential_services()
    return registry
