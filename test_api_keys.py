#!/usr/bin/env python3
"""
Test API Keys for GenAI Agent 3D

This script tests API keys for different providers (Anthropic, OpenAI, Hunyuan3D)
by making simple API calls to each service.
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path
import dotenv
from datetime import datetime

async def test_anthropic_key(api_key):
    """Test Anthropic API key with a simple request"""
    if not api_key:
        return False, "API key not provided"
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    body = {
        "model": "claude-3-haiku-20240307",
        "messages": [
            {"role": "user", "content": "Hello, please respond with just the word 'working' if you can see this message."}
        ],
        "max_tokens": 10
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=body
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if we got a response
                if data.get("content"):
                    content_blocks = data["content"]
                    for block in content_blocks:
                        if block.get("type") == "text" and "working" in block.get("text", "").lower():
                            return True, "API key is valid and working"
                    return True, "API key is valid, but unexpected response"
                return False, "API key is valid, but no content in response"
            else:
                return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

async def test_openai_key(api_key):
    """Test OpenAI API key with a simple request"""
    if not api_key:
        return False, "API key not provided"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello, please respond with just the word 'working' if you can see this message."}
        ],
        "max_tokens": 10
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=body
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if "working" in content.lower():
                    return True, "API key is valid and working"
                return True, "API key is valid, but unexpected response"
            else:
                return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

async def test_hunyuan3d_key(api_key):
    """Test Hunyuan3D API key with a simple request"""
    if not api_key:
        return False, "API key not provided"
    
    # This is a placeholder implementation since we don't have the actual API endpoint
    # Replace with actual implementation when available
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # Simulate API test with a delay
        await asyncio.sleep(1)
        
        # For now, we just check if the key is non-empty
        if len(api_key) > 10:
            return True, "API key has valid format (not verified with API)"
        else:
            return False, "API key seems too short"
    except Exception as e:
        return False, f"Error: {str(e)}"

async def test_all_keys():
    """Test all API keys"""
    # Load environment variables
    project_root = Path(__file__).parent.absolute()
    env_path = project_root / "genai_agent_project" / ".env"
    
    if not env_path.exists():
        print(f"❌ .env file not found at: {env_path}")
        return
    
    dotenv.load_dotenv(env_path)
    
    # Get API keys
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    hunyuan3d_key = os.environ.get("HUNYUAN3D_API_KEY")
    
    # Test Claude (Anthropic) API key
    print("\nTesting Claude (Anthropic) API key...")
    anthropic_success, anthropic_message = await test_anthropic_key(anthropic_key)
    if anthropic_success:
        print(f"✅ Claude API: {anthropic_message}")
    else:
        print(f"❌ Claude API: {anthropic_message}")
        print("To fix this issue, run: python fix_claude_api_key.py")
    
    # Test OpenAI API key
    print("\nTesting OpenAI API key...")
    if openai_key:
        openai_success, openai_message = await test_openai_key(openai_key)
        if openai_success:
            print(f"✅ OpenAI API: {openai_message}")
        else:
            print(f"❌ OpenAI API: {openai_message}")
    else:
        print("⚠️ OpenAI API key not set")
    
    # Test Hunyuan3D API key
    print("\nTesting Hunyuan3D API key...")
    if hunyuan3d_key:
        hunyuan_success, hunyuan_message = await test_hunyuan3d_key(hunyuan3d_key)
        if hunyuan_success:
            print(f"✅ Hunyuan3D API: {hunyuan_message}")
        else:
            print(f"❌ Hunyuan3D API: {hunyuan_message}")
    else:
        print("⚠️ Hunyuan3D API key not set")
        print("To set up Hunyuan3D, run: python setup_hunyuan3d.py")

def main():
    """Main function"""
    print("=" * 80)
    print("           Test API Keys for GenAI Agent 3D")
    print("=" * 80)
    print("\nThis script tests your API keys by making simple requests.")
    
    # Run the async tests
    asyncio.run(test_all_keys())
    
    print("\nDone testing API keys!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
