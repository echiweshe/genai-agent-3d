# Enhanced LLM Services for GenAI Agent 3D

This extension provides an enhanced Language Model (LLM) service implementation for the GenAI Agent 3D project. It offers dynamic LLM provider selection, concurrent request handling, and better timeout management.

## Setup Instructions

1. Run the setup scripts to install the necessary files:

```bash
# Navigate to your project directory
cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d

# Run the setup script to install the LLM services
python 00_setup_llm.py

# Update the main.py file to include LLM routes
python 01_update_main.py
```

2. Configure your API keys in the `.env` file:

```
# Open .env file and add your API keys
notepad .env
```

3. Start the services:

```bash
# Start all services
python genai_agent_project\manage_services.py start all

# Or start just the LLM worker
python genai_agent_project\manage_services.py start llm_worker
```

## Key Features

- **Multiple LLM Provider Support**: Integration with Ollama, OpenAI, Anthropic, and Hunyuan3D
- **Dynamic Model Selection**: UI to choose different models and parameters
- **Redis Message Bus Integration**: Reliable message passing with timeouts and retries
- **Worker-based Architecture**: Distributed processing of LLM requests
- **WebSocket Support**: Real-time LLM responses and streaming

## API Usage

### Get Available LLM Providers

```http
GET /api/llm/providers
```

Response:
```json
[
  {
    "name": "Ollama",
    "is_local": true,
    "models": [
      {
        "id": "llama3:latest",
        "name": "Llama3",
        "context_length": 8192,
        "input_cost": 0.0,
        "output_cost": 0.0
      }
    ]
  }
]
```

### Generate Text

```http
POST /api/llm/generate
```

Request:
```json
{
  "prompt": "Write a Blender Python script to create a red cube",
  "provider": "Ollama",
  "model": "llama3:latest",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

### WebSocket API

Connect to `ws://localhost:8000/api/llm/ws/{client_id}` and send:

```json
{
  "type": "generate",
  "prompt": "Create a 3D scene with a mountain and a lake",
  "provider": "Ollama",
  "model": "llama3:latest",
  "request_id": "req_12345"
}
```

## Troubleshooting

### WebSocket Connection Issues

If you're experiencing WebSocket connection issues:

1. Check that the backend server is running
2. Verify the WebSocket URL is correct (should be `ws://localhost:8000/api/llm/ws/{client_id}`)
3. Check browser console for error messages
4. Ensure Redis is running and accessible

### LLM Worker Not Starting

If the LLM worker is not starting:

1. Check the logs in `logs/llm_worker.log`
2. Verify that Redis is running
3. Check that Ollama or other LLM providers are accessible
4. Verify the API keys in the `.env` file

## Architecture

The enhanced LLM service consists of these main components:

1. **EnhancedLLMService**: The core service for interacting with language models
2. **LLMServiceManager**: Manages LLM services and routes requests via Redis
3. **LLMRedisWorker**: A separate worker process that handles LLM requests
4. **LLM API Routes**: FastAPI routes for accessing the LLM service

The components communicate using Redis as a message bus, which enables:

- Asynchronous request processing
- Reliable timeout handling
- Concurrent request management
- Distributed processing

## Testing

You can use the included LLMTester.jsx React component to test the LLM service in the frontend. Copy it to your components directory and import it into a page.

## Advanced Configuration

You can adjust additional settings in the `.env` file:

```
# Redis connection
REDIS_URL=redis://localhost:6379

# Default LLM provider and model
DEFAULT_LLM_PROVIDER=Ollama
DEFAULT_LLM_MODEL=llama3:latest

# LLM Service concurrency settings
MAX_CONCURRENT_REQUESTS=5
MAX_QUEUE_SIZE=100
REQUEST_TIMEOUT=120
```
