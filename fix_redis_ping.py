#!/usr/bin/env python
"""
Fix missing ping method in RedisMessageBus
This script adds a ping method to the RedisMessageBus class
"""

import os
import sys
import re

def find_redis_bus_file(base_dir):
    """Find the redis_bus.py file in the project"""
    for root, dirs, files in os.walk(base_dir):
        if 'redis_bus.py' in files:
            return os.path.join(root, 'redis_bus.py')
    return None

def add_ping_method(redis_bus_path):
    """Add a ping method to the RedisMessageBus class"""
    try:
        with open(redis_bus_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = redis_bus_path + '.backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"Created backup: {backup_path}")
        
        # Check if the ping method already exists
        if "async def ping" in content:
            print("ping method already exists")
            return False
        
        # Find the RedisMessageBus class
        class_match = re.search(r'class RedisMessageBus[^\n]*:', content)
        if not class_match:
            print("RedisMessageBus class not found")
            return False
        
        # Find the end of the class (last method)
        methods = re.finditer(r'(\n    async def [^\n]+\([^\n]+\):[^\n]*\n)', content)
        last_method = None
        for method in methods:
            last_method = method
        
        if last_method:
            # Find the end of the method body
            method_end = content.find('\n\n', last_method.end())
            if method_end == -1:
                method_end = len(content)
            
            # Add the ping method after the last method
            ping_method = """
    async def ping(self):
        \"\"\"Send a ping command to Redis to check connectivity\"\"\"
        try:
            if self.redis is None:
                await self.connect()
            
            if self.redis:
                result = await self.redis.ping()
                return {"status": "ok", "message": "PONG", "result": result}
            else:
                return {"status": "error", "message": "Redis not connected"}
        except Exception as e:
            self.logger.error(f"Error pinging Redis: {e}")
            return {"status": "error", "message": f"Error: {str(e)}"}
"""
            new_content = content[:method_end] + ping_method + content[method_end:]
            
            # Write the updated content
            with open(redis_bus_path, 'w') as f:
                f.write(new_content)
            
            print(f"Added ping method to RedisMessageBus in {redis_bus_path}")
            return True
        else:
            print("No methods found in RedisMessageBus class")
            return False
    except Exception as e:
        print(f"Error adding ping method: {e}")
        return False

def main():
    """Main function"""
    print("\n===== FIXING MISSING PING METHOD IN REDISMESSAGEBUS =====\n")
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Find redis_bus.py
    redis_bus_path = find_redis_bus_file(script_dir)
    
    if redis_bus_path:
        print(f"Found redis_bus.py at {redis_bus_path}")
        fixed = add_ping_method(redis_bus_path)
        
        if fixed:
            print("\n✅ Successfully added ping method to RedisMessageBus")
            print("\nPlease restart your backend server to apply the changes")
        else:
            print("\n❌ Failed to add ping method to RedisMessageBus")
    else:
        print("❌ Could not find redis_bus.py file")
        print("Please provide the full path to redis_bus.py:")
        custom_path = input("> ")
        
        if os.path.exists(custom_path):
            fixed = add_ping_method(custom_path)
            
            if fixed:
                print("\n✅ Successfully added ping method to RedisMessageBus")
                print("\nPlease restart your backend server to apply the changes")
            else:
                print("\n❌ Failed to add ping method to RedisMessageBus")
        else:
            print(f"❌ File not found: {custom_path}")

if __name__ == "__main__":
    main()
