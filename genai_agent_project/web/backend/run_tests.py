"""
Run tests for the FastAPI backend
"""

import os
import sys
import argparse
import subprocess
import time

def run_backend_server(port=8000, test_mode=False):
    """Start the backend server in a subprocess"""
    print(f"Starting backend server on port {port}{' in test mode' if test_mode else ''}...")
    
    cmd = [sys.executable, "run_server.py", "--port", str(port)]
    if test_mode:
        cmd.append("--test-mode")
    
    backend_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server a moment to start
    time.sleep(2)
    
    # Check if server started successfully
    if backend_process.poll() is not None:
        print("Error: Failed to start backend server")
        stdout, stderr = backend_process.communicate()
        print("STDOUT:", stdout.decode())
        print("STDERR:", stderr.decode())
        sys.exit(1)
    
    print("Backend server started successfully")
    return backend_process

def run_unit_tests():
    """Run pytest unit tests"""
    print("Running unit tests...")
    result = subprocess.run(["pytest", "-xvs", "tests/"])
    return result.returncode

def run_websocket_tests():
    """Run WebSocket tests specifically"""
    print("Running WebSocket tests...")
    result = subprocess.run(["pytest", "-xvs", "tests/test_websocket.py", "tests/test_extended_websocket.py"])
    return result.returncode

def run_extended_tests():
    """Run extended API and websocket tests"""
    print("Running extended tests...")
    result = subprocess.run(["pytest", "-xvs", "tests/test_extended_api.py", "tests/test_extended_websocket.py"])
    return result.returncode

def stop_backend_server(process):
    """Stop the backend server subprocess"""
    if process and process.poll() is None:
        print("Stopping backend server...")
        process.terminate()
        process.wait(timeout=5)
        print("Backend server stopped")

def main():
    """Main function to run tests"""
    parser = argparse.ArgumentParser(description="Run backend tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--extended", action="store_true", help="Run extended tests only")
    parser.add_argument("--websocket", action="store_true", help="Run WebSocket tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--port", type=int, default=8000, help="Port for backend server")
    parser.add_argument("--test-mode", action="store_true", help="Run server in test mode with minimal dependencies")
    
    args = parser.parse_args()
    
    # Default to all tests if no specific test type is selected
    if not any([args.unit, args.extended, args.websocket, args.all]):
        args.all = True
    
    # Determine which tests to run
    run_unit = args.unit or args.all
    run_extended = args.extended or args.all
    run_websocket = args.websocket or args.all
    
    # Track overall success
    success = True
    
    # Start the backend server for integration tests
    backend_process = None
    try:
        # Run unit tests
        if run_unit:
            unit_result = run_unit_tests()
            if unit_result != 0:
                success = False
                print("Unit tests failed")
            else:
                print("Unit tests passed")
        
        # Start the backend server for extended or websocket tests
        if run_extended or run_websocket:
            backend_process = run_backend_server(args.port, args.test_mode)
            
            # Run extended tests if requested
            if run_extended:
                extended_result = run_extended_tests()
                if extended_result != 0:
                    success = False
                    print("Extended tests failed")
                else:
                    print("Extended tests passed")
            
            # Run WebSocket tests if requested
            if run_websocket:
                websocket_result = run_websocket_tests()
                if websocket_result != 0:
                    success = False
                    print("WebSocket tests failed")
                else:
                    print("WebSocket tests passed")
    
    finally:
        # Stop the backend server
        if backend_process:
            stop_backend_server(backend_process)
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
