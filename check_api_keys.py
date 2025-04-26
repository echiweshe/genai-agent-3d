#!/usr/bin/env python3
"""
Check API Keys for GenAI Agent 3D

This script checks if the necessary API keys are set up correctly
and reports their status.

Usage:
    python check_api_keys.py
"""

import os
import sys
import logging
import dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_api_keys(env_path):
    """Check API keys in the .env file"""
    # Load .env file
    dotenv.load_dotenv(env_path)
    
    # Define providers and their environment variables
    providers = {
        'Anthropic (Claude)': 'ANTHROPIC_API_KEY',
        'OpenAI (GPT-4, GPT-3.5)': 'OPENAI_API_KEY',
        'Stability AI': 'STABILITY_API_KEY',
        'Replicate': 'REPLICATE_API_KEY'
    }
    
    # Check each provider
    results = {}
    for provider_name, env_var in providers.items():
        value = os.environ.get(env_var)
        status = {
            'set': bool(value),
            'value': value[-8:] if value else None,  # Show last 8 chars for security
            'format_valid': False,
            'env_var': env_var
        }
        
        # Check format
        if value:
            if env_var == 'ANTHROPIC_API_KEY' and value.startswith('sk-ant-'):
                status['format_valid'] = True
            elif env_var == 'OPENAI_API_KEY' and value.startswith('sk-'):
                status['format_valid'] = True
            elif env_var in ['STABILITY_API_KEY', 'REPLICATE_API_KEY']:
                # Less strict validation for these
                status['format_valid'] = len(value) > 10
        
        results[provider_name] = status
    
    return results

def main():
    """Main function"""
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Print banner
    print("=" * 80)
    print("           API Key Status for GenAI Agent 3D")
    print("=" * 80)
    
    # Determine .env file path
    env_path = project_root / "genai_agent_project" / ".env"
    
    # Check if .env file exists
    if not os.path.exists(env_path):
        print(f"\n❌ The .env file does not exist at: {env_path}")
        print("Run 'python setup_api_keys.py' to set up your API keys.")
        return 1
    
    # Check API keys
    results = check_api_keys(env_path)
    
    # Print results
    print(f"\nAPI keys configuration in: {env_path}")
    print("-" * 80)
    
    all_valid = True
    for provider_name, status in results.items():
        status_symbol = "✅" if status['set'] and status['format_valid'] else "❌"
        if status['set']:
            print(f"{status_symbol} {provider_name}: Set (ends with ...{status['value']})")
            if not status['format_valid']:
                print(f"   ⚠️ Warning: The key format doesn't match the expected pattern")
                all_valid = False
        else:
            print(f"{status_symbol} {provider_name}: Not set")
            all_valid = False
    
    print("-" * 80)
    
    # Show next steps
    if all_valid:
        print("\n✅ All API keys are configured correctly!")
        print("You can now use all supported AI providers in GenAI Agent 3D.")
    else:
        print("\n⚠️ Some API keys are missing or might be invalid.")
        print("To set up your API keys, run one of these scripts:")
        print("  - For all providers: python setup_api_keys.py")
        print("  - For Anthropic only: python fix_anthropic_key.py")
        print("\nSee API_KEYS_README.md for more information.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Error checking API keys: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
