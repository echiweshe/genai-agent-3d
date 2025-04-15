#!/usr/bin/env python3
"""
Helper script for integrating existing SceneX code
"""

import os
import sys
import argparse
import shutil

def detect_scenex_repo():
    """Try to detect existing SceneX repository"""
    possible_paths = [
        "../SceneX",
        "../BlenderGenAI_SceneX",
        "../SceneX_V3",
        "../SceneX_Blender_Addon_Scripts_Dir"
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return os.path.abspath(path)
    
    return None

def analyze_scenex_repo(repo_path):
    """Analyze SceneX repository structure"""
    if not repo_path or not os.path.exists(repo_path):
        print(f"Repository not found: {repo_path}")
        return
    
    print(f"Analyzing SceneX repository: {repo_path}")
    
    # Check for Python files
    python_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files")
    
    # Look for key files and classes
    coordinate_files = []
    animation_files = []
    
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            
            # Check for coordinate system related code
            if 'coordinate' in content.lower() or 'coord' in content.lower():
                coordinate_files.append(file_path)
            
            # Check for animation related code
            if 'animation' in content.lower() or 'animate' in content.lower():
                animation_files.append(file_path)
    
    print(f"Found {len(coordinate_files)} files related to coordinate systems")
    print(f"Found {len(animation_files)} files related to animation")
    
    # Return analysis results
    return {
        'python_files': python_files,
        'coordinate_files': coordinate_files,
        'animation_files': animation_files
    }

def integrate_scenex(repo_path, target_dir):
    """Integrate SceneX code into the GenAI Agent"""
    if not repo_path or not os.path.exists(repo_path):
        print(f"Repository not found: {repo_path}")
        return False
    
    # Create SceneX integration directory
    integration_dir = os.path.join(target_dir, "scenex_integration")
    os.makedirs(integration_dir, exist_ok=True)
    
    # Analyze repo
    analysis = analyze_scenex_repo(repo_path)
    if not analysis:
        return False
    
    # Copy key files
    print("\nCopying key files...")
    for file_type, files in analysis.items():
        if file_type == 'python_files':
            continue  # Skip copying all Python files
        
        for file_path in files:
            rel_path = os.path.relpath(file_path, repo_path)
            dest_path = os.path.join(integration_dir, rel_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, dest_path)
            print(f"Copied: {rel_path}")
    
    # Create integration module
    create_integration_module(integration_dir, analysis)
    
    print("\nSceneX integration complete!")
    print(f"Integration files are in: {integration_dir}")
    print("\nNext steps:")
    print("1. Review the integrated files")
    print("2. Update the SceneXTool class to use your integrated code")
    print("3. Test the integration with examples")
    
    return True

def create_integration_module(integration_dir, analysis):
    """Create an integration module to help with SceneX integration"""
    module_path = os.path.join(integration_dir, "scenex_integration.py")
    
    with open(module_path, 'w') as file:
        file.write("""\"\"\"
SceneX Integration Module

This module helps integrate your existing SceneX code with the GenAI Agent.
\"\"\"

import os
import sys
import importlib.util
import logging

logger = logging.getLogger(__name__)

# Add integration directory to path
integration_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, integration_dir)

class SceneXIntegration:
    \"\"\"
    Integration class for SceneX functionality
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize SceneX Integration\"\"\"
        self.modules = {}
        self._load_modules()
    
    def _load_modules(self):
        \"\"\"Load SceneX modules\"\"\"
        # Try to load modules from the integration directory
        for root, _, files in os.walk(integration_dir):
            for file in files:
                if file.endswith(".py") and file != "scenex_integration.py":
                    module_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]
                    
                    try:
                        # Load module dynamically
                        spec = importlib.util.spec_from_file_location(module_name, module_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Store module
                        self.modules[module_name] = module
                        logger.info(f"Loaded SceneX module: {module_name}")
                    except Exception as e:
                        logger.error(f"Error loading module {module_name}: {str(e)}")
    
    def create_scene(self, description, objects, camera, animation):
        \"\"\"
        Create a scene using SceneX
        
        Args:
            description: Scene description
            objects: List of objects to include
            camera: Camera parameters
            animation: Animation parameters
            
        Returns:
            Scene data
        \"\"\"
        # This is a placeholder implementation
        # You should replace this with calls to your actual SceneX functions
        
        logger.info(f"Creating scene: {description}")
        
        # Example usage of loaded modules (replace with your actual implementation)
        scene_data = {
            "description": description,
            "objects": []
        }
        
        for obj in objects:
            scene_data["objects"].append({
                "name": obj.get("name", "Object"),
                "type": obj.get("type", "cube"),
                "position": obj.get("location", [0, 0, 0])
            })
        
        return scene_data
    
    def generate_script(self, scene_data):
        \"\"\"
        Generate Blender script from scene data
        
        Args:
            scene_data: Scene data
            
        Returns:
            Blender Python script
        \"\"\"
        # This is a placeholder implementation
        # You should replace this with calls to your actual SceneX functions
        
        script = f\"\"\"
# SceneX generated script
import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create coordinate system
bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
coords = bpy.context.active_object
coords.name = "CoordinateSystem"

# Create objects
\"\"\"
        
        # Add objects
        for obj in scene_data.get("objects", []):
            obj_type = obj.get("type", "cube")
            obj_name = obj.get("name", "Object")
            obj_pos = obj.get("position", [0, 0, 0])
            
            script += f\"\"\"
# Create {obj_name}
bpy.ops.mesh.primitive_{obj_type}_add(location=({obj_pos[0]}, {obj_pos[1]}, {obj_pos[2]}))
obj = bpy.context.active_object
obj.name = "{obj_name}"
\"\"\"
        
        return script

# Create singleton instance
integration = SceneXIntegration()
""")
    
    print(f"Created integration module: {module_path}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Integrate SceneX code')
    parser.add_argument('--repo', type=str, help='Path to SceneX repository')
    parser.add_argument('--target', type=str, default='../genai_agent', help='Target directory for integration')
    
    args = parser.parse_args()
    
    # If repo path not provided, try to detect it
    repo_path = args.repo
    if not repo_path:
        repo_path = detect_scenex_repo()
        if repo_path:
            print(f"Detected SceneX repository: {repo_path}")
        else:
            print("SceneX repository not found. Please specify with --repo")
            return
    
    # Ensure target directory exists
    target_dir = args.target
    if not os.path.exists(target_dir):
        print(f"Target directory not found: {target_dir}")
        return
    
    # Integrate SceneX
    integrate_scenex(repo_path, target_dir)

if __name__ == "__main__":
    main()
