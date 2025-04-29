"""
This script checks and fixes the Claude API key in the environment.

It prints details about how the key is set up and can fix common issues.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

def check_claude_key():
    """Check the Claude API key setup and report any issues."""
    print("Checking Claude API key setup...\n")
    
    # Try loading from master .env first
    master_env_path = Path(__file__).parent / "genai_agent_project" / ".env"
    local_env_path = Path(__file__).parent / ".env"
    
    env_path = None
    if master_env_path.exists():
        print(f"Loading master .env from: {master_env_path}")
        load_dotenv(dotenv_path=master_env_path)
        env_path = master_env_path
    elif local_env_path.exists():
        print(f"Loading local .env from: {local_env_path}")
        load_dotenv(dotenv_path=local_env_path)
        env_path = local_env_path
    else:
        print("No .env file found!")
        return
    
    # Check for various API key formats
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    claude_api_key = os.environ.get("CLAUDE_API_KEY")  # Alternative key name
    
    print("\nAPI Key Status:")
    print(f"ANTHROPIC_API_KEY: {'Set' if anthropic_api_key else 'Not set'}")
    print(f"CLAUDE_API_KEY: {'Set' if claude_api_key else 'Not set'}")
    
    # Check key format if it exists
    if anthropic_api_key:
        print(f"\nANTHROPIC_API_KEY format: {anthropic_api_key[:10]}...{anthropic_api_key[-4:] if len(anthropic_api_key) > 14 else ''}")
        
        if not anthropic_api_key.startswith(("sk-ant-", "sk-")):
            print("Warning: The API key doesn't start with 'sk-ant-' or 'sk-', which is unusual for Claude API keys.")
            
            fix_key = input("Would you like to add 'sk-ant-' prefix to the key? (y/n): ")
            if fix_key.lower() == 'y':
                new_key = f"sk-ant-{anthropic_api_key}"
                os.environ["ANTHROPIC_API_KEY"] = new_key
                set_key(env_path, "ANTHROPIC_API_KEY", new_key)
                print(f"Updated key in {env_path}")
                print(f"New key: {new_key[:10]}...{new_key[-4:] if len(new_key) > 14 else ''}")
    
    # Test import of the ChatAnthropic class
    print("\nTesting LangChain integration:")
    try:
        from langchain.chat_models import ChatAnthropic
        print("✓ ChatAnthropic class imported successfully")
        
        version_info = "Unknown"
        try:
            import langchain
            version_info = getattr(langchain, "__version__", "Unknown")
        except:
            pass
        print(f"LangChain version: {version_info}")
        
        try:
            import anthropic
            version_info = getattr(anthropic, "__version__", "Unknown")
        except:
            version_info = "Not installed"
        print(f"Anthropic package version: {version_info}")
        
        # Check for proxies setting that might be causing issues
        if "proxies" in os.environ:
            print("\nWarning: 'proxies' environment variable is set, which might be causing issues with the Anthropic client.")
            print(f"Proxies: {os.environ['proxies']}")
        
    except ImportError as e:
        print(f"✗ Failed to import ChatAnthropic: {e}")
    except Exception as e:
        print(f"✗ Error testing ChatAnthropic: {e}")
    
    print("\nSuggested next steps:")
    
    if not anthropic_api_key and not claude_api_key:
        print("- Add your Claude API key to the .env file as ANTHROPIC_API_KEY")
    elif not anthropic_api_key.startswith(("sk-ant-", "sk-")):
        print("- Update your API key format to start with 'sk-ant-'")
    
    print("- Try running the test script: run_svg_generator_test.bat")
    print("- If problems persist, update your langchain and anthropic packages:")
    print("  pip install -U langchain==0.0.267 anthropic==0.3.11")

if __name__ == "__main__":
    check_claude_key()
