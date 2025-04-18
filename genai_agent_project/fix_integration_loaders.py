#!/usr/bin/env python
"""
Fix Integration Loaders

This script locates and fixes the integration loader code to ensure
it looks for integrations in the correct paths.
"""

import os
import re
import sys
from pathlib import Path

def find_integration_files():
    """Find all integration-related files"""
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    GENAI_DIR = os.path.join(PROJECT_ROOT, "genai_agent")
    
    # Patterns to look for
    patterns = [
        r"hunyuan.*integration",
        r"blendergpt.*integration",
        r"trellis.*integration",
        r"integration.*base",
        r"blender_gpt_tool",
        r"hunyuan_3d_tool",
        r"trellis_tool"
    ]
    
    # Find matching files
    integration_files = []
    for root, dirs, files in os.walk(GENAI_DIR):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    for pattern in patterns:
                        if re.search(pattern, content):
                            integration_files.append(file_path)
                            break
    
    return integration_files

def fix_integration_loader_file(file_path):
    """Fix a single integration loader file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Look for config path access patterns
        patterns = [
            # Change 'blender_gpt' -> 'blendergpt'
            (r"config\[['\"]integrations['\"]\]\[['\"]blender_gpt['\"]\]", r"config['integrations']['blendergpt']"),
            # Change 'hunyuan_3d' -> 'hunyuan3d'
            (r"config\[['\"]integrations['\"]\]\[['\"]hunyuan_3d['\"]\]", r"config['integrations']['hunyuan3d']"),
            # Change 'blendergpt_path' access to 'path'
            (r"(['\"]blendergpt_path['\"])", r"'path'"),
            # Change 'hunyuan_path' access to 'path'
            (r"(['\"]hunyuan_path['\"])", r"'path'"),
            # Add fallback for missing config
            (r"if\s+['\"](\w+)['\"] not in config\[['\"]integrations['\"]\]:", 
             r"if 'integrations' not in config or '\1' not in config['integrations']:"),
            # Add nested dictionary check
            (r"if\s+not os\.path\.exists\(config\[['\"]integrations['\"]\]\[['\"](\w+)['\"]\]\[['\"]path['\"]\]\):", 
             r"if 'integrations' not in config or '\1' not in config['integrations'] or 'path' not in config['integrations']['\1'] or not os.path.exists(config['integrations']['\1']['path']):"),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Only write back if changes were made
        if content != original_content:
            # Create a backup
            backup_path = f"{file_path}.bak"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("Finding and fixing integration loader files...")
    
    # Find integration-related files
    integration_files = find_integration_files()
    
    if not integration_files:
        print("No integration files found.")
        return
    
    print(f"Found {len(integration_files)} integration-related files:")
    for file in integration_files:
        print(f"  {file}")
    
    # Fix each file
    fixed_files = 0
    for file in integration_files:
        if fix_integration_loader_file(file):
            print(f"Fixed: {file}")
            fixed_files += 1
    
    print(f"\nFixed {fixed_files} out of {len(integration_files)} files.")
    print("""
This script has fixed the integration loader code to:
1. Correctly use 'blendergpt' instead of 'blender_gpt' for config access
2. Correctly use 'hunyuan3d' instead of 'hunyuan_3d' for config access
3. Fix path access to use 'path' instead of 'blendergpt_path'/'hunyuan_path'
4. Add additional checks to prevent errors with missing config entries

After running this script, the integration tools should correctly locate
and load the integrations from the proper directories.
""")
    
if __name__ == "__main__":
    main()
