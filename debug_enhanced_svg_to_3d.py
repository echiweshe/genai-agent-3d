"""
Debug script for the enhanced SVG to 3D converter
This script runs outside of Blender to help identify issues
"""

import subprocess
import os
import sys
import tempfile
import traceback

def debug_script(svg_path):
    # Create a temporary Python script to check if SVGParser class can be initialized
    temp_script = os.path.join(tempfile.gettempdir(), "debug_svg_parser.py")
    
    debug_code = f"""
import sys
import traceback

# Add the current directory to the path
sys.path.append('.')

try:
    # Import XML parser to check if SVG can be parsed
    import xml.etree.ElementTree as ET
    print("XML module loaded successfully")
    
    # Try to parse the SVG file
    tree = ET.parse('{svg_path}')
    root = tree.getroot()
    print(f"Successfully parsed SVG file. Root tag: {{root.tag}}")
    
    # Print SVG dimensions
    width = root.attrib.get('width', '800')
    height = root.attrib.get('height', '600')
    print(f"SVG dimensions: {{width}}x{{height}}")
    
    # Print child elements
    print("\\nSVG child elements:")
    for child in root:
        print(f"- {{child.tag}}")
    
except Exception as e:
    print(f"Error testing SVG parsing: {{e}}")
    traceback.print_exc()
    sys.exit(1)

print("\\nDebug completed successfully")
"""
    
    with open(temp_script, 'w') as f:
        f.write(debug_code)
    
    print(f"Running debug script for SVG: {svg_path}")
    subprocess.run([sys.executable, temp_script])

def run_with_verbose_output(blender_path, script_path, svg_path, output_path):
    """Run Blender with verbose output and capture any errors"""
    
    # Create temporary script that adds error handling
    temp_script = os.path.join(tempfile.gettempdir(), "error_handler.py")
    
    wrapper_code = f"""
import sys
import traceback

print("Starting enhanced SVG to 3D conversion with error handling")

try:
    print(f"Python version: {{sys.version}}")
    print(f"Python path: {{sys.path}}")
    
    print("\\nLoading script: {script_path}")
    
    # Execute the enhanced SVG to 3D script
    with open("{script_path}", "r") as f:
        script_code = f.read()
    
    # Add command line arguments
    sys.argv = ["{script_path}", "--", "--svg", "{svg_path}", "--output", "{output_path}", "--debug"]
    
    print(f"\\nCommand line arguments: {{sys.argv}}")
    
    try:
        exec(script_code)
        print("Script execution completed")
    except Exception as e:
        print(f"\\nERROR during script execution: {{e}}")
        traceback.print_exc()
        sys.exit(1)
        
except Exception as e:
    print(f"\\nERROR in wrapper: {{e}}")
    traceback.print_exc()
    sys.exit(1)

print("\\nComplete")
"""
    
    with open(temp_script, "w") as f:
        f.write(wrapper_code)
    
    print(f"Running Blender with verbose error handling...")
    cmd = [blender_path, "--background", "--python", temp_script]
    
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    stdout, stderr = process.communicate()
    
    print("\n--- STDOUT ---")
    print(stdout)
    
    print("\n--- STDERR ---")
    print(stderr)
    
    print(f"\nBlender process exit code: {process.returncode}")
    
    return process.returncode == 0

if __name__ == "__main__":
    # Define file paths
    blender_path = r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
    script_path = r".\genai_agent\scripts\enhanced_svg_to_3d_blender.py"
    
    # Test with a simple SVG
    test_svg_dir = "./outputs/enhanced_svg_test"
    os.makedirs(test_svg_dir, exist_ok=True)
    
    svg_path = os.path.join(test_svg_dir, "debug_test.svg")
    output_path = os.path.join(test_svg_dir, "debug_test.blend")
    
    # Create a simple test SVG
    simple_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <rect x="100" y="100" width="100" height="100" fill="red" />
  <circle cx="300" cy="150" r="50" fill="blue" />
</svg>"""
    
    with open(svg_path, "w") as f:
        f.write(simple_svg)
    
    print(f"Created test SVG at: {svg_path}")
    
    # First run a basic debug on the SVG file itself
    debug_script(svg_path)
    
    # Then try running the full script with error handling
    success = run_with_verbose_output(blender_path, script_path, svg_path, output_path)
    
    if success:
        print(f"Successfully generated 3D model at: {output_path}")
    else:
        print(f"Failed to generate 3D model")
