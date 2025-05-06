"""
Fix mathutils import issue for SVG to 3D conversion.
This script ensures the mathutils stub module is properly importable.
"""

import os
import sys
import shutil
from pathlib import Path

# Define paths
PROJECT_ROOT = Path("C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d")
SVG_TO_3D_DIR = PROJECT_ROOT / "genai_agent_project" / "genai_agent" / "svg_to_video" / "svg_to_3d"
MATHUTILS_PATH = SVG_TO_3D_DIR / "mathutils.py"
INIT_PATH = SVG_TO_3D_DIR / "__init__.py"

# Create __init__.py if it doesn't exist
if not os.path.exists(INIT_PATH):
    print(f"Creating __init__.py at {INIT_PATH}")
    with open(INIT_PATH, 'w', encoding='utf-8') as f:
        f.write('"""SVG to 3D conversion module."""\n\n')
        f.write('# Import mathutils stub to make it available when importing svg_to_3d\n')
        f.write('try:\n')
        f.write('    import mathutils\n')
        f.write('except ImportError:\n')
        f.write('    # Use internal stub if mathutils is not installed\n')
        f.write('    from . import mathutils\n')

# Check if mathutils.py exists and has content
if not os.path.exists(MATHUTILS_PATH):
    print(f"ERROR: mathutils.py not found at {MATHUTILS_PATH}")
    sys.exit(1)

# Create a site-packages mathutils directory in venv if needed
VENV_DIR = PROJECT_ROOT / "genai_agent_project" / "venv"
if os.path.exists(VENV_DIR):
    SITE_PACKAGES_DIR = None
    
    # Find site-packages directory
    possible_dirs = [
        VENV_DIR / "Lib" / "site-packages",
        VENV_DIR / "lib" / "python3.9" / "site-packages",
        VENV_DIR / "lib" / "python3.10" / "site-packages",
        VENV_DIR / "lib" / "python3.11" / "site-packages",
    ]
    
    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            SITE_PACKAGES_DIR = dir_path
            break
    
    if SITE_PACKAGES_DIR:
        MATHUTILS_SITE_DIR = SITE_PACKAGES_DIR / "mathutils"
        MATHUTILS_SITE_INIT = MATHUTILS_SITE_DIR / "__init__.py"
        
        # Create mathutils package directory if it doesn't exist
        if not os.path.exists(MATHUTILS_SITE_DIR):
            print(f"Creating mathutils package directory at {MATHUTILS_SITE_DIR}")
            os.makedirs(MATHUTILS_SITE_DIR, exist_ok=True)
        
        # Copy mathutils content to __init__.py
        print(f"Copying mathutils stub to {MATHUTILS_SITE_INIT}")
        with open(MATHUTILS_PATH, 'r', encoding='utf-8') as src:
            with open(MATHUTILS_SITE_INIT, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        # Create setup.py for the mathutils package
        SETUP_PY = MATHUTILS_SITE_DIR.parent / "mathutils_setup.py"
        print(f"Creating setup.py at {SETUP_PY}")
        with open(SETUP_PY, 'w', encoding='utf-8') as f:
            f.write('from setuptools import setup, find_packages\n\n')
            f.write('setup(\n')
            f.write('    name="mathutils",\n')
            f.write('    version="0.1.0",\n')
            f.write('    description="Stub package for Blender\'s mathutils module",\n')
            f.write('    packages=["mathutils"],\n')
            f.write(')\n')
        
        print(f"mathutils stub module installed to site-packages")
    else:
        print(f"WARNING: Could not find site-packages directory in venv")

print("Fix complete. Please run 'pip install -e .' in the mathutils package directory if needed.")
