"""
Simple Backend Server for SVG to Video Pipeline

This is a simplified version of the backend server that only provides API endpoints
for testing the SVG to Video Pipeline components.
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
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
    # Directly use the pure Anthropic version for generating SVGs
    from anthropic import Anthropic
    has_anthropic = True
    
    # Try to get the Anthropic API key
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        # Create the client
        anthropic_client = Anthropic(api_key=anthropic_api_key)
        logger.info("Initialized direct Anthropic client")
    else:
        anthropic_client = None
        has_anthropic = False
        logger.warning("Anthropic API key not found, Claude will not be available")
except ImportError:
    logger.warning("Anthropic package not installed, Claude will not be available")
    anthropic_client = None
    has_anthropic = False

# Also try the standard SVG Generator for OpenAI
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
    providers = []
    
    # Add providers from SVG Generator
    if svg_generator:
        providers.extend(svg_generator.get_available_providers())
    
    # Add direct Anthropic if available
    if has_anthropic and anthropic_client:
        if "claude" not in providers:
            providers.append("claude-direct")
    
    return providers

@app.get("/api/svg-to-video/generate-svg")
async def generate_svg_get(
    concept: str = Query(..., description="Concept description for diagram generation"),
    provider: str = Query(None, description="LLM provider to use")
):
    """Generate an SVG diagram from a concept description (GET method)"""
    return await generate_svg_internal(concept, provider)

@app.post("/api/svg-to-video/generate-svg")
async def generate_svg_post(
    concept: str = Form(..., description="Concept description for diagram generation"),
    provider: str = Form(None, description="LLM provider to use")
):
    """Generate an SVG diagram from a concept description (POST method)"""
    return await generate_svg_internal(concept, provider)

async def generate_svg_internal(concept: str, provider: str = None):
    """Internal function to handle SVG generation for both GET and POST requests"""
    if not concept:
        raise HTTPException(status_code=400, detail="Concept is required")
    
    # Check if using direct Claude
    if provider == "claude-direct" and has_anthropic and anthropic_client:
        try:
            logger.info(f"Generating SVG with direct Claude API: {concept[:50]}...")
            
            # Create the prompt
            prompt = f"""
            Create an SVG diagram that represents the following concept:
            
            {concept}
            
            Requirements:
            - Use standard SVG elements (rect, circle, path, text, etc.)
            - Include appropriate colors and styling
            - Ensure the diagram is clear and readable
            - Add proper text labels
            - Use viewBox="0 0 800 600" for dimensions
            - Wrap the entire SVG in <svg> tags
            - Do not include any explanation, just the SVG code
            
            SVG Diagram:
            """
            
            # Generate with Claude
            message = anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract SVG content
            response_text = message.content[0].text
            
            # Extract SVG tags
            import re
            if "<svg" in response_text and "</svg>" in response_text:
                svg_match = re.search(r'(<svg.*?</svg>)', response_text, re.DOTALL)
                if svg_match:
                    svg_content = svg_match.group(1)
                else:
                    svg_content = response_text
            else:
                logger.warning("Generated content does not contain valid SVG tags")
                svg_content = response_text
            
            return {"svg_content": svg_content}
        
        except Exception as e:
            logger.exception(f"Error generating SVG with Claude direct: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Use regular SVG Generator
    elif svg_generator:
        try:
            # Use the first available provider if none specified
            available_providers = svg_generator.get_available_providers()
            if not provider or provider not in available_providers:
                if available_providers:
                    provider = available_providers[0]
                else:
                    raise HTTPException(status_code=404, detail="No LLM providers available")
            
            # Generate SVG
            svg_content = await svg_generator.generate_svg(concept, provider=provider)
            
            # Return SVG content
            return {"svg_content": svg_content}
        
        except Exception as e:
            logger.exception(f"Error generating SVG with SVG Generator: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        raise HTTPException(status_code=500, detail="No SVG generation capability available")

@app.post("/api/svg-to-video/convert-svg")
async def convert_svg(
    svg_file: UploadFile = File(...),
    render_quality: str = Form("medium"),
    animation_type: str = Form("standard")
):
    """Convert an SVG file to a video"""
    # This is a placeholder for now - in a real implementation you would handle the conversion
    return {
        "task_id": "task-" + os.urandom(8).hex(),
        "status": "queued",
        "message": "SVG conversion queued"
    }

@app.get("/api/svg-to-video/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a task"""
    # This is a placeholder - in a real implementation you would check the actual task status
    return {
        "task_id": task_id,
        "status": "running",
        "progress": 50,
        "message": "Task is in progress"
    }

@app.get("/logo192.png")
async def get_logo():
    """Handle missing logo requests"""
    # You can either return a placeholder image or a 404
    raise HTTPException(status_code=404, detail="Logo not found")

if __name__ == "__main__":
    import uvicorn
    # Use port 8001 instead of 8000 to avoid conflicts
    port = 8001
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

