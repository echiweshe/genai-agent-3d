#!/usr/bin/env python
"""
Run Diagnostics for GenAI Agent 3D

This script performs diagnostics to help identify issues with the GenAI Agent 3D project:
1. Checks configuration
2. Checks Redis connection
3. Checks Ollama connection and models
4. Checks directory structure
5. Tests LLM with a simple prompt
"""

import os
import yaml
import time
import json
import logging
import subprocess
import platform
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("diagnostics")

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis library not installed. Install with: pip install redis")
    REDIS_AVAILABLE = False

def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    dependencies = {
        "yaml": "PyYAML",
        "redis": "redis",
        "aioredis": "aioredis",
        "colorama": "colorama",
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            logger.info(f"✅ {package} installed")
        except ImportError:
            logger.warning(f"❌ {package} not installed")
            missing.append(package)
    
    if missing:
        logger.warning("Missing dependencies. Install with: pip install " + " ".join(missing))
    else:
        logger.info("All dependencies installed")
    
    return len(missing) == 0

def check_config():
    """Check configuration settings"""
    logger.info("Checking configuration...")
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    if not os.path.exists(config_path):
        logger.error(f"❌ Config file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check LLM settings
        if 'llm' in config:
            logger.info(f"LLM provider: {config['llm'].get('provider', 'not set')}")
            logger.info(f"LLM model: {config['llm'].get('model', 'not set')}")
            logger.info(f"LLM timeout: {config['llm'].get('timeout', 'not set')}")
        else:
            logger.warning("❌ No LLM configuration found")
        
        # Check Redis settings
        if 'redis' in config:
            logger.info(f"Redis host: {config['redis'].get('host', 'not set')}")
            logger.info(f"Redis port: {config['redis'].get('port', 'not set')}")
        else:
            logger.warning("❌ No Redis configuration found")
        
        # Check integration paths
        if 'integrations' in config:
            for name, settings in config['integrations'].items():
                if isinstance(settings, dict) and 'path' in settings:
                    path = settings['path']
                    exists = os.path.exists(path)
                    logger.info(f"Integration {name}: {path} {'✅' if exists else '❌'}")
        else:
            logger.warning("❌ No integrations configuration found")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error reading config: {e}")
        return False

def check_redis():
    """Check Redis connection"""
    logger.info("Checking Redis connection...")
    
    if not REDIS_AVAILABLE:
        logger.warning("❌ Redis library not installed")
        return False
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        redis_config = config.get('redis', {})
        host = redis_config.get('host', 'localhost')
        port = redis_config.get('port', 6379)
        
        logger.info(f"Connecting to Redis at {host}:{port}")
        
        r = redis.Redis(host=host, port=port)
        ping_result = r.ping()
        
        if ping_result:
            logger.info("✅ Redis connection successful")
            
            # Try to publish a message
            channel = "test:diagnostics"
            message = "Diagnostic test message"
            result = r.publish(channel, message)
            logger.info(f"Published message to {channel}, received by {result} clients")
            
            return True
        else:
            logger.warning("❌ Redis ping failed")
            return False
    
    except Exception as e:
        logger.error(f"❌ Redis connection error: {e}")
        return False

def check_ollama():
    """Check Ollama connection and models"""
    logger.info("Checking Ollama...")
    
    try:
        # Check if ollama is in PATH
        ollama_path = None
        if platform.system() == "Windows":
            result = subprocess.run(["where", "ollama"], capture_output=True, text=True)
            if result.returncode == 0:
                ollama_path = result.stdout.strip()
        else:
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            if result.returncode == 0:
                ollama_path = result.stdout.strip()
        
        if ollama_path:
            logger.info(f"✅ Ollama found at: {ollama_path}")
        else:
            logger.warning("❌ Ollama not found in PATH")
        
        # Check available models
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Ollama connection successful")
            logger.info(f"Available models:\n{result.stdout}")
            
            # Check if llama3 is available
            if "llama3" in result.stdout:
                logger.info("✅ llama3 model available")
            else:
                logger.warning("❌ llama3 model not found")
                logger.info("You can pull it with: ollama pull llama3")
            
            return True
        else:
            logger.warning(f"❌ Ollama list failed: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Ollama check error: {e}")
        return False

def check_directories():
    """Check directory structure"""
    logger.info("Checking directory structure...")
    
    required_dirs = [
        "output",
        "output/scenes",
        "output/models",
        "output/diagrams",
        "output/svg",
        "examples",
        "genai_agent",
    ]
    
    for dir_path in required_dirs:
        full_path = os.path.join(os.path.dirname(__file__), dir_path)
        if os.path.exists(full_path) and os.path.isdir(full_path):
            logger.info(f"✅ Directory exists: {dir_path}")
        else:
            logger.warning(f"❌ Directory missing: {dir_path}")
            
            # Create the directory
            try:
                os.makedirs(full_path, exist_ok=True)
                logger.info(f"  Created directory: {full_path}")
            except Exception as e:
                logger.error(f"  Failed to create directory: {e}")
    
    return True

async def test_llm():
    """Test LLM with a simple prompt"""
    logger.info("Testing LLM...")
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        llm_config = config.get('llm', {})
        provider = llm_config.get('provider', 'ollama')
        model = llm_config.get('model', 'llama3')
        
        logger.info(f"Using {provider} provider with model {model}")
        
        if provider == 'ollama':
            # Use a simple prompt
            prompt = "Return a JSON array with three colors. Just return the JSON, no explanations."
            
            # Use subprocess to call ollama
            cmd = ["ollama", "run", model, prompt]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info("✅ LLM test successful")
                    logger.info(f"Response:\n{result.stdout}")
                    
                    # Check if it's valid JSON
                    try:
                        json_start = result.stdout.find("[")
                        json_end = result.stdout.rfind("]") + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            json_str = result.stdout[json_start:json_end]
                            json_data = json.loads(json_str)
                            logger.info(f"✅ Valid JSON response: {json_data}")
                        else:
                            logger.warning("❌ No valid JSON found in response")
                    
                    except json.JSONDecodeError:
                        logger.warning("❌ Invalid JSON in response")
                    
                    return True
                else:
                    logger.warning(f"❌ LLM test failed: {result.stderr}")
                    return False
            
            except subprocess.TimeoutExpired:
                logger.warning("❌ LLM test timed out after 30 seconds")
                return False
        
        else:
            logger.warning(f"❌ Provider {provider} not supported for direct testing")
            return False
    
    except Exception as e:
        logger.error(f"❌ LLM test error: {e}")
        return False

def main():
    """Main function"""
    logger.info("🔍 Running diagnostics for GenAI Agent 3D...")
    
    # Check dependencies
    check_dependencies()
    
    # Check configuration
    check_config()
    
    # Check directories
    check_directories()
    
    # Check Redis
    redis_ok = check_redis()
    
    # Check Ollama
    ollama_ok = check_ollama()
    
    # Test LLM
    if ollama_ok:
        asyncio.run(test_llm())
    
    logger.info("""
Diagnostics complete!

Next steps:
1. Address any warnings or errors shown above
2. Run a specific example: python run.py examples test_json_generation
3. Run all examples: python 00_run_all_examples.py
""")

if __name__ == "__main__":
    main()
