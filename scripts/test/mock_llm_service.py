"""
Mock LLM Service for testing purposes

This module provides a mock LLM service that can be used for testing the SVG to Video pipeline
without requiring a connection to the actual LLM service.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MockLLMServiceManager:
    """
    Mock LLM Service Manager for testing
    
    This class provides the same interface as the real LLMServiceManager but
    returns predefined responses for testing purposes.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the LLM Service Manager"""
        if cls._instance is None:
            cls._instance = MockLLMServiceManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the Mock LLM Service Manager"""
        self.available_providers = ["mock_claude", "mock_openai", "mock_ollama"]
        self.initialized = True
        logger.info("Mock LLM Service Manager initialized")
    
    async def initialize(self):
        """Initialize the service manager"""
        self.initialized = True
        logger.info("Mock LLM Service Manager initialized")
    
    async def generate_text(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        Generate text using the mock LLM service
        
        Args:
            prompt: The prompt to send
            model: The model to use
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        logger.info(f"Mock LLM generating text with model {model}")
        logger.info(f"Prompt: {prompt[:100]}...")
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        # Return a mock SVG based on the prompt
        if "flowchart" in prompt.lower():
            return self._generate_mock_flowchart()
        elif "network" in prompt.lower():
            return self._generate_mock_network_diagram()
        else:
            return self._generate_mock_diagram()
    
    async def request(self, prompt: str, provider: str = None, model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Send a request to an LLM service
        
        Args:
            prompt: The prompt to send
            provider: The provider to use
            model: The model to use
            **kwargs: Additional parameters
            
        Returns:
            Response from the LLM service
        """
        text = await self.generate_text(prompt, model)
        return {"text": text, "status": "success"}
    
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a provider is available
        
        Args:
            provider: Provider name
            
        Returns:
            True if available, False otherwise
        """
        return provider in self.available_providers
    
    async def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get a list of available LLM providers
        
        Returns:
            List of available providers and their models
        """
        return [
            {"id": "mock_claude", "name": "Mock Claude", "available": True},
            {"id": "mock_openai", "name": "Mock OpenAI", "available": True},
            {"id": "mock_ollama", "name": "Mock Ollama", "available": True}
        ]
    
    def _generate_mock_flowchart(self) -> str:
        """Generate a mock flowchart SVG"""
        return """
        <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
            <!-- Start node -->
            <rect x="350" y="50" width="100" height="60" rx="15" ry="15" fill="#4CAF50" />
            <text x="400" y="85" font-size="16" text-anchor="middle" fill="white">Start</text>
            
            <!-- Process 1 -->
            <rect x="350" y="180" width="100" height="60" fill="#2196F3" />
            <text x="400" y="215" font-size="16" text-anchor="middle" fill="white">Process 1</text>
            
            <!-- Decision -->
            <polygon points="400,310 450,360 400,410 350,360" fill="#FFC107" />
            <text x="400" y="365" font-size="16" text-anchor="middle" fill="black">Decision?</text>
            
            <!-- Process 2 -->
            <rect x="350" y="480" width="100" height="60" fill="#2196F3" />
            <text x="400" y="515" font-size="16" text-anchor="middle" fill="white">Process 2</text>
            
            <!-- End node -->
            <rect x="350" y="610" width="100" height="60" rx="15" ry="15" fill="#F44336" />
            <text x="400" y="645" font-size="16" text-anchor="middle" fill="white">End</text>
            
            <!-- Connections -->
            <line x1="400" y1="110" x2="400" y2="180" stroke="black" stroke-width="2" />
            <line x1="400" y1="240" x2="400" y2="310" stroke="black" stroke-width="2" />
            <line x1="400" y1="410" x2="400" y2="480" stroke="black" stroke-width="2" />
            <line x1="400" y1="540" x2="400" y2="610" stroke="black" stroke-width="2" />
            
            <!-- Decision branches -->
            <line x1="450" y1="360" x2="550" y2="360" stroke="black" stroke-width="2" />
            <line x1="550" y1="360" x2="550" y2="515" stroke="black" stroke-width="2" />
            <line x1="550" y1="515" x2="450" y2="515" stroke="black" stroke-width="2" />
            
            <!-- Yes/No labels -->
            <text x="420" y="440" font-size="16" text-anchor="middle" fill="black">Yes</text>
            <text x="510" y="340" font-size="16" text-anchor="middle" fill="black">No</text>
        </svg>
        """
    
    def _generate_mock_network_diagram(self) -> str:
        """Generate a mock network diagram SVG"""
        return """
        <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
            <!-- Server -->
            <rect x="350" y="50" width="100" height="80" fill="#607D8B" />
            <text x="400" y="95" font-size="16" text-anchor="middle" fill="white">Server</text>
            
            <!-- Router -->
            <rect x="350" y="250" width="100" height="60" rx="10" ry="10" fill="#9C27B0" />
            <text x="400" y="285" font-size="16" text-anchor="middle" fill="white">Router</text>
            
            <!-- Client 1 -->
            <circle cx="200" cy="400" r="40" fill="#2196F3" />
            <text x="200" y="405" font-size="16" text-anchor="middle" fill="white">Client 1</text>
            
            <!-- Client 2 -->
            <circle cx="400" cy="400" r="40" fill="#2196F3" />
            <text x="400" y="405" font-size="16" text-anchor="middle" fill="white">Client 2</text>
            
            <!-- Client 3 -->
            <circle cx="600" cy="400" r="40" fill="#2196F3" />
            <text x="600" y="405" font-size="16" text-anchor="middle" fill="white">Client 3</text>
            
            <!-- Connections -->
            <line x1="400" y1="130" x2="400" y2="250" stroke="black" stroke-width="2" />
            <line x1="400" y1="310" x2="400" y2="360" stroke="black" stroke-width="2" />
            <line x1="350" y1="280" x2="200" y2="360" stroke="black" stroke-width="2" />
            <line x1="450" y1="280" x2="600" y2="360" stroke="black" stroke-width="2" />
        </svg>
        """
    
    def _generate_mock_diagram(self) -> str:
        """Generate a generic mock diagram SVG"""
        return """
        <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
            <!-- Rectangle -->
            <rect x="100" y="100" width="200" height="150" fill="#3F51B5" />
            <text x="200" y="175" font-size="20" text-anchor="middle" fill="white">Element 1</text>
            
            <!-- Circle -->
            <circle cx="500" cy="175" r="75" fill="#E91E63" />
            <text x="500" y="175" font-size="20" text-anchor="middle" fill="white">Element 2</text>
            
            <!-- Connection -->
            <line x1="300" y1="175" x2="425" y2="175" stroke="black" stroke-width="3" />
            
            <!-- Triangle -->
            <polygon points="200,350 100,500 300,500" fill="#4CAF50" />
            <text x="200" y="450" font-size="20" text-anchor="middle" fill="white">Element 3</text>
            
            <!-- Rounded Rectangle -->
            <rect x="400" y="350" width="200" height="150" rx="20" ry="20" fill="#FFC107" />
            <text x="500" y="425" font-size="20" text-anchor="middle" fill="black">Element 4</text>
            
            <!-- Connection -->
            <line x1="300" y1="425" x2="400" y2="425" stroke="black" stroke-width="3" />
        </svg>
        """

# Also create a mock for our LLM factory's direct integrations
class MockClaudeDirectSVGGenerator:
    """Mock implementation of ClaudeDirectSVGGenerator for testing"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the mock generator"""
        pass
    
    def set_model(self, model_name: str) -> None:
        """Set the model"""
        pass
    
    def generate_svg(self, concept: str, style: Optional[str] = None) -> str:
        """Generate SVG from a concept"""
        if "flowchart" in concept.lower() or "flowchart" == style:
            return MockLLMServiceManager()._generate_mock_flowchart()
        elif "network" in concept.lower() or "network" == style:
            return MockLLMServiceManager()._generate_mock_network_diagram()
        else:
            return MockLLMServiceManager()._generate_mock_diagram()
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """Get available models"""
        return [
            {"id": "mock-claude", "name": "Mock Claude", "description": "Mock model for testing"}
        ]
