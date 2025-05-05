"""
Cleanup Script for SVG to Video Module

This script cleans up the SVG to Video module by removing deprecated files
and ensuring all components are properly located in their subdirectories.
"""

import os
import shutil
from pathlib import Path
import sys

def main():
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Define module directory
    module_dir = os.path.join(project_root, "genai_agent", "svg_to_video")
    
    print(f"Project root: {project_root}")
    print(f"Module directory: {module_dir}")
    
    # Files to remove (deprecated or duplicated)
    files_to_remove = [
        "animation_system.py",
        "svg_generator.py",
        "svg_generator_new.py",
        "video_renderer.py",
        "svg_to_3d_converter.py",
        "convert_svg_to_3d.py",
        "pipeline.py",
        "utils.py"
    ]
    
    # Remove deprecated files
    for file_name in files_to_remove:
        file_path = os.path.join(module_dir, file_name)
        if os.path.exists(file_path):
            try:
                # Create a backup first
                backup_dir = os.path.join(project_root, "archive", "svg_to_video")
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, file_name)
                
                print(f"Backing up {file_path} to {backup_path}")
                shutil.copy2(file_path, backup_path)
                
                print(f"Removing deprecated file: {file_path}")
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")
    
    # Ensure output directories exist
    output_dirs = [
        os.path.join(project_root, "output", "svg_to_video", "svg"),
        os.path.join(project_root, "output", "svg_to_video", "models"),
        os.path.join(project_root, "output", "svg_to_video", "animations"),
        os.path.join(project_root, "output", "svg_to_video", "videos")
    ]
    
    for output_dir in output_dirs:
        try:
            print(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {output_dir}: {e}")
    
    # Create symlinks for backward compatibility
    symlinks = [
        (os.path.join(project_root, "output", "svg_to_video", "svg"), 
         os.path.join(project_root, "output", "svg")),
        (os.path.join(project_root, "output", "svg_to_video", "models"), 
         os.path.join(project_root, "output", "models")),
        (os.path.join(project_root, "output", "svg_to_video", "animations"), 
         os.path.join(project_root, "output", "animations")),
        (os.path.join(project_root, "output", "svg_to_video", "videos"), 
         os.path.join(project_root, "output", "videos"))
    ]
    
    for target, link_name in symlinks:
        try:
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(link_name), exist_ok=True)
            
            # If the link already exists, remove it
            if os.path.exists(link_name):
                if os.path.islink(link_name):
                    os.unlink(link_name)
                else:
                    # If it's a directory, move its contents to the target
                    if os.path.isdir(link_name):
                        for item in os.listdir(link_name):
                            src = os.path.join(link_name, item)
                            dst = os.path.join(target, item)
                            if not os.path.exists(dst):
                                if os.path.isdir(src):
                                    shutil.copytree(src, dst)
                                else:
                                    shutil.copy2(src, dst)
                        shutil.rmtree(link_name)
            
            # Create the symlink
            print(f"Creating symlink: {link_name} -> {target}")
            # Use directory junction on Windows
            if sys.platform == "win32":
                os.system(f'mklink /J "{link_name}" "{target}"')
            else:
                os.symlink(target, link_name, target_is_directory=True)
        except Exception as e:
            print(f"Error creating symlink {link_name}: {e}")
    
    print("\nCleanup completed successfully!")
    print("The SVG to Video module has been organized and deprecated files have been removed.")
    print("Output directories have been created and symlinks have been set up for backward compatibility.")

if __name__ == "__main__":
    main()
