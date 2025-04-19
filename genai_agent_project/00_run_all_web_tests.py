#!/usr/bin/env python
"""
Run all web tests for GenAI Agent 3D project.
This script runs all the web-related tests: backend, frontend, and end-to-end.
"""
import os
import subprocess
import platform
import sys
import time
import argparse
import io
import locale

def run_command(cmd, cwd=None, env=None, encoding=None):
    """
    Run a command and stream output to the console.
    
    Args:
        cmd: Command as a list of arguments or string
        cwd: Working directory
        env: Environment variables
        encoding: Force a specific encoding for output
    
    Returns:
        Exit code of the command
    """
    if isinstance(cmd, list):
        print(f"Running command: {' '.join(cmd)}")
    else:
        print(f"Running command: {cmd}")
    
    # Create environment with system PATH
    if env is None:
        env = os.environ.copy()
    
    try:
        # Handle Windows vs Unix differences
        if platform.system() == "Windows":
            # On Windows, we need to handle encoding issues
            if encoding is None:
                encoding = locale.getpreferredencoding()
            
            if isinstance(cmd, list):
                # For Windows, convert list to string with proper quoting
                cmd_str = ""
                for arg in cmd:
                    if ' ' in arg and not (arg.startswith('"') and arg.endswith('"')):
                        cmd_str += f'"{arg}" '
                    else:
                        cmd_str += f'{arg} '
                cmd = cmd_str.strip()
            
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=env
            )
        else:
            # On Unix, use list form for better argument handling
            if isinstance(cmd, str):
                cmd = cmd.split()
            process = subprocess.Popen(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=env
            )
        
        # Stream output with encoding handling
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            try:
                if encoding:
                    line_str = line.decode(encoding, errors='replace')
                else:
                    line_str = line.decode(errors='replace')
                print(line_str, end='')
            except Exception as e:
                print(f"[Output decoding error: {e}]")
        
        # Wait for completion
        process.wait()
        return process.returncode
    
    except KeyboardInterrupt:
        print("\nCommand interrupted by user.")
        return 130
    
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1

def install_pytest(python_exe):
    """Install pytest using pip"""
    print("Installing pytest...")
    cmd = [python_exe, "-m", "pip", "install", "pytest"]
    return run_command(cmd) == 0

def run_backend_tests(backend_dir, python_exe):
    """Run backend tests with proper handling"""
    # First try to install pytest if needed
    try:
        # Check if pytest is installed
        check_cmd = [python_exe, "-c", "import pytest; print('pytest installed')"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        
        if "pytest installed" not in result.stdout:
            if not install_pytest(python_exe):
                print("Failed to install pytest. Skipping backend tests.")
                return False
    except:
        if not install_pytest(python_exe):
            print("Failed to install pytest. Skipping backend tests.")
            return False
    
    # Run the backend tests
    print(f"Running backend tests in: {backend_dir}")
    cmd = [python_exe, "-m", "pytest", "-xvs", "tests/"]
    exit_code = run_command(cmd, cwd=backend_dir)
    
    if exit_code != 0:
        print(f"Backend tests failed with exit code {exit_code}")
        return False
    return True

def run_frontend_tests(frontend_dir):
    """Run frontend tests with proper encoding handling"""
    if os.path.exists(os.path.join(frontend_dir, "package.json")):
        print(f"Running frontend tests in: {frontend_dir}")
        
        # Force the cp1252 encoding for Windows
        encoding = "cp1252" if platform.system() == "Windows" else None
        
        # Use 'npm.cmd' on Windows
        npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
        cmd = [npm_cmd, "test", "--", "--watchAll=false"]
        
        exit_code = run_command(cmd, cwd=frontend_dir, encoding=encoding)
        
        if exit_code != 0:
            print(f"Frontend tests failed with exit code {exit_code}")
            return False
        return True
    else:
        print("No package.json found in frontend directory")
        return False

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run web tests for GenAI Agent 3D project")
    parser.add_argument("--no-backend", action="store_true", help="Skip backend tests")
    parser.add_argument("--no-frontend", action="store_true", help="Skip frontend tests")
    parser.add_argument("--no-e2e", action="store_true", help="Skip end-to-end tests")
    parser.add_argument("--port", type=int, default=8000, help="Port for the backend server")
    args = parser.parse_args()
    
    # Get the project root directory
    project_dir = os.getcwd()
    
    # Navigate to the web directory
    web_dir = os.path.join(project_dir, "web")
    if not os.path.exists(web_dir):
        print(f"Error: Web directory not found at {web_dir}")
        return 1
    
    # Track test success
    all_tests_pass = True
    
    # Run backend tests
    if not args.no_backend:
        print("\n" + "="*80)
        print("=" + " BACKEND TESTS ".center(78, "="))
        print("="*80)
        
        backend_dir = os.path.join(web_dir, "backend")
        python_exe = sys.executable
        
        if os.path.exists(backend_dir):
            if not run_backend_tests(backend_dir, python_exe):
                all_tests_pass = False
        else:
            print(f"Backend directory not found at {backend_dir}")
            all_tests_pass = False
    
    # Run frontend tests
    if not args.no_frontend:
        print("\n" + "="*80)
        print("=" + " FRONTEND TESTS ".center(78, "="))
        print("="*80)
        
        frontend_dir = os.path.join(web_dir, "frontend")
        
        if os.path.exists(frontend_dir):
            if not run_frontend_tests(frontend_dir):
                all_tests_pass = False
        else:
            print(f"Frontend directory not found at {frontend_dir}")
            all_tests_pass = False
    
    # Run e2e tests
    if not args.no_e2e:
        print("\n" + "="*80)
        print("=" + " END-TO-END TESTS ".center(78, "="))
        print("="*80)
        
        e2e_dir = os.path.join(web_dir, "e2e")
        
        if os.path.exists(e2e_dir):
            # Look for test files recursively
            test_files = []
            for root, _, files in os.walk(e2e_dir):
                for file in files:
                    if file.endswith('.spec.js') or file.endswith('.test.js'):
                        test_files.append(os.path.join(root, file))
            
            if not test_files:
                print("No test files found in e2e directory. Skipping e2e tests.")
                print("Note: E2E tests should have .spec.js or .test.js extensions.")
            else:
                print(f"Found {len(test_files)} test files in e2e directory.")
                
                # Try to set up Node.js environment for E2E tests
                npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
                npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
                
                # Initialize package.json if needed
                if not os.path.exists(os.path.join(e2e_dir, "package.json")):
                    print("Initializing npm in e2e directory...")
                    run_command([npm_cmd, "init", "-y"], cwd=e2e_dir)
                
                # Install Playwright if needed
                if not os.path.exists(os.path.join(e2e_dir, "node_modules", "@playwright")):
                    print("Installing Playwright...")
                    run_command([npm_cmd, "install", "--save-dev", "@playwright/test"], cwd=e2e_dir)
                    run_command([npx_cmd, "playwright", "install"], cwd=e2e_dir)
                
                # Run the tests
                print("Running Playwright tests...")
                cmd = [npx_cmd, "playwright", "test"]
                exit_code = run_command(cmd, cwd=e2e_dir)
                
                if exit_code != 0:
                    print(f"E2E tests failed with exit code {exit_code}")
                    all_tests_pass = False
        else:
            print(f"E2E directory not found at {e2e_dir}")
            all_tests_pass = False
    
    # Summary
    print("\n" + "="*80)
    if all_tests_pass:
        print("\nAll web tests completed successfully! ✅")
        return 0
    else:
        print("\nSome tests failed. Please check the logs above for details. ❌")
        return 1

if __name__ == "__main__":
    # Add a short pause to make sure any console output is visible
    print("Starting test execution in 2 seconds...")
    time.sleep(2)
    
    try:
        # Run the main function
        exit_code = main()
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        exit_code = 130
    except Exception as e:
        print(f"\nError during test execution: {e}")
        exit_code = 1
    
    # On Windows, add a pause at the end if running in a console
    if platform.system() == "Windows" and sys.stdout.isatty():
        input("\nPress Enter to exit...")
    
    sys.exit(exit_code)
