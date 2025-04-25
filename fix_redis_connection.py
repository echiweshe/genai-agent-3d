#!/usr/bin/env python
"""
Direct fix for the Redis connection error in GenAI Agent 3D

This script fixes the "inet_pton() argument 2 must be str, not dict" error
by updating the RedisMessageBus class to handle dictionary configurations.
"""

import os
import sys
import shutil
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
services_dir = os.path.join(project_dir, "genai_agent", "services")

# Updated redis_bus.py content
redis_bus_content = '''"""
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
            self.redis_config = redis_url
            # Extract basic info for logging
            self.redis_url = redis_url.get('host', 'localhost')
            self.redis_port = redis_url.get('port', 6379)
            
            # Log full configuration 
            logger.info(f"Redis Message Bus initialized with {self.redis_url}:{self.redis_port}")
        else:
            self.redis_url = redis_url
            self.redis_port = redis_port
            self.redis_db = redis_db
            
            # Create standard config
            self.redis_config = {
                'host': self.redis_url,
                'port': self.redis_port,
                'db': self.redis_db
            }
            
            logger.info(f"Redis Message Bus initialized with {self.redis_url}:{self.redis_port}")
        
        # Initialize connection vars
        self.redis = None
        self.pubsub = None
        self.subscriptions = {}
        self.running = False
        self.listener_task = None
    
    async def connect(self):
        """Connect to Redis server"""
        if self.redis is None:
            try:
                # Extract connection params from config
                host = self.redis_url 
                port = self.redis_port
                db = self.redis_config.get('db', 0)
                
                # Create connection with extracted params
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
'''

print("=" * 80)
print("GenAI Agent 3D - Redis Connection Fix".center(80))
print("=" * 80)
print()

# Fix redis_bus.py
print("Fixing Redis Message Bus to handle dictionary configuration...")

redis_bus_path = os.path.join(services_dir, "redis_bus.py")
if os.path.exists(redis_bus_path):
    # Create a backup
    backup_path = f"{redis_bus_path}.bak"
    shutil.copy2(redis_bus_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Write the updated file
    with open(redis_bus_path, 'w') as f:
        f.write(redis_bus_content)
    
    print("✅ Successfully updated redis_bus.py")
else:
    print(f"❌ Could not find {redis_bus_path}")
    sys.exit(1)

print("\nFix applied successfully!")
print("\nNext steps:")
print("1. Restart all services with: cd genai_agent_project")
print("2. Run: python manage_services.py restart all")
print("3. Access the web interface at: http://localhost:3000")

# Ask if user wants to restart services
restart = input("\nDo you want to restart services now? (y/n): ")
if restart.lower() == 'y':
    print("\nRestarting services...")
    try:
        # Windows
        if sys.platform == "win32":
            subprocess.run([
                "cmd", "/c", 
                f"cd {project_dir} && venv\\Scripts\\activate.bat && python manage_services.py restart all"
            ], check=True)
        # Linux/macOS
        else:
            subprocess.run([
                "bash", "-c",
                f"cd {project_dir} && source venv/bin/activate && python manage_services.py restart all"
            ], check=True)
            
        print("\n✅ Services restarted successfully!")
        print("\nYou can access the web interface at: http://localhost:3000")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error restarting services: {e}")
        print("\nYou can try to manually restart services with:")
        print(f"cd {project_dir}")
        
        if sys.platform == "win32":
            print("venv\\Scripts\\activate")
        else:
            print("source venv/bin/activate")
            
        print("python manage_services.py restart all")
