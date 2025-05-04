"""
Standalone test runner for SVG to 3D converter
Run this with Blender from command line:
blender --background --python run_test.py
"""

import os
import sys
import bpy

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import and run the test
from test_converter import main

if __name__ == "__main__":
    main()
