"""
LLM Settings Manager for GenAI Agent 3D

This module provides utilities for managing LLM settings, including:
- Getting current LLM settings
- Updating LLM settings from the UI
- Saving settings to config.yaml
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
import dotenv
from pathlib import Path

# Import the enhanced environment loader
from .enhanced_env_loader import get_api_key_for_provider, get_llm_config_from_env

# Configure logging
logger = logging.getLogger(__name__)

class LLMSettingsManager:
    """Manager for LLM settings in GenAI Agent 3D"""
    
    def __init__(self, config_path=None, env_path=None):
        """
        Initialize the settings manager
        
        Args:
            config_path: Path to config.yaml (default: project_root/config.yaml)
            env_path: Path to .env file (default: project_root/.env)
        """
        # Set up paths
        self.project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.config_path = config_path or self.project_root / "config.yaml"
        self.env_path = env_path or self.project_root / ".env"
        
        # Load settings
        self.config = self._load_config()
        self.load_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.yaml"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config from {self.config_path}: {str(e)}")
            return {}
    
    def load_env_vars(self) -> Dict[str, str]:
        """Load environment variables from .env file"""
        try:
            # Load .env file
            dotenv.load_dotenv(self.env_path)
            
            # Collect relevant environment variables
            env_vars = {
                'LLM_PROVIDER': os.environ.get('LLM_PROVIDER'),
                'LLM_MODEL': os.environ.get('LLM_MODEL'),
                'LLM_TYPE': os.environ.get('LLM_TYPE'),
                'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY'),
                'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
                'STABILITY_API_KEY': os.environ.get('STABILITY_API_KEY'),
            }
            
            return {k: v for k, v in env_vars.items() if v is not None}
        except Exception as e:
            logger.error(f"Error loading environment variables: {str(e)}")
            return {}
    
    def get_current_llm_settings(self) -> Dict[str, Any]:
        """Get current LLM settings"""
        # Start with settings from config.yaml
        settings = {}
        
        if 'llm' in self.config:
            settings = {
                'provider': self.config['llm'].get('provider', 'ollama'),
                'model': self.config['llm'].get('model', 'llama3'),
                'type': self.config['llm'].get('type', 'local'),
                'timeout': self.config['llm'].get('timeout', 300),
                'generation_timeout': self.config['llm'].get('generation_timeout', 900)
            }
        
        # Override with environment variables if available
        env_config = get_llm_config_from_env()
        settings.update(env_config)
        
        # Add available providers and models
        settings['available_providers'] = self._get_available_providers()
        
        # Add API key status (whether keys are set, not the actual keys)
        settings['api_keys'] = self._get_api_key_status()
        
        return settings
    
    def _get_available_providers(self) -> List[Dict[str, Any]]:
        """Get available LLM providers from config"""
        providers = []
        
        if 'llm' in self.config and 'providers' in self.config['llm']:
            for provider_id, provider_data in self.config['llm']['providers'].items():
                provider_info = {
                    'id': provider_id,
                    'name': provider_id.capitalize(),
                    'type': provider_data.get('type', 'local'),
                    'models': provider_data.get('models', [])
                }
                providers.append(provider_info)
        else:
            # Fallback if providers not defined in config
            providers = [
                {
                    'id': 'ollama',
                    'name': 'Ollama',
                    'type': 'local',
                    'models': [
                        {'id': 'llama3', 'name': 'Llama 3'},
                        {'id': 'llama3:latest', 'name': 'Llama 3 (Latest)'}
                    ]
                },
                {
                    'id': 'anthropic',
                    'name': 'Anthropic',
                    'type': 'cloud',
                    'models': [
                        {'id': 'claude-3-sonnet-20240229', 'name': 'Claude 3 Sonnet'},
                        {'id': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus'},
                        {'id': 'claude-3-haiku-20240307', 'name': 'Claude 3 Haiku'},
                        {'id': 'claude-3.5-sonnet-20250626', 'name': 'Claude 3.5 Sonnet'}
                    ]
                },
                {
                    'id': 'openai',
                    'name': 'OpenAI',
                    'type': 'cloud',
                    'models': [
                        {'id': 'gpt-4o', 'name': 'GPT-4o'},
                        {'id': 'gpt-4', 'name': 'GPT-4'},
                        {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo'}
                    ]
                }
            ]
        
        return providers
    
    def _get_api_key_status(self) -> Dict[str, bool]:
        """Get API key status (whether keys are set, not the actual keys)"""
        return {
            'anthropic': bool(get_api_key_for_provider('anthropic')),
            'openai': bool(get_api_key_for_provider('openai')),
            'stability': bool(get_api_key_for_provider('stability'))
        }
    
    def update_llm_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update LLM settings
        
        Args:
            settings: Dictionary with new settings
                - provider: LLM provider (e.g., 'ollama', 'anthropic')
                - model: LLM model (e.g., 'llama3', 'claude-3-sonnet')
                - type: Provider type ('local' or 'cloud')
                - api_key: API key (only if updating a key)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update config.yaml
            if 'provider' in settings or 'model' in settings or 'type' in settings:
                self._update_config_yaml(settings)
            
            # Update API key in .env if provided
            if 'api_key' in settings and settings.get('provider'):
                provider = settings['provider']
                api_key = settings['api_key']
                self._update_api_key(provider, api_key)
            
            # Update environment variables in .env
            env_updates = {}
            if 'provider' in settings:
                env_updates['LLM_PROVIDER'] = settings['provider']
            if 'model' in settings:
                env_updates['LLM_MODEL'] = settings['model']
            if 'type' in settings:
                env_updates['LLM_TYPE'] = settings['type']
                
            if env_updates:
                self._update_env_file(env_updates)
            
            return True
        except Exception as e:
            logger.error(f"Error updating LLM settings: {str(e)}")
            return False
    
    def _update_config_yaml(self, settings: Dict[str, Any]) -> bool:
        """Update config.yaml with new settings"""
        try:
            # Load current config
            config = self._load_config()
            
            # Ensure llm section exists
            if 'llm' not in config:
                config['llm'] = {}
            
            # Update settings
            if 'provider' in settings:
                config['llm']['provider'] = settings['provider']
            if 'model' in settings:
                config['llm']['model'] = settings['model']
            if 'type' in settings:
                config['llm']['type'] = settings['type']
            
            # Write updated config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Update internal config
            self.config = config
            
            return True
        except Exception as e:
            logger.error(f"Error updating config.yaml: {str(e)}")
            return False
    
    def _update_api_key(self, provider: str, api_key: str) -> bool:
        """
        Update API key for a provider in .env file
        
        Args:
            provider: Provider name (e.g., 'anthropic', 'openai')
            api_key: API key
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Map provider to environment variable
        provider_env_map = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'stability': 'STABILITY_API_KEY'
        }
        
        # Get environment variable name
        env_var = provider_env_map.get(provider.lower())
        if not env_var:
            logger.warning(f"Unknown provider: {provider}. Cannot update API key.")
            return False
        
        # Update .env file
        return self._update_env_file({env_var: api_key})
    
    def _update_env_file(self, updates: Dict[str, str]) -> bool:
        """
        Update environment variables in .env file
        
        Args:
            updates: Dictionary of environment variables to update
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load current .env content
            env_content = ""
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    env_content = f.read()
            
            # Process each update
            for env_var, value in updates.items():
                # Check if variable already exists in .env
                if f"{env_var}=" in env_content:
                    # Replace existing value
                    lines = env_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith(f"{env_var}="):
                            lines[i] = f"{env_var}={value}"
                    env_content = '\n'.join(lines)
                else:
                    # Add new variable
                    if not env_content.endswith('\n'):
                        env_content += '\n'
                    env_content += f"{env_var}={value}\n"
            
            # Write updated content
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # Reload environment variables
            dotenv.load_dotenv(self.env_path, override=True)
            
            # Update os.environ
            for env_var, value in updates.items():
                os.environ[env_var] = value
            
            return True
        except Exception as e:
            logger.error(f"Error updating .env file: {str(e)}")
            return False
