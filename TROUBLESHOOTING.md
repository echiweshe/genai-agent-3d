# GenAI Agent 3D - Troubleshooting Guide

This guide addresses common issues you might encounter when setting up and running the GenAI Agent 3D with LLM integration.

## Installation Issues

### Missing Python Dependencies

If you see errors like `ModuleNotFoundError: No module named 'httpx'` or other missing modules:

1. Run the dependency installation script:
   ```
   python install_dependencies.py
   ```

2. If that doesn't work, manually install the required packages:
   ```
   cd genai_agent_project
   .\venv\Scripts\activate  # On Windows
   pip install httpx pydantic fastapi redis pyyaml requests uvicorn
   ```

### Syntax Errors in Python Scripts

If you encounter syntax errors in any of the Python scripts:

1. Make sure you're using Python 3.8 or newer: `python --version`
2. Run the updated scripts provided in this package:
   ```
   python 09_update_agent_llm.py
   ```

## Starting the Application

### Backend Won't Start

If the backend service fails to start:

1. Check Python dependencies are installed (see above)
2. Check Redis is running: `redis-cli ping` should return "PONG"
3. Check Ollama is running: `curl http://localhost:11434/api/version`
4. Look for specific error messages in the console output

### Frontend Build Errors

If the frontend fails to build with syntax errors:

1. The most common issue is with escaped characters in JavaScript files
2. Run the update script which includes fixes for these issues:
   ```
   python 09_update_agent_llm.py
   ```

### Services Restart Issues

If you have trouble restarting all services:

1. Try stopping all services first:
   ```
   cd genai_agent_project
   python manage_services.py stop all
   ```

2. Then start them again:
   ```
   python manage_services.py start all
   ```

3. Check if any processes are still running:
   - Redis server process
   - Node.js/npm processes for the frontend
   - Python processes for the backend

## LLM Integration Issues

### Can't Connect to Ollama

If the application can't connect to Ollama:

1. Make sure Ollama is installed: [https://ollama.ai/](https://ollama.ai/)
2. Start Ollama: `ollama serve`
3. Test Ollama with: `curl http://localhost:11434/api/version`

### No Models Available

If no LLM models are available:

1. Pull a model with: `ollama pull llama3.2:latest`
2. Verify the model is available: `ollama list`
3. Check the configuration in `genai_agent_project/config/llm.yaml`

### LLM Test Page Not Found

If the LLM Test page is not available in the sidebar:

1. Run the update script to ensure all UI components are properly integrated:
   ```
   python 09_update_agent_llm.py
   ```

2. Check if the route was added to App.js
3. Check if the menu item was added to AppSidebar.js

## Quick Fix Script

For a comprehensive fix that addresses most common issues:

```
python 09_update_agent_llm.py
```

This script will:
1. Install missing dependencies
2. Fix syntax errors in API routes
3. Update UI components to include the LLM Test page
4. Initialize LLM services
5. Offer to restart all services

## Still Having Issues?

If you're still experiencing problems:

1. Check the logs in the console
2. Ensure all dependencies are installed
3. Make sure Ollama and Redis are running
4. Try the update-and-run.bat script (on Windows) for a simplified update and start process
