import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Callable, Optional, Union

import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RedisMessageBus:
    def __init__(self, config: Dict[str, Any], client_id: Optional[str] = None):
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 6379)
        self.password = config.get('password')
        self.db = config.get('db', 0)

        self.client_id = client_id or str(uuid.uuid4())
        self.redis_url = f"redis://{self.host}:{self.port}/{self.db}"
        if self.password:
            self.redis_url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"

        self.redis = None
        self.pubsubs: Dict[str, redis.client.PubSub] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Union[None, asyncio.Future]]] = {}

        logger.info(f"[{self.client_id}] RedisMessageBus initialized for {self.redis_url}")

    async def connect(self):
        if not self.redis:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info(f"[{self.client_id}] Connected to Redis")
        return self.redis

    async def disconnect(self):
        for channel, pubsub in self.pubsubs.items():
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        self.pubsubs.clear()
        self._handlers.clear()
        if self.redis:
            await self.redis.close()
            self.redis = None
        logger.info(f"[{self.client_id}] Disconnected from Redis")

    async def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        try:
            await self.connect()
            await self.redis.publish(channel, json.dumps(message))
            logger.debug(f"[{self.client_id}] Published to {channel}: {message}")
            return True
        except Exception as e:
            logger.error(f"[{self.client_id}] Publish error on {channel}: {e}")
            return False

    async def subscribe(self, channel: str, handler: Callable[[Dict[str, Any]], Union[None, asyncio.Future]]):
        await self.connect()

        if channel in self.pubsubs:
            logger.warning(f"[{self.client_id}] Already subscribed to {channel}")
            return

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        self.pubsubs[channel] = pubsub
        self._handlers[channel] = handler

        asyncio.create_task(self._listen(channel, pubsub))
        logger.info(f"[{self.client_id}] Subscribed to {channel}")

    async def unsubscribe(self, channel: str):
        pubsub = self.pubsubs.get(channel)
        if pubsub:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            self.pubsubs.pop(channel, None)
            self._handlers.pop(channel, None)
            logger.info(f"[{self.client_id}] Unsubscribed from {channel}")

    async def _listen(self, channel: str, pubsub: redis.client.PubSub):
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        payload = json.loads(message['data'])
                        handler = self._handlers.get(channel)
                        if asyncio.iscoroutinefunction(handler):
                            await handler(payload)
                        else:
                            handler(payload)
                    except Exception as e:
                        logger.error(f"[{self.client_id}] Handler error on {channel}: {e}")
        except asyncio.CancelledError:
            logger.warning(f"[{self.client_id}] Listener task cancelled for {channel}")
        except Exception as e:
            logger.error(f"[{self.client_id}] Listener error on {channel}: {e}")
