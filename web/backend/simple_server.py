"""
Simple Backend Server for SVG to Video Pipeline

This is a simplified version of the backend server that only provides API endpoints
for testing the SVG to Video Pipeline components.
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from dotenv import load_dotenv

# Load .env file from the main project directory
env_path = Path(__file__).parent.parent.parent / "genai_agent_project" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment variables from {env_path}")
else:
    # Fall back to local .env file if it exists
    local_env = Path(__file__).parent.parent.parent / ".env"
    if local_env.exists():
        load_dotenv(dotenv_path=local_env)
        print(f"Loaded environment variables from {local_env}")
    else:
        print("No .env file found! API keys may not be available.")

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Create FastAPI application
app = FastAPI(
    title="SVG to Video API",
    description="Simple API for SVG to Video Pipeline",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("server")

# Create outputs directory if it doesn't exist
outputs_dir = Path(__file__).parent.parent.parent / "outputs"
outputs_dir.mkdir(exist_ok=True)

# Try to import the SVG Generator
try:
    from genai_agent.svg_to_video.svg_generator import SVGGenerator
    svg_generator = SVGGenerator()
    logger.info(f"Initialized SVG Generator with providers: {svg_generator.get_available_providers()}")
except ImportError as e:
    logger.error(f"Failed to import SVG Generator: {e}")
    svg_generator = None

# Task storage (for demonstration)
tasks = {}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Server is running"}

@app.get("/api/svg-to-video/providers")
async def list_providers():
    """List available LLM providers"""
    if svg_generator is None:
        raise HTTPException(status_code=500, detail="SVG Generator not available")
    
    providers = svg_generator.get_available_providers()
    return providers

@app.post("/api/svg-to-video/generate-svg")
async def generate_svg(concept: str, provider: str = None):
    """Generate an SVG diagram from a concept description"""
    if svg_generator is None:
        raise HTTPException(status_code=500, detail="SVG Generator not available")
    
    try:
        # Use the first available provider if none specified
        if provider is None and svg_generator.providers:
            provider = next(iter(svg_generator.providers.keys()))
        
        # Generate SVG
        svg_content = await svg_generator.generate_svg(concept, provider=provider)
        
        # Return SVG content
        return {"svg_content": svg_content}
    
    except Exception as e:
        logger.exception("Error generating SVG")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
