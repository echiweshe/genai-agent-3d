"""
SVG to Video Backend Server

This module provides the backend server for the SVG to Video pipeline.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Response, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Load environment variables from .env file
load_dotenv(os.path.join(parent_dir, ".env"))

# Import port configurations
config_path = os.path.join(parent_dir, "config", "ports.json")
try:
    with open(config_path, "r") as f:
        ports_config = json.load(f)
except Exception as e:
    print(f"Warning: Could not load port configuration: {e}")
    ports_config = {"services": {"svg_to_video_backend": 8001}}

# Load the port for the SVG to Video backend
SVG_VIDEO_PORT = ports_config.get("services", {}).get("svg_to_video_backend", 8001)

# Import routes
from api.routes import svg_video_routes

# Create FastAPI app
app = FastAPI(title="SVG to Video API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(svg_video_routes.router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "svg-to-video"}

# Serve static files in production mode
@app.on_event("startup")
async def startup_event():
    frontend_build_dir = os.path.join(parent_dir, "web", "frontend", "build")
    
    # Check if we're in production mode and the build directory exists
    if "--prod" in sys.argv and os.path.exists(frontend_build_dir):
        # Mount the frontend build directory
        app.mount("/", StaticFiles(directory=frontend_build_dir, html=True), name="frontend")

# Serve index.html for any unmatched routes in production mode
@app.get("/{full_path:path}")
async def serve_frontend(request: Request, full_path: str):
    if "--prod" in sys.argv:
        frontend_build_dir = os.path.join(parent_dir, "web", "frontend", "build")
        index_path = os.path.join(frontend_build_dir, "index.html")
        
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    # If not in production or index.html not found, return 404
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

def main():
    """Main entry point for the backend server."""
    parser = argparse.ArgumentParser(description="SVG to Video Backend Server")
    parser.add_argument("--port", type=int, default=SVG_VIDEO_PORT, help="Port to run the server on")
    parser.add_argument("--prod", action="store_true", help="Run in production mode")
    
    args = parser.parse_args()
    
    # Start the server
    import uvicorn
    
    print(f"Starting SVG to Video backend server on port {args.port}")
    if args.prod:
        print("Running in production mode")
    else:
        print("Running in development mode")
    
    uvicorn.run("main:app", host="0.0.0.0", port=args.port, reload=not args.prod)

if __name__ == "__main__":
    main()
