"""
Mock LLM Factory for testing

This module provides a mock implementation of the LLM Factory that can be used for
testing the SVG to Video pipeline without requiring a connection to actual LLM services.
"""

import logging
from typing import Dict, Any, List, Optional

from .mock_llm_service import MockClaudeDirectSVGGenerator

logger = logging.getLogger(__name__)

class MockLLMFactory:
    """Mock implementation of LLMFactory for testing"""
    
    def __init__(self, use_project_llm=True):
        """Initialize the mock factory"""
        self.providers = {
            "mock-claude": {
                "name": "Mock Claude",
                "description": "Mock Claude API for testing",
                "available": True,
                "direct": True
            },
            "mock-openai": {
                "name": "Mock OpenAI",
                "description": "Mock OpenAI API for testing",
                "available": True,
                "direct": True
            }
        }
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """Get available providers"""
        return [
            {"id": provider_id, **info}
            for provider_id, info in self.providers.items()
            if info.get("available", False)
        ]
    
    def create_generator(self, provider: str, model: Optional[str] = None) -> Any:
        """Create a generator for a provider"""
        return MockClaudeDirectSVGGenerator()
    
    async def generate_svg(self, provider: str, concept: str, model: Optional[str] = None, style: Optional[str] = None) -> str:
        """Generate SVG from a concept"""
        generator = self.create_generator(provider, model)
        return generator.generate_svg(concept, style)
