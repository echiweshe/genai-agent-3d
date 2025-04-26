# Fixing Claude API Key Issues in GenAI Agent 3D

This guide provides instructions for fixing the Claude API key authentication issue in GenAI Agent 3D.

## Quick Fix

The simplest way to fix the Claude API key issue is to use the provided script:

### On Windows:
Double-click the `fix_claude_api_key.bat` file and follow the prompts.

### On any platform:
Run the Python script directly:
```bash
python fix_claude_api_key.py
```

This script will:
1. Ask you to enter your Anthropic API key
2. Add it to the correct .env file in your project
3. Offer to restart the services to apply the changes

## Manual Fix

If you prefer to fix the issue manually:

1. Create or edit the file `genai_agent_project/.env`
2. Add your Anthropic API key in the following format:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
3. Save the file
4. Restart the GenAI Agent 3D services:
   ```bash
   python genai_agent_project/manage_services.py restart all
   ```

## Getting an Anthropic API Key

If you don't have an Anthropic API key:

1. Visit the [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the key (it starts with `sk-ant-`)

## Comprehensive Fix

For a more comprehensive set of fixes and improvements to the GenAI Agent 3D project, you can run:

```bash
python fix_all_v2.py
```

This script applies several improvements:
- Creates an enhanced environment loader
- Adds LLM settings management
- Configures API keys properly
- Adds API endpoints for managing LLM settings

## Troubleshooting

If you continue to experience issues after applying these fixes:

1. Ensure the `.env` file is in the correct location: `genai_agent_project/.env`
2. Check that your API key is valid and has not expired
3. Make sure the services have been restarted after making changes
4. Look for any error messages in the application logs

For additional help, check the project documentation or open an issue in the project repository.
