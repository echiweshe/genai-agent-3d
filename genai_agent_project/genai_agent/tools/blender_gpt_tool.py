"""
BlenderGPT Tool for generating and executing Blender scripts from natural language
"""

import logging
import os
from typing import Dict, Any, Optional

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.integrations.blender_gpt import BlenderGPTIntegration

logger = logging.getLogger(__name__)

class BlenderGPTTool(Tool):
    """
    Tool for using BlenderGPT to generate and execute Blender scripts from natural language
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the BlenderGPT Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
                - blender_path: Path to Blender executable
                - blendergpt_path: Path to BlenderGPT installation
                - api_key: OpenAI API key (if needed)
                - model: Model to use (default: gpt-4)
                - output_dir: Directory for output scripts and models
        """
        super().__init__(
            name="blender_gpt",
            description="Generate and execute Blender scripts from natural language using BlenderGPT"
        )
        
        self.redis_bus = redis_bus
        self.config = config
        
        # Output directory
        self.output_dir = config.get('output_dir', 'output/blendergpt/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the BlenderGPT integration
        self.blender_gpt = BlenderGPTIntegration(config)
        
        # Log status
        if self.blender_gpt.is_available:
            logger.info(f"BlenderGPT tool initialized successfully (version: {self.blender_gpt.version})")
        else:
            logger.warning("BlenderGPT integration is not available")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute BlenderGPT operations
        
        Args:
            parameters: Operation parameters
                - operation: Operation to perform (generate_script, execute_script, chat)
                - prompt: Natural language prompt (for generate_script and chat)
                - script: Blender script to execute (for execute_script)
                - script_path: Path to script file (alternative to script)
                - execute: Whether to execute the generated script (for generate_script)
                - history: Previous chat history (for chat)
                - model: Model to use (optional)
                - format: Output format (for execute_script)
                
        Returns:
            Operation result
        """
        operation = parameters.get('operation', 'generate_script')
        
        # Check if BlenderGPT is available
        if not self.blender_gpt.is_available:
            return {
                'status': 'error',
                'error': 'BlenderGPT integration is not available'
            }
        
        result = {}
        
        if operation == 'generate_script':
            # Generate a Blender script from natural language
            prompt = parameters.get('prompt')
            if not prompt:
                return {
                    'status': 'error',
                    'error': 'No prompt provided'
                }
            
            model = parameters.get('model', self.config.get('model', 'gpt-4'))
            
            # Generate the script
            gen_result = await self.blender_gpt.execute('generate_script', {
                'prompt': prompt,
                'model': model
            })
            
            if gen_result.get('status') != 'success':
                return gen_result
            
            # Save the script to file
            script = gen_result.get('script')
            script_path = os.path.join(self.output_dir, f"script_{hash(prompt) % 10000:04d}.py")
            with open(script_path, 'w') as f:
                f.write(script)
            
            result = {
                'status': 'success',
                'script': script,
                'script_path': script_path,
                'model': model
            }
            
            # Execute the script if requested
            if parameters.get('execute', False):
                exec_result = await self.blender_gpt.execute('execute_script', {
                    'script': script,
                    'format': parameters.get('format', 'json')
                })
                
                result['execution'] = exec_result
                
                # Update overall status based on execution result
                if exec_result.get('status') != 'success':
                    result['status'] = 'partial_success'
                    result['message'] = 'Script generated successfully, but execution failed'
            
        elif operation == 'execute_script':
            # Execute a Blender script
            script = parameters.get('script')
            script_path = parameters.get('script_path')
            
            if not script and not script_path:
                return {
                    'status': 'error',
                    'error': 'No script or script path provided'
                }
            
            result = await self.blender_gpt.execute('execute_script', {
                'script': script,
                'script_path': script_path,
                'format': parameters.get('format', 'json')
            })
            
        elif operation == 'chat':
            # Chat with BlenderGPT
            message = parameters.get('message')
            if not message:
                return {
                    'status': 'error',
                    'error': 'No message provided'
                }
            
            history = parameters.get('history', [])
            model = parameters.get('model', self.config.get('model', 'gpt-4'))
            
            result = await self.blender_gpt.execute('chat', {
                'message': message,
                'history': history,
                'model': model
            })
            
        else:
            result = {
                'status': 'error',
                'error': f"Unsupported operation: {operation}"
            }
        
        return result
