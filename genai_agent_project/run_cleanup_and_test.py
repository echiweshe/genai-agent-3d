#!/usr/bin/env python3
"""
Script to cleanup project and run integration tests
"""

import os
import sys
import subprocess
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_script(script_name, args=None):
    """Run a Python script and return success status"""
    if args is None:
        args = []
    
    cmd = [sys.executable, script_name] + args
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Output: {process.stdout}")
        if process.stderr:
            logger.warning(f"Errors: {process.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run {script_name}: {e}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Errors: {e.stderr}")
        return False

def start_ollama():
    """Start Ollama server if not already running"""
    logger.info("Checking Ollama server status...")
    
    # Import OllamaHelper
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    try:
        from genai_agent.tools.ollama_helper import OllamaHelper
        if not OllamaHelper.is_ollama_running():
            logger.info("Starting Ollama server...")
            OllamaHelper.start_ollama()
            
            # Wait for Ollama to start
            for _ in range(10):
                if OllamaHelper.is_ollama_running():
                    logger.info("Ollama server started successfully")
                    return True
                logger.info("Waiting for Ollama to start...")
                time.sleep(2)
            
            logger.warning("Failed to start Ollama server in time")
            return False
        else:
            logger.info("Ollama server is already running")
            return True
    except ImportError:
        logger.error("Could not import OllamaHelper")
        return False
    except Exception as e:
        logger.error(f"Error starting Ollama: {str(e)}")
        return False

def main():
    """Main function to run cleanup and tests"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Run cleanup script
    logger.info("Step 1: Running cleanup script")
    cleanup_success = run_script(os.path.join(project_root, "cleanup.py"))
    
    if not cleanup_success:
        logger.warning("Cleanup had issues, but continuing with tests")
    
    # Step 2: Start Ollama server
    logger.info("Step 2: Starting Ollama server")
    ollama_success = start_ollama()
    
    if not ollama_success:
        logger.warning("Failed to ensure Ollama is running. Tests might fail.")
    
    # Step 3: Run integration tests
    logger.info("Step 3: Running integration tests")
    test_success = run_script(os.path.join(project_root, "test_integration.py"))
    
    # Report results
    if test_success:
        logger.info("🎉 All steps completed successfully!")
        return 0
    else:
        logger.error("⚠️ Tests failed. Please check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
