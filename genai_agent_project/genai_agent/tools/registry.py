"""
Tool Registry for managing available tools
"""

import logging
from typing import Dict, Any, List, Callable, Awaitable, Optional

logger = logging.getLogger(__name__)

class Tool:
    """
    Base class for all tools
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a tool
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Tool must implement execute method")

class ToolRegistry:
    """
    Registry for managing tools
    """
    
    def __init__(self):
        """Initialize the Tool Registry"""
        self.tools: Dict[str, Tool] = {}
        
        logger.info("Tool Registry initialized")
    
    def register_tool(self, name: str, tool: Tool) -> bool:
        """
        Register a tool
        
        Args:
            name: Tool name
            tool: Tool instance
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.tools:
            logger.warning(f"Tool {name} already registered, overwriting")
            
        self.tools[name] = tool
        logger.info(f"Registered tool: {name}")
        return True
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            name: Tool name
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered tool: {name}")
            return True
        else:
            logger.warning(f"Tool {name} not found")
            return False
    
    def get_tool(self, name: str) -> Tool:
        """
        Get a tool by name
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance
            
        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool {name} not found")
            
        return self.tools[name]
    
    def list_tools(self) -> List[str]:
        """
        List all registered tools
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
