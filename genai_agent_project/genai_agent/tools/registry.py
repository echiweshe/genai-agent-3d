"""
Tool Registry for managing and discovering tools
"""

import logging
import importlib
from typing import Dict, Any, Optional, List, Callable, Type

logger = logging.getLogger(__name__)

class Tool:
    """
    Base class for all tools
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize tool
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool with parameters
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Tool must implement execute method")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get tool information
        
        Returns:
            Tool information
        """
        return {
            "name": self.name,
            "description": self.description
        }

class ToolRegistry:
    """
    Registry for tools
    
    Provides a central registry for tools and their discovery.
    """
    
    def __init__(self):
        """Initialize tool registry"""
        self.tools = {}
        logger.info("Tool Registry initialized")
    
    def register_tool(self, tool: Tool) -> bool:
        """
        Register a tool
        
        Args:
            tool: Tool instance
            
        Returns:
            True if registered successfully, False otherwise
        """
        if tool.name in self.tools:
            logger.warning(f"Tool {tool.name} already registered, replacing")
            
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
        return True
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            tool_name: Tool name
            
        Returns:
            True if unregistered successfully, False otherwise
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
            return True
        else:
            logger.warning(f"Tool {tool_name} not registered")
            return False
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name
        
        Args:
            tool_name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """
        Get all registered tools
        
        Returns:
            Dictionary of tool name to tool instance
        """
        return self.tools
    
    def get_tool_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered tools
        
        Returns:
            List of tool information dictionaries
        """
        return [tool.get_info() for tool in self.tools.values()]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool
        
        Args:
            tool_name: Tool name
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            return {
                "status": "error",
                "error": f"Tool {tool_name} not found"
            }
        
        try:
            logger.info(f"Executing tool: {tool_name}")
            result = await tool.execute(parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @staticmethod
    def load_tool_class(module_path: str, class_name: str) -> Type[Tool]:
        """
        Load a tool class from a module
        
        Args:
            module_path: Module path
            class_name: Class name
            
        Returns:
            Tool class
        """
        try:
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
            return tool_class
        except (ImportError, AttributeError) as e:
            logger.error(f"Error loading tool class {class_name} from {module_path}: {str(e)}")
            raise ValueError(f"Error loading tool class: {str(e)}")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any], services: Dict[str, Any]) -> 'ToolRegistry':
        """
        Create a ToolRegistry from configuration
        
        Args:
            config: Tool configuration
            services: Service instances
            
        Returns:
            ToolRegistry instance with tools loaded from configuration
        """
        registry = cls()
        
        for tool_name, tool_config in config.items():
            try:
                module_path = tool_config.get('module')
                class_name = tool_config.get('class')
                
                if not module_path or not class_name:
                    logger.warning(f"Invalid tool configuration for {tool_name}: missing module or class")
                    continue
                
                # Load tool class
                tool_class = cls.load_tool_class(module_path, class_name)
                
                # Create tool instance
                tool = tool_class(
                    redis_bus=services.get('redis_bus'),
                    config=tool_config.get('config', {})
                )
                
                # Register tool
                registry.register_tool(tool)
            except Exception as e:
                logger.error(f"Error creating tool {tool_name}: {str(e)}")
        
        return registry
