"""
Ollama Helper for managing Ollama models
"""

import os
import sys
import logging
import subprocess
import time
import platform
import requests
from typing import List, Dict, Any, Optional

import psutil  # <-- Add this at the top if not already imported

logger = logging.getLogger(__name__)

@staticmethod
def start_ollama() -> bool:
    """
    Start Ollama server

    Returns:
        True if started successfully, False otherwise
    """
    logger.info("Starting Ollama server...")

    if OllamaHelper.is_ollama_running():
        logger.info("Ollama is already running")
        return True

    # 🔍 Kill any hanging Ollama processes (defensive cleanup)
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name']
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if 'ollama' in name.lower() or 'ollama' in cmdline.lower():
                logger.warning(f"Killing hanging Ollama process: PID={proc.info['pid']} Name={name}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Get OS-specific command
    system = platform.system()

    try:
        if system == 'Windows':
            subprocess.Popen(
                ['start', '/b', 'ollama', 'serve'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace'
            )
        elif system in ['Darwin', 'Linux']:
            subprocess.Popen(
                ['nohup', 'ollama', 'serve', '&'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setpgrp
            )

        # Wait for server to start
        for i in range(10):
            time.sleep(2)
            if OllamaHelper.is_ollama_running():
                logger.info("Ollama server started successfully")
                return True
            logger.info(f"Waiting for Ollama server to start (attempt {i+1}/10)...")

        logger.error("Failed to start Ollama server after multiple attempts")
        return False
    except Exception as e:
        logger.error(f"Error starting Ollama server: {str(e)}")
        return False


class OllamaHelper:
    """
    Helper for managing Ollama models
    """
    
    @staticmethod
    def is_ollama_running() -> bool:
        """
        Check if Ollama server is running
        
        Returns:
            True if running, False otherwise
        """
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    @staticmethod
    def start_ollama() -> bool:
        """
        Start Ollama server
        
        Returns:
            True if started successfully, False otherwise
        """
        logger.info("Starting Ollama server...")
        
        # Get OS-specific command
        system = platform.system()
        
        try:
            if system == 'Windows':
                # Use start command to run in background
                subprocess.Popen(
                    ['start', '/b', 'ollama', 'serve'],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8',        # <-- FIX added
                    errors='replace'         # <-- FIX added
                )
            elif system == 'Darwin' or system == 'Linux':
                # Use nohup to run in background
                subprocess.Popen(
                    ['nohup', 'ollama', 'serve', '&'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setpgrp
                )
            
            # Wait for server to start
            max_attempts = 10
            for i in range(max_attempts):
                time.sleep(2)  # Wait 2 seconds
                if OllamaHelper.is_ollama_running():
                    logger.info("Ollama server started successfully")
                    return True
                logger.info(f"Waiting for Ollama server to start (attempt {i+1}/{max_attempts})...")
            
            logger.error("Failed to start Ollama server after multiple attempts")
            return False
        except Exception as e:
            logger.error(f"Error starting Ollama server: {str(e)}")
            return False
    
    @staticmethod
    def stop_ollama() -> bool:
        """
        Stop Ollama server
        
        Returns:
            True if stopped successfully, False otherwise
        """
        logger.info("Stopping Ollama server...")
        
        system = platform.system()
        
        try:
            if system == 'Windows':
                # Find and kill the Ollama process
                subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], 
                              check=False, capture_output=True)
            elif system == 'Darwin' or system == 'Linux':
                # Use pkill to kill the Ollama process
                subprocess.run(['pkill', '-f', 'ollama serve'], 
                              check=False, capture_output=True)
            
            # Verify it's stopped
            if not OllamaHelper.is_ollama_running():
                logger.info("Ollama server stopped successfully")
                return True
            
            logger.error("Failed to stop Ollama server")
            return False
        except Exception as e:
            logger.error(f"Error stopping Ollama server: {str(e)}")
            return False
    
    @staticmethod
    def list_models() -> List[Dict[str, Any]]:
        """
        List available Ollama models
        
        Returns:
            List of model information
        """
        if not OllamaHelper.is_ollama_running():
            logger.warning("Ollama server is not running")
            return []
        
        try:
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                return response.json().get('models', [])
            else:
                logger.error(f"Error listing models: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    @staticmethod
    def pull_model(model_name: str) -> bool:
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Model name
            
        Returns:
            True if pulled successfully, False otherwise
        """
        if not OllamaHelper.is_ollama_running():
            logger.warning("Ollama server is not running")
            if not OllamaHelper.start_ollama():
                return False
        
        logger.info(f"Pulling Ollama model: {model_name}")
        
        try:
            process = subprocess.run(
                ['ollama', 'pull', model_name],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'  # <-- FIX added
            )

            
            # Check output for success
            if "pulling manifest" in process.stdout.lower() or "pulling" in process.stdout.lower():
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            else:
                logger.warning(f"Unexpected output when pulling model: {process.stdout}")
                return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Error pulling model {model_name}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {str(e)}")
            return False
    
    @staticmethod
    def get_model_details(model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details about a specific model
        
        Args:
            model_name: Model name
            
        Returns:
            Model details or None if not found
        """
        if not OllamaHelper.is_ollama_running():
            logger.warning("Ollama server is not running")
            return None
        
        try:
            # Use the show command to get model details
            process = subprocess.run(
                ['ollama', 'show', model_name],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'  # <-- FIX added
            )
            
            # Parse the output
            lines = process.stdout.strip().split('\n')
            details = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    details[key.strip()] = value.strip()
            
            return details
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting model details for {model_name}: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Error getting model details for {model_name}: {str(e)}")
            return None


def main():
    """Main entry point for command line usage"""
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 2:
        print("Usage: python ollama_helper.py [start|stop|list|pull MODEL_NAME|details MODEL_NAME]")
        return
    
    command = sys.argv[1]
    
    if command == "start":
        success = OllamaHelper.start_ollama()
        print(f"Start Ollama: {'Success' if success else 'Failed'}")
    
    elif command == "stop":
        success = OllamaHelper.stop_ollama()
        print(f"Stop Ollama: {'Success' if success else 'Failed'}")
    
    elif command == "list":
        models = OllamaHelper.list_models()
        if models:
            print("Available models:")
            for model in models:
                size_gb = model.get('size', 0) / (1024 * 1024 * 1024)  # Convert to GB
                print(f"- {model.get('name')} (Size: {size_gb:.2f} GB)")
        else:
            print("No models found or Ollama server not running")
    
    elif command == "pull" and len(sys.argv) >= 3:
        model_name = sys.argv[2]
        success = OllamaHelper.pull_model(model_name)
        print(f"Pull model {model_name}: {'Success' if success else 'Failed'}")
    
    elif command == "details" and len(sys.argv) >= 3:
        model_name = sys.argv[2]
        details = OllamaHelper.get_model_details(model_name)
        if details:
            print(f"Details for model {model_name}:")
            for key, value in details.items():
                print(f"- {key}: {value}")
        else:
            print(f"No details found for model {model_name} or Ollama server not running")
    
    else:
        print("Unknown command or missing arguments")
        print("Usage: python ollama_helper.py [start|stop|list|pull MODEL_NAME|details MODEL_NAME]")


if __name__ == "__main__":
    main()
