#!/usr/bin/env python
"""
Combined Fix for All LLM Issues

This script fixes both major issues in the GenAI Agent 3D project:
1. 'LLMService.__init__() takes 1 positional argument but 2 were given'
2. 'inet_pton() argument 2 must be str, not dict'

It also creates the necessary API structure and restarts services.
"""

import os
import sys
import shutil
import subprocess
import time

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
services_dir = os.path.join(project_dir, "genai_agent", "services")
api_dir = os.path.join(project_dir, "genai_agent", "api")

print("=" * 80)
print("GenAI Agent 3D - Combined LLM Issues Fix".center(80))
print("=" * 80)
print()

# Fix 1: LLMService initialization error
print("Fix 1: Addressing LLMService initialization error...")

llm_api_routes_path = os.path.join(services_dir, "llm_api_routes.py")
if os.path.exists(llm_api_routes_path):
    # Create a backup
    backup_path = f"{llm_api_routes_path}.bak"
    shutil.copy2(llm_api_routes_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    with open(llm_api_routes_path, 'r') as f:
        content = f.read()
    
    # Look for the LLMService initialization
    if "_llm_service = LLMService(config)" in content:
        # Replace with correct initialization
        content = content.replace(
            "_llm_service = LLMService(config)",
            "_llm_service = LLMService()"
        )
        print("✅ Fixed LLMService initialization")
    elif "from genai_agent.services.llm import LLMService" in content:
        # Find the get_llm_service function
        get_llm_service_start = content.find("def get_llm_service()")
        if get_llm_service_start >= 0:
            # Find the end of the function
            get_llm_service_end = content.find("@router", get_llm_service_start)
            if get_llm_service_end >= 0:
                # Extract the function
                get_llm_service_func = content[get_llm_service_start:get_llm_service_end]
                
                # Create updated function
                updated_func = """def get_llm_service():
    \"\"\"
    Get or create the LLM service instance
    \"\"\"
    global _llm_service
    
    if _llm_service is None:
        try:
            # Import the LLM service
            from genai_agent.services.llm import LLMService
            
            # Create a new LLM service instance (without passing config)
            _llm_service = LLMService()
        except Exception as e:
            logger.error(f"Error creating LLM service: {str(e)}")
            raise
    
    return _llm_service
"""
                
                # Replace the function
                content = content.replace(get_llm_service_func, updated_func)
                print("✅ Updated get_llm_service function")
    
    with open(llm_api_routes_path, 'w') as f:
        f.write(content)
else:
    print(f"❌ Could not find {llm_api_routes_path}")

# Fix 2: Redis connection error
print("\nFix 2: Addressing Redis connection error...")

redis_bus_path = os.path.join(services_dir, "redis_bus.py")
if os.path.exists(redis_bus_path):
    # Create a backup
    backup_path = f"{redis_bus_path}.bak"
    shutil.copy2(redis_bus_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Create the updated redis_bus.py content
    redis_bus_content = """
\"\"\"
Redis Message Bus - Handles communication between services
\"\"\"

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable, Union
import redis.asyncio as redis

# Configure logging
logger = logging.getLogger(__name__)

class RedisMessageBus:
    \"\"\"Redis-based message bus for service communication\"\"\"
    
    def __init__(self, redis_url=\"localhost\", redis_port=6379, redis_db=0):
        \"\"\"
        Initialize Redis message bus
        
        Args:
            redis_url: Redis server URL or config dict
            redis_port: Redis server port
            redis_db: Redis database number
        \"\"\"
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
        
        logger.info(f\"Redis Message Bus initialized with {self.redis_url}:{self.redis_port}\")
    
    async def connect(self):
        \"\"\"Connect to Redis server\"\"\"
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
                logger.info(f\"Connected to Redis at {host}:{port}\")
                
                # Initialize pubsub
                self.pubsub = self.redis.pubsub()
            except Exception as e:
                logger.error(f\"Error connecting to Redis: {str(e)}\")
                raise
    
    async def disconnect(self):
        \"\"\"Disconnect from Redis server\"\"\"
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
            logger.info(\"Disconnected from Redis\")
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        \"\"\"
        Publish message to channel
        
        Args:
            channel: Channel name
            message: Message to publish (will be JSON-encoded)
        \"\"\"
        if self.redis is None:
            await self.connect()
        
        # Convert message to JSON
        message_json = json.dumps(message)
        
        # Publish message
        await self.redis.publish(channel, message_json)
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        \"\"\"
        Subscribe to channel with callback
        
        Args:
            channel: Channel name
            callback: Async callback function that takes message as argument
        \"\"\"
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
        \"\"\"
        Unsubscribe from channel
        
        Args:
            channel: Channel name
        \"\"\"
        if self.pubsub is not None:
            # Unsubscribe from channel
            await self.pubsub.unsubscribe(channel)
            
            # Remove callback
            if channel in self.subscriptions:
                del self.subscriptions[channel]
    
    async def start_listener(self):
        \"\"\"Start message listener loop\"\"\"
        if self.running:
            return
        
        self.running = True
        self.listener_task = asyncio.create_task(self._listen())
    
    async def stop_listener(self):
        \"\"\"Stop message listener loop\"\"\"
        self.running = False
        
        if self.listener_task is not None:
            try:
                self.listener_task.cancel()
                await self.listener_task
            except asyncio.CancelledError:
                pass
            self.listener_task = None
    
    async def _listen(self):
        \"\"\"Message listener loop\"\"\"
        try:
            while self.running:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                
                if message is not None:
                    channel = message[\"channel\"]
                    data = message[\"data\"]
                    
                    # Parse JSON data
                    try:
                        data_json = json.loads(data)
                    except json.JSONDecodeError:
                        logger.warning(f\"Received invalid JSON on channel {channel}: {data}\")
                        continue
                    
                    # Find and call callback
                    if channel in self.subscriptions:
                        callback = self.subscriptions[channel]
                        try:
                            await callback(data_json)
                        except Exception as e:
                            logger.error(f\"Error in message callback for channel {channel}: {str(e)}\")
                
                # Short sleep to avoid CPU spinning
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            # Normal cancellation
            pass
        except Exception as e:
            logger.error(f\"Error in message listener: {str(e)}\")
            self.running = False

# Singleton instance
_message_bus = None

def get_message_bus(redis_url=\"localhost\", redis_port=6379, redis_db=0):
    \"\"\"
    Get message bus singleton instance
    
    Args:
        redis_url: Redis server URL or config dict
        redis_port: Redis server port
        redis_db: Redis database number
        
    Returns:
        RedisMessageBus instance
    \"\"\"
    global _message_bus
    
    if _message_bus is None:
        _message_bus = RedisMessageBus(redis_url, redis_port, redis_db)
    
    return _message_bus
"""
    
    with open(redis_bus_path, 'w') as f:
        f.write(redis_bus_content)
    
    print("✅ Updated Redis Message Bus with robust implementation")
else:
    print(f"❌ Could not find {redis_bus_path}")

# Fix 3: Create API structure
print("\nFix 3: Creating API structure...")

# Create API directory if it doesn't exist
os.makedirs(api_dir, exist_ok=True)

# Create __init__.py in API directory
api_init_path = os.path.join(api_dir, "__init__.py")
api_init_content = """
\"\"\"
API package for GenAI Agent 3D
\"\"\"

from fastapi import APIRouter

# Create API router
api_router = APIRouter()

# Import sub-routers
try:
    from .llm import router as llm_router
    api_router.include_router(llm_router)
except ImportError:
    pass
"""

with open(api_init_path, 'w') as f:
    f.write(api_init_content)

print(f"✅ Created API __init__.py at {api_init_path}")

# Create llm.py in API directory
api_llm_path = os.path.join(api_dir, "llm.py")
api_llm_content = """
\"\"\"
LLM API endpoints for GenAI Agent 3D
\"\"\"

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

# Import LLM service
from ..services.llm import LLMService

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix=\"/llm\", tags=[\"llm\"])

# Create LLM service instance
llm_service = LLMService()

# Pydantic models for request/response
class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
class GenerateResponse(BaseModel):
    text: str
    
class Provider(BaseModel):
    name: str
    is_local: bool
    models: List[Dict[str, Any]]

@router.get(\"/providers\")
async def get_providers():
    \"\"\"Get available LLM providers and models\"\"\"
    try:
        # Initialize LLM service if needed
        if not llm_service.initialized:
            await llm_service.initialize()
            
        # Get providers from LLM service
        return llm_service.get_providers()
    except Exception as e:
        logger.error(f\"Error fetching providers: {str(e)}\")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(\"/generate\", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    \"\"\"Generate text from a prompt using the specified LLM\"\"\"
    try:
        if not request.prompt:
            raise HTTPException(status_code=400, detail=\"Prompt is required\")
            
        # Generate text
        text = await llm_service.generate(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            parameters=request.parameters
        )
        
        return GenerateResponse(text=text)
    except Exception as e:
        logger.error(f\"Error generating text: {str(e)}\")
        raise HTTPException(status_code=500, detail=str(e))
"""

with open(api_llm_path, 'w') as f:
    f.write(api_llm_content)

print(f"✅ Created API llm.py at {api_llm_path}")

# Ask if user wants to restart services
restart = input("\nDo you want to restart all services now? (y/n): ")
if restart.lower() == 'y':
    print("\nRestarting services...")
    
    # Path to manage_services.py
    manage_script = os.path.join(project_dir, "manage_services.py")
    
    # Windows
    if sys.platform == "win32":
        venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
        
        # Check if venv exists
        if os.path.exists(venv_python):
            try:
                # Stop services
                subprocess.run([venv_python, manage_script, "stop", "all"], 
                            cwd=project_dir, check=True)
                
                # Small delay
                time.sleep(2)
                
                # Start services
                subprocess.run([venv_python, manage_script, "start", "all"], 
                            cwd=project_dir, check=True)
                
                print("\n✅ Services restarted successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error restarting services: {e}")
        else:
            try:
                # Use system Python
                subprocess.run([sys.executable, manage_script, "stop", "all"], 
                            cwd=project_dir, check=True)
                
                # Small delay
                time.sleep(2)
                
                # Start services
                subprocess.run([sys.executable, manage_script, "start", "all"], 
                            cwd=project_dir, check=True)
                
                print("\n✅ Services restarted successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error restarting services: {e}")
    # Linux/Mac
    else:
        venv_python = os.path.join(project_dir, "venv", "bin", "python")
        
        # Check if venv exists
        if os.path.exists(venv_python):
            try:
                # Stop services
                subprocess.run([venv_python, manage_script, "stop", "all"], 
                            cwd=project_dir, check=True)
                
                # Small delay
                time.sleep(2)
                
                # Start services
                subprocess.run([venv_python, manage_script, "start", "all"], 
                            cwd=project_dir, check=True)
                
                print("\n✅ Services restarted successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error restarting services: {e}")
        else:
            try:
                # Use system Python
                subprocess.run([sys.executable, manage_script, "stop", "all"], 
                            cwd=project_dir, check=True)
                
                # Small delay
                time.sleep(2)
                
                # Start services
                subprocess.run([sys.executable, manage_script, "start", "all"], 
                            cwd=project_dir, check=True)
                
                print("\n✅ Services restarted successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error restarting services: {e}")
    
    print("\nYou can access the web interface at: http://localhost:3000")
else:
    print("\nSkipping service restart")
    print("\nTo restart services manually:")
    print(f"1. cd {project_dir}")
    if sys.platform == "win32":
        print("2. venv\\Scripts\\activate")
    else:
        print("2. source venv/bin/activate")
    print("3. python manage_services.py restart all")

print("\nDone! All LLM issues should now be fixed.")
