#!/usr/bin/env python
"""
Test Scene Output

This script tests scene generation and verifies that scenes are properly saved
to the output/scenes directory, with debugging to track the scene generation path.
"""

import os
import sys
import time
import json
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_scene_output")

def ensure_scenes_directory():
    """Make sure the output/scenes directory exists"""
    scenes_dir = os.path.join(os.path.dirname(__file__), 'output', 'scenes')
    os.makedirs(scenes_dir, exist_ok=True)
    logger.info(f"Ensured scenes directory exists: {scenes_dir}")
    return scenes_dir

def count_files_in_directory(directory):
    """Count the number of files in a directory"""
    count = 0
    for _, _, files in os.walk(directory):
        count += len(files)
    return count

def test_scene_generation():
    """Test scene generation and verify output"""
    # Make sure scenes directory exists
    scenes_dir = ensure_scenes_directory()
    
    # Count files before generation
    files_before = count_files_in_directory(scenes_dir)
    logger.info(f"Found {files_before} files in scenes directory before test")
    
    # Patch the scene_generator.py file temporarily to add debug output
    scene_generator_path = os.path.join(os.path.dirname(__file__), 'genai_agent', 'tools', 'scene_generator.py')
    
    if os.path.exists(scene_generator_path):
        # Backup the original file
        backup_path = f"{scene_generator_path}.bak"
        shutil.copy2(scene_generator_path, backup_path)
        logger.info(f"Backed up scene_generator.py to {backup_path}")
        
        # Read the file
        with open(scene_generator_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add debug logging to track where scenes are saved
        debug_code = '''
    def _save_scene(self, scene_data):
        """Save a scene to a file with debug logging"""
        try:
            import os
            import json
            from datetime import datetime
            
            # Get the output directory
            output_dir = self.parameters.get('output_dir', 'output')
            
            # Make sure it's an absolute path
            if not os.path.isabs(output_dir):
                output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), output_dir)
            
            # Create the directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate a filename based on the scene name and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            scene_name = scene_data.get('scene_name', 'unnamed_scene')
            filename = f"{scene_name}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Print debug information
            print(f"\\n[DEBUG] Saving scene to {filepath}")
            print(f"[DEBUG] Output directory: {output_dir}")
            print(f"[DEBUG] Current directory: {os.getcwd()}")
            print(f"[DEBUG] Directory exists: {os.path.exists(output_dir)}")
            
            # Save the scene to a file
            with open(filepath, 'w') as f:
                json.dump(scene_data, f, indent=2)
            
            print(f"[DEBUG] Successfully saved scene to {filepath}")
            
            return filepath
        except Exception as e:
            print(f"[DEBUG] Error saving scene: {e}")
            import traceback
            print(traceback.format_exc())
            return None
        '''
        
        # Add or replace the _save_scene method
        if '_save_scene' in content:
            # Replace the existing method
            import re
            content = re.sub(r'def _save_scene\(self, scene_data\):.*?(?=def|\Z)', 
                         debug_code, content, flags=re.DOTALL)
        else:
            # Add the method to the end of the class
            class_end = content.rfind('class')
            class_end = content.find(':', class_end)
            indent = 4  # Assuming standard 4-space indentation
            
            # Find the next class or end of file
            next_class = content.find('class', class_end + 1)
            if next_class == -1:
                next_class = len(content)
            
            # Insert the method before the next class or end of file
            content = content[:next_class] + '\n' + ' ' * indent + debug_code + '\n' + content[next_class:]
        
        # Write the modified file
        with open(scene_generator_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Added debug logging to scene_generator.py")
    
    # Run the scene generation test
    try:
        logger.info("Running scene generation test...")
        
        # Set environment variables to ensure using llama3
        os.environ["LLM_MODEL"] = "llama3"
        
        # Import and run the test
        sys.path.insert(0, os.path.dirname(__file__))
        from examples.test_scene_generation import main as run_test_scene_generation
        
        # Run the test
        run_test_scene_generation()
        
        # Wait a moment for files to be written
        time.sleep(2)
        
        # Count files after generation
        files_after = count_files_in_directory(scenes_dir)
        logger.info(f"Found {files_after} files in scenes directory after test")
        
        if files_after > files_before:
            logger.info(f"Success! {files_after - files_before} new scene files were created.")
        else:
            logger.warning("No new scene files were created in the scenes directory.")
            logger.info("Let's check the main output directory for scene files...")
            
            # Check the main output directory
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith('.json') and ('scene' in file.lower() or 'mountain' in file.lower()):
                        filepath = os.path.join(root, file)
                        logger.info(f"Found potential scene file: {filepath}")
                        
                        # Copy to scenes directory
                        dest_path = os.path.join(scenes_dir, file)
                        shutil.copy2(filepath, dest_path)
                        logger.info(f"Copied to scenes directory: {dest_path}")
        
        logger.info("Test complete!")
    
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        # Restore the original scene_generator.py file
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, scene_generator_path)
            logger.info("Restored original scene_generator.py")
            os.remove(backup_path)

if __name__ == "__main__":
    test_scene_generation()
