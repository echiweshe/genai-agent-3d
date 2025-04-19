"""
Run the FastAPI server
"""

import os
import sys
import uvicorn
import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description='Run the GenAI Agent 3D API server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--test-mode', action='store_true', help='Run server in test mode with minimal dependencies')
    args = parser.parse_args()
    
    print(f"Starting server on {args.host}:{args.port}")
    
    # Configure extra environment variables for test mode
    if args.test_mode:
        print("Running in TEST MODE - minimal dependencies will be used")
        os.environ["GENAI_TEST_MODE"] = "true"
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=log_level
    )

if __name__ == "__main__":
    main()
