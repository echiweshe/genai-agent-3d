# GenAI Agent 3D Fixes

This package contains various fixes for the GenAI Agent 3D project, specifically addressing issues with API keys and environment configuration.

## Quick Start

For the fastest fix to the Claude API key issue, run:

```bash
# On Windows
fix_claude_api_key.bat

# OR on any OS
python fix_anthropic_key.py
```

## Available Scripts

The following scripts are available:

### 1. fix_all.py

Comprehensive fix that applies all patches and guides you through the setup process.

```bash
python fix_all.py [--restart]
```

- `--restart`: Optional flag to restart services after applying fixes

### 2. fix_anthropic_key.py

Specifically fixes the Anthropic (Claude) API key issue.

```bash
python fix_anthropic_key.py [--key YOUR_API_KEY]
```

- `--key`: Optional parameter to provide your API key directly

### 3. setup_api_keys.py

Interactive script to set up API keys for all supported providers.

```bash
python setup_api_keys.py
```

### 4. check_api_keys.py

Checks the status of all API keys and provides guidance.

```bash
python check_api_keys.py
```

### 5. patch_main.py

Applies the necessary patch to the main.py file to include LLM settings API.

```bash
python patch_main.py
```

## What These Fixes Address

1. **Claude API Key Issue**: Ensures the Anthropic API key is properly loaded from the environment
2. **Environment Configuration**: Improves how API keys are loaded and managed
3. **UI Integration**: Adds API endpoints for managing LLM settings from the web interface
4. **Enhanced Error Handling**: Better error messages when API keys are missing or invalid

## Files Modified

These scripts modify or create the following files:

1. `genai_agent_project/.env`: Stores API keys and environment variables
2. `genai_agent_project/main.py`: Adds LLM settings API routes
3. `genai_agent_project/genai_agent/services/enhanced_env_loader.py`: New utility for loading environment variables
4. `genai_agent_project/genai_agent/services/llm_settings_manager.py`: New utility for managing LLM settings
5. `genai_agent_project/genai_agent/services/llm_settings_api.py`: New API endpoints for LLM settings

## After Applying Fixes

After applying the fixes, you should:

1. Restart all services using:
   ```bash
   python genai_agent_project/manage_services.py restart all
   ```

2. Access the web interface at http://localhost:3000

3. Try using Claude in the application

## Troubleshooting

If you continue to experience issues:

1. Check the logs for any error messages
2. Run `check_api_keys.py` to verify your API keys are set up correctly
3. Make sure you're using a valid API key for each provider

For more detailed information about API keys, refer to `API_KEYS_README.md`.
