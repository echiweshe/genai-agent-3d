#!/usr/bin/env python
"""
Fix LLM errors in GenAI Agent 3D

This script fixes the following errors:
1. "LLMService.__init__() takes 1 positional argument but 2 were given"
2. "inet_pton() argument 2 must be str, not dict"
"""

import os
import sys
import shutil
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
services_dir = os.path.join(project_dir, "genai_agent", "services")
api_dir = os.path.join(project_dir, "genai_agent", "api")

print("=" * 80)
print("GenAI Agent 3D - LLM Error Fixes".center(80))
print("=" * 80)
print()

# Fix 1: LLMService.__init__() error
print("Fix 1: Updating LLM API routes to fix initialization error...")

llm_api_routes_path = os.path.join(services_dir, "llm_api_routes.py")
if os.path.exists(llm_api_routes_path):
    # Create a backup
    backup_path = f"{llm_api_routes_path}.bak"
    shutil.copy2(llm_api_routes_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    with open(llm_api_routes_path, 'r') as f:
        content = f.read()
    
    # Replace the problematic line
    content = content.replace(
        "_llm_service = LLMService(config)",
        "_llm_service = LLMService()"
    )
    
    with open(llm_api_routes_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated LLM API routes to fix initialization error")
else:
    print(f"❌ Could not find {llm_api_routes_path}")

# Fix 2: inet_pton() error
print("\nFix 2: Updating Redis Message Bus to handle dictionary configuration...")

redis_bus_path = os.path.join(services_dir, "redis_bus.py")
if os.path.exists(redis_bus_path):
    # Create a backup
    backup_path = f"{redis_bus_path}.bak"
    shutil.copy2(redis_bus_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    with open(redis_bus_path, 'r') as f:
        content = f.read()
    
    # Add type imports if needed
    if "Union" not in content and "from typing import" in content:
        content = content.replace(
            "from typing import Dict, Any, List, Optional, Callable, Awaitable",
            "from typing import Dict, Any, List, Optional, Callable, Awaitable, Union"
        )
    
    # Update __init__ method
    init_code = """    def __init__(self, redis_url="localhost", redis_port=6379, redis_db=0):
        \"\"\"
        Initialize Redis message bus
        
        Args:
            redis_url: Redis server URL or config dict
            redis_port: Redis server port
            redis_db: Redis database number
        \"\"\"
        # Handle case when redis_url is a dictionary
        if isinstance(redis_url, dict):
            self.redis_config = redis_url
            # Extract basic info for logging
            self.redis_url = redis_url.get('host', 'localhost')
            self.redis_port = redis_url.get('port', 6379)
        else:
            self.redis_url = redis_url
            self.redis_port = redis_port
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
    
    # Find and replace init method
    init_start = content.find("    def __init__(self,")
    if init_start >= 0:
        init_end = content.find("    async def connect", init_start)
        if init_end >= 0:
            old_init = content[init_start:init_end]
            content = content.replace(old_init, init_code)
    
    # Update connect method
    connect_code = """    async def connect(self):
        \"\"\"Connect to Redis server\"\"\"
        if self.redis is None:
            try:
                # Use the config dictionary to connect
                self.redis = redis.Redis(
                    host=self.redis_url,
                    port=self.redis_port,
                    db=self.redis_config.get('db', 0),
                    decode_responses=True
                )
                
                # Test connection
                await self.redis.ping()
                logger.info(f"Connected to Redis at {self.redis_url}:{self.redis_port}")
                
                # Initialize pubsub
                self.pubsub = self.redis.pubsub()
            except Exception as e:
                logger.error(f"Error connecting to Redis: {str(e)}")
                raise
"""
    
    # Find and replace connect method
    connect_start = content.find("    async def connect")
    if connect_start >= 0:
        connect_end = content.find("    async def disconnect", connect_start)
        if connect_end >= 0:
            old_connect = content[connect_start:connect_end]
            content = content.replace(old_connect, connect_code)
    
    with open(redis_bus_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated Redis Message Bus to handle dictionary configuration")
else:
    print(f"❌ Could not find {redis_bus_path}")

# Create app.py file
print("\nFix 3: Creating API app.py file...")

os.makedirs(api_dir, exist_ok=True)
app_py_path = os.path.join(api_dir, "app.py")

app_py_content = """\"\"\"
API application for GenAI Agent 3D
\"\"\"

from fastapi import FastAPI
from .llm import router as llm_router

# Create FastAPI application
app = FastAPI(
    title="GenAI Agent 3D API",
    description="API for GenAI Agent 3D",
    version="0.1.0"
)

# Include API routers
app.include_router(llm_router, prefix="/api")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    \"\"\"Health check endpoint for service monitoring\"\"\"
    return {"status": "ok", "message": "API Service is healthy"}
"""

with open(app_py_path, 'w') as f:
    f.write(app_py_content)
print(f"✅ Created API app.py file at {app_py_path}")

# Create __init__.py file
init_path = os.path.join(api_dir, "__init__.py")
init_content = """\"\"\"
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

with open(init_path, 'w') as f:
    f.write(init_content)
print(f"✅ Created API __init__.py file at {init_path}")

print("\nAll fixes applied successfully!")
print("\nNext steps:")
print("1. Restart all services with: python restart_services.py")
print("2. Access the web interface at: http://localhost:3000")
print("3. Test the LLM features in the UI")

# Ask if user wants to restart services
restart = input("\nDo you want to restart services now? (y/n): ")
if restart.lower() == 'y':
    print("\nRestarting services...")
    try:
        venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
        manage_script = os.path.join(project_dir, "manage_services.py")
        
        python_cmd = venv_python if os.path.exists(venv_python) else sys.executable
        
        subprocess.run(
            [python_cmd, manage_script, "restart", "all"],
            check=True
        )
        print("\n✅ Services restarted successfully!")
        print("\nYou can access the web interface at: http://localhost:3000")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error restarting services: {e}")
        print("\nYou can try to manually restart services with:")
        print(f"cd {project_dir}")
        
        # Avoid using f-string with backslashes
        if sys.platform == "win32":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        print(activate_cmd)
        
        print("python manage_services.py restart all")
