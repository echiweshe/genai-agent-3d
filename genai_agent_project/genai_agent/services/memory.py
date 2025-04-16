"""
Memory Service for storing and retrieving agent memory
"""

import logging
import json
import os
import time
from typing import Dict, Any, List, Optional, Union

from genai_agent.services.redis_bus import RedisMessageBus

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Service for storing and retrieving agent memory
    
    Provides persistent storage for agent memory, including:
    - Conversation history
    - Scene history
    - Agent state
    """
    
    def __init__(self, redis_bus: RedisMessageBus, config: Dict[str, Any] = None):
        """
        Initialize Memory Service
        
        Args:
            redis_bus: Redis Message Bus instance
            config: Configuration parameters
        """
        self.redis_bus = redis_bus
        self.config = config or {}
        
        # Storage type: 'redis' or 'file'
        self.storage_type = self.config.get('storage_type', 'redis')
        
        # File storage path (only used if storage_type is 'file')
        self.file_path = self.config.get('file_path', 'data/memory/')
        
        # Time to live in seconds (0 = no expiration)
        self.ttl = self.config.get('ttl', 3600)
        
        # Redis key prefix
        self.key_prefix = 'memory:'
        
        logger.info(f"Memory Service initialized with {self.storage_type} storage")
        
        # Create file storage directory if needed
        if self.storage_type == 'file' and not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
    
    async def store(self, key: str, value: Union[Dict[str, Any], List[Any], str], 
                  expiration: Optional[int] = None) -> bool:
        """
        Store a value in memory
        
        Args:
            key: Memory key
            value: Value to store
            expiration: Expiration time in seconds (overrides default ttl)
            
        Returns:
            True if stored successfully, False otherwise
        """
        logger.debug(f"Storing memory: {key}")
        
        # Use provided expiration or default ttl
        ttl = expiration if expiration is not None else self.ttl
        
        if self.storage_type == 'redis':
            return await self._store_redis(key, value, ttl)
        else:
            return self._store_file(key, value, ttl)
    
    async def retrieve(self, key: str) -> Optional[Union[Dict[str, Any], List[Any], str]]:
        """
        Retrieve a value from memory
        
        Args:
            key: Memory key
            
        Returns:
            Stored value or None if not found
        """
        logger.debug(f"Retrieving memory: {key}")
        
        if self.storage_type == 'redis':
            return await self._retrieve_redis(key)
        else:
            return self._retrieve_file(key)
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from memory
        
        Args:
            key: Memory key
            
        Returns:
            True if deleted successfully, False otherwise
        """
        logger.debug(f"Deleting memory: {key}")
        
        if self.storage_type == 'redis':
            return await self._delete_redis(key)
        else:
            return self._delete_file(key)
    
    async def list_keys(self, pattern: str = '*') -> List[str]:
        """
        List memory keys matching a pattern
        
        Args:
            pattern: Key pattern
            
        Returns:
            List of matching keys
        """
        logger.debug(f"Listing memory keys: {pattern}")
        
        if self.storage_type == 'redis':
            return await self._list_keys_redis(pattern)
        else:
            return self._list_keys_file(pattern)
    
    async def store_conversation(self, conversation_id: str, 
                               messages: List[Dict[str, Any]]) -> bool:
        """
        Store conversation history
        
        Args:
            conversation_id: Conversation ID
            messages: List of conversation messages
            
        Returns:
            True if stored successfully, False otherwise
        """
        key = f"conversation:{conversation_id}"
        return await self.store(key, messages)
    
    async def retrieve_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of conversation messages
        """
        key = f"conversation:{conversation_id}"
        return await self.retrieve(key) or []
    
    async def store_scene_history(self, scene_id: str, history: List[Dict[str, Any]]) -> bool:
        """
        Store scene modification history
        
        Args:
            scene_id: Scene ID
            history: List of scene modifications
            
        Returns:
            True if stored successfully, False otherwise
        """
        key = f"scene_history:{scene_id}"
        return await self.store(key, history)
    
    async def retrieve_scene_history(self, scene_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve scene modification history
        
        Args:
            scene_id: Scene ID
            
        Returns:
            List of scene modifications
        """
        key = f"scene_history:{scene_id}"
        return await self.retrieve(key) or []
    
    async def add_scene_history_entry(self, scene_id: str, entry: Dict[str, Any]) -> bool:
        """
        Add an entry to scene modification history
        
        Args:
            scene_id: Scene ID
            entry: History entry
            
        Returns:
            True if added successfully, False otherwise
        """
        history = await self.retrieve_scene_history(scene_id)
        history.append(entry)
        return await self.store_scene_history(scene_id, history)
    
    async def _store_redis(self, key: str, value: Any, ttl: int) -> bool:
        """Store value in Redis"""
        if not await self.redis_bus.connect():
            logger.error("Cannot store in Redis: connection failed")
            return False
        
        full_key = f"{self.key_prefix}{key}"
        
        try:
            # Convert value to JSON string
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
            
            # Store in Redis
            if ttl > 0:
                await self.redis_bus.redis.setex(full_key, ttl, value_str)
            else:
                await self.redis_bus.redis.set(full_key, value_str)
            
            return True
        except Exception as e:
            logger.error(f"Error storing in Redis: {str(e)}")
            return False
    
    async def _retrieve_redis(self, key: str) -> Optional[Any]:
        """Retrieve value from Redis"""
        if not await self.redis_bus.connect():
            logger.error("Cannot retrieve from Redis: connection failed")
            return None
        
        full_key = f"{self.key_prefix}{key}"
        
        try:
            # Get from Redis
            value_str = await self.redis_bus.redis.get(full_key)
            
            if value_str is None:
                return None
            
            # Convert from bytes to string
            if isinstance(value_str, bytes):
                value_str = value_str.decode('utf-8')
            
            # Try to parse as JSON
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                # Return as string if not JSON
                return value_str
        except Exception as e:
            logger.error(f"Error retrieving from Redis: {str(e)}")
            return None
    
    async def _delete_redis(self, key: str) -> bool:
        """Delete value from Redis"""
        if not await self.redis_bus.connect():
            logger.error("Cannot delete from Redis: connection failed")
            return False
        
        full_key = f"{self.key_prefix}{key}"
        
        try:
            # Delete from Redis
            await self.redis_bus.redis.delete(full_key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Redis: {str(e)}")
            return False
    
    async def _list_keys_redis(self, pattern: str) -> List[str]:
        """List keys from Redis"""
        if not await self.redis_bus.connect():
            logger.error("Cannot list keys from Redis: connection failed")
            return []
        
        full_pattern = f"{self.key_prefix}{pattern}"
        
        try:
            # Get keys from Redis
            keys = await self.redis_bus.redis.keys(full_pattern)
            
            # Remove prefix and convert to strings
            return [key.decode('utf-8')[len(self.key_prefix):] for key in keys]
        except Exception as e:
            logger.error(f"Error listing keys from Redis: {str(e)}")
            return []
    
    def _store_file(self, key: str, value: Any, ttl: int) -> bool:
        """Store value in file"""
        file_path = os.path.join(self.file_path, f"{key}.json")
        
        try:
            # Prepare data with metadata
            data = {
                'value': value,
                'timestamp': time.time(),
                'expiration': time.time() + ttl if ttl > 0 else 0
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(data, f)
            
            return True
        except Exception as e:
            logger.error(f"Error storing in file: {str(e)}")
            return False
    
    def _retrieve_file(self, key: str) -> Optional[Any]:
        """Retrieve value from file"""
        file_path = os.path.join(self.file_path, f"{key}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            # Read from file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check expiration
            if data.get('expiration', 0) > 0 and data['expiration'] < time.time():
                # Expired, delete file
                try:
                    os.remove(file_path)
                except:
                    pass
                return None
            
            return data.get('value')
        except Exception as e:
            logger.error(f"Error retrieving from file: {str(e)}")
            return None
    
    def _delete_file(self, key: str) -> bool:
        """Delete value from file"""
        file_path = os.path.join(self.file_path, f"{key}.json")
        
        if not os.path.exists(file_path):
            return True
        
        try:
            # Delete file
            os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def _list_keys_file(self, pattern: str) -> List[str]:
        """List keys from files"""
        try:
            # List files in directory
            files = os.listdir(self.file_path)
            
            # Filter by pattern and remove extension
            import fnmatch
            keys = [os.path.splitext(f)[0] for f in files if fnmatch.fnmatch(f, f"{pattern}.json")]
            
            return keys
        except Exception as e:
            logger.error(f"Error listing keys from files: {str(e)}")
            return []
