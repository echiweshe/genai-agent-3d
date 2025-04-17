"""
TRELLIS Tool for advanced reasoning and planning
"""

import logging
import os
import json
from typing import Dict, Any, Optional, List

from genai_agent.tools.registry import Tool
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.integrations.trellis import TrellisIntegration

logger = logging.getLogger(__name__)

class TrellisTool(Tool):
    """
    Tool for using Microsoft TRELLIS for advanced reasoning and planning
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any]):
        """
        Initialize the TRELLIS Tool
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Tool configuration
                - trellis_path: Path to TRELLIS installation
                - api_key: API key for language models (if needed)
                - model: Language model to use (default: gpt-4)
                - reasoning_examples_path: Path to reasoning examples
                - output_dir: Directory for output files
        """
        super().__init__(
            name="trellis",
            description="Advanced reasoning and planning using Microsoft TRELLIS"
        )
        
        self.redis_bus = redis_bus
        self.config = config
        
        # Output directory
        self.output_dir = config.get('output_dir', 'output/trellis/')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the TRELLIS integration
        self.trellis = TrellisIntegration(config)
        
        # Log status
        if self.trellis.is_available:
            logger.info(f"TRELLIS tool initialized successfully (version: {self.trellis.version})")
        else:
            logger.warning("TRELLIS integration is not available")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute TRELLIS operations
        
        Args:
            parameters: Operation parameters
                - operation: Operation to perform (reason, plan, execute_plan, knowledge_graph)
                - query: Question or problem to reason about (for reason)
                - context: Additional context (optional)
                - goal: Goal to achieve (for plan)
                - constraints: Constraints to consider (for plan, optional)
                - resources: Available resources (for plan, optional)
                - plan: Plan to execute (for execute_plan)
                - tools: Tools available for execution (for execute_plan, optional)
                - topic: Topic for the knowledge graph (for knowledge_graph)
                - save: Whether to save results to file (default: True)
                - model: Language model to use (optional)
                
        Returns:
            Operation result
        """
        operation = parameters.get('operation', 'reason')
        
        # Check if TRELLIS is available
        if not self.trellis.is_available:
            return {
                'status': 'error',
                'error': 'TRELLIS integration is not available'
            }
        
        # Execute the operation
        result = await self.trellis.execute(operation, parameters)
        
        # If save is enabled, save the result to a file
        if parameters.get('save', True) and result.get('status') == 'success':
            try:
                # Generate a filename based on the operation
                filename = self._generate_filename(operation, parameters)
                file_path = os.path.join(self.output_dir, filename)
                
                # Save the result as JSON
                with open(file_path, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Add the file path to the result
                result['file_path'] = file_path
            except Exception as e:
                logger.warning(f"Failed to save result to file: {str(e)}")
        
        return result
    
    def _generate_filename(self, operation: str, parameters: Dict[str, Any]) -> str:
        """
        Generate a filename based on the operation and parameters
        
        Args:
            operation: Operation being performed
            parameters: Operation parameters
            
        Returns:
            Generated filename
        """
        # Base name on the operation
        if operation == 'reason':
            # Use the first few words of the query
            query = parameters.get('query', 'reasoning')
            base_name = '_'.join(query.split()[:5])
            return f"reasoning_{self._sanitize_filename(base_name)}.json"
        
        elif operation == 'plan':
            # Use the goal
            goal = parameters.get('goal', 'plan')
            base_name = '_'.join(goal.split()[:5])
            return f"plan_{self._sanitize_filename(base_name)}.json"
        
        elif operation == 'execute_plan':
            # Use a simple name with timestamp
            import time
            timestamp = int(time.time())
            return f"execute_plan_{timestamp}.json"
        
        elif operation == 'knowledge_graph':
            # Use the topic
            topic = parameters.get('topic', 'knowledge')
            base_name = self._sanitize_filename(topic)
            return f"knowledge_graph_{base_name}.json"
        
        else:
            # Default filename with timestamp
            import time
            timestamp = int(time.time())
            return f"trellis_{operation}_{timestamp}.json"
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize a string for use as a filename
        
        Args:
            name: Input string
            
        Returns:
            Sanitized filename
        """
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        
        # Remove characters that are not allowed in filenames
        import re
        name = re.sub(r'[^\w\-\.]', '', name)
        
        # Limit length
        name = name[:50]
        
        return name.lower()
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get a list of tools available for plan execution
        
        Returns:
            List of available tools
        """
        tools = []
        
        try:
            # Get all registered tools
            response = await self.redis_bus.call_rpc('tool:list', {})
            
            if 'error' not in response:
                registered_tools = response.get('tools', [])
                
                for tool_info in registered_tools:
                    # Skip this tool to avoid recursion
                    if tool_info.get('name') == self.name:
                        continue
                    
                    # Create a wrapper for the tool
                    tool_wrapper = {
                        'name': tool_info.get('name'),
                        'description': tool_info.get('description', ''),
                        'parameters': {
                            'type': 'object',
                            'properties': {}
                        }
                    }
                    
                    # Add the tool to the list
                    tools.append(tool_wrapper)
        except Exception as e:
            logger.warning(f"Failed to get available tools: {str(e)}")
        
        return tools
    
    async def spatial_reasoning(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Specialized reasoning about spatial relationships
        
        Args:
            parameters: Operation parameters
                - scene_description: Description of the scene
                - question: Question about spatial relationships
                - context: Additional context (optional)
                - model: Language model to use (optional)
                
        Returns:
            Spatial reasoning result
        """
        scene_description = parameters.get('scene_description')
        question = parameters.get('question')
        
        if not scene_description:
            return {
                'status': 'error',
                'error': 'No scene description provided'
            }
        
        if not question:
            return {
                'status': 'error',
                'error': 'No question provided'
            }
        
        # Construct a specialized spatial reasoning query
        context = parameters.get('context', '')
        combined_query = f"Scene: {scene_description}\n\nSpatial reasoning question: {question}"
        
        if context:
            combined_query += f"\n\nAdditional context: {context}"
        
        # Use the general reasoning function with spatial context
        return await self.trellis.execute('reason', {
            'query': combined_query,
            'context': "This is a spatial reasoning problem that requires understanding 3D relationships between objects.",
            'model': parameters.get('model', self.config.get('model', 'gpt-4')),
            'max_steps': parameters.get('max_steps', 5)
        })
