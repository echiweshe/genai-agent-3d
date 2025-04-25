{
  `path`: `C:\\ZB_Share\\Labs\\src\\CluadeMCP\\genai-agent-3d\\genai_agent_project\\DIRECT_LLM_README.md`,
  `content`: `# Direct LLM Access for GenAI Agent 3D

This implementation provides direct access to various LLM providers (Claude, GPT, Ollama, etc.) without using the Redis message bus. This solves the concurrency and timeout issues experienced with the Redis-based approach.

## Features

- Direct API access to multiple LLM providers:
  - Claude (Anthropic)
  - GPT (OpenAI)
  - Ollama (local LLM)
  - Gemini (Google)
  - Hunyuan (Tencent)
- Unified API for all providers
- Automatic fallback to Ollama if a provider fails
- Frontend components for LLM provider selection
- Standalone FastAPI server for independent operation

## Quick Start

### Option 1: Using the Setup Script

1. Run the setup script to install dependencies:

   ```
   python setup_direct_llm.py --install
   ```
2. Create or update your .env file with API keys:

   ```
   python setup_direct_llm.py --env
   ```
3. Run the standalone server:

   ```
   python setup_direct_llm.py --run
   ```

### Option 2: Manual Setup

1. Install required dependencies:

   ```
   pip install fastapi uvicorn pydantic python-dotenv anthropic openai google-generativeai ollama PyYAML
   ```
2. Create a .env file in the project root with your API keys:

   ```
   CLAUDE_API_KEY=your_claude_api_key
   OPENAI_API_KEY=your_openai_api_key
   GEMINI_API_KEY=your_gemini_api_key
   HUNYUAN_API_KEY=your_hunyuan_api_key
   ```
3. Start Ollama (optional, but recommended for fallback):

   ```
   ollama serve
   ```
4. Run the standalone server:

   ```
   cd web/backend
   python run_standalone.py
   ```
5. Access the API at: http://localhost:8001

## Project Structure

```
genai_agent_project/
├── services/
│   └── direct_access/
│       ├── __init__.py
│       ├── direct_llm_service.py
│       └── README.md
├── web/
│   ├── backend/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── direct_llm.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── direct_llm_service.py
│   │   ├── standalone_app.py
│   │   └── run_standalone.py
│   └── frontend/
│       └── src/
│           ├── components/
│           │   └── LLMProviderSelector.jsx
│           ├── services/
│           │   └── llmService.js
│           └── pages/
│               └── LLMPlayground.jsx
├── setup_direct_llm.py
└── DIRECT_LLM_README.md
```

## API Endpoints

The standalone server provides the following API endpoints:

- `POST /api/direct/llm/generate`: Generate a response from an LLM
- `GET /api/direct/llm/providers`: Get available LLM providers
- `GET /api/direct/llm/models`: Get available models for all providers or a specific provider

## Using the API

### Generate a Response

```python
import requests

response = requests.post(
    \"http://localhost:8001/api/direct/llm/generate\",
    json={
        \"prompt\": \"Write a short story about a robot who learns to paint.\",
        \"provider\": \"claude\",  # or \"gpt\", \"ollama\", \"gemini\", \"hunyuan\"
        \"model\": \"claude-3-7-sonnet-20250219\",  # optional
        \"temperature\": 0.7,
        \"max_tokens\": 1000,
        \"system_prompt\": \"You are a creative writing assistant.\"  # optional
    }
)

result = response.json()
print(result[\"content\"])
```

### Get Available Providers

```python
import requests

response = requests.get(\"http://localhost:8001/api/direct/llm/providers\")
providers = response.json()
print(providers)
```

### Get Available Models

```python
import requests

# Get models for all providers
response = requests.get(\"http://localhost:8001/api/direct/llm/models\")
all_models = response.json()
print(all_models)

# Get models for a specific provider
response = requests.get(\"http://localhost:8001/api/direct/llm/models?provider=claude\")
claude_models = response.json()
print(claude_models)
```

## Frontend Components

The implementation includes React components for the frontend:

- `LLMProviderSelector`: A component for selecting LLM provider, model, and parameters
- `llmService.js`: A service for communicating with the LLM API
- `LLMPlayground.jsx`: A page for testing LLM generation with different providers

## Integration with the Existing Application

The direct LLM service can be used in two ways:

1. **Standalone Mode**: Run the standalone server independently from the main application
2. **Integrated Mode**: Use the direct LLM service within the main application

### Integrated Mode

To use the direct LLM service within the main application, the `LLMService` class in `genai_agent/core/services/llm_service.py` has been modified to support direct access. It first attempts to use direct access, and falls back to Redis if direct access fails.

## Troubleshooting

### API Keys

If you're having issues with API keys:

- Check that your .env file contains the correct API keys
- Make sure the API keys have the correct permissions and are active
- Test each provider separately to identify which one is causing issues

### Ollama

If you're having issues with Ollama:

- Make sure Ollama is running: `ollama serve`
- Check that you have at least one model downloaded: `ollama list`
- If no models are available, download one: `ollama pull llama3`

### Network Issues

If you're having connection issues:

- Check that the server is running on the expected host and port
- Verify that there are no firewall or network restrictions
- Try using localhost (127.0.0.1) instead of 0.0.0.0

## Development

### Adding a New Provider

To add a new LLM provider:

1. Add a new provider constant in `DirectLLMService`
2. Add a default model in `DEFAULT_MODELS`
3. Add the provider's API key to the `api_keys` dictionary
4. Initialize the provider's client in `_init_clients`
5. Implement a `_generate_[provider]` method
6. Add the provider's models in `get_available_models`
7. Update the .env file with the new provider's API key

### API Documentation

When the server is running, you can access the API documentation at:

- http://localhost:8001/docs (Swagger UI)
- http://localhost:8001/redoc (ReDoc UI)
  `
  }
