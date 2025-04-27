#!/usr/bin/env python3
"""
Fix Claude API Integration Issues

This script fixes the Claude API integration in the GenAI Agent 3D project.
It updates the LLM service to correctly handle Claude API requests and responses.
"""

import os
import sys
import re
from pathlib import Path
import shutil
import datetime

def main():
    """Main function"""
    # Find the llm.py file
    project_root = Path(__file__).parent.absolute()
    llm_path = project_root / "genai_agent_project" / "genai_agent" / "services" / "llm.py"
    
    # Verify file exists
    if not llm_path.exists():
        print(f"Error: LLM service file not found at {llm_path}")
        return 1
    
    # Backup the original file
    backup_path = llm_path.with_suffix(f".py.bak-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(llm_path, backup_path)
    print(f"Created backup at {backup_path}")
    
    # Read the file content
    with open(llm_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the _generate_anthropic method
    updated_content = fix_anthropic_method(content)
    
    # Write updated content
    with open(llm_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("\n✅ Successfully updated Claude API integration!")
    print(f"Updated file: {llm_path}")
    
    # Update the enhanced_env_loader.py file to ensure proper API key loading
    env_loader_path = project_root / "genai_agent_project" / "genai_agent" / "services" / "enhanced_env_loader.py"
    if env_loader_path.exists():
        fix_env_loader(env_loader_path)
    
    # Verify and update .env file
    env_path = project_root / "genai_agent_project" / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if "ANTHROPIC_API_KEY=" in env_content:
            print("\n✅ Anthropic API key is already set in the .env file.")
            print("The API key should look like 'sk-ant-api03-...'")
            
            # Ask if the user wants to update the API key
            replace_key = input("Would you like to update the API key? (y/n): ").lower() == 'y'
            if replace_key:
                update_api_key(env_path)
        else:
            print("\n❌ Anthropic API key is not set in the .env file.")
            update_api_key(env_path)
    else:
        print(f"\n❌ .env file not found at {env_path}")
        print("Please create the .env file and add your Anthropic API key.")
    
    # Ask if the user wants to restart the services
    restart = input("\nWould you like to restart the services now? (y/n): ").lower() == 'y'
    if restart:
        try:
            import subprocess
            subprocess.run([sys.executable, str(project_root / "restart_services.py")], check=True)
            print("\n✅ Services restarted successfully!")
        except Exception as e:
            print(f"\n❌ Failed to restart services: {str(e)}")
            print("Please restart services manually using restart_services.py or restart_with_claude.bat")
    
    return 0

def fix_anthropic_method(content):
    """Fix the _generate_anthropic method in the LLM service"""
    # Find the _generate_anthropic method
    anthropic_method_pattern = r'async def _generate_anthropic\(.*?\):'
    match = re.search(anthropic_method_pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find _generate_anthropic method. Adding it.")
        # If method not found, add it at the end of the class
        class_end = content.rfind('async def _generate_hunyuan3d')
        if class_end == -1:
            print("Could not find the end of the class. Cannot add the method.")
            return content
        
        # Find the end of the last method to insert the new method
        method_end = content.find('    async def', class_end + 1)
        if method_end == -1:
            # If there's no next method, find the end of the class
            method_end = len(content)
        
        # Insert the fixed method before the next method
        fixed_method = '''
    async def _generate_anthropic(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Generate text using Anthropic API"""
        # Try to get API key from environment first, then config
        api_key = get_api_key_for_provider("anthropic") or self.config.get("api_key")
        
        if not api_key:
            error_msg = "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable or configure in settings."
            logger.error(error_msg)
            return error_msg
        
        # Map our generic parameters to Anthropic specific ones
        max_tokens = parameters.get("max_tokens", 2048)
        temperature = parameters.get("temperature", 0.7)
        
        # Updated headers with correct format and capitalization
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,  # Correct capitalization: X-API-Key
            "anthropic-version": "2023-06-01"
        }
        
        # Use the Messages API format (newer and recommended)
        messages_body = {
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
                    json=messages_body
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Claude API response: {data}")
                    
                    # Extract the message content from the response
                    if "content" in data and len(data["content"]) > 0:
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
'''
        updated_content = content[:method_end] + fixed_method + content[method_end:]
        return updated_content
    
    # Extract the method body
    method_start = match.start()
    method_end = find_method_end(content, method_start)
    method_body = content[method_start:method_end]
    
    # Fix headers with correct capitalization
    method_body = re.sub(
        r'"x-api-key":\s*api_key',
        '"X-API-Key": api_key',  # Correct capitalization
        method_body
    )
    
    # Fix content extraction logic
    content_extraction_pattern = r'if data\.get\(["\']content["\']\).*?return ["\']["\']'
    if re.search(content_extraction_pattern, method_body, re.DOTALL):
        method_body = re.sub(
            content_extraction_pattern,
            '''if "content" in data and len(data["content"]) > 0:
                        # Messages API returns an array of content blocks
                        content_blocks = data["content"]
                        text_blocks = [block["text"] for block in content_blocks if block["type"] == "text"]
                        return "".join(text_blocks)
                    return ""''',
            method_body,
            flags=re.DOTALL
        )
    
    # Add debug logging
    method_body = method_body.replace(
        'if response.status_code == 200:',
        'if response.status_code == 200:\n                    data = response.json()\n                    logger.debug(f"Claude API response: {data}")',
        1
    )
    
    # Replace the old method with the updated one
    updated_content = content[:method_start] + method_body + content[method_end:]
    return updated_content

def find_method_end(content, method_start):
    """Find the end of a method in the content"""
    lines = content[method_start:].split('\n')
    indent_level = len(lines[0]) - len(lines[0].lstrip())
    end_line = 0
    
    for i, line in enumerate(lines[1:], 1):
        if line.strip() and len(line) - len(line.lstrip()) <= indent_level and line.lstrip().startswith(('async def', 'def')):
            end_line = i
            break
    
    if end_line == 0:
        end_line = len(lines)
    
    return method_start + sum(len(line) + 1 for line in lines[:end_line])

def fix_env_loader(env_loader_path):
    """Fix the enhanced_env_loader.py file to ensure proper API key loading"""
    with open(env_loader_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if anthropic is in the provider_env_map
    provider_env_map_pattern = r'provider_env_map\s*=\s*{[^}]*}'
    provider_env_map_match = re.search(provider_env_map_pattern, content, re.DOTALL)
    
    if provider_env_map_match:
        provider_env_map = provider_env_map_match.group(0)
        
        if "'anthropic':" not in provider_env_map and '"anthropic":' not in provider_env_map:
            # Add anthropic to the provider_env_map
            updated_map = provider_env_map.replace(
                '}',
                ",\n        'anthropic': 'ANTHROPIC_API_KEY'\n    }"
            )
            updated_content = content.replace(provider_env_map, updated_map)
            
            # Write updated content
            with open(env_loader_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"\n✅ Updated enhanced_env_loader.py to include Anthropic API key mapping")
    else:
        print(f"\n❌ Could not find provider_env_map in {env_loader_path}")

def update_api_key(env_path):
    """Update the Anthropic API key in the .env file"""
    print("\nAnthropic API Key Setup")
    print("=======================")
    print("You need to provide your Anthropic API key to use Claude models.")
    print("The API key should start with 'sk-ant-'")
    
    api_key = input("Enter your Anthropic API key: ")
    if not api_key:
        print("No API key provided. Skipping.")
        return
    
    # Basic validation
    if not api_key.startswith("sk-ant-"):
        print("Warning: The API key doesn't seem to have the expected format.")
        print("It should typically start with 'sk-ant-'")
        continue_anyway = input("Continue anyway? (y/n): ").lower() == 'y'
        if not continue_anyway:
            print("Operation cancelled.")
            return
    
    # Read current content
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update or add the API key
    if "ANTHROPIC_API_KEY=" in content:
        # Replace existing key
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("ANTHROPIC_API_KEY="):
                lines[i] = f"ANTHROPIC_API_KEY={api_key}"
                break
            elif line.strip().startswith("# ANTHROPIC_API_KEY="):
                lines[i] = f"ANTHROPIC_API_KEY={api_key}"
                break
        
        updated_content = '\n'.join(lines)
    else:
        # Add new key
        if not content.endswith('\n'):
            content += '\n'
        updated_content = content + f"ANTHROPIC_API_KEY={api_key}\n"
    
    # Write updated content
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("\n✅ Anthropic API key has been successfully updated in the .env file!")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
