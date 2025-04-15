"""
Context Manager for maintaining state across tasks
"""

import logging
from typing import Dict, Any, Optional

from genai_agent.services.memory import MemoryService

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manages context information across tasks
    """
    
    def __init__(self, memory_service: MemoryService):
        """
        Initialize the Context Manager
        
        Args:
            memory_service: Memory service for persistent storage
        """
        self.memory_service = memory_service
        self.active_context: Dict[str, Any] = {}
        
        logger.info("Context Manager initialized")
    
    async def update_context(self, key: str, value: Any):
        """
        Update a context value
        
        Args:
            key: Context key
            value: Context value
        """
        self.active_context[key] = value
        await self.memory_service.store(f"context:{key}", value)
        logger.debug(f"Updated context: {key}")
    
    async def get_context(self, key: str) -> Optional[Any]:
        """
        Get a context value
        
        Args:
            key: Context key
            
        Returns:
            Context value or None if not found
        """
        # Try active context first
        if key in self.active_context:
            return self.active_context[key]
        
        # Try memory service
        value = await self.memory_service.retrieve(f"context:{key}")
        
        # Update active context if found
        if value is not None:
            self.active_context[key] = value
            
        return value
    
    async def get_full_context(self) -> Dict[str, Any]:
        """
        Get the full context
        
        Returns:
            Dictionary with all context values
        """
        # Get all context from memory service
        memory_keys = await self.memory_service.list_keys("context:")
        
        # Load any missing keys from memory
        for key in memory_keys:
            short_key = key.replace("context:", "")
            if short_key not in self.active_context:
                value = await self.memory_service.retrieve(key)
                if value is not None:
                    self.active_context[short_key] = value
        
        return self.active_context
    
    async def clear_context(self):
        """
        Clear all context
        """
        self.active_context = {}
        
        # Clear context in memory
        memory_keys = await self.memory_service.list_keys("context:")
        for key in memory_keys:
            await self.memory_service.delete(key)
            
        logger.info("Context cleared")
