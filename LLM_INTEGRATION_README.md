# GenAI Agent 3D - LLM Integration

This package provides a simple way to integrate enhanced LLM capabilities into your GenAI Agent 3D project, including multiple LLM providers, a settings UI, and a testing component.

## Quick Start

For the fastest way to get everything working:

1. Run the all-in-one fix script:
   ```bash
   # From the project root
   python 07_fix_all.py
   ```

2. Restart all services:
   ```bash
   cd genai_agent_project
   .\venv\Scripts\activate
   python manage_services.py restart all
   ```

3. Test the new functionality:
   - Visit http://localhost:3000/llm-test to test the LLM API
   - Visit your settings page to see multiple LLM providers

## What's Included

This integration adds several important components:

1. **Enhanced LLM API Routes**: Simple API endpoints for LLM operations:
   - `GET /api/llm/providers` - List available LLM providers and models
   - `POST /api/llm/generate` - Generate text using a specified provider/model
   - `POST /api/llm/classify-task` - Classify a task using LLM

2. **Settings Management API**: Endpoints for saving and loading settings:
   - `GET /api/settings` - Get all settings
   - `POST /api/settings` - Update settings for a specific section

3. **LLM Tester Component**: A simple React component for testing LLM functionality.

4. **Settings UI Enhancements**: Improved UI for selecting LLM providers and models.

## Implementation Details

### Backend

The integration creates the following files in your project:

- `genai_agent_project/genai_agent/services/llm_api_routes.py`: LLM API routes
- `genai_agent_project/genai_agent/services/settings_api.py`: Settings API routes

The implementation uses your existing LLM service directly instead of creating a new implementation, making it simpler to integrate.

### Frontend

The integration adds:

- A new LLM test page at `/llm-test`
- Enhanced Settings UI for LLM provider selection
- Support for selecting from multiple LLM providers

## Individual Fix Scripts

If you prefer to apply changes individually, you can use these scripts:

- `03_direct_integration.py`: Creates the basic LLM API integration
- `04_integrate_frontend.py`: Adds the LLM tester component to the frontend
- `05_fix_api_routes.py`: Fixes issues with the LLM API routes
- `06_enhance_settings_page.py`: Enhances the settings page with multiple providers

## Troubleshooting

### Backend fails to start

If the backend fails to start with module import errors:

1. Make sure the required files exist:
   ```
   dir genai_agent_project\genai_agent\services\llm_api_routes.py
   ```

2. Check that there are `__init__.py` files in each directory:
   ```
   dir genai_agent_project\genai_agent\services\__init__.py
   ```

3. Examine the backend logs for specific error messages.

### LLM providers not showing up

If you don't see providers in the LLM test page:

1. Make sure the backend is running: `python manage_services.py status backend`
2. Check browser console for API errors
3. Verify that the `/api/llm/providers` endpoint is returning data:
   ```
   curl http://localhost:8000/api/llm/providers
   ```

### Text generation fails

If generating text doesn't work:

1. Make sure Ollama is running: `python manage_services.py status ollama`
2. Check if the Ollama models are available: `ollama list`
3. Look for errors in the browser console and backend logs

## Next Steps

Once the basic integration is working, you can enhance it by:

1. Adding actual API key support for cloud providers (OpenAI, Anthropic)
2. Implementing model switching based on user selection
3. Adding streaming responses for better user experience
4. Creating a more advanced LLM settings UI with usage statistics
