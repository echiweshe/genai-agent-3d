#!/usr/bin/env python
"""
Script to run the LLM Worker for the GenAI Agent 3D project.
This script launches the LLM Redis Worker which processes LLM requests.
"""

import os
import sys
import asyncio
import logging
import signal
import time

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Import the LLM Redis Worker
from genai_agent.services.llm_redis_worker import LLMRedisWorker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def run_worker(redis_url="redis://localhost:6379"):
    """Run the LLM Redis Worker"""
    worker = LLMRedisWorker(redis_url=redis_url)
    
    try:
        logger.info("Starting LLM Redis Worker...")
        await worker.start()
        
        # Keep running until interrupted
        stop_event = asyncio.Event()
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down worker...")
            stop_event.set()
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, signal_handler)
        
        # Wait for stop event
        await stop_event.wait()
    
    except Exception as e:
        logger.error(f"Error running LLM Redis Worker: {e}")
    
    finally:
        logger.info("Stopping LLM Redis Worker...")
        await worker.stop()
        logger.info("LLM Redis Worker stopped")

def main():
    """Main entry point"""
    try:
        # Get Redis URL from environment or use default
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        
        logger.info(f"Starting LLM Redis Worker with Redis URL: {redis_url}")
        
        # Run the worker
        asyncio.run(run_worker(redis_url))
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting...")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
