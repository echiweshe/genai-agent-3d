#!/usr/bin/env python3
"""
Fix for the RedisMessageBus ping attribute issue in GenAI Agent 3D
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    return backup_path

def fix_redis_ping():
    """Add the ping method to RedisMessageBus class"""
    file_path = "genai_agent_project/genai_agent/services/redis_bus.py"
    
    if not os.path.exists(file_path):
        # Try alternate path for direct execution
        file_path = os.path.join("C:", os.sep, "ZB_Share", "Labs", "src", "CluadeMCP", 
                               "genai-agent-3d", "genai_agent_project", "genai_agent", 
                               "services", "redis_bus.py")
        if not os.path.exists(file_path):
            print(f"❌ Could not find redis_bus.py")
            return False
    
    # Create backup
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the RedisMessageBus class exists
    if "class RedisMessageBus" not in content:
        print(f"❌ Could not find RedisMessageBus class in {file_path}")
        return False
    
    # Check if ping method already exists
    if "async def ping" in content:
        print("✅ Ping method already exists")
        return True
    
    # Find the position to insert the ping method (after the disconnect method)
    disconnect_method_match = re.search(r'async def disconnect\(self\):.*?""".*?logger\.info\("Disconnected from Redis"\)', content, re.DOTALL)
    
    if not disconnect_method_match:
        print(f"❌ Could not find disconnect method in {file_path}")
        return False
    
    insertion_point = disconnect_method_match.end()
    
    # Define the ping method - using triple quotes properly
    ping_method = '''
    
    async def ping(self):
        """Check if Redis connection is alive"""
        try:
            if self.redis is None:
                await self.connect()
                
            if self.redis:
                # Test connection
                pong = await self.redis.ping()
                return {"status": "ok", "message": "PONG" if pong else "Connection exists but ping failed"}
            return {"status": "error", "message": "Redis connection not initialized"}
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return {"status": "error", "message": str(e)}
'''
    
    # Insert the ping method
    modified_content = content[:insertion_point] + ping_method + content[insertion_point:]
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("✅ Added ping method to RedisMessageBus class")
    return True

if __name__ == "__main__":
    print("="*80)
    print("          RedisMessageBus Ping Fix for GenAI Agent 3D           ")
    print("="*80)
    
    success = fix_redis_ping()
    
    if success:
        print("\n✅ Fix successfully applied!")
        print("\nThis fix addresses the 'RedisMessageBus' object has no attribute 'ping' error.")
        print("You should now be able to see the system status as 'Online' instead of 'Offline'.")
        
        # Ask if user wants to restart services
        restart = input("Do you want to restart all services now? (y/n): ")
        if restart.lower() == 'y':
            print("\nRestarting services...")
            os.system('cd genai_agent_project && python manage_services.py restart all')
            print("Services restarted!")
        else:
            print("\nSkipping service restart")
            print("To restart services manually:")
            print("cd genai_agent_project")
            print("python manage_services.py restart all")
    else:
        print("\n❌ Failed to apply fix.")
        print("Please check the error messages above and fix manually if needed.")
