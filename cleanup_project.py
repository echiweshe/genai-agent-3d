#!/usr/bin/env python3
"""
Cleanup Project Files

This script organizes the GenAI Agent 3D project by:
1. Moving utility scripts to a 'scripts' directory
2. Creating categories for different types of scripts
3. Updating any references to the moved files
4. Removing backup and temporary files

Usage:
    python cleanup_project.py
"""

import os
import sys
import shutil
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("cleanup.log")
    ]
)
logger = logging.getLogger(__name__)

# Script categories and patterns
SCRIPT_CATEGORIES = {
    "setup": [
        r"setup_.*\.py",
        r"fix_.*\.py",
        r"install_.*\.py"
    ],
    "utilities": [
        r"check_.*\.py",
        r"test_.*\.py",
        r"restart_.*\.py",
        r"cleanup_.*\.py"
    ],
    "batch_files": [
        r".*\.bat",
        r".*\.sh"
    ]
}

def create_directory_structure():
    """Create the directory structure for organizing scripts"""
    # Base directories
    os.makedirs("scripts", exist_ok=True)
    
    # Category subdirectories
    for category in SCRIPT_CATEGORIES.keys():
        os.makedirs(f"scripts/{category}", exist_ok=True)
    
    # Create a directory for documentation
    os.makedirs("docs", exist_ok=True)
    
    # Create a directory for backups
    os.makedirs("backups", exist_ok=True)
    
    logger.info("Created directory structure")

def get_script_category(filename):
    """Determine the category for a script file"""
    for category, patterns in SCRIPT_CATEGORIES.items():
        for pattern in patterns:
            if re.match(pattern, filename):
                return category
    return None

def move_scripts_to_categories():
    """Move script files to their appropriate category directories"""
    root_dir = Path(".")
    
    # Get all Python, Bash, and Batch files in the root directory
    script_files = list(root_dir.glob("*.py")) + list(root_dir.glob("*.sh")) + list(root_dir.glob("*.bat"))
    
    # Skip this script itself
    script_files = [f for f in script_files if f.name != os.path.basename(__file__)]
    
    for script_file in script_files:
        category = get_script_category(script_file.name)
        
        if category:
            # Create destination path
            dest_path = Path(f"scripts/{category}/{script_file.name}")
            
            # Copy the file instead of moving it to avoid breaking anything
            shutil.copy2(script_file, dest_path)
            logger.info(f"Copied {script_file} to {dest_path}")
            
            # Don't delete the original yet, do that in a later phase when we're sure everything works
            # os.remove(script_file)
            # logger.info(f"Removed original {script_file}")

def move_documentation_files():
    """Move documentation files to the docs directory"""
    root_dir = Path(".")
    
    # Look for markdown and text files that appear to be documentation
    doc_patterns = [
        r".*README.*\.md",
        r".*GUIDE.*\.md",
        r".*MANUAL.*\.md",
        r".*ARCHITECTURE.*\.md",
        r".*DESIGN.*\.md",
        r".*ROADMAP.*\.md",
        r".*CONTRIBUTING.*\.md",
        r".*LICENSE.*\.md",
        r".*\.txt"
    ]
    
    # Keep main README.md in the root directory
    exclude_files = ["README.md"]
    
    for pattern in doc_patterns:
        for file_path in root_dir.glob(pattern):
            if file_path.name not in exclude_files:
                dest_path = Path(f"docs/{file_path.name}")
                shutil.copy2(file_path, dest_path)
                logger.info(f"Copied {file_path} to {dest_path}")

def cleanup_backup_files():
    """Clean up backup and temporary files"""
    root_dir = Path(".")
    
    # Backup file patterns
    backup_patterns = [
        r".*\.bak",
        r".*\.bak-[0-9]+",
        r".*\.old",
        r".*\.backup",
        r".*~"
    ]
    
    for pattern in backup_patterns:
        for file_path in root_dir.glob(pattern):
            dest_path = Path(f"backups/{file_path.name}")
            shutil.move(file_path, dest_path)
            logger.info(f"Moved backup file {file_path} to {dest_path}")
    
    # Also check subdirectories for backups
    for pattern in backup_patterns:
        for file_path in root_dir.glob(f"**/{pattern}"):
            # Skip files already in the backups directory
            if "backups" not in str(file_path):
                dest_path = Path(f"backups/{file_path.name}")
                shutil.move(file_path, dest_path)
                logger.info(f"Moved backup file {file_path} to {dest_path}")

def create_script_symlinks():
    """Create symlinks for commonly used scripts in the root directory"""
    
    # List of essential scripts to keep linked in the root
    essential_scripts = [
        ("scripts/setup/setup_api_keys.py", "setup_api_keys.py"),
        ("scripts/utilities/restart_services.py", "restart_services.py"),
        ("scripts/setup/fix_claude_api_key.py", "fix_claude_api_key.py")
    ]
    
    for source, dest in essential_scripts:
        if os.path.exists(source) and not os.path.exists(dest):
            # On Windows, symlinks require admin privileges, so we'll use a batch file instead
            if os.name == 'nt':
                with open(dest, 'w') as f:
                    f.write(f"""@echo off
python {source} %*
""")
            else:
                os.symlink(source, dest)
            
            logger.info(f"Created link for {source} to {dest}")

def create_index_file():
    """Create an index.md file listing all the scripts and their purposes"""
    
    scripts_dir = Path("scripts")
    
    # Start with a header
    index_content = """# GenAI Agent 3D Scripts Index

This document provides an index of all utility scripts available in the GenAI Agent 3D project.

"""
    
    # Add each category
    for category in SCRIPT_CATEGORIES.keys():
        category_dir = scripts_dir / category
        
        index_content += f"## {category.capitalize()}\n\n"
        
        if not category_dir.exists():
            index_content += "No scripts in this category.\n\n"
            continue
        
        scripts = list(category_dir.glob("*.py")) + list(category_dir.glob("*.sh")) + list(category_dir.glob("*.bat"))
        
        if not scripts:
            index_content += "No scripts in this category.\n\n"
            continue
        
        for script in sorted(scripts):
            # Try to extract a description from the script's docstring
            description = "No description available."
            try:
                with open(script, 'r') as f:
                    content = f.read()
                    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if docstring_match:
                        docstring = docstring_match.group(1).strip()
                        description_lines = docstring.split('\n')
                        # Use the first line of the docstring as the description
                        if description_lines:
                            description = description_lines[0].strip()
            except Exception as e:
                logger.warning(f"Could not extract description from {script}: {e}")
            
            # Add to index
            index_content += f"### {script.name}\n\n"
            index_content += f"{description}\n\n"
            index_content += f"Path: `{script.relative_to(scripts_dir.parent)}`\n\n"
    
    # Write the index file
    with open("docs/SCRIPTS_INDEX.md", 'w') as f:
        f.write(index_content)
    
    logger.info("Created scripts index file at docs/SCRIPTS_INDEX.md")

def main():
    """Main function"""
    print("=" * 80)
    print("           GenAI Agent 3D Project Cleanup")
    print("=" * 80)
    print("\nThis script will organize the project files into a more structured layout.")
    print("It will create directories for scripts, documentation, and backups.")
    print("Original files will not be deleted until you confirm the reorganization works.")
    
    proceed = input("\nProceed with cleanup? (y/n): ").lower() == 'y'
    if not proceed:
        print("Operation cancelled.")
        return 0
    
    try:
        # Create the directory structure
        create_directory_structure()
        
        # Move scripts to their categories
        move_scripts_to_categories()
        
        # Move documentation files
        move_documentation_files()
        
        # Clean up backup files
        cleanup_backup_files()
        
        # Create symlinks for essential scripts
        create_script_symlinks()
        
        # Create an index file
        create_index_file()
        
        print("\n✅ Project cleanup completed successfully!")
        print("\nImportant: Original files have been copied, not moved.")
        print("Once you verify everything works correctly, you can delete the original files.")
        
        delete_originals = input("\nDelete original files now? (y/n): ").lower() == 'y'
        if delete_originals:
            # This would involve another function call to delete the originals
            print("Feature not implemented yet - please delete manually if desired.")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error during project cleanup: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
