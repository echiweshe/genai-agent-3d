#!/usr/bin/env python3
"""
Direct Fix for RedisMessageBus Ping Method

This script directly adds the ping method to the RedisMessageBus class
without any string manipulation or regex matching, which avoids syntax issues.
"""

import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    return backup_path

def direct_redis_fix():
    """Directly add ping method to the Redis bus file"""
    # Find the redis_bus.py file
    file_path = "genai_agent_project/genai_agent/services/redis_bus.py"
    
    if not os.path.exists(file_path):
        # Try absolute path
        file_path = os.path.join("C:", os.sep, "ZB_Share", "Labs", "src", "CluadeMCP", 
                              "genai-agent-3d", "genai_agent_project", "genai_agent", 
                              "services", "redis_bus.py")
        if not os.path.exists(file_path):
            print(f"❌ Could not find redis_bus.py")
            return False

    # Create a backup
    backup_file(file_path)
    
    # Create a new file with the ping method added
    temp_file = file_path + ".new"
    
    with open(file_path, 'r', encoding='utf-8') as infile, open(temp_file, 'w', encoding='utf-8') as outfile:
        # Flag to track if we've inserted the ping method
        ping_added = False
        
        # Flag to check if the ping method already exists
        ping_exists = False
        
        # Process the file line by line
        for line in infile:
            # Write the current line
            outfile.write(line)
            
            # If we find the end of the disconnect method and haven't added ping yet
            if "logger.info(\"Disconnected from Redis\")" in line and not ping_added and not ping_exists:
                # Add the ping method
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
                outfile.write(ping_method)
                ping_added = True
            
            # Check if the ping method already exists
            if "async def ping" in line:
                ping_exists = True
                print("✅ Ping method already exists")
        
    # Replace the original file if the ping method was added
    if ping_added:
        shutil.move(temp_file, file_path)
        print("✅ Added ping method to RedisMessageBus class")
        return True
    elif ping_exists:
        # The ping method already exists, no need to replace the file
        os.remove(temp_file)
        return True
    else:
        # Could not find the right place to add the ping method
        os.remove(temp_file)
        print("❌ Could not find the right location to add the ping method.")
        print("Please check if the structure of redis_bus.py has changed.")
        return False

if __name__ == "__main__":
    print("="*80)
    print("          Direct Redis Bus Fix for GenAI Agent 3D           ")
    print("="*80)
    
    success = direct_redis_fix()
    
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
