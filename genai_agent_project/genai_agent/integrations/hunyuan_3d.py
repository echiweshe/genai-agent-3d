"""
Integration with Hunyuan-3D 2.0 (https://github.com/Tencent/Hunyuan3D-2)

This integration allows using Hunyuan-3D for high-quality text-to-3D model generation.
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

class Hunyuan3DIntegration(BaseIntegration):
    """Integration with Hunyuan-3D 2.0"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Hunyuan-3D integration
        
        Args:
            config: Integration configuration
                - hunyuan_path: Path to Hunyuan-3D installation
                - use_gpu: Whether to use GPU (default: True)
                - device: GPU device to use (default: cuda:0)
                - output_dir: Directory for output models (default: output/hunyuan)
                - supported_formats: List of supported output formats
        """
        super().__init__(config)
    
    def _initialize(self):
        """Initialize the Hunyuan-3D integration and check if it's available"""
        self.hunyuan_path = self.config.get('hunyuan_path')
        
        if not self.hunyuan_path:
            raise ValueError("Hunyuan-3D path is required")
        
        if not os.path.exists(self.hunyuan_path):
            raise FileNotFoundError(f"Hunyuan-3D not found at {self.hunyuan_path}")
        
        # Check for main script
        main_script = os.path.join(self.hunyuan_path, 'run.py')
        if not os.path.exists(main_script):
            raise FileNotFoundError(f"Hunyuan-3D main script not found at {main_script}")
        
        # Set options
        self.use_gpu = self.config.get('use_gpu', True)
        self.device = self.config.get('device', 'cuda:0')
        self.output_dir = self.config.get('output_dir', 'output/hunyuan')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Supported output formats
        self.supported_formats = self.config.get('supported_formats', ['obj', 'glb', 'gltf', 'usdz'])
        
        # Try to get the version
        try:
            # Look for version in requirements.txt or README
            version_file = os.path.join(self.hunyuan_path, 'VERSION')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    self._version = f.read().strip()
            else:
                # Try to get version from git
                process = subprocess.run(
                    ['git', '-C', self.hunyuan_path, 'describe', '--tags'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if process.returncode == 0:
                    self._version = process.stdout.strip()
                else:
                    self._version = "Unknown"
        except Exception as e:
            logger.warning(f"Failed to read Hunyuan-3D version: {str(e)}")
            self._version = "Unknown"
    
    def get_capabilities(self) -> List[str]:
        """Get the list of capabilities provided by Hunyuan-3D"""
        return [
            'text_to_3d_model',
            'high_quality_model_generation',
            'texture_generation',
            'multi_view_consistent_generation'
        ]
    
    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation using Hunyuan-3D
        
        Args:
            operation: Operation to execute
                - generate_model: Generate a 3D model from a text prompt
                - convert_format: Convert a model to a different format
            parameters: Operation parameters
                
        Returns:
            Operation result
        """
        if not self.is_available:
            return {
                'status': 'error',
                'error': 'Hunyuan-3D integration is not available'
            }
        
        if operation == 'generate_model':
            return await self._generate_model(parameters)
        elif operation == 'convert_format':
            return await self._convert_format(parameters)
        else:
            return {
                'status': 'error',
                'error': f"Unsupported operation: {operation}"
            }
    
    async def _generate_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a 3D model from a text prompt
        
        Args:
            parameters:
                - prompt: Text prompt
                - format: Output format (obj, glb, gltf, usdz)
                - name: Model name
                - resolution: Model resolution
                - steps: Number of generation steps
                - seed: Random seed (optional)
                
        Returns:
            Generated model info
        """
        prompt = parameters.get('prompt')
        if not prompt:
            return {
                'status': 'error',
                'error': 'No prompt provided'
            }
        
        output_format = parameters.get('format', 'obj')
        if output_format not in self.supported_formats:
            return {
                'status': 'error',
                'error': f"Unsupported format: {output_format}. Supported formats: {', '.join(self.supported_formats)}"
            }
        
        name = parameters.get('name', f"hunyuan_model_{hash(prompt) % 10000:04d}")
        resolution = parameters.get('resolution', 256)
        steps = parameters.get('steps', 50)
        seed = parameters.get('seed')
        
        # Create a temporary file for the config
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            config = {
                "prompt": prompt,
                "output_format": output_format,
                "resolution": resolution,
                "steps": steps,
            }
            
            if seed is not None:
                config["seed"] = seed
                
            json.dump(config, temp_file)
            config_path = temp_file.name
        
        try:
            # Prepare the output path
            output_path = os.path.join(self.output_dir, f"{name}.{output_format}")
            
            # Prepare the command to run Hunyuan-3D
            command = [
                sys.executable,
                os.path.join(self.hunyuan_path, 'run.py'),
                '--config', config_path,
                '--output', output_path
            ]
            
            if self.use_gpu:
                command.extend(['--device', self.device])
            else:
                command.extend(['--device', 'cpu'])
            
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
                    'error': f"Hunyuan-3D failed with exit code {process.returncode}",
                    'stderr': stderr.decode()
                }
            
            # Check if the output file exists
            if not os.path.exists(output_path):
                return {
                    'status': 'error',
                    'error': f"Output file not found at {output_path}"
                }
            
            return {
                'status': 'success',
                'model_path': output_path,
                'model_name': name,
                'format': output_format,
                'prompt': prompt,
                'resolution': resolution,
                'steps': steps,
                'seed': seed
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            # Clean up the temporary file
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    async def _convert_format(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a model to a different format
        
        Args:
            parameters:
                - input_path: Path to input model
                - output_format: Output format
                - name: Output name (optional)
                
        Returns:
            Conversion result
        """
        input_path = parameters.get('input_path')
        if not input_path:
            return {
                'status': 'error',
                'error': 'No input path provided'
            }
        
        if not os.path.exists(input_path):
            return {
                'status': 'error',
                'error': f"Input file not found at {input_path}"
            }
        
        output_format = parameters.get('output_format')
        if not output_format:
            return {
                'status': 'error',
                'error': 'No output format provided'
            }
        
        if output_format not in self.supported_formats:
            return {
                'status': 'error',
                'error': f"Unsupported format: {output_format}. Supported formats: {', '.join(self.supported_formats)}"
            }
        
        name = parameters.get('name')
        if not name:
            # Use the input filename with the new extension
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            name = f"{base_name}_converted"
        
        # Prepare the output path
        output_path = os.path.join(self.output_dir, f"{name}.{output_format}")
        
        try:
            # Prepare the command to run the conversion
            command = [
                sys.executable,
                os.path.join(self.hunyuan_path, 'tools', 'convert.py'),
                '--input', input_path,
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
                    'error': f"Conversion failed with exit code {process.returncode}",
                    'stderr': stderr.decode()
                }
            
            # Check if the output file exists
            if not os.path.exists(output_path):
                return {
                    'status': 'error',
                    'error': f"Output file not found at {output_path}"
                }
            
            return {
                'status': 'success',
                'input_path': input_path,
                'output_path': output_path,
                'format': output_format
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
