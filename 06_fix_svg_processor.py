#!/usr/bin/env python
"""
Fix SVG Processor Script

This script fixes issues with backslashes in f-strings in the svg_processor.py file.
"""

import os
import re
import sys

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
svg_processor_path = os.path.join(project_dir, "genai_agent", "tools", "svg_processor.py")

print("=" * 80)
print("GenAI Agent 3D - SVG Processor Fixer".center(80))
print("=" * 80)
print()

if not os.path.exists(svg_processor_path):
    print(f"❌ SVG Processor file not found at: {svg_processor_path}")
    print("Creating a simple SVG processor stub...")
    
    # Create the tools directory if it doesn't exist
    os.makedirs(os.path.join(project_dir, "genai_agent", "tools"), exist_ok=True)
    
    # Create a stub SVG processor
    svg_processor_stub = """
'''
SVG Processor - Processes and converts SVG files into 3D models
'''

import os
import logging
import tempfile
import subprocess
from pathlib import Path
from ..config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

class SVGProcessor:
    '''Tool for processing SVG files'''
    
    def __init__(self):
        '''Initialize SVG processor'''
        self.settings = get_settings()
        self.name = "svg_processor"
        self.description = "Process SVG files and convert them to 3D models"
        
    def process_svg(self, svg_content, output_format="obj"):
        '''
        Process SVG content and convert to specified 3D format
        
        Args:
            svg_content: SVG content as string
            output_format: Output format (obj, stl, etc.)
            
        Returns:
            Path to output file
        '''
        logger.info(f"Processing SVG to {output_format}")
        
        # Create temporary SVG file
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp_svg:
            tmp_svg.write(svg_content.encode('utf-8'))
            svg_path = tmp_svg.name
        
        # Create output file path
        output_path = f"{svg_path[:-4]}.{output_format}"
        
        # Here we would normally convert the SVG to 3D
        # For now, just create an empty output file
        with open(output_path, 'w') as f:
            f.write(f"# SVG Conversion Result\\n")
            f.write(f"# Original SVG: {svg_path}\\n")
            f.write(f"# This is a placeholder {output_format} file\\n")
        
        # Clean up temporary SVG file
        try:
            os.unlink(svg_path)
        except:
            pass
        
        return output_path

def register_tool(agent):
    '''Register SVG processor tool with agent'''
    tool = SVGProcessor()
    agent.register_tool(tool.name, tool)
    logger.info("Registered tool: svg_processor")
    return tool
"""
    
    with open(svg_processor_path, "w") as f:
        f.write(svg_processor_stub)
    
    print(f"✅ Created SVG processor stub at: {svg_processor_path}")
    sys.exit(0)

# If the file exists, fix the f-string issues
print(f"Found SVG Processor at: {svg_processor_path}")
print("Checking for f-string issues...")

with open(svg_processor_path, "r", errors="replace") as f:
    content = f.read()

# Find all f-strings with backslashes
matches = re.findall(r'f"[^"\\]*\\[^"]*"', content)
matches.extend(re.findall(r"f'[^'\\]*\\[^']*'", content))

if matches:
    print(f"Found {len(matches)} f-strings with backslashes:")
    for i, match in enumerate(matches):
        print(f"  {i+1}. {match}")
        
        # Replace backslashes with double backslashes in f-strings
        fixed_match = match.replace("\\", "\\\\")
        content = content.replace(match, fixed_match)
    
    # Write fixed content back to file
    with open(svg_processor_path, "w") as f:
        f.write(content)
    
    print(f"✅ Fixed {len(matches)} f-string issues in: {svg_processor_path}")
else:
    print("✅ No f-string issues found, file is clean.")

print("\nSVG Processor fixes completed!")
