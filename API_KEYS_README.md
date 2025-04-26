# Managing API Keys Securely in GenAI Agent 3D

This guide explains how to properly manage API keys and other sensitive information in the GenAI Agent 3D project.

## IMPORTANT: Never Commit API Keys to the Repository

API keys and other credentials should **never** be committed to version control. GitHub and other repository hosts actively scan for committed secrets and will block pushes that contain sensitive information.

## Proper API Key Management

### Using Environment Variables

The best practice is to store API keys in environment variables rather than in source code or configuration files. GenAI Agent 3D supports loading API keys from environment variables.

### Using .env Files (Local Development Only)

For local development, you can use `.env` files to store your API keys. These files should:

1. **Never be committed to the repository**
2. Be listed in `.gitignore`
3. Only exist on your local development machine

## Setting Up API Keys

### Method 1: Using the Management Tool

The simplest way to set up your API keys is to use the management tool:

```
python manage_system.py
```

Then select "API Key Management" from the menu and follow the prompts.

### Method 2: Editing .env Files

You can manually edit the `.env` files in the project:

1. Open `.env` in the project root
2. Replace placeholders with your actual API keys:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   OPENAI_API_KEY=your_actual_api_key_here
   ```

### Method 3: Using Environment Variables

Set environment variables before running the application:

**Windows:**
```
set ANTHROPIC_API_KEY=your_actual_api_key_here
```

**Linux/macOS:**
```
export ANTHROPIC_API_KEY=your_actual_api_key_here
```

## Required API Keys

Depending on your configuration, you may need the following API keys:

- **Anthropic API Key**: Required when using Claude as your LLM provider
- **OpenAI API Key**: Required when using OpenAI models
- **Stability API Key**: Required for image generation features

## Security Best Practices

1. **Never share API keys** in public forums, chat, or code repositories
2. **Rotate API keys** periodically, especially if you suspect they may be compromised
3. Use **environment variables** whenever possible instead of hardcoded values
4. Keep `.env` files **local** and do not synchronize them with others
5. Use **placeholder values** in example configuration files
6. Consider using a **secrets manager** for production deployments

## Troubleshooting GitHub Push Rejection

If you accidentally commit API keys and GitHub rejects your push, follow these steps:

1. Remove the sensitive information from your files
2. Commit the changes
3. Try pushing again

If you've already pushed sensitive information:

1. Rotate your API keys immediately (get new ones)
2. Remove the sensitive information from your repository
3. Consider using tools like BFG Repo-Cleaner or git-filter-repo to completely remove the sensitive information from your Git history
