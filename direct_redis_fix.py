#!/usr/bin/env python
"""
Direct Redis Connection Fix

This script directly patches the Redis connection code to fix the 
'inet_pton() argument 2 must be str, not dict' error by modifying
how Redis connections are created in the application.
"""

import os
import sys
import shutil
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
services_dir = os.path.join(project_dir, "genai_agent", "services")

print("=" * 80)
print("GenAI Agent 3D - Direct Redis Connection Fix".center(80))
print("=" * 80)
print()

# Path to the redis_bus.py file
redis_bus_path = os.path.join(services_dir, "redis_bus.py")

# Check if the file exists
if not os.path.exists(redis_bus_path):
    print(f"❌ Could not find {redis_bus_path}")
    sys.exit(1)

# Create a backup
backup_path = f"{redis_bus_path}.bak"
shutil.copy2(redis_bus_path, backup_path)
print(f"✅ Created backup at {backup_path}")

# Read the current content
with open(redis_bus_path, 'r') as f:
    content = f.read()

# Modify __init__ method
if "def __init__(self, redis_url=" in content:
    # Find the start of the method
    init_start = content.find("def __init__(self, redis_url=")
    if init_start >= 0:
        # Find the end of the method
        init_end = content.find("async def connect", init_start)
        if init_end >= 0:
            # Extract the method
            init_method = content[init_start:init_end]
            
            # Create updated method
            updated_init = """def __init__(self, redis_url="localhost", redis_port=6379, redis_db=0):
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
        
        logger.info(f"Redis Message Bus initialized with {self.redis_url}:{self.redis_port}")
    """
            
            # Replace the method
            content = content.replace(init_method, updated_init)
            print("✅ Updated __init__ method")

# Modify connect method
if "async def connect" in content:
    # Find the start of the method
    connect_start = content.find("async def connect")
    if connect_start >= 0:
        # Find the end of the method
        connect_end = content.find("async def disconnect", connect_start)
        if connect_end >= 0:
            # Extract the method
            connect_method = content[connect_start:connect_end]
            
            # Create updated method
            updated_connect = """async def connect(self):
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
                logger.info(f"Connected to Redis at {host}:{port}")
                
                # Initialize pubsub
                self.pubsub = self.redis.pubsub()
            except Exception as e:
                logger.error(f"Error connecting to Redis: {str(e)}")
                raise
    """
            
            # Replace the method
            content = content.replace(connect_method, updated_connect)
            print("✅ Updated connect method")

# Add Union to imports if needed
if "from typing import" in content and "Union" not in content:
    content = content.replace(
        "from typing import Dict, Any, List, Optional, Callable, Awaitable",
        "from typing import Dict, Any, List, Optional, Callable, Awaitable, Union"
    )
    print("✅ Updated imports to include Union type")

# Write the updated content back to the file
with open(redis_bus_path, 'w') as f:
    f.write(content)

print("\n✅ Redis connection fix applied successfully")

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
            # Stop services
            subprocess.run([venv_python, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([venv_python, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
        else:
            # Use system Python
            subprocess.run([sys.executable, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([sys.executable, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
    # Linux/Mac
    else:
        venv_python = os.path.join(project_dir, "venv", "bin", "python")
        
        # Check if venv exists
        if os.path.exists(venv_python):
            # Stop services
            subprocess.run([venv_python, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([venv_python, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
        else:
            # Use system Python
            subprocess.run([sys.executable, manage_script, "stop", "all"], 
                          cwd=project_dir, check=True)
            
            # Small delay
            import time
            time.sleep(2)
            
            # Start services
            subprocess.run([sys.executable, manage_script, "start", "all"], 
                          cwd=project_dir, check=True)
    
    print("\n✅ Services restarted successfully")
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

print("\nDone! The Redis connection issue should now be fixed.")
