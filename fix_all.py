#!/usr/bin/env python3
"""
Fix All Issues for GenAI Agent 3D

This script applies all the necessary fixes to the GenAI Agent 3D project:
1. Creates enhanced environment loader
2. Patches the main.py file to include LLM settings API
3. Checks and configures API keys
4. Restarts the services if requested

Usage:
    python fix_all.py [--restart]
"""

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

def run_script(script_path):
    """Run a Python script and return its exit code"""
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_path}: {e}")
        return e.returncode
    except Exception as e:
        logger.error(f"Exception running {script_path}: {e}")
        return 1

def restart_services():
    """Restart all services using manage_services.py"""
    try:
        # Get the path to manage_services.py
        manage_services = Path("genai_agent_project/manage_services.py")
        
        if not manage_services.exists():
            logger.error(f"Could not find {manage_services}")
            return False
        
        # Run the script to restart all services
        print("\nRestarting all services...")
        result = subprocess.run(
            [sys.executable, manage_services, "restart", "all"], 
            check=True
        )
        
        if result.returncode == 0:
            print("✅ All services restarted successfully")
            return True
        else:
            print("❌ Failed to restart services")
            return False
    
    except Exception as e:
        logger.error(f"Error restarting services: {e}")
        print(f"❌ Error restarting services: {e}")
        return False

def apply_fixes():
    """Apply all fixes to the project"""
    fixes = [
        {
            "name": "Patching main.py",
            "script": "patch_main.py",
            "description": "Adding LLM settings API to main.py"
        },
        {
            "name": "Setting up API keys",
            "script": "setup_api_keys.py",
            "description": "Configuring API keys for all providers",
            "optional": True
        }
    ]
    
    # Apply fixes
    success_count = 0
    for i, fix in enumerate(fixes, 1):
        print(f"\n[{i}/{len(fixes)}] {fix['name']}")
        print(f"Description: {fix['description']}")
        
        if fix.get("optional", False):
            apply = input("Apply this fix? (y/n): ").lower() == 'y'
            if not apply:
                print(f"Skipping {fix['name']}")
                continue
        
        print(f"Applying {fix['name']}...")
        exit_code = run_script(fix["script"])
        
        if exit_code == 0:
            print(f"✅ {fix['name']} applied successfully")
            success_count += 1
        else:
            print(f"❌ Failed to apply {fix['name']}")
            if not fix.get("optional", False):
                return False
    
    # Return overall success
    return success_count > 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Fix All Issues for GenAI Agent 3D")
    parser.add_argument("--restart", action="store_true", help="Restart services after applying fixes")
    args = parser.parse_args()
    
    # Change to the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Print banner
    print("=" * 80)
    print("           Fix All Issues for GenAI Agent 3D")
    print("=" * 80)
    print("\nThis script will apply all necessary fixes to the GenAI Agent 3D project.")
    print("Make sure all services are stopped before proceeding.")
    
    # Confirm before proceeding
    proceed = input("\nProceed with fixes? (y/n): ").lower() == 'y'
    if not proceed:
        print("Operation cancelled by user.")
        return 1
    
    # Apply fixes
    if apply_fixes():
        print("\n✅ Fixes applied successfully!")
        
        # Check API keys
        print("\nChecking API keys...")
        run_script("check_api_keys.py")
        
        # Restart services if requested
        if args.restart:
            restart_services()
        else:
            print("\nTo apply the changes, restart the services:")
            print("python genai_agent_project/manage_services.py restart all")
        
        print("\nDone! GenAI Agent 3D should now work correctly with all AI providers.")
        return 0
    else:
        print("\n❌ Failed to apply all fixes.")
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
