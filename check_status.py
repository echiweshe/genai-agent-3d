#!/usr/bin/env python3
"""
System Status Checker for GenAI Agent 3D

This script checks the status of all components of the GenAI Agent 3D system
and reports any issues it finds.
"""

import os
import sys
import subprocess
import time
import json
import requests
import yaml
import re
from urllib.parse import urlparse

def check_running_services():
    """Check if all required services are running"""
    services = {
        "redis": {
            "status": False,
            "port": 6379,
            "message": ""
        },
        "ollama": {
            "status": False,
            "port": 11434,
            "message": ""
        },
        "backend": {
            "status": False,
            "port": 8000,
            "message": ""
        },
        "frontend": {
            "status": False,
            "port": 3000,
            "message": ""
        }
    }
    
    # Check Redis
    try:
        redis_check = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if redis_check.stdout.strip() == "PONG":
            services["redis"]["status"] = True
            services["redis"]["message"] = "Redis is running and responsive"
        else:
            services["redis"]["message"] = f"Redis not responding: {redis_check.stderr}"
    except subprocess.TimeoutExpired:
        services["redis"]["message"] = "Redis check timed out"
    except Exception as e:
        services["redis"]["message"] = f"Error checking Redis: {str(e)}"
    
    # Check Ollama
    try:
        ollama_url = "http://localhost:11434/api/version"
        response = requests.get(ollama_url, timeout=5)
        if response.status_code == 200:
            services["ollama"]["status"] = True
            services["ollama"]["message"] = f"Ollama is running (version: {response.json().get('version', 'unknown')})"
        else:
            services["ollama"]["message"] = f"Ollama API responded with status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        services["ollama"]["message"] = "Could not connect to Ollama API"
    except Exception as e:
        services["ollama"]["message"] = f"Error checking Ollama: {str(e)}"
    
    # Check backend
    try:
        backend_url = "http://localhost:8000/api/health"
        response = requests.get(backend_url, timeout=5)
        if response.status_code == 200:
            services["backend"]["status"] = True
            services["backend"]["message"] = "Backend API is running and healthy"
        else:
            services["backend"]["message"] = f"Backend API responded with status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        services["backend"]["message"] = "Could not connect to Backend API"
    except Exception as e:
        services["backend"]["message"] = f"Error checking Backend: {str(e)}"
    
    # Check frontend
    try:
        frontend_url = "http://localhost:3000"
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            services["frontend"]["status"] = True
            services["frontend"]["message"] = "Frontend is running"
        else:
            services["frontend"]["message"] = f"Frontend responded with status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        services["frontend"]["message"] = "Could not connect to Frontend"
    except Exception as e:
        services["frontend"]["message"] = f"Error checking Frontend: {str(e)}"
    
    return services

def check_system_status():
    """Check the overall system status via the status API"""
    try:
        status_url = "http://localhost:8000/status"
        response = requests.get(status_url, timeout=5)
        
        if response.status_code == 200:
            status_data = response.json()
            
            # Check if it has the expected structure
            if "status" in status_data:
                return {
                    "online": status_data.get("status") == "ok",
                    "data": status_data
                }
            else:
                return {
                    "online": False,
                    "data": status_data,
                    "message": "Status endpoint returned unexpected data structure"
                }
        else:
            return {
                "online": False,
                "message": f"Status endpoint returned status code {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "online": False,
            "message": "Could not connect to status endpoint"
        }
    except Exception as e:
        return {
            "online": False,
            "message": f"Error checking system status: {str(e)}"
        }

def check_llm_configuration():
    """Check the LLM configuration in config.yaml and .env"""
    result = {
        "config_file": {
            "status": False,
            "provider": "",
            "model": "",
            "has_api_key": False,
            "message": ""
        },
        "env_file": {
            "status": False,
            "provider": "",
            "model": "",
            "has_api_key": False,
            "message": ""
        }
    }
    
    # Check config.yaml
    config_file = "genai_agent_project/config.yaml"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if 'llm' in config:
                result["config_file"]["status"] = True
                result["config_file"]["provider"] = config['llm'].get('provider', '')
                result["config_file"]["model"] = config['llm'].get('model', '')
                result["config_file"]["has_api_key"] = 'api_key' in config['llm'] and bool(config['llm']['api_key'])
                result["config_file"]["message"] = f"Config file exists with provider={result['config_file']['provider']}, model={result['config_file']['model']}"
            else:
                result["config_file"]["message"] = "Config file exists but has no LLM section"
        except Exception as e:
            result["config_file"]["message"] = f"Error reading config file: {str(e)}"
    else:
        result["config_file"]["message"] = "Config file not found"
    
    # Check .env file
    env_file = "genai_agent_project/.env"
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract LLM settings
            provider_match = re.search(r'^LLM_PROVIDER=(.*)$', content, re.MULTILINE)
            model_match = re.search(r'^LLM_MODEL=(.*)$', content, re.MULTILINE)
            anthropic_key_match = re.search(r'^ANTHROPIC_API_KEY=(.*)$', content, re.MULTILINE)
            openai_key_match = re.search(r'^OPENAI_API_KEY=(.*)$', content, re.MULTILINE)
            
            result["env_file"]["status"] = True
            
            if provider_match:
                result["env_file"]["provider"] = provider_match.group(1)
            
            if model_match:
                result["env_file"]["model"] = model_match.group(1)
            
            # Check if it has the appropriate API key based on provider
            if provider_match:
                provider = provider_match.group(1).lower()
                if provider == "anthropic" and anthropic_key_match:
                    result["env_file"]["has_api_key"] = bool(anthropic_key_match.group(1))
                elif provider == "openai" and openai_key_match:
                    result["env_file"]["has_api_key"] = bool(openai_key_match.group(1))
            
            result["env_file"]["message"] = f"Env file exists with provider={result['env_file']['provider']}, model={result['env_file']['model']}"
            
        except Exception as e:
            result["env_file"]["message"] = f"Error reading env file: {str(e)}"
    else:
        result["env_file"]["message"] = "Env file not found"
    
    return result

def test_llm_generation():
    """Test LLM text generation via the API"""
    try:
        generate_url = "http://localhost:8000/api/llm/generate"
        test_prompt = "Generate a simple test response to confirm you are working."
        
        payload = {
            "prompt": test_prompt,
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        
        response = requests.post(generate_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("text", "")
            
            if generated_text and len(generated_text) > 10:
                return {
                    "success": True,
                    "text": generated_text[:100] + ("..." if len(generated_text) > 100 else ""),
                    "message": "LLM generation successful"
                }
            else:
                return {
                    "success": False,
                    "text": generated_text,
                    "message": "LLM returned empty or very short response"
                }
        else:
            error_message = response.text
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_message = error_data["detail"]
            except:
                pass
            
            return {
                "success": False,
                "status_code": response.status_code,
                "message": f"LLM generation failed: {error_message}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Could not connect to LLM API"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "LLM generation request timed out"
        }
    except Exception as e:
        return {
            "success": False, 
            "message": f"Error during LLM generation test: {str(e)}"
        }

def check_api_routes():
    """Check if the API routes are properly configured"""
    api_endpoints = [
        {
            "name": "Health Check",
            "url": "http://localhost:8000/api/health",
            "method": "GET"
        },
        {
            "name": "Status",
            "url": "http://localhost:8000/status",
            "method": "GET"
        },
        {
            "name": "LLM Providers",
            "url": "http://localhost:8000/api/llm/providers",
            "method": "GET"
        },
        {
            "name": "Tools",
            "url": "http://localhost:8000/tools",
            "method": "GET"
        }
    ]
    
    results = {}
    
    for endpoint in api_endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"], timeout=5)
            else:
                continue  # Skip other methods for now
            
            results[endpoint["name"]] = {
                "status": response.status_code == 200,
                "status_code": response.status_code,
                "message": f"API returned status code {response.status_code}"
            }
            
            # Add additional info for some endpoints
            if endpoint["name"] == "LLM Providers" and response.status_code == 200:
                try:
                    providers = response.json()
                    provider_names = [provider.get("name") for provider in providers]
                    results[endpoint["name"]]["providers"] = provider_names
                except:
                    pass
            
            if endpoint["name"] == "Tools" and response.status_code == 200:
                try:
                    tools = response.json().get("tools", [])
                    tool_names = [tool.get("name") for tool in tools]
                    results[endpoint["name"]]["tools"] = tool_names
                except:
                    pass
            
        except requests.exceptions.ConnectionError:
            results[endpoint["name"]] = {
                "status": False,
                "message": "Could not connect to API endpoint"
            }
        except Exception as e:
            results[endpoint["name"]] = {
                "status": False,
                "message": f"Error checking API endpoint: {str(e)}"
            }
    
    return results

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"{title:^80}")
    print("="*80)

def print_result(label, status, message, indent=0):
    """Print a formatted result line"""
    status_text = "✅ SUCCESS" if status else "❌ FAILED"
    indent_text = " " * indent
    print(f"{indent_text}{status_text} | {label}: {message}")

def main():
    """Main function"""
    print_header("GenAI Agent 3D - System Status Check")
    
    # Check running services
    print_header("Service Status")
    services = check_running_services()
    all_services_running = True
    
    for service_name, service_info in services.items():
        print_result(f"{service_name.capitalize()} Service", service_info["status"], service_info["message"])
        if not service_info["status"]:
            all_services_running = False
    
    # Check system status
    print_header("System Status")
    system_status = check_system_status()
    
    if "message" in system_status:
        print_result("System Status", system_status["online"], system_status["message"])
    else:
        print_result("System Status", system_status["online"], "System is online" if system_status["online"] else "System is offline")
        
        if "data" in system_status and "agent" in system_status["data"]:
            agent_data = system_status["data"]["agent"]
            print_result("Agent Status", agent_data.get("initialized", False), 
                      f"Agent initialized with {agent_data.get('tools', 0)} tools", indent=2)
        
        if "data" in system_status and "redis" in system_status["data"]:
            redis_data = system_status["data"]["redis"]
            print_result("Redis Status", redis_data.get("status") == "ok", 
                      redis_data.get("message", "No message"), indent=2)
    
    # Check LLM configuration
    print_header("LLM Configuration")
    llm_config = check_llm_configuration()
    
    print_result("Config File", llm_config["config_file"]["status"], llm_config["config_file"]["message"])
    if llm_config["config_file"]["status"]:
        print_result("Provider", bool(llm_config["config_file"]["provider"]), 
                  f"Provider: {llm_config['config_file']['provider']}", indent=2)
        print_result("Model", bool(llm_config["config_file"]["model"]), 
                  f"Model: {llm_config['config_file']['model']}", indent=2)
        print_result("API Key", llm_config["config_file"]["has_api_key"], 
                  "API key is set" if llm_config["config_file"]["has_api_key"] else "API key is missing", indent=2)
    
    print_result("Env File", llm_config["env_file"]["status"], llm_config["env_file"]["message"])
    if llm_config["env_file"]["status"]:
        print_result("Provider", bool(llm_config["env_file"]["provider"]), 
                  f"Provider: {llm_config['env_file']['provider']}", indent=2)
        print_result("Model", bool(llm_config["env_file"]["model"]), 
                  f"Model: {llm_config['env_file']['model']}", indent=2)
        print_result("API Key", llm_config["env_file"]["has_api_key"], 
                  "API key is set" if llm_config["env_file"]["has_api_key"] else "API key is missing", indent=2)
    
    # Check API routes
    print_header("API Routes")
    api_routes = check_api_routes()
    
    for endpoint_name, endpoint_info in api_routes.items():
        print_result(endpoint_name, endpoint_info["status"], endpoint_info["message"])
        
        # Print additional info for some endpoints
        if "providers" in endpoint_info:
            print(f"    Available Providers: {', '.join(endpoint_info['providers'])}")
        
        if "tools" in endpoint_info:
            print(f"    Available Tools: {', '.join(endpoint_info['tools'])}")
    
    # Test LLM generation only if all services are running
    if all_services_running and system_status["online"]:
        print_header("LLM Generation Test")
        generation_test = test_llm_generation()
        
        print_result("LLM Generation", generation_test["success"], generation_test["message"])
        if generation_test["success"] and "text" in generation_test:
            print("\nSample Generated Text:")
            print(f"    \"{generation_test['text']}\"")
    
    # Print summary
    print_header("Summary")
    
    all_checks_passed = (
        all_services_running and 
        system_status["online"] and
        llm_config["config_file"]["status"] and
        llm_config["config_file"]["has_api_key"]
    )
    
    if all_checks_passed:
        print("✅ All system checks PASSED! The GenAI Agent 3D system is running correctly.")
    else:
        print("⚠️ Some system checks FAILED. Please review the issues above.")
        
        # Provide tips based on failed checks
        print("\nTroubleshooting Tips:")
        
        if not all_services_running:
            print("  • Make sure all services are running:")
            print("    - Run 'python restart_services.py' to restart all services")
            print("    - Or use 'cd genai_agent_project && python manage_services.py restart all'")
        
        if not system_status["online"]:
            print("  • System is showing as offline:")
            print("    - Check Redis connection issues - verify Redis is running")
            print("    - Check logs for specific error messages")
        
        if not llm_config["config_file"]["has_api_key"]:
            print("  • Missing API key:")
            print("    - Run 'python manage_api_keys.py' to set your API keys")
            print("    - Make sure to set the correct API key for your chosen provider")
        
        if "generation_test" in locals() and not generation_test["success"]:
            print("  • LLM generation failed:")
            print(f"    - Error: {generation_test.get('message', 'Unknown error')}")
            print("    - Check if your API key is valid and has sufficient credits")
            print("    - Verify internet connection if using a cloud provider")

if __name__ == "__main__":
    main()
