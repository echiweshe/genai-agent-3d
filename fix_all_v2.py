
import os
import sys
import argparse
import logging
import subprocess
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Print banner
    print("=" * 80)
    print("           Fix All Issues for GenAI Agent 3D (Version 2)")
    print("=" * 80)
    print("\nThis script will apply all necessary fixes to the GenAI Agent 3D project.")
    print("It will add environment loader, LLM settings API, and configure API keys.")
    
    # Confirm before proceeding
    proceed = input("\nProceed with fixes? (y/n): ").lower() == 'y'
    if not proceed:
        print("Operation cancelled by user.")
        return 1
    
    # Apply fixes
    success = apply_all_fixes()
    
    if success:
        print("\n✅ All fixes applied successfully!")
        print("\nTo apply the changes, restart the services:")
        print("python genai_agent_project/manage_services.py restart all")
        
        # Ask if user wants to restart services
        restart = input("\nWould you like to restart services now? (y/n): ").lower() == 'y'
        if restart:
            try:
                subprocess.run([sys.executable, "genai_agent_project/manage_services.py", "restart", "all"], check=True)
                print("\n✅ Services restarted successfully!")
            except Exception as e:
                print(f"\n❌ Failed to restart services: {str(e)}")
                print("Please restart services manually.")
        
        print("\nDone! GenAI Agent 3D should now work correctly with all AI providers.")
        return 0
    else:
        print("\n❌ Some fixes failed to apply.")
        print("Please check the error messages above and try again.")
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
