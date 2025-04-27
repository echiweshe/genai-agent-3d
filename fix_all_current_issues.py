#!/usr/bin/env python3
"""
Fix All Current Issues - GenAI Agent 3D

This script runs all the fix scripts to resolve current issues in the GenAI Agent 3D project.
It fixes the Claude API integration, Hunyuan3D integration, output directory linking,
and content preview issues.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixManager:
    """Manages the execution of fix scripts"""
    
    def __init__(self, project_root):
        """Initialize the fix manager"""
        self.project_root = project_root
        self.fixes_to_run = []
        self.results = {}
    
    def add_fix(self, script_name, description, priority=1):
        """Add a fix script to the list"""
        script_path = self.project_root / script_name
        
        if script_path.exists():
            self.fixes_to_run.append({
                'name': script_name,
                'path': script_path,
                'description': description,
                'priority': priority  # Lower number = higher priority
            })
            logger.info(f"Added fix script: {script_name}")
        else:
            logger.warning(f"Fix script not found: {script_path}")
    
    def run_fixes(self):
        """Run all fix scripts in priority order"""
        # Sort fixes by priority
        self.fixes_to_run.sort(key=lambda x: x['priority'])
        
        print("\n=== Running Fix Scripts ===\n")
        
        for fix in self.fixes_to_run:
            script_name = fix['name']
            script_path = fix['path']
            description = fix['description']
            
            print(f"\n--- Running: {script_name} ---")
            print(f"Description: {description}")
            
            # Ask for confirmation to run the script
            confirm = input(f"Run this fix script? (y/n): ").lower()
            if confirm != 'y':
                print(f"Skipping {script_name}...")
                self.results[script_name] = "SKIPPED"
                continue
            
            # Run the script
            try:
                start_time = time.time()
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    check=False,
                    capture_output=True,
                    text=True
                )
                end_time = time.time()
                
                # Check result
                if result.returncode == 0:
                    print(f"✅ {script_name} completed successfully!")
                    self.results[script_name] = "SUCCESS"
                else:
                    print(f"❌ {script_name} failed with exit code {result.returncode}")
                    print("Error output:")
                    print(result.stderr)
                    self.results[script_name] = "FAILED"
                
                # Print execution time
                print(f"Execution time: {end_time - start_time:.2f} seconds")
                
                # Wait a moment before running the next script
                time.sleep(1)
            
            except Exception as e:
                print(f"❌ Error running {script_name}: {str(e)}")
                self.results[script_name] = "ERROR"
    
    def print_summary(self):
        """Print a summary of fix script results"""
        print("\n=== Fix Scripts Summary ===\n")
        
        success_count = sum(1 for result in self.results.values() if result == "SUCCESS")
        failed_count = sum(1 for result in self.results.values() if result == "FAILED")
        skipped_count = sum(1 for result in self.results.values() if result == "SKIPPED")
        error_count = sum(1 for result in self.results.values() if result == "ERROR")
        
        print(f"Total fix scripts: {len(self.results)}")
        print(f"Successfully completed: {success_count}")
        print(f"Failed: {failed_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Errors: {error_count}")
        
        if failed_count > 0 or error_count > 0:
            print("\nFailed or error scripts:")
            for script_name, result in self.results.items():
                if result in ["FAILED", "ERROR"]:
                    print(f"- {script_name}: {result}")

def main():
    """Main function"""
    # Get project root
    project_root = Path(__file__).parent.absolute()
    
    print("===========================================")
    print("  Fix All Current Issues - GenAI Agent 3D")
    print("===========================================")
    print(f"Project root: {project_root}")
    print("\nThis script will run various fix scripts to resolve current issues.")
    print("You will be prompted before each script is run.")
    
    # Initialize fix manager
    fix_manager = FixManager(project_root)
    
    # Add fix scripts in priority order
    fix_manager.add_fix(
        "fix_claude_integration.py",
        "Fixes Claude API integration issues",
        priority=1
    )
    
    fix_manager.add_fix(
        "fix_hunyuan3d_integration.py",
        "Fixes Hunyuan3D integration issues",
        priority=2
    )
    
    fix_manager.add_fix(
        "fix_output_directories.py",
        "Fixes output directory linking issues",
        priority=3
    )
    
    fix_manager.add_fix(
        "fix_content_preview.py",
        "Fixes content preview in generator pages",
        priority=4
    )
    
    fix_manager.add_fix(
        "cleanup_claude_integration.py",
        "Organizes Claude integration scripts and documentation",
        priority=5
    )
    
    # Check if other fix scripts exist and add them
    other_fixes = [
        ("fix_all_v2.py", "Comprehensive fixes for all components", 6),
        ("fix_redis_connection.py", "Fixes Redis connection issues", 7),
        ("fix_llm_errors.py", "Fixes LLM service errors", 8),
        ("fix_blender_scripts.py", "Fixes Blender script integration", 9),
        ("fix_models_endpoint.py", "Fixes models endpoint", 10)
    ]
    
    for script_name, description, priority in other_fixes:
        script_path = project_root / script_name
        if script_path.exists():
            fix_manager.add_fix(script_name, description, priority)
    
    # Ask for confirmation to begin
    print("\nThe following fix scripts will be run (in order):")
    for i, fix in enumerate(fix_manager.fixes_to_run, 1):
        print(f"{i}. {fix['name']} - {fix['description']}")
    
    confirm = input("\nProceed with fixes? (y/n): ").lower()
    if confirm != 'y':
        print("Operation cancelled by user.")
        return 1
    
    # Run the fix scripts
    fix_manager.run_fixes()
    
    # Print summary
    fix_manager.print_summary()
    
    # Ask if the user wants to restart the services
    restart = input("\nWould you like to restart the services now? (y/n): ").lower()
    if restart == 'y':
        try:
            restart_script = project_root / "restart_services.py"
            if restart_script.exists():
                print("\nRestarting services...")
                subprocess.run([sys.executable, str(restart_script)], check=False)
                print("Services restarted.")
            else:
                print("\nRestart script not found. Please restart services manually.")
        except Exception as e:
            print(f"\nError restarting services: {str(e)}")
            print("Please restart services manually.")
    
    print("\nFix operations completed. Check the summary above for results.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
