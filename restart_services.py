#!/usr/bin/env python3
"""
Restart GenAI Agent 3D Services

This script provides a user-friendly way to restart the GenAI Agent 3D services
with improved logging and error handling.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("restart_services.log")
    ]
)
logger = logging.getLogger(__name__)

def restart_services():
    """Restart all GenAI Agent 3D services"""
    try:
        # Change to the project root directory
        project_root = Path(__file__).parent.absolute()
        os.chdir(project_root)
        
        manage_services_path = project_root / "genai_agent_project" / "manage_services.py"
        
        if not manage_services_path.exists():
            logger.error(f"Could not find manage_services.py at {manage_services_path}")
            return False
        
        # Stop all services first
        logger.info("Stopping all services...")
        subprocess.run(
            [sys.executable, str(manage_services_path), "stop", "all"],
            check=True
        )
        
        # Give some time for services to shut down
        time.sleep(3)
        
        # Start all services
        logger.info("Starting all services...")
        subprocess.run(
            [sys.executable, str(manage_services_path), "start", "all"],
            check=True
        )
        
        logger.info("All services restarted successfully!")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("           Restart GenAI Agent 3D Services")
    print("=" * 80)
    print("\nThis script will restart all GenAI Agent 3D services.")
    print("This includes: Redis, Ollama, Backend, and Frontend services.")
    
    proceed = input("\nProceed with restart? (y/n): ").lower() == 'y'
    if not proceed:
        print("Operation cancelled.")
        return 0
    
    print("\nRestarting services (this may take a minute)...")
    success = restart_services()
    
    if success:
        print("\n✅ All services have been restarted successfully!")
        print("You can now access the web interface at: http://localhost:3000")
        
        # Ask if user wants to open the web interface
        open_browser = input("\nOpen web interface in browser? (y/n): ").lower() == 'y'
        if open_browser:
            try:
                import webbrowser
                webbrowser.open("http://localhost:3000")
            except Exception as e:
                print(f"Could not open browser: {e}")
                print("Please open http://localhost:3000 manually in your browser.")
        
        return 0
    else:
        print("\n❌ Failed to restart services. Check the logs for details.")
        print("You can try running the manage_services.py script directly:")
        print("python genai_agent_project/manage_services.py restart all")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
