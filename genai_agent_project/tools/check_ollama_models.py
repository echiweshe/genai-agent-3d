#!/usr/bin/env python3
"""
Script to check available Ollama models and their configurations
"""

import os
import sys
import json
import requests
import subprocess
import argparse
from typing import List, Dict, Any, Optional

def get_ollama_models() -> List[Dict[str, Any]]:
    """
    Get available Ollama models
    
    Returns:
        List of model information dictionaries
    """
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            return response.json().get('models', [])
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []
    except requests.RequestException as e:
        print(f"Connection error: {str(e)}")
        return []

def show_model_details(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Show details for a specific model
    
    Args:
        model_name: Model name
        
    Returns:
        Model details or None if error
    """
    try:
        process = subprocess.run(
            ['ollama', 'show', model_name],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Parse output into a dictionary
        lines = process.stdout.strip().split('\n')
        details = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                details[key.strip()] = value.strip()
        
        return details
    except subprocess.CalledProcessError as e:
        print(f"Error showing model {model_name}: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def pull_model(model_name: str) -> bool:
    """
    Pull a model from Ollama registry
    
    Args:
        model_name: Model name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Pulling model: {model_name}")
        subprocess.run(['ollama', 'pull', model_name], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error pulling model {model_name}: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def list_models_verbose() -> None:
    """List all models with detailed information"""
    models = get_ollama_models()
    
    if not models:
        print("No models found or Ollama server not running")
        return
    
    print(f"Found {len(models)} models:")
    for model in models:
        name = model.get('name', 'unknown')
        size_gb = model.get('size', 0) / (1024 * 1024 * 1024)
        print(f"\n[{name}]")
        print(f"  Size: {size_gb:.2f} GB")
        
        # Get additional details
        details = show_model_details(name)
        if details:
            for key, value in details.items():
                if key != 'name':  # Already printed name
                    print(f"  {key}: {value}")

def find_similar_models(model_name: str) -> List[str]:
    """
    Find models with similar names
    
    Args:
        model_name: Model name to search for
        
    Returns:
        List of similar model names
    """
    models = get_ollama_models()
    similar = []
    
    # Check for exact match first
    if any(m.get('name') == model_name for m in models):
        return [model_name]
    
    # Check for partial matches
    for model in models:
        name = model.get('name', '')
        if model_name.lower() in name.lower() or name.lower() in model_name.lower():
            similar.append(name)
    
    return similar

def check_model(model_name: str) -> None:
    """
    Check if a specific model is available and show details
    
    Args:
        model_name: Model name
    """
    models = get_ollama_models()
    found = False
    
    for model in models:
        if model.get('name') == model_name:
            found = True
            size_gb = model.get('size', 0) / (1024 * 1024 * 1024)
            print(f"Model {model_name} is available (Size: {size_gb:.2f} GB)")
            
            # Show details
            details = show_model_details(model_name)
            if details:
                print("Details:")
                for key, value in details.items():
                    print(f"  {key}: {value}")
            
            break
    
    if not found:
        print(f"Model {model_name} is not available")
        
        # Check for similar models
        similar = find_similar_models(model_name)
        if similar:
            print("Similar models found:")
            for name in similar:
                print(f"  - {name}")
            
            print("\nYou might want to use one of these similar models instead.")
            print("Or pull the model with: ollama pull " + model_name)
        else:
            print("No similar models found. You may need to pull it with: ollama pull " + model_name)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Check Ollama models")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available models')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if a specific model is available')
    check_parser.add_argument('model', help='Model name to check')
    
    # Pull command
    pull_parser = subparsers.add_parser('pull', help='Pull a model')
    pull_parser.add_argument('model', help='Model name to pull')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        if args.verbose:
            list_models_verbose()
        else:
            models = get_ollama_models()
            if models:
                print(f"Found {len(models)} models:")
                for model in models:
                    name = model.get('name', 'unknown')
                    size_gb = model.get('size', 0) / (1024 * 1024 * 1024)
                    print(f"- {name} (Size: {size_gb:.2f} GB)")
            else:
                print("No models found or Ollama server not running")
    
    elif args.command == 'check':
        check_model(args.model)
    
    elif args.command == 'pull':
        pull_model(args.model)
    
    else:
        # Default to list if no command specified
        models = get_ollama_models()
        if models:
            print(f"Found {len(models)} models:")
            for model in models:
                name = model.get('name', 'unknown')
                size_gb = model.get('size', 0) / (1024 * 1024 * 1024)
                print(f"- {name} (Size: {size_gb:.2f} GB)")
        else:
            print("No models found or Ollama server not running")

if __name__ == "__main__":
    main()
