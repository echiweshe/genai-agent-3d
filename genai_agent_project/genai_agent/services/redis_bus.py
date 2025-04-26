
"""
Redis Message Bus - Handles communication between services
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable, Union
import redis.asyncio as redis

# Configure logging
logger = logging.getLogger(__name__)

class RedisMessageBus:
    """Redis-based message bus for service communication"""
    
    def __init__(self, redis_url="localhost", redis_port=6379, redis_db=0):
        """
        Initialize Redis message bus
        
        Args:
            redis_url: Redis server URL or config dict
            redis_port: Redis server port
            redis_db: Redis database number
        """
        # Handle case when redis_url is a dictionary
        if isinstance(redis_url, dict):
            self.redis_config = redis_url.copy()  # Make a copy to avoid reference issues
            # Extract basic info for logging
            self.redis_url = str(redis_url.get('host', 'localhost'))  # Ensure it's a string
            self.redis_port = int(redis_url.get('port', 6379))  # Ensure it's an integer
        else:
            self.redis_url = str(redis_url)  # Ensure it's a string
            self.redis_port = int(redis_port)  # Ensure it's an integer
            self.redis_db = redis_db
            self.redis_config = {
                'host': self.redis_url,
                'port': self.redis_port,
                'db': self.redis_db
            }
            
        self.redis = None
        self.pubsub = None
        self.subscriptions = {}
        self.running = False
        self.listener_task = None
        
        logger.info(f"Redis Message Bus initialized with {self.redis_url}:{self.redis_port}")
    
    async def connect(self):
        """Connect to Redis server"""
        if self.redis is None:
            try:
                # Ensure we have string and int types for host and port
                host = str(self.redis_url)
                port = int(self.redis_port)
                db = int(self.redis_config.get('db', 0))
                
                # Create connection with proper types
                self.redis = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    decode_responses=True
                )
                
                # Test connection
                await self.redis.ping()
                logger.info(f"Connected to Redis at {host}:{port}")
                
                # Initialize pubsub
                self.pubsub = self.redis.pubsub()
            except Exception as e:
                logger.error(f"Error connecting to Redis: {str(e)}")
                raise
    
    async def disconnect(self):
        """Disconnect from Redis server"""
        if self.redis is not None:
            # Stop listener if running
            await self.stop_listener()
            
            # Unsubscribe from all channels
            if self.pubsub is not None:
                await self.pubsub.unsubscribe()
                await self.pubsub.close()
            
            # Close Redis connection
            await self.redis.close()
            self.redis = None
            logger.info("Disconnected from Redis")
    
    async def ping(self):
        """Check if Redis connection is alive"""
        try:
            if self.redis is None:
                await self.connect()
                
            if self.redis:
                # Test connection
                pong = await self.redis.ping()
                return {"status": "ok", "message": "PONG" if pong else "Connection exists but ping failed"}
            return {"status": "error", "message": "Redis connection not initialized"}
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def ping(self):
        """Check if Redis connection is alive"""
        try:
            if self.redis is None:
                await self.connect()
                
            if self.redis:
                # Test connection
                pong = await self.redis.ping()
                return {"status": "ok", "message": "PONG" if pong else "Connection exists but ping failed"}
            return {"status": "error", "message": "Redis connection not initialized"}
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """
        Publish message to channel
        
        Args:
            channel: Channel name
            message: Message to publish (will be JSON-encoded)
        """
        if self.redis is None:
            await self.connect()
        
        # Convert message to JSON
        message_json = json.dumps(message)
        
        # Publish message
        await self.redis.publish(channel, message_json)
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """
        Subscribe to channel with callback
        
        Args:
            channel: Channel name
            callback: Async callback function that takes message as argument
        """
        if self.redis is None:
            await self.connect()
        
        # Initialize pubsub if needed
        if self.pubsub is None:
            self.pubsub = self.redis.pubsub()
        
        # Subscribe to channel
        await self.pubsub.subscribe(channel)
        
        # Store callback
        self.subscriptions[channel] = callback
        
        # Start listener if not already running
        if not self.running:
            await self.start_listener()
    
    async def unsubscribe(self, channel: str):
        """
        Unsubscribe from channel
        
        Args:
            channel: Channel name
        """
        if self.pubsub is not None:
            # Unsubscribe from channel
            await self.pubsub.unsubscribe(channel)
            
            # Remove callback
            if channel in self.subscriptions:
                del self.subscriptions[channel]
    
    async def start_listener(self):
        """Start message listener loop"""
        if self.running:
            return
        
        self.running = True
        self.listener_task = asyncio.create_task(self._listen())
    
    async def stop_listener(self):
        """Stop message listener loop"""
        self.running = False
        
        if self.listener_task is not None:
            try:
                self.listener_task.cancel()
                await self.listener_task
            except asyncio.CancelledError:
                pass
            self.listener_task = None
    
    async def _listen(self):
        """Message listener loop"""
        try:
            while self.running:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                
                if message is not None:
                    channel = message["channel"]
                    data = message["data"]
                    
                    # Parse JSON data
                    try:
                        data_json = json.loads(data)
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid JSON on channel {channel}: {data}")
                        continue
                    
                    # Find and call callback
                    if channel in self.subscriptions:
                        callback = self.subscriptions[channel]
                        try:
                            await callback(data_json)
                        except Exception as e:
                            logger.error(f"Error in message callback for channel {channel}: {str(e)}")
                
                # Short sleep to avoid CPU spinning
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            # Normal cancellation
            pass
        except Exception as e:
            logger.error(f"Error in message listener: {str(e)}")
            self.running = False

# Singleton instance
_message_bus = None

def get_message_bus(redis_url="localhost", redis_port=6379, redis_db=0):
    """
    Get message bus singleton instance
    
    Args:
        redis_url: Redis server URL or config dict
        redis_port: Redis server port
        redis_db: Redis database number
        
    Returns:
        RedisMessageBus instance
    """
    global _message_bus
    
    if _message_bus is None:
        _message_bus = RedisMessageBus(redis_url, redis_port, redis_db)
    
    return _message_bus
