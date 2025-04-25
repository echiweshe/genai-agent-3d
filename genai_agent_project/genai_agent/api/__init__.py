
"""
API package for GenAI Agent 3D
"""

from fastapi import APIRouter

# Create API router
api_router = APIRouter()

# Import sub-routers
try:
    from .llm import router as llm_router
    api_router.include_router(llm_router)
except ImportError:
    pass
