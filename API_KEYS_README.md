# Setting Up API Keys for GenAI Agent 3D

This document provides instructions for setting up API keys for various AI providers in GenAI Agent 3D.

## Quick Fix for Claude API Key Issue

If you're experiencing issues with Claude (Anthropic) API authentication, you can use the `fix_anthropic_key.py` script:

```bash
python fix_anthropic_key.py
```

This script will:
1. Prompt you to enter your Anthropic API key
2. Save it to the correct location in your project
3. Ensure it's loaded properly by the application

Alternatively, you can provide the API key directly on the command line:

```bash
python fix_anthropic_key.py --key your_anthropic_api_key_here
```

## Setting Up Multiple API Keys

For a more comprehensive setup of all supported AI providers, use the `setup_api_keys.py` script:

```bash
python setup_api_keys.py
```

This interactive script will guide you through setting up API keys for:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Stability AI
- Replicate

## Manual API Key Setup

If you prefer to set up API keys manually, follow these steps:

1. Create or edit the `.env` file in the `genai_agent_project` directory
2. Add your API keys in the following format:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   STABILITY_API_KEY=your_stability_api_key_here
   REPLICATE_API_KEY=your_replicate_api_key_here
   ```
3. Save the file
4. Restart the GenAI Agent 3D application

## Obtaining API Keys

### Anthropic (Claude)
1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to the API Keys section
4. Create a new API key
5. Copy the key (it starts with `sk-ant-`)

### OpenAI
1. Visit [https://platform.openai.com/](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to the API section
4. Create a new API key
5. Copy the key (it starts with `sk-`)

### Stability AI
1. Visit [https://platform.stability.ai/](https://platform.stability.ai/)
2. Create an account or sign in
3. Navigate to the Account/API Keys section
4. Copy your API key

## Troubleshooting

If you're still experiencing issues after setting up your API keys:

1. Make sure the GenAI Agent 3D application has been restarted
2. Check that your API keys are valid and have not expired
3. Verify that the `.env` file is in the correct location: `genai_agent_project/.env`
4. Make sure the API keys are in the correct format (no extra spaces or quotes)
5. Check the application logs for any error messages related to API authentication

For persistent issues, please check the project documentation or open an issue on the project repository.
