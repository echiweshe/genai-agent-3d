#!/usr/bin/env python3
"""
Script to run everything: cleanup, start Ollama, and run all tests
"""

import os
import sys
import subprocess
import logging
import time
import asyncio
from env_loader import get_env, get_config


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
        process = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run {script_name}: {e}")
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
    """Main function to run all scripts"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    scripts_to_run = [
        # Step 1: Clean up
        {"name": "Cleanup Script", "path": os.path.join(project_root, "cleanup.py")},
        
        # Step 2: Start Ollama (handled via function, not script)
        
        # Step 3: Run tests
        {"name": "Integration Tests", "path": os.path.join(project_root, "test_integration.py")},
        {"name": "JSON Generation Test", "path": os.path.join(project_root, "examples", "test_json_generation.py")},
        {"name": "Improved Scene Test", "path": os.path.join(project_root, "examples", "improved_scene_test.py")}
    ]
    
    # Step 1: Run cleanup script
    logger.info("=== Step 1: Running Cleanup Script ===")
    cleanup_success = run_script(scripts_to_run[0]["path"])
    
    if not cleanup_success:
        logger.warning("Cleanup had issues, but continuing with tests")
    
    # Step 2: Start Ollama server
    logger.info("=== Step 2: Starting Ollama Server ===")
    ollama_success = start_ollama()
    
    if not ollama_success:
        logger.warning("Failed to ensure Ollama is running. Tests might fail.")
    
    # Step 3-5: Run all test scripts
    results = {}
    for i in range(1, len(scripts_to_run)):
        script = scripts_to_run[i]
        logger.info(f"=== Step {i+2}: Running {script['name']} ===")
        script_success = run_script(script["path"])
        results[script["name"]] = script_success
        
        # Give Redis time to clean up between tests
        time.sleep(1)
    
    # Report results
    logger.info("\n=== Test Results Summary ===")
    all_passed = True
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All tests completed successfully!")
        logger.info("\nYou can now run the interactive shell with: python run.py shell")
        return 0
    else:
        logger.warning("\n⚠️ Some tests had issues, but the system should still work with fallback mechanisms.")
        logger.info("\nYou can still run the interactive shell with: python run.py shell")
        return 1

if __name__ == "__main__":
    sys.exit(main())
