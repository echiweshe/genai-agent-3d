"""
Quick fix script to restart the backend after making changes.
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def restart_backend():
    """Restart the backend service."""
    logger.info("Restarting backend service...")
    
    # Path to the manage_services.py script
    manage_services = os.path.join("genai_agent_project", "manage_services.py")
    
    if not os.path.exists(manage_services):
        logger.error(f"manage_services.py script not found: {manage_services}")
        return False
    
    try:
        subprocess.run([sys.executable, manage_services, "restart", "backend"], check=True)
        logger.info("Backend service restarted successfully")
        return True
    except Exception as e:
        logger.error(f"Error restarting backend service: {str(e)}")
        return False

if __name__ == "__main__":
    restart_backend()
