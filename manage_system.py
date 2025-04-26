#!/usr/bin/env python3
"""
GenAI Agent 3D - System Management Tool

This script provides a comprehensive UI for managing all aspects of your
GenAI Agent 3D system, including:
- Starting/stopping services
- Setting API keys
- Running status checks
- Repairing common issues
"""

import os
import sys
import subprocess
import time
import yaml
import re
import shutil
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a formatted header"""
    clear_screen()
    print("="*80)
    print(f"{title:^80}")
    print("="*80)
    print()

def print_menu(options):
    """Print a formatted menu"""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print()

def get_input(prompt, options_count):
    """Get user input with validation"""
    while True:
        try:
            choice = input(prompt)
            if choice.lower() == 'q':
                return 'q'
            choice = int(choice)
            if 1 <= choice <= options_count:
                return choice
            else:
                print(f"Please enter a number between 1 and {options_count} or 'q' to quit.")
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")

def run_command(command, cwd=None):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return {
            "success": True,
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "output": e.stdout,
            "error": e.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def manage_services():
    """Service management menu"""
    while True:
        print_header("Service Management")
        
        options = [
            "Start all services",
            "Stop all services",
            "Restart all services",
            "Start specific service",
            "Stop specific service",
            "Check service status",
            "Return to main menu"
        ]
        
        print_menu(options)
        choice = get_input("Enter your choice (or 'q' to quit): ", len(options))
        
        if choice == 'q':
            return
        
        if choice == 1:  # Start all
            print("\nStarting all services...")
            result = run_command("python manage_services.py start all", cwd="genai_agent_project")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 2:  # Stop all
            print("\nStopping all services...")
            result = run_command("python manage_services.py stop all", cwd="genai_agent_project")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 3:  # Restart all
            print("\nRestarting all services...")
            result = run_command("python manage_services.py restart all", cwd="genai_agent_project")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 4:  # Start specific
            print_header("Start Specific Service")
            service_options = ["redis", "ollama", "backend", "frontend", "llm_worker"]
            for i, service in enumerate(service_options, 1):
                print(f"{i}. {service}")
            
            service_choice = get_input("\nSelect service to start: ", len(service_options))
            if service_choice == 'q':
                continue
            
            service = service_options[service_choice - 1]
            print(f"\nStarting {service} service...")
            result = run_command(f"python manage_services.py start {service}", cwd="genai_agent_project")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 5:  # Stop specific
            print_header("Stop Specific Service")
            service_options = ["redis", "ollama", "backend", "frontend", "llm_worker"]
            for i, service in enumerate(service_options, 1):
                print(f"{i}. {service}")
            
            service_choice = get_input("\nSelect service to stop: ", len(service_options))
            if service_choice == 'q':
                continue
            
            service = service_options[service_choice - 1]
            print(f"\nStopping {service} service...")
            result = run_command(f"python manage_services.py stop {service}", cwd="genai_agent_project")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 6:  # Check status
            print("\nChecking service status...")
            result = run_command("python check_status.py")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 7:  # Back to main
            return
        
        input("\nPress Enter to continue...")

def manage_api_keys():
    """API key management menu"""
    while True:
        print_header("API Key Management")
        
        options = [
            "View current API keys",
            "Update API keys (interactive)",
            "Set Anthropic API key",
            "Set OpenAI API key",
            "Return to main menu"
        ]
        
        print_menu(options)
        choice = get_input("Enter your choice (or 'q' to quit): ", len(options))
        
        if choice == 'q':
            return
        
        if choice == 1:  # View keys
            print("\nCurrent API Keys:")
            env_file = ".env"
            
            if os.path.exists(env_file):
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract API keys
                anthropic_key_match = re.search(r'^ANTHROPIC_API_KEY=(.*)$', content, re.MULTILINE)
                openai_key_match = re.search(r'^OPENAI_API_KEY=(.*)$', content, re.MULTILINE)
                stability_key_match = re.search(r'^STABILITY_API_KEY=(.*)$', content, re.MULTILINE)
                
                print(f"  Anthropic API Key: {mask_key(anthropic_key_match.group(1)) if anthropic_key_match else 'Not set'}")
                print(f"  OpenAI API Key: {mask_key(openai_key_match.group(1)) if openai_key_match else 'Not set'}")
                print(f"  Stability API Key: {mask_key(stability_key_match.group(1)) if stability_key_match else 'Not set'}")
            else:
                print("  .env file not found")
        
        elif choice == 2:  # Update all keys
            print("\nRunning API key update script...")
            result = run_command("python manage_api_keys.py")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 3:  # Set Anthropic key
            print("\nSetting Anthropic API key...")
            api_key = input("Enter your Anthropic API key: ").strip()
            if api_key:
                update_env_key("ANTHROPIC_API_KEY", api_key)
                update_config_key("anthropic", api_key)
                print("✅ Anthropic API key updated successfully")
            else:
                print("❌ No API key provided")
        
        elif choice == 4:  # Set OpenAI key
            print("\nSetting OpenAI API key...")
            api_key = input("Enter your OpenAI API key: ").strip()
            if api_key:
                update_env_key("OPENAI_API_KEY", api_key)
                update_config_key("openai", api_key)
                print("✅ OpenAI API key updated successfully")
            else:
                print("❌ No API key provided")
        
        elif choice == 5:  # Back to main
            return
        
        input("\nPress Enter to continue...")

def mask_key(key):
    """Mask an API key for display"""
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]

def update_env_key(key_name, key_value):
    """Update an API key in the .env files"""
    env_files = [".env", "genai_agent_project/.env"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            # Create backup
            backup_file = f"{env_file}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            shutil.copy2(env_file, backup_file)
            
            # Read the current content
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update the API key
            pattern = re.compile(f'^{key_name}=.*$', re.MULTILINE)
            match = pattern.search(content)
            
            if match:
                # Update existing entry
                content = pattern.sub(f'{key_name}={key_value}', content)
            else:
                # Add new entry
                content += f'\n{key_name}={key_value}\n'
            
            # Write the updated content
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Updated {key_name} in {env_file}")

def update_config_key(provider, key_value):
    """Update an API key in the config.yaml file"""
    config_file = "genai_agent_project/config.yaml"
    
    if os.path.exists(config_file):
        # Create backup
        backup_file = f"{config_file}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(config_file, backup_file)
        
        # Read the current config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Update LLM API key if provider matches
        if 'llm' in config and config['llm'].get('provider', '').lower() == provider.lower():
            config['llm']['api_key'] = key_value
        
        # Write the updated config
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"Updated API key in {config_file}")

def manage_llm_providers():
    """LLM provider management menu"""
    while True:
        print_header("LLM Provider Management")
        
        options = [
            "Set Claude as default provider",
            "Set Ollama as default provider",
            "Set OpenAI as default provider",
            "Update to latest API formats",
            "Test LLM generation",
            "Return to main menu"
        ]
        
        print_menu(options)
        choice = get_input("Enter your choice (or 'q' to quit): ", len(options))
        
        if choice == 'q':
            return
        
        if choice == 1:  # Set Claude
            print("\nSetting Claude as the default LLM provider...")
            
            # Update config file
            config_file = "genai_agent_project/config.yaml"
            if os.path.exists(config_file):
                # Read the current config
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # Update LLM provider
                if 'llm' not in config:
                    config['llm'] = {}
                
                config['llm']['provider'] = 'anthropic'
                config['llm']['model'] = 'claude-3-sonnet-20240229'
                config['llm']['type'] = 'cloud'
                
                # Write the updated config
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False)
            
            # Update .env files
            update_env_key("LLM_PROVIDER", "anthropic")
            update_env_key("LLM_MODEL", "claude-3-sonnet-20240229")
            update_env_key("LLM_TYPE", "cloud")
            
            print("✅ Claude is now set as the default LLM provider")
            
            # Ask to restart
            restart = input("\nDo you want to restart services to apply changes? (y/n): ")
            if restart.lower() == 'y':
                print("\nRestarting services...")
                result = run_command("python manage_services.py restart all", cwd="genai_agent_project")
                print(result.get("output", ""))
        
        elif choice == 2:  # Set Ollama
            print("\nSetting Ollama as the default LLM provider...")
            
            # Update config file
            config_file = "genai_agent_project/config.yaml"
            if os.path.exists(config_file):
                # Read the current config
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # Update LLM provider
                if 'llm' not in config:
                    config['llm'] = {}
                
                config['llm']['provider'] = 'ollama'
                config['llm']['model'] = 'llama3:latest'
                config['llm']['type'] = 'local'
                
                # Write the updated config
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False)
            
            # Update .env files
            update_env_key("LLM_PROVIDER", "ollama")
            update_env_key("LLM_MODEL", "llama3:latest")
            update_env_key("LLM_TYPE", "local")
            
            print("✅ Ollama is now set as the default LLM provider")
            
            # Ask to restart
            restart = input("\nDo you want to restart services to apply changes? (y/n): ")
            if restart.lower() == 'y':
                print("\nRestarting services...")
                result = run_command("python manage_services.py restart all", cwd="genai_agent_project")
                print(result.get("output", ""))
        
        elif choice == 3:  # Set OpenAI
            print("\nSetting OpenAI as the default LLM provider...")
            
            # Update config file
            config_file = "genai_agent_project/config.yaml"
            if os.path.exists(config_file):
                # Read the current config
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # Update LLM provider
                if 'llm' not in config:
                    config['llm'] = {}
                
                config['llm']['provider'] = 'openai'
                config['llm']['model'] = 'gpt-4o'
                config['llm']['type'] = 'cloud'
                
                # Write the updated config
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False)
            
            # Update .env files
            update_env_key("LLM_PROVIDER", "openai")
            update_env_key("LLM_MODEL", "gpt-4o")
            update_env_key("LLM_TYPE", "cloud")
            
            print("✅ OpenAI is now set as the default LLM provider")
            
            # Ask to restart
            restart = input("\nDo you want to restart services to apply changes? (y/n): ")
            if restart.lower() == 'y':
                print("\nRestarting services...")
                result = run_command("python manage_services.py restart all", cwd="genai_agent_project")
                print(result.get("output", ""))
        
        elif choice == 4:  # Update APIs
            print("\nUpdating to latest API formats...")
            result = run_command("python update_anthropic_api.py")
            print(result.get("output", ""))
            if not result.get("success", False):
                print(f"Error: {result.get('error', 'Unknown error')}")
        
        elif choice == 5:  # Test LLM
            print("\nTesting LLM generation...")
            
            # Get the current LLM provider
            current_provider = "unknown"
            config_file = "genai_agent_project/config.yaml"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                if 'llm' in config:
                    current_provider = config['llm'].get('provider', 'unknown')
            
            print(f"Current LLM provider: {current_provider}")
            
            # Construct a test prompt
            test_prompt = input("\nEnter a test prompt (or press Enter for default): ").strip()
            if not test_prompt:
                test_prompt = "Generate a short paragraph about artificial intelligence."
            
            print(f"\nSending prompt: \"{test_prompt}\"")
            print("Waiting for response (this may take a moment)...")
            
            # Send request to API
            try:
                import requests
                response = requests.post(
                    "http://localhost:8000/api/llm/generate",
                    json={
                        "prompt": test_prompt,
                        "parameters": {
                            "temperature": 0.7,
                            "max_tokens": 150
                        }
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("\nGenerated text:")
                    print(f"\"{result.get('text', 'No text generated')}\"")
                else:
                    print(f"\nError: API returned status code {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"\nError: {str(e)}")
        
        elif choice == 6:  # Back to main
            return
        
        input("\nPress Enter to continue...")

def troubleshoot_system():
    """System troubleshooting menu"""
    while True:
        print_header("System Troubleshooting")
        
        options = [
            "Run system health check",
            "Fix Redis ping issue",
            "Fix LLM service issues",
            "Apply all fixes",
            "Show logs",
            "Return to main menu"
        ]
        
        print_menu(options)
        choice = get_input("Enter your choice (or 'q' to quit): ", len(options))
        
        if choice == 'q':
            return
        
        if choice == 1:  # Health check
            print("\nRunning system health check...")
            result = run_command("python check_status.py")
            print(result.get("output", ""))
        
        elif choice == 2:  # Fix Redis ping
            print("\nFixing Redis ping issue...")
            result = run_command("python direct_redis_fix.py")
            print(result.get("output", ""))
        
        elif choice == 3:  # Fix LLM
            print("\nFixing LLM service issues...")
            result = run_command("python fix_llm_errors.py")
            print(result.get("output", ""))
        
        elif choice == 4:  # Apply all fixes
            print("\nApplying all fixes...")
            result = run_command("python fix_all_issues.py")
            print(result.get("output", ""))
        
        elif choice == 5:  # Show logs
            print_header("Log Viewer")
            log_options = [
                "main.log",
                "backend.log",
                "frontend.log",
                "redis.log",
                "ollama.log"
            ]
            
            for i, log in enumerate(log_options, 1):
                print(f"{i}. {log}")
            
            log_choice = get_input("\nSelect log to view: ", len(log_options))
            if log_choice == 'q':
                continue
            
            log_file = log_options[log_choice - 1]
            log_path = f"genai_agent_project/logs/{log_file}"
            
            if os.path.exists(log_path):
                print(f"\nShowing last 20 lines of {log_file}:\n")
                
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line in lines[-20:]:
                        print(line.strip())
            else:
                print(f"\nLog file not found: {log_path}")
        
        elif choice == 6:  # Back to main
            return
        
        input("\nPress Enter to continue...")

def main():
    """Main function"""
    while True:
        print_header("GenAI Agent 3D - System Management Tool")
        
        options = [
            "Service Management",
            "API Key Management",
            "LLM Provider Management",
            "System Troubleshooting",
            "Open Web Interface",
            "Exit"
        ]
        
        print_menu(options)
        choice = get_input("Enter your choice (or 'q' to quit): ", len(options))
        
        if choice == 'q' or choice == 6:
            print("\nExiting...")
            break
        
        if choice == 1:  # Service Management
            manage_services()
        
        elif choice == 2:  # API Key Management
            manage_api_keys()
        
        elif choice == 3:  # LLM Provider Management
            manage_llm_providers()
        
        elif choice == 4:  # System Troubleshooting
            troubleshoot_system()
        
        elif choice == 5:  # Open Web Interface
            print("\nOpening web interface...")
            try:
                import webbrowser
                webbrowser.open("http://localhost:3000")
                print("Browser opened to http://localhost:3000")
            except Exception as e:
                print(f"Could not open browser: {str(e)}")
                print("Please manually open http://localhost:3000 in your browser.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
