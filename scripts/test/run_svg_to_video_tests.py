"""
Run SVG to Video Tests

This script runs all the tests for the SVG to Video pipeline.
"""

import os
import sys
import unittest
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def discover_and_run_tests(test_path, pattern="test_*.py"):
    """Discover and run tests in the specified path."""
    print(f"\n{'='*80}")
    print(f"Running tests in: {test_path}")
    print(f"{'='*80}\n")
    
    if not os.path.exists(test_path):
        print(f"Test path not found: {test_path}")
        return False
    
    # Discover tests
    test_suite = unittest.defaultTestLoader.discover(
        start_dir=test_path,
        pattern=pattern
    )
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """Run all SVG to Video tests."""
    # Base path for SVG to Video tests
    base_path = os.path.join(project_root, "tests", "svg_to_video")
    
    # Test directories
    test_dirs = [
        os.path.join(base_path, "svg_generator"),
        os.path.join(base_path, "svg_to_3d"),
        os.path.join(base_path, "animation"),
        os.path.join(base_path, "rendering"),
        os.path.join(base_path, "pipeline")
    ]
    
    # Run tests in each directory
    success = True
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            dir_success = discover_and_run_tests(test_dir)
            success = success and dir_success
    
    return success

def run_specific_module(module_name):
    """Run tests for a specific module."""
    base_path = os.path.join(project_root, "tests", "svg_to_video")
    
    # Map module names to test directories
    module_dirs = {
        "svg_generator": os.path.join(base_path, "svg_generator"),
        "svg_to_3d": os.path.join(base_path, "svg_to_3d"),
        "animation": os.path.join(base_path, "animation"),
        "rendering": os.path.join(base_path, "rendering"),
        "pipeline": os.path.join(base_path, "pipeline")
    }
    
    if module_name not in module_dirs:
        print(f"Unknown module: {module_name}")
        print(f"Available modules: {', '.join(module_dirs.keys())}")
        return False
    
    # Run tests for the specified module
    return discover_and_run_tests(module_dirs[module_name])

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run SVG to Video tests")
    parser.add_argument(
        "--module", "-m",
        choices=["svg_generator", "svg_to_3d", "animation", "rendering", "pipeline"],
        help="Test a specific module"
    )
    
    args = parser.parse_args()
    
    # Create test output directories
    os.makedirs(os.path.join(project_root, "output", "test_results"), exist_ok=True)
    
    # Run tests
    if args.module:
        success = run_specific_module(args.module)
    else:
        success = run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
