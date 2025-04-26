#!/usr/bin/env python3
"""
Add Anthropic Claude Support to GenAI Agent 3D

This script adds support for Anthropic's Claude models and sets it as the default LLM provider.
"""

import os
import re
import shutil
import json
import yaml
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    return backup_path

def update_llm_service():
    """Update the LLM service to support Anthropic Claude"""
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
    
    # Check if Anthropic support already exists
    if "_generate_anthropic" in content:
        print("✅ Anthropic support already exists")
        
        # Just update the config to use anthropic as default
        update_config()
        return True
    
    # Add Anthropic provider to the _discover_providers method
    anthropic_provider_code = '''
            # Add Anthropic provider
            self.providers["anthropic"] = {
                "name": "Anthropic",
                "is_local": False,
                "base_url": "https://api.anthropic.com",
                "models": [
                    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
                    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
                    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
                    {"id": "claude-3.5-sonnet-20250626", "name": "Claude 3.5 Sonnet"}
                ]
            }
'''
    
    # Find the end of the _discover_providers method's Ollama section
    ollama_section_end = content.find('''            self.providers["ollama"]["models"] = [''')
    if ollama_section_end == -1:
        print("❌ Could not find the right location to add Anthropic provider")
        return False
    
    # Find the end of the self.providers["ollama"] block
    insert_pos = content.find("        except Exception as e:", ollama_section_end)
    if insert_pos == -1:
        print("❌ Could not find the right location to add Anthropic provider")
        return False
    
    # Insert Anthropic provider
    content = content[:insert_pos] + anthropic_provider_code + content[insert_pos:]
    
    # Add Anthropic generate method
    anthropic_method = '''
    async def _generate_anthropic(self, prompt: str, model: str, parameters: Dict[str, Any]) -> str:
        """Generate text using Anthropic API"""
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
        
        # Build request body
        request_body = {
            "model": model,
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/complete",
                    headers=headers,
                    json=request_body
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("completion", "")
                else:
                    error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Error generating text with Anthropic: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
'''
    
    # Add Anthropic method before the last closing brace
    last_brace = content.rfind("}")
    content = content[:last_brace] + anthropic_method + content[last_brace:]
    
    # Update generate method to support Anthropic
    generate_provider_check = '''        # Generate based on provider
        if provider.lower() == "ollama":
            return await self._generate_ollama(prompt, model, parameters)
        elif provider.lower() == "anthropic":
            return await self._generate_anthropic(prompt, model, parameters)
        else:
            raise ValueError(f"Unsupported provider: {provider}")'''
    
    # Find and replace the provider check
    provider_check_pattern = r'''        # Generate based on provider.*?raise ValueError\(f"Unsupported provider: \{provider\}"\)'''
    content = re.sub(provider_check_pattern, generate_provider_check, content, flags=re.DOTALL)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added Anthropic Claude support to LLM service")
    
    # Update config to use anthropic as default
    update_config()
    
    return True

def update_config():
    """Update the config.yaml to use Anthropic Claude as the default provider"""
    file_path = "genai_agent_project/config.yaml"
    
    if not os.path.exists(file_path):
        # Try absolute path
        file_path = os.path.join("C:", os.sep, "ZB_Share", "Labs", "src", "CluadeMCP", 
                              "genai-agent-3d", "genai_agent_project", "config.yaml")
        if not os.path.exists(file_path):
            print(f"❌ Could not find config.yaml")
            return False
    
    # Create a backup
    backup_file(file_path)
    
    # Read the config file
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Update the config to use Anthropic Claude as default
    if 'llm' not in config:
        config['llm'] = {}
    
    config['llm']['type'] = 'cloud'
    config['llm']['provider'] = 'anthropic'
    config['llm']['model'] = 'claude-3-sonnet-20240229'
    
    # Get API key from environment or prompt user
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nAnthropic API key not found in environment.")
        api_key_input = input("Enter your Anthropic API key (or leave blank to add later): ").strip()
        if api_key_input:
            config['llm']['api_key'] = api_key_input
    else:
        config['llm']['api_key'] = api_key
    
    # Write the updated config
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ Updated config to use Anthropic Claude as default LLM provider")
    return True

def update_llm_api_routes():
    """Update the LLM API routes to support Anthropic models in the UI"""
    file_path = "genai_agent_project/genai_agent/services/llm_api_routes.py"
    
    if not os.path.exists(file_path):
        # Try absolute path
        file_path = os.path.join("C:", os.sep, "ZB_Share", "Labs", "src", "CluadeMCP", 
                              "genai-agent-3d", "genai_agent_project", "genai_agent", 
                              "services", "llm_api_routes.py")
        if not os.path.exists(file_path):
            print(f"❌ Could not find llm_api_routes.py")
            return False
    
    # Create a backup
    backup_file(file_path)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the providers function has Anthropic already
    if '"name": "Anthropic"' in content and 'claude-3-sonnet' in content:
        print("✅ Anthropic already listed in providers")
        return True
    
    # Find the providers function
    providers_func_match = re.search(r'@router\.get\("/providers"\).*?async def get_providers\(\):.*?return providers', content, re.DOTALL)
    if not providers_func_match:
        print("❌ Could not find providers function")
        return False
    
    # Get the entire function content
    providers_func = providers_func_match.group(0)
    
    # Check if there's a list of providers in the function
    if "providers = [" not in providers_func:
        print("❌ Could not find providers list in function")
        return False
    
    # Add Anthropic to the providers list
    anthropic_provider = '''                {
                    "name": "Anthropic",
                    "is_local": False,
                    "models": [
                        {
                            "id": "claude-3-sonnet-20240229",
                            "name": "Claude 3 Sonnet",
                            "context_length": 200000,
                            "input_cost": 0.000003,
                            "output_cost": 0.000015
                        },
                        {
                            "id": "claude-3-opus-20240229",
                            "name": "Claude 3 Opus",
                            "context_length": 200000,
                            "input_cost": 0.00003,
                            "output_cost": 0.00015
                        },
                        {
                            "id": "claude-3-haiku-20240307",
                            "name": "Claude 3 Haiku",
                            "context_length": 200000,
                            "input_cost": 0.00000025,
                            "output_cost": 0.00000125
                        },
                        {
                            "id": "claude-3.5-sonnet-20250626",
                            "name": "Claude 3.5 Sonnet",
                            "context_length": 200000,
                            "input_cost": 0.000005,
                            "output_cost": 0.000025
                        }
                    ]
                },'''
    
    # Replace OpenAI section with OpenAI + Anthropic
    if '"name": "OpenAI"' in providers_func:
        # Insert after OpenAI
        modified_func = providers_func.replace(
            '"name": "OpenAI",',
            '"name": "OpenAI",\n                "is_local": False,'
        )
        
        # Add Anthropic after OpenAI section
        openai_end = modified_func.find('}', modified_func.find('"name": "OpenAI"'))
        openai_section_end = modified_func.find('},', openai_end) + 2
        modified_func = modified_func[:openai_section_end] + '\n            ' + anthropic_provider + modified_func[openai_section_end:]
    else:
        # Just add after Ollama
        ollama_end = providers_func.find('}', providers_func.find('"name": "Ollama"'))
        ollama_section_end = providers_func.find('},', ollama_end) + 2
        modified_func = providers_func[:ollama_section_end] + '\n            ' + anthropic_provider + providers_func[ollama_section_end:]
    
    # Replace original function with modified function
    updated_content = content.replace(providers_func, modified_func)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Updated LLM API routes to include Anthropic models")
    return True

def create_env_file():
    """Create or update .env file with Anthropic API key placeholder"""
    file_path = "genai_agent_project/.env"
    
    # Check if file exists
    if os.path.exists(file_path):
        # Read existing file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if ANTHROPIC_API_KEY is already in the file
        if "ANTHROPIC_API_KEY" in content:
            print("✅ .env file already has ANTHROPIC_API_KEY")
            return True
        
        # Append to existing file
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("\n# Anthropic API key for Claude models\n")
            f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
    else:
        # Create new file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Environment variables for GenAI Agent 3D\n\n")
            f.write("# Anthropic API key for Claude models\n")
            f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
    
    print("✅ Created/updated .env file with Anthropic API key placeholder")
    return True

def main():
    """Main function"""
    print("="*80)
    print("          Add Anthropic Claude Support to GenAI Agent 3D           ")
    print("="*80)
    
    success = True
    
    print("\n1. Adding Anthropic Claude support to LLM service...")
    if not update_llm_service():
        success = False
    
    print("\n2. Updating LLM API routes to include Anthropic models...")
    if not update_llm_api_routes():
        success = False
    
    print("\n3. Creating/updating .env file...")
    if not create_env_file():
        success = False
    
    if success:
        print("\n✅ Successfully added Anthropic Claude support to GenAI Agent 3D!")
        print("\nTo use Anthropic Claude:")
        print("1. Make sure you have an Anthropic API key")
        print("2. Set your API key in genai_agent_project/.env or as an environment variable")
        print("3. Restart the services")
        
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
        print("\n❌ Failed to add Anthropic Claude support.")
        print("Please check the error messages above and fix manually if needed.")

if __name__ == "__main__":
    main()
