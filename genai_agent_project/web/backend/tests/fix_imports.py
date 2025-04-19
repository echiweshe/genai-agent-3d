"""
This script fixes import issues in the test suite by adding the project root to sys.path.
Import this at the beginning of conftest.py to resolve module import errors.
"""
import os
import sys

# Get the project root directory (two levels up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Add project root to the path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to sys.path")

# Print the current path for debugging
print(f"sys.path now includes: {sys.path}")
