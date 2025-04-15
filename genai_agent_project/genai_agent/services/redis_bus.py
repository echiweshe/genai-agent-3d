"""
Redis Message Bus for service communication
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Callable, Awaitable, Optional, List

import redis.asyncio as redis_async

logger = logging.getLogger(__name__)

class RedisMessageBus:
    """
    Message bus implementation using Redis pub/sub for service communication
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Redis Message Bus
        
        Args:
            config: Redis configuration parameters
        """
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6379)
        self.password = config.get('password')
        self.db = config.get('db', 0)
        
        self.redis = redis_async.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            decode_responses=True
        )
        
        self.service_id = str(uuid.uuid4())
        self.subscribers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        self.pubsub = None
        self.listener_task = None
        
        logger.info(f"Redis Message Bus initialized with service_id: {self.service_id}")
    
    async def start(self):
        """Start the message bus and listener"""
        self.pubsub = self.redis.pubsub()
        self.listener_task = asyncio.create_task(self._message_listener())
        logger.info("Redis Message Bus started")
    
    async def stop(self):
        """Stop the message bus and listener"""
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass
            
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
            
        await self.redis.close()
        logger.info("Redis Message Bus stopped")
    
    async def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """
        Publish a message to a channel
        
        Args:
            channel: Channel name to publish to
            message: Message data to publish
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add service_id to message
            message['service_id'] = self.service_id
            
            # Publish message
            data = json.dumps(message)
            await self.redis.publish(channel, data)
            return True
        except Exception as e:
            logger.error(f"Error publishing message to {channel}: {str(e)}")
            return False
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """
        Subscribe to a channel
        
        Args:
            channel: Channel name to subscribe to
            callback: Async function to call when a message is received
        """
        if channel not in self.subscribers:
            self.subscribers[channel] = []
            
            # Subscribe to channel in Redis
            if self.pubsub:
                await self.pubsub.subscribe(channel)
            
        self.subscribers[channel].append(callback)
        logger.info(f"Subscribed to channel: {channel}")
    
    async def unsubscribe(self, channel: str, callback: Optional[Callable] = None):
        """
        Unsubscribe from a channel
        
        Args:
            channel: Channel name to unsubscribe from
            callback: Specific callback to unsubscribe, or None for all
        """
        if channel in self.subscribers:
            if callback is None:
                self.subscribers[channel] = []
            else:
                self.subscribers[channel] = [cb for cb in self.subscribers[channel] if cb != callback]
                
            # If no subscribers left for this channel, unsubscribe from Redis
            if not self.subscribers[channel] and self.pubsub:
                await self.pubsub.unsubscribe(channel)
                
            logger.info(f"Unsubscribed from channel: {channel}")
    
    async def _message_listener(self):
        """Listen for messages and dispatch to subscribers"""
        if not self.pubsub:
            self.pubsub = self.redis.pubsub()
            
        # Subscribe to all channels with subscribers
        for channel in self.subscribers.keys():
            await self.pubsub.subscribe(channel)
        
        # Listen for messages
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel']
                    data = json.loads(message['data'])
                    
                    # Skip messages from this service
                    if data.get('service_id') == self.service_id:
                        continue
                    
                    # Dispatch to all subscribers
                    for callback in self.subscribers.get(channel, []):
                        try:
                            await callback(data)
                        except Exception as e:
                            logger.error(f"Error in subscriber callback for {channel}: {str(e)}")
        except asyncio.CancelledError:
            logger.info("Message listener cancelled")
        except Exception as e:
            logger.error(f"Error in message listener: {str(e)}")
            # Restart listener after a short delay
            await asyncio.sleep(1)
            self.listener_task = asyncio.create_task(self._message_listener())
