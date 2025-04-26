# GenAI Agent 3D - Quick Start Guide

This guide provides steps to quickly fix both errors encountered in the GenAI Agent 3D project.

## Error 1: LLMService Initialization

**Error Message:**
```
LLMService.__init__() takes 1 positional argument but 2 were given
```

**Quick Fix:**
1. Run the LLMService initialization fix:
   ```
   python fix_llmservice_init.py
   ```
   or double-click `fix_llmservice_init.bat` (Windows)

**What This Does:**
- Updates the `agent.py` file to initialize LLMService without passing a configuration parameter
- Creates a backup of the original file
- Offers to restart services

## Error 2: Redis Connection

**Error Message:**
```
inet_pton() argument 2 must be str, not dict
```

**Quick Fix:**
1. Run the Redis connection fix:
   ```
   python surgical_redis_fix.py
   ```
   or double-click `surgical_fix.bat` (Windows)

**What This Does:**
- Updates the `redis_bus.py` file to handle dictionary configurations properly
- Creates a backup of the original file
- Offers to restart services

## Fix Both Issues at Once

If you're experiencing both issues, you can fix them both at once:

1. Run the complete fix script:
   ```
   python fix_all_llm_issues.py
   ```
   or double-click `fix_all_llm_issues.bat` (Windows)

**What This Does:**
- Fixes both the LLMService initialization and Redis connection issues
- Creates proper API structure
- Creates backups of all modified files
- Offers to restart services

## After Applying Fixes

After applying any fixes, restart all services:

```
cd genai_agent_project
python manage_services.py restart all
```

Then access the web interface at: http://localhost:3000

## Troubleshooting

If you still encounter issues:

1. Check the console output for specific error messages
2. Try stopping all services first, then starting them again:
   ```
   python manage_services.py stop all
   python manage_services.py start all
   ```
3. Verify Redis and Ollama are running properly
4. Check that the LLM models are available in Ollama

## Next Steps

Once the application is running:

1. Navigate to the LLM Test page in the sidebar
2. Try generating text with different models
3. Integrate LLM capabilities into your 3D modeling workflow

For more detailed information, see the files in the `docs/` directory.
