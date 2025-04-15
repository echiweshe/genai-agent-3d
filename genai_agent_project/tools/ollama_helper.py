#!/usr/bin/env python3
"""
Helper script for managing Ollama integration
"""

import os
import sys
import argparse
import subprocess
import platform
import requests
import time
import json
from pathlib import Path

OLLAMA_WINDOWS_URL = "https://ollama.com/download/ollama-windows-amd64.zip"
OLLAMA_DEFAULT_URL = "http://localhost:11434"
OLLAMA_API_LIST_MODELS = "/api/tags"
OLLAMA_API_PULL_MODEL = "/api/pull"

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["where", "ollama"], capture_output=True, text=True)
            return result.returncode == 0
        else:
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            return result.returncode == 0
    except Exception:
        return False

def check_ollama_running():
    """Check if Ollama server is running"""
    try:
        response = requests.get(f"{OLLAMA_DEFAULT_URL}/api/tags")
        return response.status_code == 200
    except Exception:
        return False

def start_ollama_server():
    """Start Ollama server"""
    try:
        if platform.system() == "Windows":
            # On Windows, start in background
            subprocess.Popen(["ollama", "serve"], 
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # On Linux/Mac, start in background
            subprocess.Popen(["ollama", "serve"], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("Starting Ollama server...", end="")
        for _ in range(30):  # Try for 30 seconds
            if check_ollama_running():
                print(" Ready!")
                return True
            time.sleep(1)
            print(".", end="", flush=True)
        
        print("\nFailed to start Ollama server in time")
        return False
    except Exception as e:
        print(f"\nError starting Ollama server: {str(e)}")
        return False

def list_models():
    """List available models"""
    if not check_ollama_running():
        if not start_ollama_server():
            print("Could not start Ollama server. Please start it manually.")
            return
    
    try:
        response = requests.get(f"{OLLAMA_DEFAULT_URL}{OLLAMA_API_LIST_MODELS}")
        if response.status_code == 200:
            models = response.json().get("models", [])
            if not models:
                print("No models found. Use 'python tools/ollama_helper.py pull llama3' to download a model.")
                return
            
            print("\nInstalled models:")
            for model in models:
                print(f"- {model.get('name'):<15} (Size: {model.get('size')/(1024*1024*1024):.1f} GB)")
        else:
            print(f"Error listing models: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def pull_model(model_name):
    """Pull a model from Ollama library"""
    if not check_ollama_running():
        if not start_ollama_server():
            print("Could not start Ollama server. Please start it manually.")
            return
    
    try:
        print(f"Pulling model {model_name}...")
        response = requests.post(
            f"{OLLAMA_DEFAULT_URL}{OLLAMA_API_PULL_MODEL}",
            json={"name": model_name}
        )
        
        if response.status_code == 200:
            print(f"Successfully pulled model {model_name}")
        else:
            print(f"Error pulling model: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_generate(model_name, prompt):
    """Test generation with a model"""
    if not check_ollama_running():
        if not start_ollama_server():
            print("Could not start Ollama server. Please start it manually.")
            return
    
    try:
        print(f"Testing model {model_name} with prompt: '{prompt}'")
        response = requests.post(
            f"{OLLAMA_DEFAULT_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse:")
            print(result.get("response", "No response"))
        else:
            print(f"Error generating text: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def install_ollama():
    """Install Ollama (Windows only for now)"""
    if platform.system() != "Windows":
        print("Automatic installation only supported on Windows currently.")
        print("For Linux/Mac, please visit: https://ollama.com/download")
        return
    
    try:
        import zipfile
        import tempfile
        
        print("Downloading Ollama...")
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "ollama.zip")
        
        # Download
        response = requests.get(OLLAMA_WINDOWS_URL)
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Install - for Windows, just copy to a location in PATH
        # Assuming user has administrator privileges
        install_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Ollama')
        os.makedirs(install_dir, exist_ok=True)
        
        ollama_exe = os.path.join(temp_dir, "ollama.exe")
        target_path = os.path.join(install_dir, "ollama.exe")
        
        import shutil
        shutil.copy2(ollama_exe, target_path)
        
        # Add to PATH if not already
        path_env = os.environ.get('PATH', '')
        if install_dir not in path_env:
            print(f"Adding {install_dir} to PATH for current session")
            os.environ['PATH'] = f"{install_dir};{path_env}"
            
            # Also suggest permanent PATH addition
            print("\nTo add Ollama to PATH permanently:")
            print(f"1. Add this directory to your PATH: {install_dir}")
            print("2. Or run this in PowerShell as Administrator:")
            print(f'   [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;{install_dir}", "User")')
        
        print("\nOllama installed successfully!")
        
        # Clean up
        try:
            os.remove(zip_path)
        except:
            pass
    except Exception as e:
        print(f"Error installing Ollama: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Ollama Helper')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check Ollama installation and server')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start Ollama server')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available models')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull a model')
    pull_parser.add_argument('model', type=str, help='Model name to pull (e.g., llama3)')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test generation with a model')
    test_parser.add_argument('model', type=str, help='Model name to use')
    test_parser.add_argument('--prompt', type=str, default='Hello, world!', help='Prompt to use')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install Ollama')
    
    args = parser.parse_args()
    
    if not args.command:
        # If no command specified, check status and show help
        installed = check_ollama_installed()
        running = check_ollama_running()
        
        print("Ollama status:")
        print(f"- Installed: {'Yes' if installed else 'No'}")
        print(f"- Server running: {'Yes' if running else 'No'}")
        
        if not installed:
            print("\nOllama is not installed. Use 'python tools/ollama_helper.py install' to install it.")
        elif not running:
            print("\nOllama server is not running. Use 'python tools/ollama_helper.py start' to start it.")
        else:
            list_models()
        
        parser.print_help()
        return
    
    if args.command == 'check':
        installed = check_ollama_installed()
        running = check_ollama_running()
        
        print("Ollama status:")
        print(f"- Installed: {'Yes' if installed else 'No'}")
        print(f"- Server running: {'Yes' if running else 'No'}")
        
        if installed and running:
            list_models()
    
    elif args.command == 'start':
        if not check_ollama_installed():
            print("Ollama is not installed. Please install it first.")
            return
        
        if check_ollama_running():
            print("Ollama server is already running.")
        else:
            start_ollama_server()
    
    elif args.command == 'list':
        list_models()
    
    elif args.command == 'pull':
        pull_model(args.model)
    
    elif args.command == 'test':
        test_generate(args.model, args.prompt)
    
    elif args.command == 'install':
        install_ollama()

if __name__ == "__main__":
    main()
