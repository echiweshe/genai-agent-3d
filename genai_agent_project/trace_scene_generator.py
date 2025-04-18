#!/usr/bin/env python
"""
Trace Scene Generator Output

This script directly modifies the scene generator to add extensive logging,
then runs a simple scene generation test to trace where files are being saved.
"""

import os
import sys
import logging
import traceback
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("scene_trace.log"), logging.StreamHandler()]
)
logger = logging.getLogger("trace_scene")

def patch_scene_generator():
    """Add debug logging to the scene generator"""
    # Find the scene_generator.py file
    scene_generator_path = os.path.join(
        os.path.dirname(__file__), 
        'genai_agent', 
        'tools', 
        'scene_generator.py'
    )
    
    if not os.path.exists(scene_generator_path):
        logger.error(f"Scene generator not found at {scene_generator_path}")
        return False
    
    # Create a backup
    backup_path = f"{scene_generator_path}.trace.bak"
    shutil.copy2(scene_generator_path, backup_path)
    logger.info(f"Backed up scene_generator.py to {backup_path}")
    
    # Read the file
    with open(scene_generator_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add logging to key methods
    debug_statements = [
        ("def __init__", "        print(f\"[TRACE] Scene Generator initialized with parameters: {parameters}\")\n"),
        ("def generate_scene", "        print(f\"[TRACE] Generating scene with description: {description}, style: {style}, name: {name}\")\n"),
        ("return scene_result", "        print(f\"[TRACE] Scene generation result: {scene_result}\")\n"),
        ("def _generate_with_llm", "        print(f\"[TRACE] Generating with LLM, prompt length: {len(prompt)}\")\n"),
        ("def _extract_json", "        print(f\"[TRACE] Extracting JSON from LLM response of length: {len(response) if response else 0}\")\n"),
        ("def _create_fallback_scene", "        print(f\"[TRACE] Creating fallback scene with description: {description}, style: {style}, name: {name}\")\n"),
        ("scene_id = None", "        # Add file saving\n        self._save_scene_to_file(scene_result)\n"),
    ]
    
    for marker, debug_code in debug_statements:
        pos = content.find(marker)
        if pos != -1:
            # Find the end of the line
            line_end = content.find('\n', pos)
            if line_end != -1:
                # Insert after the line
                content = content[:line_end+1] + debug_code + content[line_end+1:]
    
    # Add a method to explicitly save scene to file
    save_method = """
    def _save_scene_to_file(self, scene_data):
        \"\"\"Save scene to a file in the output/scenes directory\"\"\"
        try:
            # Make sure we have a scenes directory
            scenes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'output', 'scenes')
            os.makedirs(scenes_dir, exist_ok=True)
            
            # Generate a filename
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            scene_name = scene_data.get('scene_name', 'unnamed_scene')
            filename = f"{scene_name}_{timestamp}.json"
            filepath = os.path.join(scenes_dir, filename)
            
            # Log information
            print(f"[TRACE] Saving scene to file: {filepath}")
            print(f"[TRACE] Scene data: {scene_data}")
            print(f"[TRACE] Scenes directory exists: {os.path.exists(scenes_dir)}")
            print(f"[TRACE] Current working directory: {os.getcwd()}")
            
            # Write to file
            import json
            with open(filepath, 'w') as f:
                json.dump(scene_data, f, indent=2)
            
            print(f"[TRACE] Successfully saved scene to: {filepath}")
            return filepath
        except Exception as e:
            print(f"[TRACE] Error saving scene to file: {str(e)}")
            print(traceback.format_exc())
            return None
"""
    
    # Add the save method to the class
    class_end = content.find("class SceneGeneratorTool")
    if class_end != -1:
        # Find the next class or end of file
        next_class = content.find("class ", class_end + 1)
        if next_class == -1:
            next_class = len(content)
        
        # Insert the method before the next class
        content = content[:next_class] + save_method + content[next_class:]
    
    # Add os import if not present
    if "import os" not in content:
        content = "import os\nimport traceback\n" + content
    
    # Write the modified file
    with open(scene_generator_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info("Added debug logging to scene_generator.py")
    return True

def create_scenes_directory():
    """Create the output/scenes directory"""
    scenes_dir = os.path.join(os.path.dirname(__file__), 'output', 'scenes')
    os.makedirs(scenes_dir, exist_ok=True)
    logger.info(f"Created scenes directory: {scenes_dir}")
    
    # Create a test file to verify permissions
    test_file = os.path.join(scenes_dir, "test_permissions.txt")
    try:
        with open(test_file, 'w') as f:
            f.write("This is a test file to verify write permissions.")
        logger.info(f"Successfully wrote test file: {test_file}")
        os.remove(test_file)
    except Exception as e:
        logger.error(f"Error writing to scenes directory: {e}")
        return False
    
    return True

def run_simple_scene_test():
    """Run a simple scene generation test"""
    try:
        logger.info("Running simple scene generation test...")
        
        # Set environment variables
        os.environ["LLM_MODEL"] = "llama3"
        
        # Create a simple test script
        test_file = os.path.join(os.path.dirname(__file__), 'simple_scene_test.py')
        with open(test_file, 'w') as f:
            f.write("""
import os
import sys
from genai_agent.tools.scene_generator import SceneGeneratorTool

def main():
    # Initialize the scene generator
    scene_generator = SceneGeneratorTool(parameters={'output_dir': 'output/scenes'})
    
    # Generate a scene
    print("\\nGenerating scene...")
    result = scene_generator.generate_scene(
        description="A simple test scene with a mountain landscape", 
        style="basic", 
        name="TestScene"
    )
    
    print(f"\\nGeneration result: {result}")
    
    # Check output directory
    scenes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output', 'scenes')
    print(f"\\nScenes directory: {scenes_dir}")
    print(f"Directory exists: {os.path.exists(scenes_dir)}")
    
    if os.path.exists(scenes_dir):
        files = os.listdir(scenes_dir)
        print(f"Files in directory: {files}")
    
    print("\\nTest complete!")

if __name__ == "__main__":
    main()
""")
        
        # Run the test
        logger.info("Executing simple scene test...")
        import subprocess
        result = subprocess.run(
            [sys.executable, test_file], 
            capture_output=True, 
            text=True,
            env=os.environ
        )
        
        logger.info(f"Test exit code: {result.returncode}")
        logger.info(f"Test stdout: {result.stdout}")
        logger.info(f"Test stderr: {result.stderr}")
        
        # Clean up
        os.remove(test_file)
        
        return result.returncode == 0
    
    except Exception as e:
        logger.error(f"Error running test: {e}")
        logger.error(traceback.format_exc())
        return False

def restore_scene_generator(backup_path):
    """Restore the original scene generator"""
    scene_generator_path = os.path.join(
        os.path.dirname(__file__), 
        'genai_agent', 
        'tools', 
        'scene_generator.py'
    )
    
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, scene_generator_path)
        logger.info(f"Restored original scene_generator.py from {backup_path}")
        os.remove(backup_path)
        return True
    
    logger.error(f"Backup file not found: {backup_path}")
    return False

def check_scene_files():
    """Check for scene files in various locations"""
    # Check the scenes directory
    scenes_dir = os.path.join(os.path.dirname(__file__), 'output', 'scenes')
    scene_files = []
    
    if os.path.exists(scenes_dir):
        for file in os.listdir(scenes_dir):
            if file.endswith('.json'):
                scene_files.append(os.path.join(scenes_dir, file))
    
    # Check other potential locations
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.json') and os.path.join(root, file) not in scene_files:
                scene_files.append(os.path.join(root, file))
    
    if scene_files:
        logger.info(f"Found {len(scene_files)} scene files:")
        for file in scene_files:
            logger.info(f"  {file}")
        
        # Copy all scene files to scenes directory
        for file in scene_files:
            if os.path.dirname(file) != scenes_dir:
                dest = os.path.join(scenes_dir, os.path.basename(file))
                shutil.copy2(file, dest)
                logger.info(f"Copied to scenes directory: {dest}")
    else:
        logger.warning("No scene files found in any output directory")

def main():
    """Main function"""
    logger.info("Starting scene generator trace...")
    
    # Create the scenes directory
    if not create_scenes_directory():
        logger.error("Failed to create scenes directory")
        return
    
    # Patch the scene generator
    backup_path = os.path.join(
        os.path.dirname(__file__), 
        'genai_agent', 
        'tools', 
        'scene_generator.py.trace.bak'
    )
    
    try:
        if not patch_scene_generator():
            logger.error("Failed to patch scene generator")
            return
        
        # Run the test
        if not run_simple_scene_test():
            logger.warning("Scene test did not complete successfully")
        
        # Check for scene files
        check_scene_files()
    
    finally:
        # Restore the original scene generator
        restore_scene_generator(backup_path)
    
    logger.info("Scene generator trace complete")

if __name__ == "__main__":
    main()
