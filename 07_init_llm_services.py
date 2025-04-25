#!/usr/bin/env python
"""
Initialize LLM Services for GenAI Agent 3D

This script initializes and tests the LLM services required for the GenAI Agent 3D
platform. It checks Ollama availability, tests model access, and sets up the 
necessary configuration.
"""

import os
import sys
import requests
import time
import yaml
import json
import subprocess

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
config_dir = os.path.join(project_dir, "config")

print("=" * 80)
print("GenAI Agent 3D - LLM Services Initializer".center(80))
print("=" * 80)
print()

# Create config directory if it doesn't exist
os.makedirs(config_dir, exist_ok=True)

# Step 1: Check if Ollama is installed and running
print("Step 1: Checking Ollama installation and status...")

ollama_url = "http://127.0.0.1:11434"
ollama_running = False

try:
    response = requests.get(f"{ollama_url}/api/version", timeout=5)
    if response.status_code == 200:
        ollama_data = response.json()
        print(f"✅ Ollama is running: {ollama_data.get('version', 'unknown version')}")
        ollama_running = True
    else:
        print(f"❌ Ollama API returned status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ Could not connect to Ollama: {e}")

if not ollama_running:
    print("\nOllama is not running. Attempting to start it...")
    
    # Try to start Ollama (platform-specific)
    try:
        if sys.platform == "win32":
            # Windows - try to start Ollama from Program Files
            ollama_paths = [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Ollama", "ollama.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Ollama", "ollama.exe"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama", "ollama.exe"),
            ]
            
            for path in ollama_paths:
                if os.path.exists(path):
                    print(f"Found Ollama at: {path}")
                    try:
                        subprocess.Popen([path, "serve"], 
                                        creationflags=subprocess.CREATE_NO_WINDOW,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                        print("✅ Started Ollama in the background")
                        # Wait for Ollama to start
                        time.sleep(5)
                        ollama_running = True
                        break
                    except Exception as e:
                        print(f"❌ Failed to start Ollama: {e}")
            
            if not ollama_running:
                print("❌ Could not find Ollama executable")
        else:
            # Linux/Mac - try to use ollama command
            try:
                subprocess.Popen(["ollama", "serve"], 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                print("✅ Started Ollama in the background")
                # Wait for Ollama to start
                time.sleep(5)
                ollama_running = True
            except Exception as e:
                print(f"❌ Failed to start Ollama: {e}")
    except Exception as e:
        print(f"❌ Error attempting to start Ollama: {e}")

# Verify Ollama is now running
if not ollama_running:
    try:
        response = requests.get(f"{ollama_url}/api/version", timeout=5)
        if response.status_code == 200:
            ollama_data = response.json()
            print(f"✅ Ollama is now running: {ollama_data.get('version', 'unknown version')}")
            ollama_running = True
    except:
        pass

if not ollama_running:
    print("\n⚠️ Ollama is not running. You'll need to install and start it manually:")
    print("1. Download Ollama from https://ollama.ai/")
    print("2. Install and start Ollama")
    print("3. Run this script again")
    
    proceed = input("\nDo you want to proceed anyway? (y/n): ")
    if proceed.lower() != 'y':
        sys.exit(1)

print()

# Step 2: Check available models
print("Step 2: Checking available models...")

available_models = []
model_to_use = "llama3.2:latest"  # Default model
models_found = False

if ollama_running:
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            
            # Handle different API versions
            if "models" in models_data:
                # Newer Ollama API (0.5.0+)
                models = models_data["models"]
                available_models = [model["name"] for model in models]
            else:
                # Older Ollama API
                available_models = [model["name"] for model in models_data.get("models", [])]
            
            if available_models:
                print(f"✅ Found {len(available_models)} installed models:")
                for model in available_models:
                    print(f"  - {model}")
                models_found = True
            else:
                print("❌ No models found in Ollama")
        else:
            print(f"❌ Failed to get models: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking models: {e}")

# Step 3: Pull a model if none found
if ollama_running and not models_found:
    print("\nNo models found. Pulling a default model...")
    
    recommended_models = [
        {"name": "llama3.2:latest", "desc": "Meta's Llama 3.2 (8B) - Recommended"},
        {"name": "llama3:latest", "desc": "Meta's Llama 3 (8B) - Alternative"},
        {"name": "phi3:latest", "desc": "Microsoft's Phi-3 (3.8B) - Lightweight"}
    ]
    
    print("Recommended models:")
    for i, model in enumerate(recommended_models):
        print(f"{i+1}. {model['desc']}")
    
    choice = input("\nSelect a model to pull (1-3) or enter another model name [1]: ")
    
    if not choice:
        choice = "1"
    
    if choice.isdigit() and 1 <= int(choice) <= len(recommended_models):
        model_to_use = recommended_models[int(choice)-1]["name"]
    else:
        model_to_use = choice
    
    print(f"Pulling model: {model_to_use}")
    print("This may take several minutes depending on your internet connection and the model size...")
    
    try:
        # Use subprocess to display progress
        result = subprocess.run(
            ["ollama", "pull", model_to_use],
            check=True,
            text=True,
            capture_output=True
        )
        print("✅ Model pulled successfully")
        available_models.append(model_to_use)
    except Exception as e:
        print(f"❌ Failed to pull model: {e}")
        print("You can pull a model manually with: ollama pull llama3.2:latest")

print()

# Step 4: Create LLM configuration
print("Step 4: Creating LLM configuration...")

llm_config_path = os.path.join(config_dir, "llm.yaml")

# Default configuration
llm_config = {
    "type": "local",
    "provider": "ollama",
    "model": model_to_use if model_to_use in available_models else "llama3.2:latest",
    "parameters": {
        "temperature": 0.7,
        "max_tokens": 2048
    },
    "providers": {
        "ollama": {
            "base_url": ollama_url
        }
    }
}

# Save configuration
with open(llm_config_path, "w") as f:
    yaml.dump(llm_config, f, default_flow_style=False)

print(f"✅ Created LLM configuration at: {llm_config_path}")
print(f"   Provider: {llm_config['provider']}")
print(f"   Model: {llm_config['model']}")

print()

# Step 5: Test the model
print("Step 5: Testing LLM with a simple prompt...")

if ollama_running and available_models:
    test_model = llm_config["model"]
    test_prompt = "Write a brief description of what a 3D modeling agent could do."
    
    print(f"Testing model: {test_model}")
    print(f"Prompt: \"{test_prompt}\"")
    print("Generating response...")
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": test_model,
                "prompt": test_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 200  # Limit response size for quick test
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            
            print("\nResponse from model:")
            print("-" * 40)
            print(generated_text.strip())
            print("-" * 40)
            print("✅ Model test successful!")
        else:
            print(f"❌ Model test failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing model: {e}")
else:
    print("⚠️ Skipping model test as no models are available")

print()
print("=" * 80)
print("LLM Services Initialization Complete!".center(80))
print("=" * 80)
print()
print("Next Steps:")
print("1. Run the final fixes: python 08_final_fixes.py")
print("2. Start the application: python genai_agent_project/manage_services.py restart all")
print("3. Access the web interface at: http://localhost:3000")
print()
print("For more information, see the documentation in the docs/ directory.")
