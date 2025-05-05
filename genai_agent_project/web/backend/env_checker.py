"""
Environment Variable Checker for GenAI Agent 3D

This script checks if Anthropic API key is properly set in the environment.
"""

import os
import sys
import logging
import traceback
import dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def find_env_file():
    """Find the .env file"""
    # Start with current directory
    current_dir = Path.cwd()
    
    # Check current directory
    env_path = current_dir / ".env"
    if env_path.exists():
        return env_path
    
    # Check parent directory
    parent_dir = current_dir.parent
    env_path = parent_dir / ".env"
    if env_path.exists():
        return env_path
    
    # Check grandparent directory
    grandparent_dir = parent_dir.parent
    env_path = grandparent_dir / ".env"
    if env_path.exists():
        return env_path
    
    return None

def load_env_variables():
    """Load environment variables from .env file"""
    # Try to find .env file
    env_path = find_env_file()
    
    if env_path:
        logger.info(f"Found .env file at: {env_path}")
        # Load .env file
        dotenv.load_dotenv(env_path)
        return True
    else:
        logger.warning("No .env file found")
        return False

def check_api_keys():
    """Check if required API keys are available in environment"""
    # Check Anthropic API key
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        logger.info(f"Anthropic API key is set: {anthropic_api_key[:8]}...")
    else:
        logger.error("Anthropic API key is not set")
        
    # Check other API keys if needed
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        logger.info(f"OpenAI API key is set: {openai_api_key[:8]}...")
    else:
        logger.warning("OpenAI API key is not set")
    
    # Return True if Anthropic API key is set
    return bool(anthropic_api_key)

def setup_env_variables():
    """Set up environment variables from parent directory .env file"""
    # Look for .env file in parent directories
    if not load_env_variables():
        logger.warning("Could not load environment variables from .env file")
        
        # Try parent .env
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        
        if env_path.exists():
            logger.info(f"Found .env file at project root: {env_path}")
            dotenv.load_dotenv(env_path)
            logger.info("Loaded environment variables from project root .env file")
        else:
            logger.warning(f"No .env file found at project root: {env_path}")
    
    # Copy ANTHROPIC_API_KEY from parent if not set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        # Look in config.yaml
        try:
            import yaml
            
            config_path = Path(__file__).parent.parent / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Check if API key is in config
                if 'llm' in config and 'api_key' in config['llm'] and config['llm']['api_key']:
                    api_key = config['llm']['api_key']
                    os.environ["ANTHROPIC_API_KEY"] = api_key
                    logger.info(f"Set ANTHROPIC_API_KEY from config.yaml: {api_key[:8]}...")
                    return True
        except Exception as e:
            logger.error(f"Error reading config.yaml: {str(e)}")
    
    return check_api_keys()

if __name__ == "__main__":
    try:
        logger.info("Checking environment variables...")
        
        if setup_env_variables():
            logger.info("Environment variables are properly set")
            sys.exit(0)
        else:
            logger.error("Environment variables are not properly set")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error checking environment variables: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
