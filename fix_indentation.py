#!/usr/bin/env python
"""
Fix Indentation Error in main.py
This script fixes the indentation error at line 359 in main.py
"""

import os
import sys
import re

def fix_indentation_error(main_py_path):
    """Fix the indentation error in main.py"""
    try:
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Create backup
        backup_path = main_py_path + '.indent_backup'
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"Created backup: {backup_path}")
        
        # Find the problematic lines
        lines = content.splitlines()
        models_endpoint_line = None
        
        for i, line in enumerate(lines):
            if '@app.get("/models")' in line:
                models_endpoint_line = i
                break
        
        if models_endpoint_line is not None:
            print(f"Found models endpoint at line {models_endpoint_line + 1}")
            
            # Check if there's a function def before it without a proper block
            function_def_line = None
            for i in range(models_endpoint_line - 1, -1, -1):
                if "def " in lines[i] and lines[i].strip().endswith(":"):
                    function_def_line = i
                    break
            
            if function_def_line is not None:
                print(f"Found function definition at line {function_def_line + 1}: {lines[function_def_line]}")
                
                # Look for proper indentation in this function
                has_proper_indentation = False
                for i in range(function_def_line + 1, models_endpoint_line):
                    if lines[i].strip() and lines[i][0].isspace():
                        has_proper_indentation = True
                        break
                
                if not has_proper_indentation:
                    print("Function is missing indented block. Adding pass statement.")
                    
                    # Add a pass statement with proper indentation
                    if function_def_line + 1 < len(lines):
                        indent = "    "  # Standard Python indentation
                        lines.insert(function_def_line + 1, f"{indent}pass")
                
                # Now rebuild the content
                new_content = "\n".join(lines)
                
                # Write the fixed content
                with open(main_py_path, 'w') as f:
                    f.write(new_content)
                
                print(f"Fixed indentation error in {main_py_path}")
                return True
            else:
                print("No function definition found before models endpoint")
        else:
            print("Models endpoint not found")
        
        return False
    except Exception as e:
        print(f"Error fixing indentation: {e}")
        return False

def find_main_py_file():
    """Find the main.py file in the project"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(script_dir, "genai_agent_project", "web", "backend", "main.py")
    
    if os.path.exists(main_py_path):
        return main_py_path
    
    # Try alternative paths
    alternatives = [
        os.path.join(script_dir, "web", "backend", "main.py"),
        os.path.join(script_dir, "backend", "main.py")
    ]
    
    for path in alternatives:
        if os.path.exists(path):
            return path
    
    # If still not found, search for it
    for root, dirs, files in os.walk(script_dir):
        if "main.py" in files:
            return os.path.join(root, "main.py")
    
    return None

def main():
    """Main function"""
    print("\n===== FIXING INDENTATION ERROR IN MAIN.PY =====\n")
    
    # Find main.py
    main_py_path = find_main_py_file()
    
    if main_py_path:
        print(f"Found main.py at {main_py_path}")
        fixed = fix_indentation_error(main_py_path)
        
        if fixed:
            print("\n✅ Successfully fixed indentation error")
            print("\nPlease restart your backend server to apply the changes")
        else:
            print("\n❌ Failed to fix indentation error")
            print("\nTry manually adding a 'pass' statement after any empty function definition")
    else:
        print("❌ Could not find main.py file")
        print("Please provide the full path to main.py:")
        custom_path = input("> ")
        
        if os.path.exists(custom_path):
            fixed = fix_indentation_error(custom_path)
            
            if fixed:
                print("\n✅ Successfully fixed indentation error")
                print("\nPlease restart your backend server to apply the changes")
            else:
                print("\n❌ Failed to fix indentation error")
                print("\nTry manually adding a 'pass' statement after any empty function definition")
        else:
            print(f"❌ File not found: {custom_path}")

if __name__ == "__main__":
    main()
