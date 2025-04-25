"""
API application for GenAI Agent 3D
"""

from fastapi import FastAPI
from .llm import router as llm_router

# Create FastAPI application
app = FastAPI(
    title="GenAI Agent 3D API",
    description="API for GenAI Agent 3D",
    version="0.1.0"
)

# Include API routers
app.include_router(llm_router, prefix="/api")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for service monitoring"""
    return {"status": "ok", "message": "API Service is healthy"}
