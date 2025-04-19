#!/usr/bin/env python
"""
Fix the ToolRegistry issue in GenAI Agent 3D
This script analyzes and fixes the 'ToolRegistry' object has no attribute 'get_tools' error
"""
import os
import sys
import importlib.util
import inspect
import re

def find_tool_registry_class():
    """Find the ToolRegistry class file in the project"""
    print("Searching for ToolRegistry class...")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Likely locations for the ToolRegistry class
    likely_dirs = [
        os.path.join(project_dir, "genai_agent"),
        os.path.join(project_dir, "genai_agent", "tools"),
        os.path.join(project_dir, "web", "backend"),
    ]
    
    # Look for ToolRegistry class in Python files
    registry_files = []
    for base_dir in likely_dirs:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if 'class ToolRegistry' in content:
                                    registry_files.append((file_path, content))
                                    print(f"  Found ToolRegistry in: {file_path}")
                        except Exception as e:
                            pass  # Skip files with read errors
    
    return registry_files

def analyze_tool_registry_files(registry_files):
    """Analyze the ToolRegistry class files"""
    for file_path, content in registry_files:
        print(f"\nAnalyzing {file_path}:")
        
        # Find available methods in ToolRegistry
        methods = []
        class_match = re.search(r'class ToolRegistry.*?:(.*?)(?:class|\Z)', content, re.DOTALL)
        if class_match:
            class_content = class_match.group(1)
            method_matches = re.finditer(r'def\s+(\w+)\s*\(', class_content)
            for match in method_matches:
                methods.append(match.group(1))
            
            print(f"  Available methods: {', '.join(methods)}")
            
            # Check if there's a method similar to get_tools
            similar_method = None
            for method in methods:
                if 'tool' in method.lower() and ('get' in method.lower() or 'list' in method.lower()):
                    similar_method = method
                    print(f"  Found similar method to 'get_tools': {similar_method}")
        else:
            print("  Could not extract class content")
    
    return registry_files

def create_tool_registry_patch(registry_files):
    """Create a patch for the ToolRegistry class"""
    if not registry_files:
        print("No ToolRegistry files found to patch")
        return
    
    # Choose the most likely file to patch
    file_path, content = registry_files[0]
    
    print(f"\nCreating patch for: {file_path}")
    
    # Look for list_tools or similar method that could be used instead of get_tools
    replacement_method = None
    for method in ['list_tools', 'get_all_tools', 'available_tools', 'get_available_tools']:
        if re.search(rf'def\s+{method}\s*\(', content):
            replacement_method = method
            break
    
    # Create the patch content
    patch_content = """
    def get_tools(self):
        \"\"\"
        Get all registered tools.
        This method is added to fix compatibility with the backend API.
        \"\"\"
"""
    
    if replacement_method:
        print(f"  Found existing method '{replacement_method}' to use as implementation for get_tools")
        patch_content += f"        # Delegate to existing method\n        return self.{replacement_method}()\n"
    else:
        # Create a new implementation based on the structure of the class
        print("  Creating new implementation for get_tools")
        
        # Check if there's a self.tools property by looking for common patterns
        if re.search(r'self\.tools\s*=', content):
            patch_content += "        # Return the tools dictionary or list\n        return self.tools\n"
        elif re.search(r'self\._tools\s*=', content):
            patch_content += "        # Return the tools dictionary or list\n        return self._tools\n"
        else:
            # Fallback implementation that returns an empty list
            patch_content += "        # Fallback implementation\n        return []\n"
    
    # Create backup
    backup_path = file_path + '.bak'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  Created backup at: {backup_path}")
        
        # Now modify the file
        class_pattern = r'(class ToolRegistry.*?:.*?)((?:    )?(?:class|\Z))'
        if re.search(class_pattern, content, re.DOTALL):
            # Add the get_tools method to the ToolRegistry class
            modified_content = re.sub(
                class_pattern,
                r'\1' + patch_content + r'\2',
                content,
                flags=re.DOTALL
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"  Successfully patched {file_path}")
            print(f"  Added get_tools method to ToolRegistry class")
            return True
        else:
            print(f"  Could not patch {file_path}: Class pattern not found")
            return False
        
    except Exception as e:
        print(f"  Error patching {file_path}: {e}")
        return False

def fix_backend_api():
    """Fix the backend API to handle missing get_tools method"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_main_path = os.path.join(project_dir, "web", "backend", "main.py")
    
    if not os.path.exists(backend_main_path):
        print(f"Backend main.py not found at {backend_main_path}")
        return False
    
    try:
        with open(backend_main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup
        backup_path = backend_main_path + '.bak'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created backup of backend main.py at: {backup_path}")
        
        # Find the tools endpoint that calls get_tools
        tools_endpoint_pattern = r'(@app.get\([\'"]\/tools[\'"]\).*?async def get_tools\(\).*?try:.*?)agent\.tool_registry\.get_tools\(\)(.*?)except Exception as e:(.*?)return \{.*?\}'
        
        if re.search(tools_endpoint_pattern, content, re.DOTALL):
            # Modify the endpoint to handle the case when get_tools is missing
            modified_content = re.sub(
                tools_endpoint_pattern,
                r'\1try:\n            return agent.tool_registry.get_tools()\n        except AttributeError:\n            # Fallback for when get_tools is not available\n            try:\n                # Try common alternative methods\n                if hasattr(agent.tool_registry, "list_tools"):\n                    return agent.tool_registry.list_tools()\n                elif hasattr(agent.tool_registry, "get_all_tools"):\n                    return agent.tool_registry.get_all_tools()\n                elif hasattr(agent.tool_registry, "tools") and isinstance(agent.tool_registry.tools, list):\n                    return agent.tool_registry.tools\n                elif hasattr(agent.tool_registry, "_tools") and isinstance(agent.tool_registry._tools, list):\n                    return agent.tool_registry._tools\n                else:\n                    return []\n            except Exception as inner_e:\n                logger.error(f"Error in fallback methods: {inner_e}")\n                return []\2\3return {"status": "error", "message": str(e)}',
                content,
                flags=re.DOTALL
            )
            
            with open(backend_main_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"Successfully patched backend main.py to handle missing get_tools method")
            return True
        else:
            print(f"Could not patch backend main.py: Tools endpoint pattern not found")
            return False
        
    except Exception as e:
        print(f"Error patching backend main.py: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "="*80)
    print(" GenAI Agent 3D - Fix ToolRegistry Issue ".center(80, "="))
    print("="*80 + "\n")
    
    print("This script will fix the 'ToolRegistry' object has no attribute 'get_tools' error.")
    
    if input("Continue? (y/n): ").lower() != 'y':
        return 1
    
    # Find and analyze ToolRegistry class
    registry_files = find_tool_registry_class()
    if not registry_files:
        print("\nCould not find ToolRegistry class. Try Plan B: modifying backend API.")
        backend_patched = fix_backend_api()
        
        if backend_patched:
            print("\n✅ Backend API patched successfully to handle missing get_tools method.")
            print("   You should now restart your backend server to apply the changes.")
        else:
            print("\n❌ Could not fix the issue automatically.")
            print("   You may need to modify the code manually.")
        return 0
    
    # Analyze files
    analyze_tool_registry_files(registry_files)
    
    # Create patch
    if input("\nApply the patch to add get_tools method? (y/n): ").lower() == 'y':
        patched = create_tool_registry_patch(registry_files)
        if patched:
            print("\n✅ ToolRegistry class patched successfully.")
            print("   You should now restart your backend server to apply the changes.")
        else:
            print("\n❌ Patch failed. Try Plan B: modifying backend API.")
            backend_patched = fix_backend_api()
            
            if backend_patched:
                print("\n✅ Backend API patched successfully to handle missing get_tools method.")
                print("   You should now restart your backend server to apply the changes.")
            else:
                print("\n❌ Could not fix the issue automatically.")
                print("   You may need to modify the code manually.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
