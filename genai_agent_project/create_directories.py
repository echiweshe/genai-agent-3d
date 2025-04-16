#!/usr/bin/env python3
"""
Script to create the directory structure for the GenAI Agent project
"""

import os
import sys

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def create_file(path, content=""):
    """Create file with content if it doesn't exist"""
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created file: {path}")

def main():
    """Create directory structure"""
    # Base directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Core package
    create_directory(os.path.join(base_dir, "genai_agent"))
    create_file(os.path.join(base_dir, "genai_agent", "__init__.py"), 
                '"""GenAI Agent - 3D scene generation framework"""\n\n__version__ = "0.1.0"\n')
    
    # Services
    create_directory(os.path.join(base_dir, "genai_agent", "services"))
    create_file(os.path.join(base_dir, "genai_agent", "services", "__init__.py"))
    
    # Tools
    create_directory(os.path.join(base_dir, "genai_agent", "tools"))
    create_file(os.path.join(base_dir, "genai_agent", "tools", "__init__.py"))
    
    # Models
    create_directory(os.path.join(base_dir, "genai_agent", "models"))
    create_file(os.path.join(base_dir, "genai_agent", "models", "__init__.py"))
    
    # Utils
    create_directory(os.path.join(base_dir, "genai_agent", "utils"))
    create_file(os.path.join(base_dir, "genai_agent", "utils", "__init__.py"))
    
    # Examples
    create_directory(os.path.join(base_dir, "examples"))
    create_file(os.path.join(base_dir, "examples", "__init__.py"))
    
    # Tests
    create_directory(os.path.join(base_dir, "tests"))
    create_file(os.path.join(base_dir, "tests", "__init__.py"))
    
    # Addons
    create_directory(os.path.join(base_dir, "addons"))
    
    print("Directory structure created successfully!")

if __name__ == "__main__":
    main()
