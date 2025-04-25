# GenAI Agent 3D - LLM Integration Guide

This guide will help you quickly get the LLM integration working with your existing GenAI Agent 3D project.

## Step 1: Fix Module Paths and Install Required Files

First, we need to create the simplified LLM integration that works directly with your existing architecture:

```bash
# Navigate to your project directory
cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

# Run the direct integration script
python 03_direct_integration.py
```

This will:
- Create the necessary module structure
- Install a simplified LLM API that interfaces with your existing LLM service
- Update the main.py file to include the LLM routes

## Step 2: Integrate the Frontend Tester

Next, let's add a simple LLM testing page to your frontend:

```bash
# Run the frontend integration script
python 04_integrate_frontend.py
```

This will:
- Add a SimpleLLMTester component to your frontend
- Create a new LLMTestPage that uses this component
- Update App.js to add a route to this page

## Step 3: Restart All Services

Now restart all the services to apply the changes:

```bash
# Navigate to the project directory
cd genai_agent_project

# Activate the virtual environment
.\venv\Scripts\activate

# Restart all services
python manage_services.py restart all
```

## Step 4: Test the LLM Integration

Open your browser and navigate to:
```
http://localhost:3000/llm-test
```

You should see the LLM Tester page with:
- Provider selection
- Model selection
- Prompt input
- Generate button

## Troubleshooting

### If the backend fails to start:

Check the error message. If it's related to missing modules, you might need to ensure paths are set correctly:

1. Check that all the files were created in the right locations:
   ```
   dir genai_agent_project\genai_agent\services\llm_api_routes.py
   ```

2. Make sure the `__init__.py` files exist in all package directories.

3. If necessary, modify your PYTHONPATH to include the project root:
   ```
   set PYTHONPATH=%PYTHONPATH%;C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project
   ```

### If no LLM providers show up:

1. Check if Ollama is running correctly:
   ```
   python manage_services.py status ollama
   ```

2. Look at browser console for errors related to API calls.

3. Check the backend logs for any errors related to the `/api/llm/providers` endpoint.

### If text generation fails:

1. Make sure the model specified is available in Ollama. You can check by running:
   ```
   ollama list
   ```

2. Look at backend logs to see if there are any errors while processing the generate request.

## Understanding the Implementation

The integration we've added uses a simplified approach:

1. The `/api/llm/providers` endpoint returns information about your current LLM setup
2. The `/api/llm/generate` endpoint uses your existing LLM service to generate text
3. The frontend component provides a simple UI to interact with these endpoints

This approach minimizes changes to your existing codebase while providing the functionality you need.

## Next Steps

Once the basic integration is working, you can:

1. Enhance the frontend component with more options and better error handling
2. Expand the API to support more LLM providers
3. Add advanced features like streaming responses and model selection

Enjoy using your enhanced GenAI Agent 3D with improved LLM integration!
