# GenAI Agent 3D - LLM Integration Installation Guide

This guide walks you through the installation and setup of the LLM integration for GenAI Agent 3D.

## Prerequisites

Before installing, make sure you have:

1. **Python 3.8+** installed and configured
2. **Node.js 14+** installed for the frontend
3. The base GenAI Agent 3D platform installed
4. **Ollama** installed for local LLM inference (or access to a cloud LLM API)

## Installation Steps

### Step 1: Install Ollama (if not already installed)

Ollama provides local LLM inference capabilities:

1. Download Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Install following the instructions for your platform
3. Start Ollama:
   - Windows: Launch the Ollama app
   - macOS: Launch the Ollama app
   - Linux: Run `ollama serve` in a terminal

### Step 2: Run the Update Script

The update script will apply all necessary changes to integrate LLM capabilities:

```bash
# Navigate to the project directory
cd genai-agent-3d

# Run the update script
python update_agent_llm.py
```

This script will:
1. Fix API routes for LLM integration
2. Fix SVG processor issues
3. Initialize LLM services
4. Apply final fixes to ensure everything works

### Step 3: Pull LLM Models (if not done during setup)

If you skipped model download during the setup, you can pull models manually:

```bash
# Pull the recommended model (Llama 3.2)
ollama pull llama3.2:latest

# OR a smaller, faster model
ollama pull phi3:latest
```

### Step 4: Start the Services

If you didn't restart services at the end of the update script, start them manually:

```bash
cd genai_agent_project
python manage_services.py restart all
```

### Step 5: Access the Web Interface

Open your browser and navigate to:

```
http://localhost:3000
```

You should see the GenAI Agent 3D interface with a new "LLM Test" option in the sidebar.

## Configuration

### LLM Provider Configuration

To configure the LLM provider:

1. Navigate to the **Settings** page in the web interface
2. Under "Language Model Settings", select your provider and model
3. Click "Save Model Settings"

Alternatively, edit the configuration files directly:

```
genai_agent_project/config/llm.yaml
```

### Using Cloud Providers

To use cloud LLM providers (OpenAI, Anthropic, etc.) instead of local Ollama:

1. Edit `config/llm.yaml` 
2. Set `provider` to your chosen provider (e.g., "anthropic")
3. Add your API key in the appropriate provider section
4. Restart the services

Example configuration for Anthropic Claude:

```yaml
type: cloud
provider: anthropic
model: claude-3-opus-20240229

providers:
  anthropic:
    api_key: your-api-key-here
    base_url: https://api.anthropic.com
```

## Troubleshooting

### Services Won't Start

If services won't start:

1. Check that Redis is running: `redis-cli ping` should return "PONG"
2. Check that Ollama is running: `curl http://localhost:11434/api/version`
3. Check for errors in the console output

### LLM Not Responding

If the LLM isn't responding:

1. Verify Ollama is running
2. Check if the model is downloaded: `ollama list`
3. Try pulling the model again: `ollama pull llama3.2:latest`
4. Check the backend logs for API errors

### Frontend Errors

If you encounter frontend errors:

1. Check browser console for JavaScript errors
2. Verify that the backend API is accessible
3. Try clearing browser cache and refreshing

## Next Steps

After installation:

1. Try the **LLM Test** page to verify everything works
2. Explore the integration with the 3D generation tools
3. Check the [LLM Integration Guide](./llm_integration.md) for usage details

---

For additional help, refer to the full documentation or open an issue in the project repository.
