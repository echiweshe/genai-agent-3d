"""
Integration with BlenderGPT (https://github.com/gd3kr/BlenderGPT)

This integration allows using BlenderGPT for generating and executing Blender scripts
from natural language descriptions.
"""

import os
import sys
import logging
import subprocess
import tempfile
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple

from genai_agent.integrations.base import BaseIntegration

logger = logging.getLogger(__name__)

class BlenderGPTIntegration(BaseIntegration):
    """Integration with BlenderGPT"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the BlenderGPT integration
        
        Args:
            config: Integration configuration
                - blender_path: Path to Blender executable
                - blendergpt_path: Path to BlenderGPT installation
                - api_key: OpenAI API key (if needed)
                - model: Model to use (default: gpt-4)
        """
        super().__init__(config)
    
    def _initialize(self):
        """Initialize the BlenderGPT integration and check if it's available"""
        self.blender_path = self.config.get('blender_path')
        self.blendergpt_path = self.config.get('blendergpt_path')
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'gpt-4')
        
        # Check if paths are provided
        if not self.blender_path:
            raise ValueError("Blender path is required")
            
        if not self.blendergpt_path:
            raise ValueError("BlenderGPT path is required")
        
        # Check if paths exist
        if not os.path.exists(self.blender_path):
            raise FileNotFoundError(f"Blender executable not found at {self.blender_path}")
            
        if not os.path.exists(self.blendergpt_path):
            raise FileNotFoundError(f"BlenderGPT not found at {self.blendergpt_path}")
        
        # Check if the addon is installed correctly
        addon_path = os.path.join(self.blendergpt_path, 'blendergpt_addon.py')
        if not os.path.exists(addon_path):
            raise FileNotFoundError(f"BlenderGPT addon not found at {addon_path}")
        
        # Try to get the version from the addon file
        try:
            with open(addon_path, 'r') as f:
                content = f.read()
                # Look for version string
                import re
                version_match = re.search(r'"version"\s*:\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', content)
                if version_match:
                    self._version = f"{version_match.group(1)}.{version_match.group(2)}.{version_match.group(3)}"
                else:
                    self._version = "Unknown"
        except Exception as e:
            logger.warning(f"Failed to read BlenderGPT version: {str(e)}")
            self._version = "Unknown"
    
    def get_capabilities(self) -> List[str]:
        """Get the list of capabilities provided by BlenderGPT"""
        return [
            'natural_language_to_blender_script',
            'script_execution_in_blender',
            'interactive_chat'
        ]
    
    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation using BlenderGPT
        
        Args:
            operation: Operation to execute
                - generate_script: Generate a Blender script from a prompt
                - execute_script: Execute a script in Blender
                - chat: Interactive chat with BlenderGPT
            parameters: Operation parameters
                
        Returns:
            Operation result
        """
        if not self.is_available:
            return {
                'status': 'error',
                'error': 'BlenderGPT integration is not available'
            }
        
        if operation == 'generate_script':
            return await self._generate_script(parameters)
        elif operation == 'execute_script':
            return await self._execute_script(parameters)
        elif operation == 'chat':
            return await self._chat(parameters)
        else:
            return {
                'status': 'error',
                'error': f"Unsupported operation: {operation}"
            }
    
    async def _generate_script(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a Blender script from a prompt
        
        Args:
            parameters:
                - prompt: Text prompt
                - model: Model to use (optional, default: gpt-4)
                
        Returns:
            Generated script
        """
        prompt = parameters.get('prompt')
        if not prompt:
            return {
                'status': 'error',
                'error': 'No prompt provided'
            }
        
        model = parameters.get('model', self.model)
        
        # Create a temporary file for the result
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            output_path = temp_file.name
        
        try:
            # Prepare the command to run Blender with the BlenderGPT addon
            command = [
                self.blender_path,
                '--background',
                '--python',
                os.path.join(self.blendergpt_path, 'blendergpt_headless.py'),
                '--',
                '--prompt', prompt,
                '--output', output_path,
                '--model', model
            ]
            
            # Add API key if provided
            if self.api_key:
                command.extend(['--api_key', self.api_key])
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Check if the process succeeded
            if process.returncode != 0:
                return {
                    'status': 'error',
                    'error': f"BlenderGPT failed with exit code {process.returncode}",
                    'stderr': stderr.decode()
                }
            
            # Read the generated script
            with open(output_path, 'r') as f:
                script = f.read()
            
            return {
                'status': 'success',
                'script': script,
                'model': model
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            # Clean up the temporary file
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    async def _execute_script(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a script in Blender
        
        Args:
            parameters:
                - script: Script to execute
                - script_path: Path to script file (alternative to script)
                - format: Output format (json, text)
                
        Returns:
            Execution result
        """
        script = parameters.get('script')
        script_path = parameters.get('script_path')
        output_format = parameters.get('format', 'json')
        
        if not script and not script_path:
            return {
                'status': 'error',
                'error': 'No script or script path provided'
            }
        
        # If script is provided directly, write it to a temporary file
        temp_script_path = None
        if script and not script_path:
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                temp_file.write(script.encode())
                temp_script_path = temp_file.name
                script_path = temp_script_path
        
        try:
            # Create a temporary file for the result
            with tempfile.NamedTemporaryFile(suffix='.json' if output_format == 'json' else '.txt', delete=False) as temp_file:
                output_path = temp_file.name
            
            # Prepare the command to run Blender with the script
            command = [
                self.blender_path,
                '--background',
                '--python',
                script_path,
                '--',
                '--output', output_path,
                '--format', output_format
            ]
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Check if the process succeeded
            if process.returncode != 0:
                return {
                    'status': 'error',
                    'error': f"Script execution failed with exit code {process.returncode}",
                    'stderr': stderr.decode()
                }
            
            # Read the result
            with open(output_path, 'r') as f:
                if output_format == 'json':
                    try:
                        result = json.load(f)
                    except json.JSONDecodeError:
                        return {
                            'status': 'error',
                            'error': 'Failed to parse JSON output'
                        }
                else:
                    result = {
                        'output': f.read()
                    }
            
            return {
                'status': 'success',
                **result
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            # Clean up temporary files
            if temp_script_path and os.path.exists(temp_script_path):
                os.unlink(temp_script_path)
            
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    async def _chat(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interactive chat with BlenderGPT
        
        Args:
            parameters:
                - message: Chat message
                - history: Previous chat history (optional)
                - model: Model to use (optional, default: gpt-4)
                
        Returns:
            Chat response
        """
        message = parameters.get('message')
        if not message:
            return {
                'status': 'error',
                'error': 'No message provided'
            }
        
        history = parameters.get('history', [])
        model = parameters.get('model', self.model)
        
        # Create a temporary file for the chat history
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            json.dump(history, temp_file)
            history_path = temp_file.name
        
        # Create a temporary file for the result
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            result_path = temp_file.name
        
        try:
            # Prepare the command to run Blender with the BlenderGPT addon in chat mode
            command = [
                self.blender_path,
                '--background',
                '--python',
                os.path.join(self.blendergpt_path, 'blendergpt_chat.py'),
                '--',
                '--message', message,
                '--history', history_path,
                '--output', result_path,
                '--model', model
            ]
            
            # Add API key if provided
            if self.api_key:
                command.extend(['--api_key', self.api_key])
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Check if the process succeeded
            if process.returncode != 0:
                return {
                    'status': 'error',
                    'error': f"BlenderGPT chat failed with exit code {process.returncode}",
                    'stderr': stderr.decode()
                }
            
            # Read the result
            with open(result_path, 'r') as f:
                try:
                    result = json.load(f)
                except json.JSONDecodeError:
                    return {
                        'status': 'error',
                        'error': 'Failed to parse JSON output'
                    }
            
            return {
                'status': 'success',
                'response': result.get('response'),
                'updated_history': result.get('history')
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            # Clean up temporary files
            if os.path.exists(history_path):
                os.unlink(history_path)
            
            if os.path.exists(result_path):
                os.unlink(result_path)
