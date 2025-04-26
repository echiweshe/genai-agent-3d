#!/usr/bin/env python3
"""
Update Anthropic API to Messages Format

This script updates the Anthropic integration to use the newer Messages API
instead of the older Completion API.
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    return backup_path

def update_anthropic_api():
    """Update the Anthropic API integration to use the Messages API"""
    # Find the llm.py file
    file_path = "genai_agent_project/genai_agent/services/llm.py"
    
    if not os.path.exists(file_path):
        # Try absolute path
        file_path = os.path.join("C:", os.sep, "ZB_Share", "Labs", "src", "CluadeMCP", 
                              "genai-agent-3d", "genai_agent_project", "genai_agent", 
                              "services", "llm.py")
        if not os.path.exists(file_path):
            print(f"❌ Could not find llm.py")
            return False

    # Create a backup
    backup_file(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the _generate_anthropic method exists
    if "_generate_anthropic" not in content:
        print("❌ Could not find _generate_anthropic method")
        return False
    
    # Find the _generate_anthropic method
    anthropic_method_pattern = re.compile(r'async def _generate_anthropic.*?def|async def _generate_anthropic.*?$', re.DOTALL)
    match = anthropic_method_pattern.search(content)
    
    if not match:
        print("❌ Could not locate the _generate_anthropic method")
        return False
    
    # Get the current method text
    method_text = match.group(0)
    
    # If the method text ends with 'def', we need to remove that last bit
    if method_text.endswith('def'):
        method_text = method_text[:-3]
    
    # Create the updated method with the Messages API
    updated_method = """async def _generate_anthropic(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Generate text using Anthropic API with the Messages format"""
        api_key = os.environ.get("ANTHROPIC_API_KEY") or self.config.get("api_key")
        if not api_key:
            error_msg = "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable or configure in settings."
            logger.error(error_msg)
            return error_msg
        
        # Map our generic parameters to Anthropic specific ones
        max_tokens = parameters.get("max_tokens", 2048)
        temperature = parameters.get("temperature", 0.7)
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Build request body using the Messages API format
        request_body = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=request_body
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Extract the message content from the response
                    if data.get("content") and len(data["content"]) > 0:
                        # Messages API returns an array of content blocks
                        content_blocks = data["content"]
                        text_blocks = [block["text"] for block in content_blocks if block["type"] == "text"]
                        return "".join(text_blocks)
                    return ""
                else:
                    error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Error generating text with Anthropic: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    """
    
    # Replace the old method with the updated one
    updated_content = content.replace(method_text, updated_method)
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Updated Anthropic API to use the Messages format")
    return True

if __name__ == "__main__":
    print("="*80)
    print("      Update Anthropic API Integration to Messages Format      ")
    print("="*80)
    
    success = update_anthropic_api()
    
    if success:
        print("\n✅ Successfully updated the Anthropic API integration to use the Messages API!")
        print("\nThis update provides several benefits:")
        print("- Uses the newer, recommended Messages API format")
        print("- Better handling of content blocks")
        print("- More consistent with other LLM provider APIs")
        
        # Ask if user wants to restart services
        restart = input("\nDo you want to restart all services now? (y/n): ")
        if restart.lower() == 'y':
            print("\nRestarting services...")
            os.system('cd genai_agent_project && python manage_services.py restart all')
            print("Services restarted!")
        else:
            print("\nSkipping service restart")
            print("To restart services manually:")
            print("cd genai_agent_project")
            print("python manage_services.py restart all")
    else:
        print("\n❌ Failed to update the Anthropic API integration.")
        print("Please check the error messages above and fix manually if needed.")
