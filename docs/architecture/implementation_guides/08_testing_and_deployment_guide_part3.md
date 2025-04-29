="redis://localhost:6379"):
    """Initialize a render farm worker."""
    self.worker_id = worker_id
    self.redis_bus = RedisBus(redis_url)
    self.running = False
    
    # Worker capabilities
    self.capabilities = {
        "gpu": True if self._check_gpu_available() else False,
        "cpu_cores": os.cpu_count(),
        "memory": self._get_available_memory(),
        "blender_version": self._get_blender_version()
    }
    
    logger.info(f"Worker {worker_id} initialized with capabilities: {self.capabilities}")
    
    def _check_gpu_available(self):
        """Check if GPU is available for rendering."""
        # This is a simplified check, in a real implementation 
        # you would use more sophisticated detection
        try:
            import subprocess
            # Try to detect GPU with Blender
            result = subprocess.run(
                ["blender", "--factory-startup", "-b", "--python-expr",
                 "import bpy; print('GPU_AVAILABLE' if bpy.context.preferences.addons['cycles'].preferences.has_active_device() else 'GPU_UNAVAILABLE'); exit()"],
                capture_output=True, text=True, timeout=30
            )
            return "GPU_AVAILABLE" in result.stdout
        except Exception as e:
            logger.warning(f"Error checking GPU availability: {str(e)}")
            return False
    
    def _get_available_memory(self):
        """Get available system memory in GB."""
        try:
            import psutil
            return round(psutil.virtual_memory().total / (1024**3), 1)  # Convert to GB
        except ImportError:
            logger.warning("psutil not available, cannot determine memory")
            return 0
    
    def _get_blender_version(self):
        """Get the Blender version."""
        try:
            import subprocess
            result = subprocess.run(
                ["blender", "--version"], 
                capture_output=True, text=True, timeout=10
            )
            import re
            match = re.search(r'Blender\s+(\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
            return "unknown"
        except Exception as e:
            logger.warning(f"Error getting Blender version: {str(e)}")
            return "unknown"
    
    async def start(self):
        """Start the worker."""
        await self.redis_bus.connect()
        
        # Register with the farm manager
        await self.redis_bus.publish("render_farm:workers", {
            "action": "register",
            "worker_id": self.worker_id,
            "capabilities": self.capabilities
        })
        
        # Subscribe to task channel
        await self.redis_bus.subscribe(f"render_farm:tasks:{self.worker_id}", self._handle_task)
        
        # Subscribe to global tasks
        await self.redis_bus.subscribe("render_farm:tasks:all", self._handle_task)
        
        # Start the message processing
        await self.redis_bus.start()
        
        self.running = True
        
        # Start the heartbeat
        asyncio.create_task(self._send_heartbeat())
        
        logger.info(f"Worker {self.worker_id} started")
    
    async def stop(self):
        """Stop the worker."""
        self.running = False
        
        # Unregister from the farm manager
        await self.redis_bus.publish("render_farm:workers", {
            "action": "unregister",
            "worker_id": self.worker_id
        })
        
        await self.redis_bus.stop()
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    async def _send_heartbeat(self):
        """Send periodic heartbeat to the farm manager."""
        while self.running:
            await self.redis_bus.publish("render_farm:heartbeat", {
                "worker_id": self.worker_id,
                "timestamp": time.time(),
                "status": "available"  # or "busy" if handling a task
            })
            
            await asyncio.sleep(30)  # Heartbeat every 30 seconds
    
    async def _handle_task(self, task_data):
        """Handle a rendering task."""
        task_id = task_data.get("task_id")
        response_channel = task_data.get("response_channel")
        
        if not task_id or not response_channel:
            logger.warning(f"Invalid task data received: {task_data}")
            return
        
        logger.info(f"Worker {self.worker_id} received task {task_id}")
        
        try:
            # Update status to busy
            await self.redis_bus.publish("render_farm:heartbeat", {
                "worker_id": self.worker_id,
                "timestamp": time.time(),
                "status": "busy",
                "task_id": task_id
            })
            
            # Execute the task
            result = await self._execute_render_task(task_data)
            
            # Send response
            await self.redis_bus.publish(response_channel, {
                "worker_id": self.worker_id,
                "task_id": task_id,
                "status": "completed",
                "result": result
            })
            
            logger.info(f"Worker {self.worker_id} completed task {task_id}")
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            
            # Send error response
            await self.redis_bus.publish(response_channel, {
                "worker_id": self.worker_id,
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            })
        
        finally:
            # Update status back to available
            await self.redis_bus.publish("render_farm:heartbeat", {
                "worker_id": self.worker_id,
                "timestamp": time.time(),
                "status": "available"
            })
    
    async def _execute_render_task(self, task_data):
        """Execute the actual rendering task."""
        # Extract task details
        task_type = task_data.get("type", "render")
        blend_file = task_data.get("blend_file")
        output_path = task_data.get("output_path")
        options = task_data.get("options", {})
        
        if not blend_file or not output_path:
            raise ValueError("Missing required task parameters")
        
        # Ensure the file exists
        if not os.path.exists(blend_file):
            raise FileNotFoundError(f"Blend file not found: {blend_file}")
        
        # Determine the Blender script to use
        script_name = "video_renderer.py"
        if task_type == "convert_svg":
            script_name = "svg_to_3d_blender.py"
        elif task_type == "animate":
            script_name = "scenex_animation.py"
        
        # Get script path
        script_dir = options.get("script_dir", "scripts")
        script_path = os.path.join(script_dir, script_name)
        
        # Construct command arguments
        cmd_args = [blend_file, output_path]
        
        # Add quality setting for rendering
        if task_type == "render" and "quality" in options:
            cmd_args.append(options["quality"])
        
        # Execute the task
        import subprocess
        cmd = [
            "blender",
            "--background",
            "--python", script_path,
            "--"
        ] + cmd_args
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            # Use a timeout to prevent tasks from hanging indefinitely
            timeout = options.get("timeout", 3600)  # Default: 1 hour
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            if process.returncode != 0:
                error_msg = stderr.decode()
                raise RuntimeError(f"Process failed with code {process.returncode}: {error_msg}")
            
            # Check if output was created
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Output file was not created: {output_path}")
            
            return {
                "output_path": output_path,
                "size": os.path.getsize(output_path),
                "execution_time": time.time() - task_data.get("timestamp", time.time())
            }
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Task execution timed out after {timeout} seconds")

# Example usage: run a worker
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Render Farm Worker")
    parser.add_argument("--id", help="Worker ID", default=f"worker-{os.getpid()}")
    parser.add_argument("--redis", help="Redis URL", default="redis://localhost:6379")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run worker
    async def main():
        worker = RenderFarmWorker(args.id, args.redis)
        
        try:
            await worker.start()
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Worker interrupted")
        finally:
            await worker.stop()
    
    asyncio.run(main())
```

### Render Farm Manager

```python
# render_farm_manager.py
import asyncio
import time
import json
import logging
import uuid
from redis_bus import RedisBus

logger = logging.getLogger(__name__)

class RenderFarmManager:
    """Manager for coordinating render farm workers."""
    
    def __init__(self, redis_url="redis://localhost:6379"):
        """Initialize the render farm manager."""
        self.redis_bus = RedisBus(redis_url)
        self.running = False
        self.workers = {}  # Track available workers
        self.tasks = {}    # Track active tasks
    
    async def start(self):
        """Start the render farm manager."""
        await self.redis_bus.connect()
        
        # Subscribe to worker registrations
        await self.redis_bus.subscribe("render_farm:workers", self._handle_worker_registration)
        
        # Subscribe to worker heartbeats
        await self.redis_bus.subscribe("render_farm:heartbeat", self._handle_worker_heartbeat)
        
        # Subscribe to task requests
        await self.redis_bus.subscribe("render_farm:tasks", self._handle_task_request)
        
        # Start the message processing
        await self.redis_bus.start()
        
        self.running = True
        
        # Start the worker cleanup task
        asyncio.create_task(self._cleanup_workers())
        
        logger.info("Render Farm Manager started")
    
    async def stop(self):
        """Stop the render farm manager."""
        self.running = False
        await self.redis_bus.stop()
        logger.info("Render Farm Manager stopped")
    
    async def _handle_worker_registration(self, data):
        """Handle worker registration and unregistration."""
        action = data.get("action")
        worker_id = data.get("worker_id")
        
        if not worker_id:
            logger.warning(f"Invalid worker registration data: {data}")
            return
        
        if action == "register":
            # Register worker
            self.workers[worker_id] = {
                "id": worker_id,
                "capabilities": data.get("capabilities", {}),
                "last_heartbeat": time.time(),
                "status": "available"
            }
            logger.info(f"Worker {worker_id} registered")
            
        elif action == "unregister":
            # Unregister worker
            if worker_id in self.workers:
                self.workers.pop(worker_id)
                logger.info(f"Worker {worker_id} unregistered")
    
    async def _handle_worker_heartbeat(self, data):
        """Handle worker heartbeat."""
        worker_id = data.get("worker_id")
        
        if not worker_id:
            logger.warning(f"Invalid worker heartbeat data: {data}")
            return
        
        if worker_id in self.workers:
            # Update worker status
            self.workers[worker_id].update({
                "last_heartbeat": time.time(),
                "status": data.get("status", "available"),
                "task_id": data.get("task_id")
            })
        else:
            # Worker not registered yet
            logger.warning(f"Heartbeat from unregistered worker: {worker_id}")
    
    async def _handle_task_request(self, data):
        """Handle a task request."""
        task_id = data.get("task_id", str(uuid.uuid4()))
        response_channel = data.get("response_channel")
        
        if not response_channel:
            logger.warning(f"Task {task_id} missing response channel")
            return
        
        logger.info(f"Received task request: {task_id}")
        
        # Store task information
        self.tasks[task_id] = {
            "id": task_id,
            "data": data,
            "timestamp": time.time(),
            "status": "pending",
            "response_channel": response_channel
        }
        
        # Find a suitable worker for the task
        worker_id = await self._find_worker_for_task(data)
        
        if worker_id:
            # Assign task to worker
            await self._assign_task(task_id, worker_id)
        else:
            # No suitable worker available
            logger.warning(f"No suitable worker available for task {task_id}")
            
            # Send response
            await self.redis_bus.publish(response_channel, {
                "task_id": task_id,
                "status": "error",
                "error": "No suitable worker available"
            })
            
            # Remove task
            self.tasks.pop(task_id, None)
    
    async def _find_worker_for_task(self, task_data):
        """Find a suitable worker for a task."""
        # Get task requirements
        requirements = task_data.get("requirements", {})
        
        # Filter available workers
        available_workers = {
            worker_id: worker 
            for worker_id, worker in self.workers.items()
            if worker.get("status") == "available"
        }
        
        if not available_workers:
            return None
        
        # Check for GPU requirement
        if requirements.get("gpu", False):
            gpu_workers = {
                worker_id: worker 
                for worker_id, worker in available_workers.items()
                if worker.get("capabilities", {}).get("gpu", False)
            }
            
            if gpu_workers:
                available_workers = gpu_workers
        
        # Check for memory requirement
        min_memory = requirements.get("min_memory_gb", 0)
        if min_memory > 0:
            memory_workers = {
                worker_id: worker 
                for worker_id, worker in available_workers.items()
                if worker.get("capabilities", {}).get("memory", 0) >= min_memory
            }
            
            if memory_workers:
                available_workers = memory_workers
        
        # Return the first suitable worker
        # In a more sophisticated implementation, you would use a better selection algorithm
        if available_workers:
            return next(iter(available_workers.keys()))
        
        return None
    
    async def _assign_task(self, task_id, worker_id):
        """Assign a task to a worker."""
        if task_id not in self.tasks or worker_id not in self.workers:
            return False
        
        task = self.tasks[task_id]
        task_data = task["data"]
        response_channel = task["response_channel"]
        
        # Update task status
        task["status"] = "assigned"
        task["worker_id"] = worker_id
        
        # Send task to worker
        await self.redis_bus.publish(f"render_farm:tasks:{worker_id}", {
            **task_data,
            "task_id": task_id,
            "response_channel": f"render_farm:results:{task_id}",
            "timestamp": time.time()
        })
        
        # Subscribe to the result
        await self.redis_bus.subscribe(f"render_farm:results:{task_id}", 
                                     lambda result: self._handle_task_result(task_id, result, response_channel))
        
        logger.info(f"Task {task_id} assigned to worker {worker_id}")
        
        return True
    
    async def _handle_task_result(self, task_id, result, response_channel):
        """Handle a task result."""
        if task_id not in self.tasks:
            logger.warning(f"Result for unknown task: {task_id}")
            return
        
        # Update task status
        task = self.tasks[task_id]
        task["status"] = result.get("status", "completed")
        task["result"] = result
        
        # Forward the result to the original requester
        await self.redis_bus.publish(response_channel, result)
        
        # Clean up task
        self.tasks.pop(task_id, None)
        
        logger.info(f"Task {task_id} completed with status: {task['status']}")
    
    async def _cleanup_workers(self):
        """Clean up workers that haven't sent heartbeats."""
        while self.running:
            current_time = time.time()
            inactive_workers = []
            
            for worker_id, worker in self.workers.items():
                last_heartbeat = worker.get("last_heartbeat", 0)
                
                # Worker is considered inactive if no heartbeat for 2 minutes
                if current_time - last_heartbeat > 120:
                    inactive_workers.append(worker_id)
            
            # Remove inactive workers
            for worker_id in inactive_workers:
                logger.warning(f"Worker {worker_id} inactive, removing")
                self.workers.pop(worker_id, None)
            
            # Sleep for a while
            await asyncio.sleep(60)  # Check every minute

# Example usage: run the manager
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Render Farm Manager")
    parser.add_argument("--redis", help="Redis URL", default="redis://localhost:6379")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run manager
    async def main():
        manager = RenderFarmManager(args.redis)
        
        try:
            await manager.start()
            
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Manager interrupted")
        finally:
            await manager.stop()
    
    asyncio.run(main())
```

## Security Considerations

When deploying your SVG to Video pipeline, consider the following security aspects:

### API Authentication

Implement proper authentication for client access:

```python
# api_auth.py
import jwt
import time
from functools import wraps
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

# Secret key for JWT signing - in production, this should be loaded securely
SECRET_KEY = "your-secret-key-change-this-in-production"

def generate_token(user_id, permissions, expires_in=3600):
    """Generate a JWT token."""
    payload = {
        "user_id": user_id,
        "permissions": permissions,
        "exp": time.time() + expires_in
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def auth_required(handler):
    """Authentication middleware for aiohttp handlers."""
    @wraps(handler)
    async def wrapper(request):
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return web.json_response({"error": "Authentication required"}, status=401)
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        try:
            # Verify token
            payload = verify_token(token)
            
            # Add user info to request
            request["user"] = payload
            
            # Call the handler
            return await handler(request)
            
        except ValueError as e:
            return web.json_response({"error": str(e)}, status=401)
    
    return wrapper

def require_permission(permission):
    """Middleware to check for specific permission."""
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request):
            user = request.get("user")
            
            if not user:
                return web.json_response({"error": "Authentication required"}, status=401)
            
            permissions = user.get("permissions", [])
            
            if permission not in permissions:
                return web.json_response({"error": "Permission denied"}, status=403)
            
            return await handler(request)
        
        return wrapper
    
    return decorator
```

### Content Validation

Ensure input validation to prevent security issues:

```python
# content_validation.py
import logging
import re
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

def is_valid_svg(svg_content):
    """Validate SVG content for security and correctness."""
    # Check for basic SVG structure
    if not svg_content.strip().startswith("<svg") or "</svg>" not in svg_content:
        return False
    
    try:
        # Parse XML
        root = ET.fromstring(svg_content)
        
        # Check namespace
        if "svg" not in root.tag:
            return False
        
        # Validate size (prevent excessively large SVGs)
        viewBox = root.get("viewBox", "0 0 100 100")
        parts = viewBox.split()
        if len(parts) == 4:
            width = float(parts[2])
            height = float(parts[3])
            if width > 10000 or height > 10000:
                logger.warning(f"SVG too large: {width}x{height}")
                return False
        
        # Check for potentially malicious content
        # Script tags are a security risk
        scripts = root.findall(".//script")
        if scripts:
            logger.warning("SVG contains script elements")
            return False
        
        # Check for external references
        for elem in root.findall(".//*"):
            for attr in elem.attrib:
                value = elem.attrib[attr]
                if attr in ["href", "xlink:href"] and (value.startswith("http") or value.startswith("//")):
                    logger.warning(f"SVG contains external reference: {value}")
                    return False
        
        # SVG seems valid and safe
        return True
        
    except Exception as e:
        logger.error(f"Error validating SVG: {str(e)}")
        return False

def validate_concept(concept):
    """Validate a concept description for security."""
    # Check length
    if not concept or len(concept) > 5000:
        return False, "Concept must be between 1 and 5000 characters"
    
    # Check for potentially malicious content
    # This is a very basic check, in a real system you would use more sophisticated methods
    dangerous_patterns = [
        r'<script', r'javascript:', r'onerror=', r'onclick='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, concept, re.IGNORECASE):
            return False, "Concept contains potentially unsafe content"
    
    return True, "Concept is valid"
```

## Conclusion

This testing and deployment guide provides comprehensive information for implementing, testing, and deploying the SVG to Video pipeline. By following these practices, you can ensure a reliable, secure, and performant system that meets your needs.

For further assistance or to report issues, contact the development team or refer to the project documentation.

---

## Appendix

### Environment Variables

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional Configuration
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
BLENDER_PATH=/path/to/blender
OUTPUT_DIR=/path/to/outputs
```

### Example Scripts

#### Start the SVG Video Service

```bash
#!/bin/bash
# start_service.sh

# Load environment variables
source .env

# Start Redis if not already running
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Starting Redis..."
    redis-server --daemonize yes
fi

# Start the service
python service_launcher.py --config config.json
```

#### Run a Test Job

```bash
#!/bin/bash
# test_job.sh

# Load environment variables
source .env

# Generate a test video
python pipeline_cli.py generate "A flowchart showing the process of user registration" test_output.mp4 --provider claude --quality medium

# Check if output was created
if [ -f test_output.mp4 ]; then
    echo "Test job completed successfully!"
    echo "Output: test_output.mp4"
else
    echo "Test job failed!"
fi
```
