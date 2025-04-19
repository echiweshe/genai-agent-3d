"""
Master script to run all tests for the GenAI Agent 3D web application
"""

import os
import sys
import argparse
import subprocess
import time
import platform

# Paths
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
E2E_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "e2e")

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def run_command(command, cwd=None, env=None):
    """Run a command and return success status"""
    print(f"Running command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            env=env,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False

def run_manual_websocket_test(args):
    """Run the manual WebSocket test"""
    print_header("MANUAL WEBSOCKET TEST")
    
    # Start the server in test mode
    print("Starting server in test mode...")
    server_cmd = [sys.executable, "run_server.py", "--test-mode"]
    if args.port:
        server_cmd.extend(["--port", str(args.port)])
    
    server_process = None
    try:
        server_process = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=BACKEND_DIR
        )
        
        # Give the server a moment to start
        time.sleep(3)
        
        if server_process.poll() is not None:
            print("Error: Failed to start backend server")
            stdout, stderr = server_process.communicate()
            print("STDOUT:", stdout.decode())
            print("STDERR:", stderr.decode())
            return False
        
        print("Server started successfully. Running WebSocket test...")
        
        # Run the manual WebSocket test
        test_cmd = [sys.executable, "tests/manual_websocket_test.py"]
        if args.port:
            test_cmd.extend(["--port", str(args.port)])
        
        if args.verbose:
            test_cmd.append("--verbose")
        
        cmd = " ".join(test_cmd)
        success = run_command(cmd, cwd=BACKEND_DIR)
        return success
    
    finally:
        # Stop the server
        if server_process and server_process.poll() is None:
            print("Stopping server...")
            if platform.system() == "Windows":
                # On Windows, we need to use taskkill to forcefully terminate the process
                subprocess.run(f"taskkill /F /PID {server_process.pid}", shell=True)
            else:
                server_process.terminate()
                server_process.wait(timeout=5)
            print("Server stopped")

def run_backend_tests(args):
    """Run backend tests"""
    print_header("BACKEND TESTS")
    
    test_cmd = [sys.executable, "run_tests.py"]
    
    if args.unit_only:
        test_cmd.append("--unit")
    elif args.extended_only:
        test_cmd.append("--extended")
    elif args.websocket_only:
        test_cmd.append("--websocket")
    else:
        test_cmd.append("--all")
    
    if args.port:
        test_cmd.extend(["--port", str(args.port)])
        
    if args.test_mode:
        test_cmd.append("--test-mode")
    
    cmd = " ".join(test_cmd)
    return run_command(cmd, cwd=BACKEND_DIR)

def run_frontend_tests(args):
    """Run frontend tests"""
    print_header("FRONTEND TESTS")
    
    # Create the node command
    test_cmd = ["node", "run_tests.js"]
    
    if args.unit_only:
        test_cmd.append("--unit-only")
    elif args.component_only:
        test_cmd.append("--component-only")
    elif args.e2e_only:
        test_cmd.append("--e2e-only")
    else:
        test_cmd.append("--all")
    
    if args.coverage:
        # Coverage is enabled by default
        pass
    else:
        test_cmd.append("--no-coverage")
    
    if args.watch:
        test_cmd.append("--watch")
    
    cmd = " ".join(test_cmd)
    return run_command(cmd, cwd=FRONTEND_DIR)

def run_e2e_tests(args):
    """Run end-to-end tests"""
    print_header("END-TO-END TESTS")
    
    # Start the backend server if requested
    backend_process = None
    if args.start_backend:
        print("Starting backend server for E2E tests...")
        backend_cmd = [sys.executable, os.path.join(BACKEND_DIR, "run_server.py")]
        
        if args.port:
            backend_cmd.extend(["--port", str(args.port)])
        
        backend_process = subprocess.Popen(
            backend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give the server a moment to start
        time.sleep(3)
        
        # Check if server started successfully
        if backend_process.poll() is not None:
            print("Error: Failed to start backend server")
            stdout, stderr = backend_process.communicate()
            print("STDOUT:", stdout.decode())
            print("STDERR:", stderr.decode())
            return False
        
        print("Backend server started successfully")
    
    try:
        # Run Playwright tests
        playwright_cmd = "npx playwright test"
        
        if args.ui:
            playwright_cmd += " --ui"
        
        if args.debug:
            playwright_cmd += " --debug"
        
        success = run_command(playwright_cmd, cwd=E2E_DIR)
        return success
    
    finally:
        # Stop the backend server if it was started
        if backend_process and backend_process.poll() is None:
            print("Stopping backend server...")
            if platform.system() == "Windows":
                # On Windows, we need to use taskkill to forcefully terminate the process
                subprocess.run(f"taskkill /F /PID {backend_process.pid}", shell=True)
            else:
                backend_process.terminate()
                backend_process.wait(timeout=5)
            print("Backend server stopped")

def main():
    """Main function to run tests"""
    parser = argparse.ArgumentParser(description="Run all tests for GenAI Agent 3D web application")
    
    # Test selection arguments
    test_selection = parser.add_argument_group("Test Selection")
    test_selection.add_argument("--backend", action="store_true", help="Run backend tests only")
    test_selection.add_argument("--frontend", action="store_true", help="Run frontend tests only")
    test_selection.add_argument("--e2e", action="store_true", help="Run E2E tests only")
    test_selection.add_argument("--manual-websocket", action="store_true", help="Run manual WebSocket tests only")
    
    # Backend test options
    backend_options = parser.add_argument_group("Backend Test Options")
    backend_options.add_argument("--unit-only", action="store_true", help="Run backend unit tests only")
    backend_options.add_argument("--extended-only", action="store_true", help="Run backend extended tests only")
    backend_options.add_argument("--websocket-only", action="store_true", help="Run backend WebSocket tests only")
    backend_options.add_argument("--test-mode", action="store_true", help="Run server in test mode with minimal dependencies")
    
    # Frontend test options
    frontend_options = parser.add_argument_group("Frontend Test Options")
    frontend_options.add_argument("--component-only", action="store_true", help="Run frontend component tests only")
    frontend_options.add_argument("--coverage", action="store_true", help="Generate coverage reports")
    frontend_options.add_argument("--watch", action="store_true", help="Run tests in watch mode")
    
    # E2E test options
    e2e_options = parser.add_argument_group("E2E Test Options")
    e2e_options.add_argument("--start-backend", action="store_true", help="Start backend server for E2E tests")
    e2e_options.add_argument("--ui", action="store_true", help="Run tests with Playwright UI")
    e2e_options.add_argument("--debug", action="store_true", help="Run tests in debug mode")
    
    # Common options
    parser.add_argument("--port", type=int, default=8000, help="Port for backend server")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # If no specific test type is selected, run all tests
    run_all = not any([args.backend, args.frontend, args.e2e, args.manual_websocket])
    
    # Track overall success
    success = True
    
    # Run manual WebSocket tests (this is separate to avoid running it in the default "all" mode)
    if args.manual_websocket:
        websocket_success = run_manual_websocket_test(args)
        success = success and websocket_success
    else:
        # Run backend tests
        if args.backend or run_all:
            backend_success = run_backend_tests(args)
            success = success and backend_success
        
        # Run frontend tests
        if args.frontend or run_all:
            frontend_success = run_frontend_tests(args)
            success = success and frontend_success
        
        # Run E2E tests
        if args.e2e or run_all:
            e2e_success = run_e2e_tests(args)
            success = success and e2e_success
    
    # Print summary
    print_header("TEST SUMMARY")
    if success:
        print("✅ All requested tests passed successfully!")
    else:
        print("❌ Some tests failed. See above for details.")
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
