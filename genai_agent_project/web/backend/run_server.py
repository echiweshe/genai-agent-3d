"""
Run the FastAPI server
"""

import os
import sys
import uvicorn
import argparse
import logging
import socket
from contextlib import closing

def is_port_in_use(host, port):
    """Check if a port is in use."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def find_free_port(start_port, host='0.0.0.0', max_attempts=100):
    """Find a free port starting from the given port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(host, port):
            return port
    raise RuntimeError(f"Could not find a free port after {max_attempts} attempts starting from {start_port}")

def run_server(host, port, reload=False, log_level=logging.INFO, test_mode=False, max_retries=5):
    """Run the server with multiple attempts to find a free port if needed."""
    for i in range(max_retries):
        try:
            print(f"Starting server on {host}:{port}")
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                reload=reload,
                log_level=log_level
            )
            break  # If we reach here, server started successfully
        except OSError as e:
            if e.errno == 10048:  # Port already in use
                if i < max_retries - 1:  # Not the last attempt
                    print(f"Port {port} is already in use. Finding another port...")
                    port = find_free_port(port + 1, host)
                    print(f"Trying port {port}...")
                else:
                    print(f"ERROR: Could not find a free port after {max_retries} attempts.")
                    print("Try manually specifying a different port with --port")
                    sys.exit(1)
            else:
                print(f"ERROR: {str(e)}")
                sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run the GenAI Agent 3D API server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--test-mode', action='store_true', help='Run server in test mode with minimal dependencies')
    parser.add_argument('--auto-port', action='store_true', help='Automatically find a free port if the specified one is in use')
    args = parser.parse_args()
    
    # Configure extra environment variables for test mode
    if args.test_mode:
        print("Running in TEST MODE - minimal dependencies will be used")
        os.environ["GENAI_TEST_MODE"] = "true"
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    if args.auto_port:
        # If auto-port is enabled, use our custom server runner
        run_server(args.host, args.port, args.reload, log_level, args.test_mode)
    else:
        # Otherwise, use normal uvicorn runner (will fail if port is in use)
        try:
            uvicorn.run(
                "main:app",
                host=args.host,
                port=args.port,
                reload=args.reload,
                log_level=log_level
            )
        except OSError as e:
            if e.errno == 10048:  # Port already in use
                print(f"ERROR: Port {args.port} is already in use.")
                print("You can use --auto-port to automatically find an available port")
                print("or specify a different port with --port")
            else:
                print(f"ERROR: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
