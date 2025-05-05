G: {str(e)}")
    
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

### Service Launcher

```python
# service_launcher.py
import os
import asyncio
import logging
import argparse
import signal
import json
from pipeline_config import PipelineConfig
from svg_video_service import SVGVideoService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instance for signal handling
service = None

async def main():
    global service
    
    parser = argparse.ArgumentParser(description='SVG Video Service')
    parser.add_argument('--config', help='Path to configuration file')
    args = parser.parse_args()
    
    # Load configuration
    config = PipelineConfig(args.config)
    
    # Configure logging level
    logging.getLogger().setLevel(config.get("log_level", "INFO"))
    
    # Create and start service
    service = SVGVideoService(config.config)
    
    # Set up signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))
    
    # Start service
    await service.start()
    
    # Keep the service running until a signal is received
    while True:
        await asyncio.sleep(1)

async def shutdown():
    """Gracefully shut down the service."""
    global service
    
    if service:
        logger.info("Shutting down service...")
        await service.stop()
    
    # Stop the event loop
    asyncio.get_event_loop().stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
```

### Client API

```python
# svg_video_client.py
import os
import asyncio
import logging
from redis_bus import RedisBus

logger = logging.getLogger(__name__)

class SVGVideoClient:
    """Client for interacting with the SVG Video Service."""
    
    def __init__(self, redis_url="redis://localhost:6379"):
        """Initialize the client."""
        self.redis_bus = RedisBus(redis_url)
    
    async def connect(self):
        """Connect to the Redis bus."""
        await self.redis_bus.connect()
    
    async def close(self):
        """Close the client connection."""
        await self.redis_bus.stop()
    
    async def generate_svg(self, concept, provider="claude", save_file=False, timeout=60, session_id=None):
        """Generate an SVG diagram from a concept."""
        request = {
            "concept": concept,
            "provider": provider,
            "save_file": save_file,
            "session_id": session_id
        }
        
        response = await self.redis_bus.request("svg:generate", request, timeout=timeout)
        return response
    
    async def create_video(self, svg_path=None, svg_content=None, timeout=300):
        """Create a video from an SVG file or content."""
        if not svg_path and not svg_content:
            raise ValueError("Either svg_path or svg_content must be provided")
        
        request = {
            "svg_path": svg_path,
            "svg_content": svg_content
        }
        
        response = await self.redis_bus.request("video:create", request, timeout=timeout)
        return response
    
    async def process_pipeline(self, concept, provider="claude", options=None, timeout=600):
        """Process a concept through the full pipeline."""
        request = {
            "concept": concept,
            "provider": provider,
            "options": options or {}
        }
        
        response = await self.redis_bus.request("pipeline:process", request, timeout=timeout)
        return response
```

### Example Client Usage

```python
# example_client.py
import asyncio
import logging
from svg_video_client import SVGVideoClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def example_usage():
    # Create client
    client = SVGVideoClient()
    
    try:
        # Connect to service
        await client.connect()
        
        # Generate SVG
        logger.info("Generating SVG diagram...")
        svg_result = await client.generate_svg(
            concept="A microservices architecture with API Gateway, Authentication Service, Business Logic Service, and Database",
            provider="claude",
            save_file=True
        )
        
        if svg_result.get("status") == "success":
            logger.info("SVG generated successfully!")
            
            # Process through full pipeline
            logger.info("Creating video from the concept...")
            pipeline_result = await client.process_pipeline(
                concept="A microservices architecture with API Gateway, Authentication Service, Business Logic Service, and Database",
                provider="claude",
                options={"render_quality": "medium"}
            )
            
            if pipeline_result.get("status") == "success":
                logger.info(f"Video created successfully: {pipeline_result.get('output_path')}")
            else:
                logger.error(f"Error creating video: {pipeline_result.get('error')}")
        else:
            logger.error(f"Error generating SVG: {svg_result.get('error')}")
    
    finally:
        # Close client connection
        await client.close()

if __name__ == "__main__":
    asyncio.run(example_usage())
```

## Deployment Configurations

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3'

services:
  redis:
    image: redis:6
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  svg_video_service:
    build:
      context: .
      dockerfile: Dockerfile.service
    environment:
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./scripts:/app/scripts
      - ./outputs:/app/outputs
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
```

### Service Dockerfile

```dockerfile
# Dockerfile.service
FROM ubuntu:22.04

# Install Blender and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    blender \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for potential API
EXPOSE 8000

# Run the service
CMD ["python3", "service_launcher.py", "--config", "config.json"]
```

### Requirements File

```
# requirements.txt
langchain>=0.0.267
openai>=0.27.0
anthropic>=0.3.0
aioredis>=2.0.0
```

## Scaling Strategies

### Horizontal Scaling

For handling higher load, the service can be horizontally scaled:

```yaml
# docker-compose.scale.yml
version: '3'

services:
  redis:
    image: redis:6
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  svg_generator:
    build:
      context: .
      dockerfile: Dockerfile.svg_generator
    environment:
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    deploy:
      replicas: 3
    restart: unless-stopped

  video_processor:
    build:
      context: .
      dockerfile: Dockerfile.video_processor
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./scripts:/app/scripts
      - ./outputs:/app/outputs
    deploy:
      replicas: 2
    restart: unless-stopped

volumes:
  redis_data:
```

### Job Queue Management

For better handling of long-running tasks:

```python
# job_queue_manager.py
import asyncio
import logging
import time
import json
from typing import Dict, Any, List
from redis_bus import RedisBus

logger = logging.getLogger(__name__)

class JobQueueManager:
    """Manager for job queues using Redis."""
    
    def __init__(self, redis_url="redis://localhost:6379"):
        """Initialize the job queue manager."""
        self.redis_bus = RedisBus(redis_url)
        self.running = False
    
    async def connect(self):
        """Connect to Redis."""
        await self.redis_bus.connect()
    
    async def start(self):
        """Start the job queue manager."""
        await self.connect()
        self.running = True
        
        # Start the job processing loop
        asyncio.create_task(self._process_job_queue())
        
        logger.info("Job Queue Manager started")
    
    async def stop(self):
        """Stop the job queue manager."""
        self.running = False
        await self.redis_bus.stop()
        logger.info("Job Queue Manager stopped")
    
    async def add_job(self, job_type, job_data):
        """Add a job to the queue."""
        job_id = job_data.get("job_id") or f"{job_type}_{int(time.time())}_{hash(json.dumps(job_data))}"
        
        job_info = {
            "job_id": job_id,
            "type": job_type,
            "data": job_data,
            "status": "pending",
            "created_at": time.time()
        }
        
        # Add to queue
        await self.redis_bus.redis.lpush(f"jobs:{job_type}:queue", json.dumps(job_info))
        
        # Add to job registry
        await self.redis_bus.redis.hset("jobs:registry", job_id, json.dumps(job_info))
        
        logger.info(f"Added job {job_id} of type {job_type} to queue")
        
        return job_id
    
    async def get_job_status(self, job_id):
        """Get the status of a job."""
        job_info = await self.redis_bus.redis.hget("jobs:registry", job_id)
        
        if not job_info:
            return {"status": "not_found"}
        
        return json.loads(job_info)
    
    async def update_job_status(self, job_id, status, result=None):
        """Update the status of a job."""
        job_info = await self.get_job_status(job_id)
        
        if job_info.get("status") == "not_found":
            return False
        
        job_info["status"] = status
        job_info["updated_at"] = time.time()
        
        if result:
            job_info["result"] = result
        
        # Update job registry
        await self.redis_bus.redis.hset("jobs:registry", job_id, json.dumps(job_info))
        
        # Publish status update
        await self.redis_bus.publish(f"jobs:status:{job_id}", {
            "job_id": job_id,
            "status": status,
            "result": result
        })
        
        logger.info(f"Updated job {job_id} status to {status}")
        
        return True
    
    async def _process_job_queue(self):
        """Process jobs from the queues."""
        # This is a simplified example. In a real implementation,
        # you would have worker processes pulling jobs from the queue.
        pass

# Extended functionality would include:
# - Job prioritization
# - Worker management
# - Job cancellation
# - Rate limiting
# - Retry logic
```

## Implementation Notes

### Message Patterns

The implementation uses several Redis-based messaging patterns:

1. **Publish/Subscribe**: For event notifications and responses
2. **Request/Reply**: For synchronous client-server communication
3. **Job Queues**: For asynchronous task processing

### Service Discovery

A simple service discovery mechanism can be implemented using Redis:

```python
# service_registry.py
import asyncio
import json
import time
import uuid
from redis_bus import RedisBus

class ServiceRegistry:
    """Service registry for microservices discovery."""
    
    def __init__(self, redis_url="redis://localhost:6379"):
        """Initialize the service registry."""
        self.redis_bus = RedisBus(redis_url)
        self.service_id = str(uuid.uuid4())
        self.running = False
    
    async def register(self, service_name, service_info):
        """Register a service."""
        await self.redis_bus.connect()
        
        # Add service information
        service_key = f"services:{service_name}:{self.service_id}"
        service_data = {
            **service_info,
            "service_id": self.service_id,
            "registered_at": time.time(),
            "last_heartbeat": time.time()
        }
        
        # Store service data with TTL
        await self.redis_bus.redis.setex(
            service_key,
            60,  # 60 second TTL
            json.dumps(service_data)
        )
        
        # Start heartbeat
        self.running = True
        asyncio.create_task(self._heartbeat(service_name, service_info))
        
        return self.service_id
    
    async def unregister(self, service_name):
        """Unregister a service."""
        self.running = False
        service_key = f"services:{service_name}:{self.service_id}"
        await self.redis_bus.redis.delete(service_key)
    
    async def discover(self, service_name):
        """Discover services by name."""
        pattern = f"services:{service_name}:*"
        keys = await self.redis_bus.redis.keys(pattern)
        
        services = []
        for key in keys:
            service_data = await self.redis_bus.redis.get(key)
            if service_data:
                services.append(json.loads(service_data))
        
        return services
    
    async def _heartbeat(self, service_name, service_info):
        """Send heartbeat to keep service registration alive."""
        service_key = f"services:{service_name}:{self.service_id}"
        
        while self.running:
            service_data = {
                **service_info,
                "service_id": self.service_id,
                "registered_at": service_info.get("registered_at", time.time()),
                "last_heartbeat": time.time()
            }
            
            await self.redis_bus.redis.setex(
                service_key,
                60,  # 60 second TTL
                json.dumps(service_data)
            )
            
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
```

## Dependencies

- Python 3.9+
- Redis
- aioredis
- LangChain
- Provider-specific packages (OpenAI, Anthropic, etc.)

## Testing

### Integration Testing

```python
# test_infrastructure_integration.py
import os
import asyncio
import unittest
from redis_bus import RedisBus
from svg_video_client import SVGVideoClient

class TestInfrastructureIntegration(unittest.TestCase):
    async def async_setup(self):
        """Set up test resources."""
        # Create Redis bus
        self.redis_bus = RedisBus("redis://localhost:6379")
        await self.redis_bus.connect()
        
        # Create client
        self.client = SVGVideoClient("redis://localhost:6379")
        await self.client.connect()
    
    async def async_teardown(self):
        """Clean up test resources."""
        if hasattr(self, 'redis_bus'):
            await self.redis_bus.stop()
        
        if hasattr(self, 'client'):
            await self.client.close()
    
    async def async_test_message_bus(self):
        """Test Redis message bus."""
        # Set up handler
        test_result = {}
        
        async def test_handler(data):
            test_result["received"] = data
        
        # Subscribe to test channel
        await self.redis_bus.subscribe("test:channel", test_handler)
        
        # Publish a message
        test_message = {"test": "data", "value": 42}
        await self.redis_bus.publish("test:channel", test_message)
        
        # Wait for message processing
        await asyncio.sleep(0.1)
        
        # Check that message was received
        self.assertIn("received", test_result)
        self.assertEqual(test_result["received"]["test"], "data")
        self.assertEqual(test_result["received"]["value"], 42)
    
    async def async_test_request_reply(self):
        """Test request/reply pattern."""
        # Set up handler
        async def echo_handler(data):
            # Echo the data back
            response_channel = data.get("response_channel")
            if response_channel:
                await self.redis_bus.publish(response_channel, {
                    "echo": data
                })
        
        # Subscribe to test channel
        await self.redis_bus.subscribe("test:echo", echo_handler)
        
        # Send request
        response = await self.redis_bus.request("test:echo", {"message": "Hello"})
        
        # Check response
        self.assertIn("echo", response)
        self.assertEqual(response["echo"]["message"], "Hello")
    
    def test_message_bus(self):
        asyncio.run(self.async_test_message_bus())
    
    def test_request_reply(self):
        asyncio.run(self.async_test_request_reply())

if __name__ == "__main__":
    unittest.main()
```

## Known Limitations

1. No authentication or authorization
2. Limited scaling capabilities with basic Redis
3. No persistent job storage beyond Redis
4. Basic error handling and recovery
5. No monitoring or metrics collection

## Next Steps

1. Implement authentication and authorization
2. Add monitoring and metrics collection
3. Enhance job queue with prioritization and rate limiting
4. Implement more sophisticated service discovery
5. Add support for distributed processing with Ray
6. Create a web API for the service
7. Implement comprehensive logging and tracing