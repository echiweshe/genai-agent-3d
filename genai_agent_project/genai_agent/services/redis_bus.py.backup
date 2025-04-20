"""
Redis Message Bus for inter-service communication
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Callable, Optional, List, Tuple, Union

import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RedisMessageBus:
    """
    Asynchronous Redis-based message bus for inter-service communication
    
    Provides pub/sub functionality for services to communicate with each other
    through Redis channels.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Redis Message Bus
        
        Args:
            config: Redis configuration parameters
                - host: Redis host (default: localhost)
                - port: Redis port (default: 6379)
                - password: Redis password (default: None)
                - db: Redis database (default: 0)
        """
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6379)
        self.password = config.get('password')
        self.db = config.get('db', 0)
        
        # Create Redis URL (used when connecting)
        self.redis_url = f"redis://{self.host}:{self.port}/{self.db}"
        if self.password:
            self.redis_url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
            
        # Redis connection and pubsub objects
        self.redis = None
        self.pubsub = None
        
        # Subscription management
        self._subscription_tasks = {}
        self._event_handlers = {}
        self._rpc_handlers = {}
        self._response_futures = {}
        
        # Fallback mode (used when Redis is unavailable)
        self.use_fallback = False
        self.in_memory_data = {}
        self.in_memory_subscriptions = {}
        
        logger.info(f"Redis Message Bus initialized with {self.host}:{self.port}")
        
    async def connect(self):
        """Connect to Redis server"""
        if self.redis is None:
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    logger.debug(f"Connecting to Redis at {self.host}:{self.port} (attempt {retry_count+1}/{max_retries})")
                    
                    # Connect to Redis with decode_responses to get strings
                    self.redis = await redis.from_url(
                        self.redis_url, 
                        decode_responses=True
                    )
                    
                    # Test connection
                    await self.redis.ping()
                    
                    # Create PubSub object
                    self.pubsub = self.redis.pubsub()
                    
                    logger.info(f"Connected to Redis at {self.host}:{self.port}")
                    self.use_fallback = False
                    return True
                
                except Exception as e:
                    logger.error(f"Failed to connect to Redis (attempt {retry_count+1}/{max_retries}): {str(e)}")
                    self.redis = None
                    retry_count += 1
                    
                    if retry_count < max_retries:
                        await asyncio.sleep(1)  # Wait before retrying
            
            # If we get here, all retries failed
            logger.warning("Failed to connect to Redis after multiple attempts. Using in-memory fallback.")
            self.use_fallback = True
            return True  # Return success even with fallback
        
        return True
    
    async def disconnect(self):
        """Disconnect from Redis server"""
        if not self.use_fallback and self.redis is not None:
            # Cancel all subscription tasks
            for task in self._subscription_tasks.values():
                task.cancel()
                
            # Close pubsub and Redis connection
            if self.pubsub:
                await self.pubsub.close()
            await self.redis.close()
            self.redis = None
            self.pubsub = None
            logger.info("Disconnected from Redis")
        
        # Clear in-memory data in fallback mode
        if self.use_fallback:
            self.in_memory_data = {}
            self.in_memory_subscriptions = {}
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """
        Publish message to a channel
        
        Args:
            channel: Channel name
            message: Message to publish
        """
        if not self.use_fallback:
            # Real Redis implementation
            if not await self.connect():
                logger.error("Cannot publish message: Redis connection failed")
                return False
                
            try:
                message_str = json.dumps(message)
                await self.redis.publish(channel, message_str)
                logger.debug(f"Published message to {channel}")
                return True
            except Exception as e:
                logger.error(f"Failed to publish message: {str(e)}")
                return False
        else:
            # In-memory fallback implementation
            logger.debug(f"Using in-memory fallback to publish to {channel}")
            
            # Store the message (optional)
            self.in_memory_data[channel] = message
            
            # Notify subscribers
            if channel in self.in_memory_subscriptions:
                for handler in self.in_memory_subscriptions[channel]:
                    try:
                        asyncio.create_task(handler(message))
                    except Exception as e:
                        logger.error(f"Error in message handler: {str(e)}")
            
            return True
    
    async def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to a channel
        
        Args:
            channel: Channel name
            handler: Message handler function
        """
        if not self.use_fallback:
            # Real Redis implementation
            if not await self.connect():
                logger.error(f"Failed to subscribe to {channel}: Redis connection failed")
                return False
                
            try:
                # Register handler
                if channel not in self._event_handlers:
                    self._event_handlers[channel] = []
                self._event_handlers[channel].append(handler)
                
                # Subscribe to channel if not already subscribed
                if channel not in self._subscription_tasks:
                    await self.pubsub.subscribe(channel)
                    
                    # Start listener task
                    task = asyncio.create_task(self._listen_for_messages(channel))
                    self._subscription_tasks[channel] = task
                    
                logger.info(f"Subscribed to channel: {channel}")
                return True
            except Exception as e:
                logger.error(f"Failed to subscribe to {channel}: {str(e)}")
                return False
        else:
            # In-memory fallback implementation
            logger.debug(f"Using in-memory fallback to subscribe to {channel}")
            
            if channel not in self.in_memory_subscriptions:
                self.in_memory_subscriptions[channel] = []
            
            self.in_memory_subscriptions[channel].append(handler)
            
            logger.info(f"Subscribed to channel: {channel}")
            return True
    
    async def unsubscribe(self, channel: str, handler: Optional[Callable] = None):
        """
        Unsubscribe from a channel
        
        Args:
            channel: Channel name
            handler: Message handler function to remove (if None, remove all)
        """
        if not self.use_fallback:
            # Real Redis implementation
            if channel not in self._event_handlers:
                return True
                
            if handler is None:
                # Remove all handlers for this channel
                self._event_handlers[channel] = []
            else:
                # Remove specific handler
                if handler in self._event_handlers[channel]:
                    self._event_handlers[channel].remove(handler)
            
            # If no more handlers, unsubscribe from channel
            if not self._event_handlers[channel] and channel in self._subscription_tasks:
                task = self._subscription_tasks[channel]
                task.cancel()
                del self._subscription_tasks[channel]
                
                if self.pubsub:
                    await self.pubsub.unsubscribe(channel)
                
                logger.info(f"Unsubscribed from channel: {channel}")
        else:
            # In-memory fallback implementation
            if channel not in self.in_memory_subscriptions:
                return True
            
            if handler is None:
                # Remove all handlers
                self.in_memory_subscriptions[channel] = []
            else:
                # Remove specific handler
                if handler in self.in_memory_subscriptions[channel]:
                    self.in_memory_subscriptions[channel].remove(handler)
            
            logger.info(f"Unsubscribed from channel: {channel}")
        
        return True
    
    async def register_rpc(self, method: str, handler: Callable[[Dict[str, Any]], Any]):
        """
        Register RPC method handler
        
        Args:
            method: RPC method name
            handler: Method handler function
        """
        self._rpc_handlers[method] = handler
        
        # Subscribe to RPC requests
        channel = f"rpc:{method}"
        await self.subscribe(channel, self._handle_rpc_request)
        
        logger.info(f"Registered RPC method: {method}")
    
    async def call_rpc(self, method: str, params: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        """
        Call RPC method
        
        Args:
            method: RPC method name
            params: Method parameters
            timeout: Timeout in seconds
            
        Returns:
            Method result or error
        """
        if not self.use_fallback:
            # Real Redis implementation
            if not await self.connect():
                return {"error": "Redis connection failed"}
                
            # Generate request ID
            request_id = str(uuid.uuid4())
            
            # Create response future
            response_future = asyncio.Future()
            self._response_futures[request_id] = response_future
            
            # Subscribe to response channel
            response_channel = f"rpc:response:{request_id}"
            await self.subscribe(response_channel, self._handle_rpc_response)
            
            # Create request message
            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params
            }
            
            # Publish request
            request_channel = f"rpc:{method}"
            await self.publish(request_channel, request)
            
            try:
                # Wait for response with timeout
                return await asyncio.wait_for(response_future, timeout)
            except asyncio.TimeoutError:
                logger.error(f"RPC call to {method} timed out after {timeout} seconds")
                return {"error": f"RPC call timed out after {timeout} seconds"}
            finally:
                # Clean up
                if request_id in self._response_futures:
                    del self._response_futures[request_id]
                await self.unsubscribe(response_channel)
        else:
            # In-memory fallback implementation
            # For simplicity, just try to find and call the handler directly
            if method in self._rpc_handlers:
                handler = self._rpc_handlers[method]
                try:
                    result = await handler(params)
                    return {"result": result}
                except Exception as e:
                    logger.error(f"Error in RPC handler: {str(e)}")
                    return {"error": str(e)}
            else:
                return {"error": f"Method '{method}' not found"}
    
    async def _listen_for_messages(self, channel: str):
        """
        Listen for messages on a channel
        
        Args:
            channel: Channel name
        """
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    data = message['data']
                    
                    try:
                        payload = json.loads(data)
                        await self._dispatch_message(channel, payload)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in message: {data}")
        except asyncio.CancelledError:
            logger.debug(f"Message listener for {channel} cancelled")
        except Exception as e:
            logger.error(f"Error in message listener for {channel}: {str(e)}")
    
    async def _dispatch_message(self, channel: str, message: Dict[str, Any]):
        """
        Dispatch message to registered handlers
        
        Args:
            channel: Channel name
            message: Message payload
        """
        if channel in self._event_handlers:
            for handler in self._event_handlers[channel]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {str(e)}")
    
    async def _handle_rpc_request(self, request: Dict[str, Any]):
        """
        Handle RPC request
        
        Args:
            request: RPC request message
        """
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        if not method or not request_id:
            return
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if method in self._rpc_handlers:
            try:
                handler = self._rpc_handlers[method]
                result = await handler(params)
                response["result"] = result
            except Exception as e:
                logger.error(f"Error in RPC handler for {method}: {str(e)}")
                response["error"] = str(e)
        else:
            response["error"] = f"Method '{method}' not found"
        
        # Send response
        response_channel = f"rpc:response:{request_id}"
        await self.publish(response_channel, response)
    
    async def _handle_rpc_response(self, response: Dict[str, Any]):
        """
        Handle RPC response
        
        Args:
            response: RPC response message
        """
        request_id = response.get('id')
        if request_id in self._response_futures:
            future = self._response_futures[request_id]
            if not future.done():
                if 'error' in response:
                    future.set_exception(Exception(response['error']))
                else:
                    future.set_result(response.get('result', {}))
