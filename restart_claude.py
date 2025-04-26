#!/usr/bin/env python3
"""
Restart Services with Claude as Default LLM

This script restarts all services for the GenAI Agent 3D project
with Claude as the default LLM provider.
"""

import os
import subprocess
import sys
import time

def restart_services():
    """Restart all services"""
    print("="*80)
    print("             Restarting GenAI Agent 3D Services               ")
    print("="*80)
    
    try:
        # Change to the project directory
        os.chdir("genai_agent_project")
        
        # Run the restart command
        print("\nStopping all services...")
        stop_result = subprocess.run(
            ["python", "manage_services.py", "stop", "all"],
            check=True,
            capture_output=True,
            text=True
        )
        print(stop_result.stdout)
        
        # Wait a bit for services to fully stop
        time.sleep(2)
        
        print("\nStarting all services...")
        start_result = subprocess.run(
            ["python", "manage_services.py", "start", "all"],
            check=True,
            capture_output=True,
            text=True
        )
        print(start_result.stdout)
        
        print("\n✅ Services restarted successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error restarting services: {str(e)}")
        if e.stdout:
            print("Standard output:")
            print(e.stdout)
        if e.stderr:
            print("Error output:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False
    finally:
        # Change back to the original directory
        os.chdir("..")

if __name__ == "__main__":
    print("This script will restart all services for the GenAI Agent 3D project.")
    print("Claude has been set as the default LLM provider.")
    print()
    
    continue_prompt = input("Do you want to continue? (y/n): ")
    if continue_prompt.lower() != "y":
        print("Operation cancelled.")
        sys.exit(0)
    
    success = restart_services()
    
    if success:
        print("\nAll services have been restarted with Claude as the default LLM.")
        print("\nThe system should now be online and the LLM integration should be working.")
        print("\nCheck the system status in the web interface to verify.")
        
        # Ask if user wants to open browser
        browser_prompt = input("\nOpen browser to web interface? (y/n): ")
        if browser_prompt.lower() == "y":
            try:
                import webbrowser
                webbrowser.open("http://localhost:3000")
                print("Browser opened to http://localhost:3000")
            except Exception as e:
                print(f"Could not open browser automatically: {str(e)}")
                print("Please manually open http://localhost:3000 in your browser.")
    else:
        print("\nFailed to restart services.")
        print("You can try restarting them manually with:")
        print("cd genai_agent_project")
        print("python manage_services.py restart all")
