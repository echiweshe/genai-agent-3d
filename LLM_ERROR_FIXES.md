# GenAI Agent 3D - LLM Error Fixes

This document explains how to fix the LLM errors encountered in the GenAI Agent 3D project.

## Error 1: `LLMService.__init__() takes 1 positional argument but 2 were given`

This error occurs because the `llm_api_routes.py` file is trying to pass a configuration parameter to the LLMService constructor, but the LLMService class doesn't accept any parameters besides `self`.

### Fix:

1. Open `genai_agent_project/genai_agent/services/llm_api_routes.py`
2. Find the line that creates the LLM service:
   ```python
   _llm_service = LLMService(config)
   ```
3. Change it to:
   ```python
   _llm_service = LLMService()
   ```

## Error 2: `inet_pton() argument 2 must be str, not dict`

This error occurs because the Redis message bus is trying to connect to Redis using a dictionary configuration instead of a string URL.

### Fix:

1. Open `genai_agent_project/genai_agent/services/redis_bus.py`
2. Update the `__init__` method to handle dictionary configurations:
   ```python
   def __init__(self, redis_url="localhost", redis_port=6379, redis_db=0):
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
   ```
3. Update the `connect` method to use the extracted configuration:
   ```python
   async def connect(self):
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
   ```

## Automatic Fix Script

For your convenience, I've created a script that automatically applies all these fixes. You can run it using:

```bash
python fix_llm_errors.py
```

This script will:
1. Fix the LLMService initialization error
2. Update the Redis Message Bus to handle dictionary configurations
3. Create necessary API initialization files
4. Offer to restart services for you

## After Applying the Fixes

Once you've applied the fixes, restart all services with:

```bash
python restart_services.py
```

Or manually using:

```bash
cd genai_agent_project
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Linux/macOS
python manage_services.py restart all
```

Then access the web interface at: http://localhost:3000

## Further Steps

If you encounter any additional issues:

1. Check the `python manage_services.py restart all` output for error messages
2. Look for log messages in the console output
3. Verify that all services are running (Redis, Ollama, Backend, Frontend)
4. Try stopping all services before starting them again
