#!/usr/bin/env python
"""
Surgical Fix for Redis Connection Error

This script addresses only the inet_pton() error by making a minimal change
to the redis_bus.py file to handle dictionary configuration correctly.
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
print("GenAI Agent 3D - Surgical Redis Connection Fix".center(80))
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

# Add the necessary function to handle dictionary configurations
connect_function = """
    async def connect(self):
        \"\"\"Connect to Redis server\"\"\"
        if self.redis is None:
            try:
                # Handle case when redis_url is a dictionary
                if isinstance(self.redis_url, dict):
                    # Extract connection parameters
                    host = str(self.redis_url.get('host', 'localhost'))
                    port = int(self.redis_url.get('port', 6379))
                    db = int(self.redis_url.get('db', 0))
                    
                    # Create connection with proper types
                    self.redis = redis.Redis(
                        host=host,
                        port=port,
                        db=db,
                        decode_responses=True
                    )
                else:
                    # Standard connection
                    self.redis = redis.Redis(
                        host=self.redis_url,
                        port=self.redis_port,
                        db=self.redis_db,
                        decode_responses=True
                    )
                
                # Test connection
                await self.redis.ping()
                
                # Extract host and port for logging
                if isinstance(self.redis_url, dict):
                    host = self.redis_url.get('host', 'localhost')
                    port = self.redis_url.get('port', 6379)
                else:
                    host = self.redis_url
                    port = self.redis_port
                
                logger.info(f"Connected to Redis at {host}:{port}")
                
                # Initialize pubsub
                self.pubsub = self.redis.pubsub()
            except Exception as e:
                logger.error(f"Error connecting to Redis: {str(e)}")
                raise
"""

# Look for the connect method
connect_start = content.find("async def connect")
if connect_start >= 0:
    # Find the end of the method
    connect_end = content.find("async def", connect_start + 5)
    if connect_end > 0:
        # Replace the connect method
        old_connect = content[connect_start:connect_end]
        content = content.replace(old_connect, connect_function)
        print("✅ Updated connect method")
    else:
        print("❌ Could not find end of connect method")
else:
    print("❌ Could not find connect method")

# Write the updated content back to the file
with open(redis_bus_path, 'w') as f:
    f.write(content)

print("\n✅ Applied surgical fix to redis_bus.py")
print("\nThis fix addresses only the inet_pton() error by updating the")
print("connect method to handle dictionary configurations properly.")

# Ask if user wants to restart services
restart = input("\nDo you want to restart all services now? (y/n): ")
if restart.lower() == 'y':
    print("\nRestarting services...")
    
    # Path to manage_services.py
    manage_script = os.path.join(project_dir, "manage_services.py")
    
    try:
        # Use system Python to avoid venv issues
        subprocess.run([sys.executable, manage_script, "restart", "all"], 
                      cwd=project_dir, check=True)
        
        print("\n✅ Services restarted successfully")
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
else:
    print("\nSkipping service restart")
    print("\nTo restart services manually:")
    print(f"cd {project_dir}")
    if sys.platform == "win32":
        print("venv\\Scripts\\activate")
    else:
        print("source venv/bin/activate")
    print("python manage_services.py restart all")

print("\nDone! The Redis connection issue should now be fixed.")
