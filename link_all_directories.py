#!/usr/bin/env python3
"""
GenAI Agent 3D - Master Directory Linking Script

This script creates symbolic links (Linux/Mac) or directory junctions (Windows)
between web frontend and backend agent directories to ensure both systems
can access the same files regardless of path differences.

Handles: models, scenes, diagrams, tools, and temp directories.
"""

import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header."""
    separator = "=" * 60
    print(f"\n{Colors.BOLD}{Colors.HEADER}{separator}")
    print(f"    {text}")
    print(f"{separator}{Colors.END}\n")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}{Colors.BOLD}✓ {text}{Colors.END}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}{Colors.BOLD}! {text}{Colors.END}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}{Colors.BOLD}✗ {text}{Colors.END}")

def print_info(text):
    """Print an info message."""
    print(f"{Colors.BLUE}→ {text}{Colors.END}")

def get_project_dirs():
    """Determine the project directories based on script location."""
    # Get the directory where this script is located
    script_dir = Path(__file__).resolve().parent
    
    # Set project directories
    agent_output = script_dir / "genai_agent_project" / "output"
    frontend_output = script_dir / "genai_agent_project" / "web" / "backend" / "output"
    
    return script_dir, agent_output, frontend_output

def ensure_directories_exist(agent_output, frontend_output):
    """Ensure the main output directories exist."""
    for directory in [agent_output, frontend_output]:
        if not directory.exists():
            print_info(f"Creating directory: {directory}")
            directory.mkdir(parents=True, exist_ok=True)

def backup_directory(source, backup_suffix="_backup"):
    """Backup the contents of a directory if it exists."""
    if not source.exists():
        return False
    
    backup_dir = source.parent / f"{source.name}{backup_suffix}"
    
    # Create backup directory if it doesn't exist
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
    
    # Copy files if there are any
    if any(source.iterdir()):
        print_info(f"Backing up files from {source} to {backup_dir}")
        # Use different copy methods based on OS
        if platform.system() == "Windows":
            subprocess.run(f'xcopy /E /I /Y "{source}\\*" "{backup_dir}\\"', shell=True)
        else:
            subprocess.run(f'cp -R "{source}/"* "{backup_dir}/" 2>/dev/null || true', shell=True)
    
    return True

def create_symlink(target, link_name):
    """Create a symbolic link (Linux/Mac) or directory junction (Windows)."""
    # Ensure target directory exists
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
    
    # Remove link directory if it exists
    if link_name.exists():
        if platform.system() == "Windows":
            # Windows requires special handling for directory junctions
            subprocess.run(f'rmdir /S /Q "{link_name}"', shell=True)
        else:
            shutil.rmtree(link_name)
    
    # Create the symbolic link based on OS
    if platform.system() == "Windows":
        # Windows uses directory junctions with mklink
        subprocess.run(f'mklink /J "{link_name}" "{target}"', shell=True)
    else:
        # Linux/Mac use standard symbolic links
        os.symlink(target, link_name, target_is_directory=True)
    
    # Verify the link was created
    if link_name.exists():
        print_success(f"Created link: {link_name} → {target}")
        return True
    else:
        print_error(f"Failed to create link: {link_name} → {target}")
        return False

def copy_backed_up_files(source_backup, destination):
    """Copy files from backup to the destination directory."""
    if not source_backup.exists() or not any(source_backup.iterdir()):
        return  # Nothing to copy
    
    print_info(f"Copying files from {source_backup} to {destination}")
    
    # Use different copy methods based on OS
    if platform.system() == "Windows":
        subprocess.run(f'xcopy /E /I /Y "{source_backup}\\*" "{destination}\\"', shell=True)
    else:
        subprocess.run(f'cp -R "{source_backup}/"* "{destination}/" 2>/dev/null || true', shell=True)

def link_directory(directory_name, agent_output, frontend_output):
    """Process a specific directory type (models, scenes, etc.)."""
    print_info(f"Processing {directory_name} directory...")
    
    # Setup paths
    frontend_dir = frontend_output / directory_name
    agent_dir = agent_output / directory_name
    backup_dir = frontend_output / f"{directory_name}_backup"
    
    # Backup existing frontend files
    had_existing_files = backup_directory(frontend_dir)
    
    # Create the symlink
    success = create_symlink(agent_dir, frontend_dir)
    
    # Copy backed up files to agent directory
    if success and had_existing_files:
        copy_backed_up_files(backup_dir, agent_dir)
    
    return success

def restart_backend_server(script_dir):
    """Attempt to restart the backend server."""
    print_info("Attempting to restart the backend server...")
    
    manage_script = script_dir / "genai_agent_project" / "manage_services.py"
    
    if manage_script.exists():
        try:
            subprocess.run(f'python "{manage_script}" restart backend', shell=True)
            print_success("Backend server restart command sent.")
        except Exception as e:
            print_warning(f"Error restarting backend server: {e}")
            print_info("Please restart the backend server manually.")
    else:
        print_warning("Could not find manage_services.py script.")
        print_info("Please restart the backend server manually.")

def main():
    """Main function to process all directories."""
    print_header("GenAI Agent 3D - Link All Directories")
    
    script_dir, agent_output, frontend_output = get_project_dirs()
    
    print_info(f"Script directory: {script_dir}")
    print_info(f"Agent output directory: {agent_output}")
    print_info(f"Frontend output directory: {frontend_output}")
    
    # Ensure main directories exist
    ensure_directories_exist(agent_output, frontend_output)
    
    # Directories to process
    directories = ["models", "scenes", "diagrams", "tools", "temp"]
    
    # Process each directory
    success_count = 0
    for directory in directories:
        if link_directory(directory, agent_output, frontend_output):
            success_count += 1
    
    # Summary
    print_header("Directory Linking Complete")
    
    if success_count == len(directories):
        print_success(f"All {success_count} directories have been successfully linked!")
    else:
        print_warning(f"{success_count} out of {len(directories)} directories were successfully linked.")
    
    print_info("Now both the web frontend and agent will access the same files.")
    print_info(f"Main output directory: {agent_output}")
    print_info(f"Backups of original files are in: {frontend_output}/*_backup folders")
    
    # Ask to restart backend server
    restart = input("\nDo you want to restart the backend server now? (y/n): ")
    if restart.lower() in ['y', 'yes']:
        restart_backend_server(script_dir)
    else:
        print_info("Please remember to restart your backend server manually for changes to take effect:")
        print_info("  python manage_services.py restart backend")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nAn error occurred: {e}")
        sys.exit(1)
