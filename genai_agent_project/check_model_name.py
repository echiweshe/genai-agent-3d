"""
Script to check the exact name of available Ollama models
"""

import subprocess
import sys
import json

def main():
    print("Checking Ollama installation and models...")
    
    # Run ollama list command
    try:
        print("Running 'ollama list' command...")
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        print("\nOllama List Output:")
        print(result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
    except Exception as e:
        print(f"Error running ollama list: {str(e)}")
    
    # Try API approach
    try:
        import requests
        print("\nQuerying Ollama API...")
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            if not models:
                print("No models found through API.")
            else:
                print(f"Found {len(models)} models:")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0) / (1024 * 1024 * 1024)  # Convert to GB
                    print(f"- {name} (Size: {size:.2f} GB)")
        else:
            print(f"API error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error querying API: {str(e)}")
    
    print("\nCheckung for deepseek-coder specifically...")
    try:
        result = subprocess.run(['ollama', 'show', 'deepseek-coder'], capture_output=True, text=True)
        print("Ollama Show Output:")
        print(result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
    except Exception as e:
        print(f"Error running ollama show: {str(e)}")

if __name__ == "__main__":
    main()
