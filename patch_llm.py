#!/usr/bin/env python3
"""
Patch LLM Service to Use Enhanced Environment Loader

This script updates the LLM service module to use the enhanced environment loader,
which improves API key handling.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file"""
    try:
        backup_path = f"{file_path}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"Created backup at {backup_path}")
        return True
    except Exception as e:
        print(f"Failed to create backup of {file_path}: {str(e)}")
        return False

def patch_llm_service():
    """Update the LLM service to use enhanced environment loader"""
    # Define the file path
    project_root = Path(__file__).parent.absolute()
    file_path = project_root / "genai_agent_project" / "genai_agent" / "services" / "llm.py"
    
    # Check if file exists
    if not file_path.exists():
        print(f"LLM service file not found at {file_path}")
        return False
    
    # Create backup
    if not backup_file(file_path):
        return False
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already patched
    if "from .enhanced_env_loader import" in content:
        print("LLM service file already patched")
        return True
    
    # Add import statement
    import_section_end = content.find("# Configure logging")
    if import_section_end == -1:
        print("Could not find import section in LLM service file")
        return False
    
    updated_content = content[:import_section_end] + \
                     "\n# Import the enhanced environment loader\n" + \
                     "from .enhanced_env_loader import get_api_key_for_provider, get_llm_config_from_env\n" + \
                     content[import_section_end:]
    
    # Find API key loading code to patch
    api_key_section = updated_content.find("api_key = os.environ.get")
    if api_key_section != -1:
        lines = updated_content.split('\n')
        patched_lines = []
        
        # Add the enhanced loader code
        for line in lines:
            if line.strip().startswith("api_key = os.environ.get"):
                patched_lines.append("        # Try to get API key from environment first, then config")
                patched_lines.append("        api_key = get_api_key_for_provider(provider) or self.config.get(\"api_key\")")
            else:
                patched_lines.append(line)
        
        updated_content = '\n'.join(patched_lines)
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Successfully patched LLM service file at {file_path}")
    return True

def main():
    """Main function"""
    print("=" * 80)
    print("         Patch LLM Service for Enhanced API Key Handling")
    print("=" * 80)
    
    success = patch_llm_service()
    
    if success:
        print("\n✅ LLM service patched successfully!")
        print("You'll need to restart the services for changes to take effect:")
        print("python genai_agent_project/manage_services.py restart all")
        
        # Ask if the user wants to restart services
        restart = input("\nWould you like to restart services now? (y/n): ").lower() == 'y'
        if restart:
            try:
                import subprocess
                subprocess.run([sys.executable, "genai_agent_project/manage_services.py", "restart", "all"], check=True)
                print("\n✅ Services restarted successfully!")
            except Exception as e:
                print(f"\n❌ Failed to restart services: {str(e)}")
                print("Please restart services manually.")
        
        return 0
    else:
        print("\n❌ Failed to patch LLM service.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
