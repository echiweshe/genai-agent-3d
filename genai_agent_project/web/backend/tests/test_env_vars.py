"""
A simple test to check environment variables are loaded properly
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def check_api_keys():
    """
    Check if API keys are available in environment
    """
    api_keys = {
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "STABILITY_API_KEY": os.environ.get("STABILITY_API_KEY"),
    }
    
    for key, value in api_keys.items():
        if value:
            logger.info(f"{key} is set: {value[:8]}...")
        else:
            logger.warning(f"{key} is not set")
    
    return all(api_keys.values())

if __name__ == "__main__":
    logger.info("Checking environment variables...")
    if check_api_keys():
        logger.info("All API keys are set")
    else:
        logger.warning("Some API keys are missing")
