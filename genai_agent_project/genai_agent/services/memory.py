"""
Memory Service for persistent storage
"""

import logging
import json
from typing import Dict, Any, List, Optional

from genai_agent.services.redis_bus import RedisMessageBus

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Service for persistent storage using Redis
    """
    
    def __init__(self, redis_bus: RedisMessageBus):
        """
        Initialize the Memory Service
        
        Args:
            redis_bus: Redis Message Bus instance
        """
        self.redis_bus = redis_bus
        
        logger.info("Memory Service initialized")
    
    async def store(self, key: str, value: Any) -> bool:
        """
        Store a value
        
        Args:
            key: Storage key
            value: Value to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize value to JSON
            serialized = json.dumps(value)
            
            # Store in Redis
            await self.redis_bus.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Error storing value for {key}: {str(e)}")
            return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value
        
        Args:
            key: Storage key
            
        Returns:
            Retrieved value or None if not found
        """
        try:
            # Get from Redis
            serialized = await self.redis_bus.redis.get(key)
            
            if serialized is None:
                return None
                
            # Deserialize JSON
            return json.loads(serialized)
        except Exception as e:
            logger.error(f"Error retrieving value for {key}: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value
        
        Args:
            key: Storage key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete from Redis
            result = await self.redis_bus.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting value for {key}: {str(e)}")
            return False
    
    async def list_keys(self, pattern: str) -> List[str]:
        """
        List keys matching a pattern
        
        Args:
            pattern: Key pattern to match
            
        Returns:
            List of matching keys
        """
        try:
            # Get keys from Redis
            keys = await self.redis_bus.redis.keys(pattern)
            return [key for key in keys]
        except Exception as e:
            logger.error(f"Error listing keys for pattern {pattern}: {str(e)}")
            return []
