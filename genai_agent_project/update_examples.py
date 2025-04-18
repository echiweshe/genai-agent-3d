#!/usr/bin/env python
"""
Update Example Files to Use Environment Variables

This script finds and modifies all example files to use
environment variables instead of hardcoded values.
"""

import os
import re
import sys
from pathlib import Path

# Files to exclude
EXCLUDE_DIRS = [
    "venv",
    "__pycache__",
    ".git",
]

def add_env_loader_import(content):
    """Add import for env_loader if not already present"""
    if "from env_loader import" not in content and "import env_loader" not in content:
        # Check if there are other imports
        if re.search(r'^import\s+', content, re.MULTILINE):
            # Add after the last import
            last_import = list(re.finditer(r'^(?:import|from)\s+.*?$', content, re.MULTILINE))[-1]
            end_pos = last_import.end()
            return content[:end_pos] + "\nfrom env_loader import get_env, get_config\n" + content[end_pos:]
        else:
            # Add at the beginning
            return "from env_loader import get_env, get_config\n\n" + content
    return content

def replace_model_references(content):
    """Replace hardcoded model references with get_env calls"""
    # Replace direct model string assignments
    patterns = [
        (r'(model\s*=\s*)["\']([^"\']+)["\']', r'\1get_env("LLM_MODEL", "\2")'),
        (r'(llm_model\s*=\s*)["\']([^"\']+)["\']', r'\1get_env("LLM_MODEL", "\2")'),
        (r'(["\']model["\']:\s*)["\']([^"\']+)["\']', r'\1get_env("LLM_MODEL", "\2")'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def replace_path_references(content):
    """Replace hardcoded path references with get_env calls"""
    # Replace integration paths
    patterns = [
        (r'["\']C:\\\\path\\\\to\\\\BlenderGPT["\']', r'get_env("BLENDERGPT_PATH", "integrations/blendergpt")'),
        (r'["\']C:/path/to/BlenderGPT["\']', r'get_env("BLENDERGPT_PATH", "integrations/blendergpt")'),
        (r'["\']C:\\\\path\\\\to\\\\Hunyuan3D-2["\']', r'get_env("HUNYUAN3D_PATH", "integrations/hunyuan3d")'),
        (r'["\']C:/path/to/Hunyuan3D-2["\']', r'get_env("HUNYUAN3D_PATH", "integrations/hunyuan3d")'),
        (r'["\']C:\\\\path\\\\to\\\\TRELLIS["\']', r'get_env("TRELLIS_PATH", "integrations/trellis")'),
        (r'["\']C:/path/to/TRELLIS["\']', r'get_env("TRELLIS_PATH", "integrations/trellis")'),
    ]
    
    # Replace output paths
    output_patterns = [
        (r'(output_dir\s*=\s*)["\']output/(\w+)["\']', r'\1get_env("\2_OUTPUT_DIR", "output/\2")'),
    ]
    
    for pattern, replacement in patterns + output_patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def replace_config_loads(content):
    """Replace direct config loading with get_config"""
    # Find config loading patterns and replace them
    patterns = [
        (r'(?:yaml\.safe_load\(open\(["\']config\.yaml["\']\).+?\))', 'get_config()'),
        (r'with open\(["\']config\.yaml["\']\).*?as f:\s*config = yaml\.safe_load\(f\)', 'config = get_config()'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    return content

def update_file(file_path):
    """Update a single file to use environment variables"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add import for env_loader
        content = add_env_loader_import(content)
        
        # Replace model references
        content = replace_model_references(content)
        
        # Replace path references
        content = replace_path_references(content)
        
        # Replace config loading
        content = replace_config_loads(content)
        
        # Only write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def process_directory(directory):
    """Process all Python files in a directory"""
    files_modified = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    files_modified += 1
                    print(f"Updated: {file_path}")
    
    return files_modified

def main():
    """Main function"""
    print("Updating example files to use environment variables...")
    
    # Define project directory
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    
    # Create the env_loader.py file in the project root if it doesn't exist
    env_loader_path = os.path.join(PROJECT_ROOT, "env_loader.py")
    if not os.path.exists(env_loader_path):
        print(f"Error: env_loader.py not found at {env_loader_path}")
        print("Please create this file first.")
        return
    
    # Create .env file in the project root if it doesn't exist
    env_file_path = os.path.join(PROJECT_ROOT, ".env")
    if not os.path.exists(env_file_path):
        print(f"Error: .env file not found at {env_file_path}")
        print("Please create this file first.")
        return
    
    # Process examples directory
    examples_dir = os.path.join(PROJECT_ROOT, "examples")
    if os.path.exists(examples_dir):
        print(f"Processing examples directory: {examples_dir}")
        files_modified = process_directory(examples_dir)
        print(f"Modified {files_modified} example files")
    else:
        print(f"Examples directory not found: {examples_dir}")
    
    # Also update scripts in the project root
    print("Processing scripts in project root...")
    files_modified = 0
    for file in os.listdir(PROJECT_ROOT):
        if file.endswith('.py') and file not in ['env_loader.py', 'update_examples.py']:
            file_path = os.path.join(PROJECT_ROOT, file)
            if update_file(file_path):
                files_modified += 1
                print(f"Updated: {file_path}")
    print(f"Modified {files_modified} script files in project root")
    
    print("\nUpdate complete!")
    print("Now you can modify environment variables in the .env file without changing code.")

if __name__ == "__main__":
    main()
