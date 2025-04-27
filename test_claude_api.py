#!/usr/bin/env python3
"""
Test Claude API Integration

This script tests the Claude API integration in the GenAI Agent 3D project.
It sends a simple request to the Claude API and checks if the response is valid.
"""

import os
import sys
import asyncio
import json
import httpx
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_claude_api():
    """Test Claude API integration"""
    # Load API key from environment
    env_path = Path(__file__).parent / "genai_agent_project" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Anthropic API key not found in environment variables.")
        print(f"Please ensure the API key is set in {env_path}")
        return False
    
    if not api_key.startswith("sk-ant-"):
        print(f"⚠️ Warning: Your API key ({api_key[:10]}...) doesn't start with 'sk-ant-'")
        print("This may not be a valid Anthropic API key.")
    
    print(f"Found API key: {api_key[:10]}...")
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,  # Note the correct capitalization
        "anthropic-version": "2023-06-01"
    }
    
    body = {
        "model": "claude-3-sonnet-20240229",
        "messages": [
            {"role": "user", "content": "Hello, Claude! Please respond with a short greeting."}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    try:
        print("\nSending test request to Claude API...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=body
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if the response contains content
                if "content" in data and len(data["content"]) > 0:
                    content_blocks = data["content"]
                    text_blocks = [block["text"] for block in content_blocks if block["type"] == "text"]
                    text = "".join(text_blocks)
                    
                    print("\n✅ Claude API integration is working correctly!")
                    print(f"\nResponse from Claude: {text}")
                    
                    # Print usage information
                    if "usage" in data:
                        usage = data["usage"]
                        print(f"\nUsage information:")
                        print(f"- Input tokens: {usage.get('input_tokens', 'N/A')}")
                        print(f"- Output tokens: {usage.get('output_tokens', 'N/A')}")
                    
                    return True
                else:
                    print("❌ Response does not contain expected content block.")
                    print(f"Response data: {json.dumps(data, indent=2)}")
                    return False
            else:
                print(f"❌ Request failed with status code {response.status_code}.")
                error_text = response.text
                try:
                    error_json = response.json()
                    print(f"Error response: {json.dumps(error_json, indent=2)}")
                except:
                    print(f"Error response: {error_text}")
                
                # Check for common error types
                if response.status_code == 401:
                    print("\nThis appears to be an authentication error.")
                    print("Please verify that your API key is correct and has not expired.")
                elif response.status_code == 400:
                    print("\nThis appears to be a bad request error.")
                    print("The request format might be incorrect or the model name might be invalid.")
                elif response.status_code == 429:
                    print("\nThis appears to be a rate limit error.")
                    print("You may have exceeded your API usage limits.")
                
                return False
    except Exception as e:
        print(f"❌ Error during API request: {str(e)}")
        return False

def main():
    """Main function"""
    print("Testing Claude API Integration")
    print("=============================")
    
    # Run the async test function
    result = asyncio.run(test_claude_api())
    
    if result:
        print("\n✅ Claude API test completed successfully.")
        return 0
    else:
        print("\n❌ Claude API test failed.")
        print("\nSuggested next steps:")
        print("1. Verify your API key in the .env file")
        print("2. Check your internet connection")
        print("3. Run the fix_claude_integration.py script")
        print("4. Check if your API key has proper permissions")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
