"""
Hunyuan-3D Tool for high-quality text-to-3D model generation
"""

import logging
import os
from typing import Dict, Any, Optional

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.integrations.hunyuan_3d import Hunyuan3DIntegration

logger = logging.getLogger(__name__)

class Hunyuan3DTool(Tool):
    """
    Tool for using Hunyuan-3D to generate high-quality 3D models from text descriptions
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the Hunyuan-3D Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
                - hunyuan_path: Path to Hunyuan-3D installation
                - use_gpu: Whether to use GPU (default: True)
                - device: GPU device to use (default: cuda:0)
                - output_dir: Directory for output models
                - supported_formats: List of supported output formats
        """
        super().__init__(
            name="hunyuan_3d",
            description="Generate high-quality 3D models from text descriptions using Hunyuan-3D"
        )
        
        self.redis_bus = redis_bus
        self.config = config
        
        # Output directory
        self.output_dir = config.get('output_dir', 'output/hunyuan/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the Hunyuan-3D integration
        integration_config = config.copy()
        integration_config['output_dir'] = self.output_dir
        self.hunyuan_3d = Hunyuan3DIntegration(integration_config)
        
        # Log status
        if self.hunyuan_3d.is_available:
            logger.info(f"Hunyuan-3D tool initialized successfully (version: {self.hunyuan_3d.version})")
        else:
            logger.warning("Hunyuan-3D integration is not available")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Hunyuan-3D operations
        
        Args:
            parameters: Operation parameters
                - operation: Operation to perform (generate_model, convert_format)
                - prompt: Text description of the model to generate
                - format: Output format (obj, glb, gltf, usdz)
                - name: Model name
                - resolution: Model resolution
                - steps: Number of generation steps
                - seed: Random seed (optional)
                - input_path: Path to input model (for convert_format)
                - output_format: Output format (for convert_format)
                
        Returns:
            Operation result
        """
        operation = parameters.get('operation', 'generate_model')
        
        # Check if Hunyuan-3D is available
        if not self.hunyuan_3d.is_available:
            return {
                'status': 'error',
                'error': 'Hunyuan-3D integration is not available'
            }
        
        # Forward the operation to the integration
        result = await self.hunyuan_3d.execute(operation, parameters)
        
        # If the operation was successful and we have a model
        if result.get('status') == 'success' and 'model_path' in result:
            model_path = result['model_path']
            
            # If the asset manager is available, register the model
            asset_manager = await self._get_asset_manager()
            if asset_manager:
                try:
                    # Store the model as an asset
                    asset_id = await asset_manager.store_asset(model_path, {
                        'name': result.get('model_name', os.path.basename(model_path)),
                        'type': 'hunyuan_model',
                        'format': result.get('format', 'unknown'),
                        'prompt': parameters.get('prompt', ''),
                        'resolution': parameters.get('resolution', 256),
                        'steps': parameters.get('steps', 50),
                        'seed': parameters.get('seed')
                    }, asset_type='model')
                    
                    # Add asset ID to the result
                    result['asset_id'] = asset_id
                except Exception as e:
                    logger.warning(f"Failed to register model as asset: {str(e)}")
        
        return result
    
    async def _get_asset_manager(self) -> Optional[Any]:
        """Get the asset manager service if available"""
        try:
            response = await self.redis_bus.call_rpc('service:get_by_name', {'service_name': 'asset_manager'})
            if 'error' not in response:
                return response.get('service')
        except Exception as e:
            logger.warning(f"Failed to get asset manager: {str(e)}")
        
        return None
