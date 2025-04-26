# Resolving GitHub Push Protection Issues

This guide explains how to resolve the GitHub push protection issues you're encountering with your GenAI Agent 3D repository.

## The Issue

GitHub has detected sensitive information (API keys) in your commit and is blocking the push. Specifically, it found:
- An Anthropic API key in `genai_agent_project/config.yaml` 

## Fix Steps

### 1. Remove Sensitive Information

We've already created updated versions of all files with API keys replaced by placeholders:
- `config.yaml` - API keys replaced with placeholders
- `.env` files - API keys replaced with placeholders
- Added `.gitignore` to prevent these files from being committed in the future

### 2. Commit These Changes

```bash
git add genai_agent_project/config.yaml
git add .env
git add genai_agent_project/.env
git add .gitignore
git add .env.template
git add genai_agent_project/config.template.yaml
git add API_KEYS_README.md
git add setup_configuration.py
git add setup_configuration.bat
git add GITHUB_PUSH_FIX.md

git commit -m "Remove API keys and add secure configuration handling"
```

### 3. Try Pushing Again

```bash
git push
```

If GitHub still rejects the push because the API keys are in the commit history, you have two options:

### Option A: Allow the Secret on GitHub

1. Visit the URL provided in the rejection message:
   ```
   https://github.com/echiweshe/genai-agent-3d/security/secret-scanning/unblock-secret/2wGGxPKKxFjzZlndbOWYkYsh0NI
   ```

2. From there, you can choose to mark the secret as a false positive or removed.
   - Choose "This secret has been revoked and can be ignored" if you've already rotated the API key

### Option B: Rewrite Git History (Advanced)

This completely removes the secrets from your Git history, but it rewrites history which can be problematic if others are working with this repository.

1. Install the BFG Repo-Cleaner:
   ```
   https://rtyley.github.io/bfg-repo-cleaner/
   ```

2. Run the following command from outside your repository:
   ```
   java -jar bfg.jar --replace-text secrets.txt my-repo.git
   ```

   Where `secrets.txt` contains the API keys you want to remove, each on a separate line.

3. Then run:
   ```
   cd my-repo.git
   git reflog expire --expire=now --all && git gc --prune=now --aggressive
   git push --force
   ```

## Preventing Future Issues

To prevent future issues with API keys:

1. Use the provided `setup_configuration.py` script to manage API keys locally
2. Never commit files with actual API keys to the repository
3. Always use the template files (`.env.template` and `config.template.yaml`) for version control
4. Make sure `.gitignore` includes all files that might contain secrets
5. Consider using environment variables instead of configuration files for sensitive information

## API Key Security Best Practices

1. **Rotate Your API Keys**: Since your API keys were committed to a repository, even if briefly, you should generate new API keys from your providers (Anthropic, OpenAI, etc.)

2. **Use Environment Variables**: When possible, use environment variables instead of configuration files

3. **Use Secret Managers**: For production systems, consider using AWS Secrets Manager, Azure Key Vault, or similar services

For more detailed information, refer to the `API_KEYS_README.md` file.
