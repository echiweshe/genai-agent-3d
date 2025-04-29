"""
GenAI Agent 3D - Backend API

This is the main FastAPI application that serves the backend API for the GenAI Agent 3D project.
It integrates with the SVG to Video pipeline and provides endpoints for generating SVGs, 
converting them to 3D models, and rendering videos.
"""

import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sys
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import API routes
from api.routes import svg_video_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("backend")

# Create FastAPI application
app = FastAPI(
    title="GenAI Agent 3D API",
    description="API for generating SVG diagrams and converting them to 3D videos",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(svg_video_routes.router)

# Error handler for uncaught exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# Create outputs directory if it doesn't exist
outputs_dir = Path(__file__).parent.parent.parent / "outputs"
outputs_dir.mkdir(exist_ok=True)

# Mount outputs directory for serving generated files
app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Root endpoint that redirects to the built frontend
@app.get("/")
async def root():
    frontend_path = Path(__file__).parent.parent / "frontend" / "build" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    else:
        return {"message": "GenAI Agent 3D API", "frontend": "Not found"}

# Serve static frontend if available
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
