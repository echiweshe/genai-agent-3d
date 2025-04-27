#!/usr/bin/env python3
"""
Test Hunyuan3D API Integration

This script tests the Hunyuan3D API integration in the GenAI Agent 3D project.
It sends a simple request to the fal.ai Hunyuan3D API and checks if the response is valid.
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

async def test_hunyuan3d_api():
    """Test Hunyuan3D API integration via fal.ai"""
    # Load API key from environment
    env_path = Path(__file__).parent / "genai_agent_project" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    api_key = os.environ.get("HUNYUAN3D_API_KEY")
    if not api_key:
        print("❌ Hunyuan3D API key not found in environment variables.")
        print(f"Please ensure the API key is set in {env_path}")
        return False
    
    if not api_key.startswith("key-"):
        print(f"⚠️ Warning: Your API key ({api_key[:10]}...) doesn't start with 'key-'")
        print("This may not be a valid fal.ai API key.")
    
    print(f"Found API key: {api_key[:10]}...")
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Key {api_key}"  # Note the format is "Key" not "Bearer"
    }
    
    # Using a simple prompt for testing
    body = {
        "prompt": "A simple red cube on a white surface, 3D model",
        "negative_prompt": "low quality, distorted",
        "num_inference_steps": 10,  # Lower for faster test
        "guidance_scale": 7.5,
        "width": 512,  # Smaller for faster test
        "height": 512,  # Smaller for faster test
    }
    
    model_id = "fal-ai/hunyuan3d/multi-view"  # Using the base model for testing
    endpoint = f"/models/{model_id}/infer"
    
    try:
        print("\nSending test request to Hunyuan3D API via fal.ai...")
        print("This may take a minute or more as 3D generation is resource-intensive.")
        print("Using a simplified prompt and parameters to speed up the test.")
        
        async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for 3D generation
            response = await client.post(
                f"https://api.fal.ai{endpoint}",
                headers=headers,
                json=body
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Hunyuan3D API integration is working correctly!")
                
                # Print response data
                print("\nResponse from Hunyuan3D:")
                
                if "images" in data:
                    print(f"\nGenerated images:")
                    for i, image_url in enumerate(data["images"], 1):
                        print(f"{i}. {image_url}")
                
                if "rendered_frames" in data:
                    print(f"\nRendered frames:")
                    for i, frame in enumerate(data["rendered_frames"], 1):
                        print(f"{i}. {frame}")
                
                if "3d_model" in data:
                    print(f"\n3D Model: {data['3d_model']}")
                
                if "mesh_url" in data:
                    print(f"\nMesh URL: {data['mesh_url']}")
                
                # Print some metadata if available
                if "seed" in data:
                    print(f"\nSeed used: {data['seed']}")
                
                return True
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
                    print("The request format might be incorrect or some parameters might be invalid.")
                elif response.status_code == 429:
                    print("\nThis appears to be a rate limit error.")
                    print("You may have exceeded your API usage limits.")
                elif response.status_code == 402:
                    print("\nThis appears to be a payment required error.")
                    print("Your account might not have sufficient credits for this operation.")
                
                return False
    except httpx.ReadTimeout:
        print("❌ The request timed out. Hunyuan3D generation can take several minutes.")
        print("Consider increasing the timeout value or simplifying your request parameters.")
        return False
    except Exception as e:
        print(f"❌ Error during API request: {str(e)}")
        return False

def main():
    """Main function"""
    print("Testing Hunyuan3D API Integration")
    print("=================================")
    
    # Run the async test function
    result = asyncio.run(test_hunyuan3d_api())
    
    if result:
        print("\n✅ Hunyuan3D API test completed successfully.")
        print("\nNote: Each API call to Hunyuan3D incurs costs based on your fal.ai account plan.")
        print("Check your fal.ai dashboard for usage information.")
        return 0
    else:
        print("\n❌ Hunyuan3D API test failed.")
        print("\nSuggested next steps:")
        print("1. Verify your API key in the .env file")
        print("2. Check your internet connection")
        print("3. Run the fix_hunyuan3d_integration.py script")
        print("4. Check if your fal.ai account has credits/permissions")
        print("5. Check the fal.ai status page to ensure the service is operational")
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
