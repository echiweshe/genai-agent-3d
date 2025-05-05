#### Step 2: Redis Message Bus Integration

```python
# redis_bus.py
import json
import asyncio
import logging
import aioredis
import uuid
from typing import Dict, Any, Callable, List, Optional

logger = logging.getLogger(__name__)

class RedisBus:
    """Redis-based message bus for pipeline communication."""
    
    def __init__(self, redis_url="redis://localhost:6379"):
        """Initialize the Redis bus."""
        self.redis_url = redis_url
        self.redis = None
        self.pubsub = None
        self.running = False
        self.handlers = {}
        
        # Pending requests tracking
        self.pending_requests = {}
    
    async def connect(self):
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        self.pubsub = self.redis.pubsub()
        logger.info(f"Connected to Redis at {self.redis_url}")
    
    async def start(self):
        """Start the message processing loop."""
        if not self.redis:
            await self.connect()
        
        self.running = True
        asyncio.create_task(self._process_messages())
        logger.info("Redis message bus started")
    
    async def stop(self):
        """Stop the message bus."""
        self.running = False
        
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis:
            await self.redis.close()
        
        logger.info("Redis message bus stopped")
    
    async def subscribe(self, channel: str, handler: Callable):
        """Subscribe to a channel with a handler function."""
        if not self.redis:
            await self.connect()
        
        if channel not in self.handlers:
            self.handlers[channel] = []
            await self.pubsub.subscribe(channel)
        
        self.handlers[channel].append(handler)
        logger.info(f"Subscribed to channel: {channel}")
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish a message to a channel."""
        if not self.redis:
            await self.connect()
        
        await self.redis.publish(channel, json.dumps(message))
        logger.debug(f"Published to {channel}: {message}")
    
    async def request(self, channel: str, message: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Send a request and wait for a response."""
        if not self.redis:
            await self.connect()
        
        # Create a unique request ID
        request_id = str(uuid.uuid4())
        response_channel = f"response:{request_id}"
        
        # Set up future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        # Subscribe to response channel
        async def response_handler(response):
            future.set_result(response)
        
        await self.subscribe(response_channel, response_handler)
        
        # Send request with ID
        message["request_id"] = request_id
        message["response_channel"] = response_channel
        await self.publish(channel, message)
        
        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            # Clean up on timeout
            self.pending_requests.pop(request_id, None)
            return {"error": f"Request timed out after {timeout} seconds"}
        finally:
            # Unsubscribe from response channel
            if response_channel in self.handlers:
                self.handlers.pop(response_channel, None)
                await self.pubsub.unsubscribe(response_channel)
    
    async def _process_messages(self):
        """Process incoming messages from subscribed channels."""
        while self.running:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message is None:
                    await asyncio.sleep(0.01)
                    continue
                
                # Parse message
                channel = message["channel"]
                try:
                    data = json.loads(message["data"])
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received on channel {channel}")
                    continue
                
                # Handle message
                if channel in self.handlers:
                    for handler in self.handlers[channel]:
                        try:
                            asyncio.create_task(handler(data))
                        except Exception as e:
                            logger.error(f"Error in message handler: {str(e)}")
            
            except Exception as e:
                logger.error(f"Error processing messages: {str(e)}")
                await asyncio.sleep(1.0)
```

#### Step 3: Service Integration

```python
# svg_video_service.py
import os
import asyncio
import logging
from redis_bus import RedisBus
from langchain_manager import LangChainManager
from svg_to_video_pipeline import SVGToVideoPipeline

logger = logging.getLogger(__name__)

class SVGVideoService:
    """Service for handling SVG to Video pipeline requests."""
    
    def __init__(self, config=None):
        """Initialize the service."""
        self.config = config or {}
        
        # Initialize components
        self.redis_bus = RedisBus(self.config.get("redis_url", "redis://localhost:6379"))
        self.langchain_manager = LangChainManager(self.config)
        self.pipeline = SVGToVideoPipeline(self.config)
        
        # Set up output directory
        self.output_dir = self.config.get("output_dir", "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("SVG Video Service initialized")
    
    async def start(self):
        """Start the service."""
        # Connect to Redis
        await self.redis_bus.connect()
        
        # Subscribe to request channels
        await self.redis_bus.subscribe("svg:generate", self._handle_svg_generation)
        await self.redis_bus.subscribe("video:create", self._handle_video_creation)
        await self.redis_bus.subscribe("pipeline:process", self._handle_pipeline_process)
        
        # Start message processing
        await self.redis_bus.start()
        
        logger.info("SVG Video Service started")
    
    async def stop(self):
        """Stop the service."""
        await self.redis_bus.stop()
        logger.info("SVG Video Service stopped")
    
    async def _handle_svg_generation(self, data):
        """Handle SVG generation requests."""
        request_id = data.get("request_id")
        response_channel = data.get("response_channel")
        
        concept = data.get("concept")
        provider = data.get("provider", "claude")
        session_id = data.get("session_id")
        
        if not concept:
            await self._send_error_response(response_channel, "Missing concept parameter")
            return
        
        try:
            # Generate SVG
            svg_content = await self.langchain_manager.generate_svg(
                concept, 
                provider_name=provider,
                session_id=session_id
            )
            
            # Save SVG to file if requested
            svg_path = None
            if data.get("save_file", False):
                filename = f"svg_{request_id}.svg"
                svg_path = os.path.join(self.output_dir, filename)
                
                with open(svg_path, "w", encoding="utf-8") as f:
                    f.write(svg_content)
            
            # Send response
            response = {
                "status": "success",
                "svg_content": svg_content,
                "svg_path": svg_path
            }
            
            if response_channel:
                await self.redis_bus.publish(response_channel, response)
            
        except Exception as e:
            logger.error(f"Error generating SVG: {str(e)}")
            await self._send_error_response(response_channel, f"Error generating SVG: {str(e)}")
    
    async def _handle_video_creation(self, data):
        """Handle video creation from existing SVG."""
        request_id = data.get("request_id")
        response_channel = data.get("response_channel")
        
        svg_path = data.get("svg_path")
        svg_content = data.get("svg_content")
        
        if not svg_path and not svg_content:
            await self._send_error_response(response_channel, "Missing SVG content or path")
            return
        
        try:
            # Create temporary SVG file if content provided
            if not svg_path and svg_content:
                import tempfile
                fd, svg_path = tempfile.mkstemp(suffix=".svg")
                with os.fdopen(fd, "w") as f:
                    f.write(svg_content)
            
            # Set output path
            filename = f"video_{request_id}.mp4"
            output_path = os.path.join(self.output_dir, filename)
            
            # Process through pipeline (starting from SVG to 3D conversion)
            # Note: This is simplified and would need to be expanded
            model_path = await self.pipeline._convert_svg_to_3d(svg_path)
            animated_path = await self.pipeline._apply_animations(model_path)
            video_path = await self.pipeline._render_video(animated_path, output_path)
            
            # Send response
            response = {
                "status": "success",
                "video_path": video_path
            }
            
            if response_channel:
                await self.redis_bus.publish(response_channel, response)
            
        except Exception as e:
            logger.error(f"Error creating video: {str(e)}")
            await self._send_error_response(response_channel, f"Error creating video: {str(e)}")
    
    async def _handle_pipeline_process(self, data):
        """Handle end-to-end pipeline processing."""
        request_id = data.get("request_id")
        response_channel = data.get("response_channel")
        
        concept = data.get("concept")
        provider = data.get("provider", "claude")
        options = data.get("options", {})
        
        if not concept:
            await self._send_error_response(response_channel, "Missing concept parameter")
            return
        
        try:
            # Set output path
            filename = f"video_{request_id}.mp4"
            output_path = os.path.join(self.output_dir, filename)
            
            # Run full pipeline
            result = await self.pipeline.process(
                concept,
                output_path,
                {
                    "provider": provider,
                    **options
                }
            )
            
            # Send response
            if response_channel:
                await self.redis_bus.publish(response_channel, result)
            
        except Exception as e:
            logger.error(f"Error in pipeline processing: {str(e)}")
            await self._send_error_response(response_channel, f"Error in pipeline: {str(e)}")
    
    async def _send_error_response(self, response_channel, error_message):
        """Send an error response to the specified channel."""
        if response_channel:
            await self.redis_bus.publish(response_channel, {
                "status": "error",
                "error": error_message
            })
```
