"""
GenAI Agent core module
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from genai_agent.services.llm import LLMService
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.registry import ToolRegistry
from genai_agent.core.task_manager import TaskManager
from genai_agent.core.context_manager import ContextManager
from genai_agent.services.memory import MemoryService

logger = logging.getLogger(__name__)

class GenAIAgent:
    """
    Main agent class for orchestrating all components
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the GenAI Agent with configuration
        
        Args:
            config: Dictionary containing configuration for all components
        """
        self.config = config
        logger.info("Initializing GenAI Agent")
        
        # Initialize services
        self.redis_bus = RedisMessageBus(config.get('services', {}).get('redis', {}))
        self.llm_service = LLMService(config.get('services', {}).get('llm', {}))
        self.memory_service = MemoryService(self.redis_bus)
        
        # Initialize core components
        self.context_manager = ContextManager(self.memory_service)
        self.tool_registry = ToolRegistry()
        self.task_manager = TaskManager(
            llm_service=self.llm_service,
            tool_registry=self.tool_registry,
            context_manager=self.context_manager
        )
        
        # Register tools
        self._register_tools()
        
        logger.info("GenAI Agent initialized successfully")
    
    def _register_tools(self):
        """Register all enabled tools from configuration"""
        tool_config = self.config.get('tools', {})
        enabled_tools = tool_config.get('enabled', [])
        
        for tool_name in enabled_tools:
            self._register_tool(tool_name, tool_config.get(tool_name, {}))
    
    def _register_tool(self, tool_name: str, tool_config: Dict[str, Any]):
        """Register a specific tool"""
        # Import the tool class dynamically
        try:
            module_path = f"genai_agent.tools.{tool_name}"
            module = __import__(module_path, fromlist=[''])
            # Handle special case for tool names
            if tool_name == 'scenex_tool':
                tool_class = getattr(module, 'SceneXTool')
            elif tool_name == 'svg_processor':
                tool_class = getattr(module, 'SVGProcessorTool')
            else:
                tool_class = getattr(module, self._to_camel_case(tool_name) + 'Tool')
            
            # Initialize tool with appropriate services
            tool = tool_class(self.redis_bus, tool_config)
            
            # Register tool
            self.tool_registry.register_tool(tool_name, tool)
            logger.info(f"Registered tool: {tool_name}")
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to register tool {tool_name}: {str(e)}")
    
    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """Convert snake_case to CamelCase"""
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
    
    async def process_instruction(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a natural language instruction
        
        Args:
            instruction: The user instruction to process
            context: Optional context information
            
        Returns:
            Processing result as a dictionary
        """
        logger.info(f"Processing instruction: {instruction}")
        
        # Start services if not already started
        await self.redis_bus.start()
        
        # Update context if provided
        if context:
            for key, value in context.items():
                await self.context_manager.update_context(key, value)
        
        # Get full context
        full_context = await self.context_manager.get_full_context()
        
        # Plan execution
        execution_plan = await self.task_manager.plan_execution(instruction, full_context)
        
        # Execute plan
        result = await self.task_manager.execute_plan(execution_plan)
        
        logger.info("Instruction processing completed")
        return result
    
    async def cleanup(self):
        """Clean up resources"""
        await self.redis_bus.stop()
        logger.info("GenAI Agent resources cleaned up")
