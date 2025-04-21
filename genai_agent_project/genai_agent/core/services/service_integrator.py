"""
Service Integrator Module
----------------------
Provides a unified interface for accessing all core services
with convenience methods for common operations.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple, Generator, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("ServiceIntegrator")

class ServiceIntegrator:
    """
    Integrates access to all core services through a unified interface.
    Provides convenience methods for common cross-service operations.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceIntegrator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the service integrator."""
        from genai_agent.core.services.service_initialization import get_registry
        
        self.registry = get_registry()
        
        # Load individual services
        self._initialize_services()
        
        logger.info("Service Integrator initialized")
    
    def _initialize_services(self):
        """Initialize and load all required services."""
        # Ensure essential services are initialized
        if not self.registry.get_service("llm") or not self.registry.get_service("blender"):
            from genai_agent.core.services.service_initialization import initialize_services
            initialize_services()
        
        # Get service instances
        self.llm = self.registry.get_service("llm")
        self.blender = self.registry.get_service("blender")
        
        # Check critical services
        if not self.llm:
            logger.error("LLM service not available")
            raise RuntimeError("LLM service not available")
        
        if not self.blender:
            logger.error("Blender service not available")
            raise RuntimeError("Blender service not available")
    
    def check_services(self) -> Dict[str, bool]:
        """
        Check the availability of all services.
        
        Returns:
            Dictionary mapping service names to their availability status
        """
        # Refresh service references
        self._initialize_services()
        
        # Check status of all services
        service_status = {
            "llm": self.llm is not None,
            "blender": self.blender is not None,
        }
        
        logger.info(f"Service availability: {service_status}")
        return service_status
    
    def generate_text(self, 
                     prompt: str, 
                     output_file: Optional[str] = None,
                     **kwargs) -> str:
        """
        Generate text using the LLM service.
        
        Args:
            prompt: The text prompt to send to the LLM
            output_file: If specified, save output to this file
            **kwargs: Additional parameters for text generation
            
        Returns:
            Generated text response
        """
        return self.llm.generate(prompt=prompt, output_file=output_file, **kwargs)
    
    def stream_text(self, 
                   prompt: str, 
                   callback: Optional[callable] = None,
                   output_file: Optional[str] = None,
                   **kwargs) -> Generator[str, None, str]:
        """
        Stream text generation from the LLM service.
        
        Args:
            prompt: The text prompt to send to the LLM
            callback: Function to call with each text chunk
            output_file: If specified, save complete output to this file
            **kwargs: Additional parameters for text generation
            
        Returns:
            Generator yielding text chunks
        """
        return self.llm.generate_stream(
            prompt=prompt, 
            callback=callback,
            output_file=output_file, 
            **kwargs
        )
    
    def execute_blender_script(self, 
                              script_path: str, 
                              params: Optional[Dict[str, Any]] = None,
                              output_file: Optional[str] = None,
                              **kwargs) -> Dict[str, Any]:
        """
        Execute a Blender script.
        
        Args:
            script_path: Path to the Blender script
            params: Dictionary of parameters to pass to the script
            output_file: Path to save output file
            **kwargs: Additional parameters for script execution
            
        Returns:
            Dictionary with execution results
        """
        return self.blender.run_script(
            script_path=script_path,
            params=params,
            output_file=output_file,
            **kwargs
        )
    
    async def execute_blender_script_async(self, 
                                          script_path: str, 
                                          params: Optional[Dict[str, Any]] = None,
                                          output_file: Optional[str] = None,
                                          **kwargs) -> Dict[str, Any]:
        """
        Execute a Blender script asynchronously.
        
        Args:
            script_path: Path to the Blender script
            params: Dictionary of parameters to pass to the script
            output_file: Path to save output file
            **kwargs: Additional parameters for script execution
            
        Returns:
            Dictionary with execution results
        """
        return await self.blender.run_script_async(
            script_path=script_path,
            params=params,
            output_file=output_file,
            **kwargs
        )
    
    def generate_3d_model(self, 
                         description: str, 
                         output_file: str = 'model.glb',
                         **kwargs) -> Dict[str, Any]:
        """
        Generate a 3D model from a description.
        
        Args:
            description: Text description of the model to generate
            output_file: Path to save the output model
            **kwargs: Additional parameters for model generation
            
        Returns:
            Dictionary with generation results
        """
        return self.blender.generate_model(
            description=description,
            output_file=output_file,
            **kwargs
        )
    
    def generate_3d_model_from_llm(self, 
                                  prompt: str, 
                                  output_file: str = 'model.glb',
                                  enhanced_description: bool = True,
                                  **kwargs) -> Dict[str, Any]:
        """
        Generate a 3D model using LLM-enhanced description.
        
        Args:
            prompt: Initial description prompt
            output_file: Path to save the output model
            enhanced_description: Whether to use LLM to enhance the description
            **kwargs: Additional parameters for model generation
            
        Returns:
            Dictionary with generation results including enhanced description
        """
        # If enhanced description requested, use LLM to improve the prompt
        if enhanced_description:
            enhancement_prompt = f"""
            I need to create a detailed 3D model from this description:
            
            "{prompt}"
            
            Please enhance this description with specific details about:
            1. Overall shape and dimensions
            2. Key visual features
            3. Colors and materials
            4. Textures
            5. Any moving parts or mechanisms
            
            Format your response as a detailed description that could be used by a 3D modeling system.
            """
            
            try:
                # Generate enhanced description
                enhanced_desc = self.llm.generate(
                    prompt=enhancement_prompt,
                    max_tokens=1024,
                    temperature=0.7
                )
                
                logger.info("Generated enhanced description using LLM")
                
                # Use enhanced description for model generation
                result = self.blender.generate_model(
                    description=enhanced_desc,
                    output_file=output_file,
                    **kwargs
                )
                
                # Include both descriptions in result
                result["original_prompt"] = prompt
                result["enhanced_description"] = enhanced_desc
                
                return result
                
            except Exception as e:
                logger.error(f"Error generating enhanced description: {str(e)}")
                logger.info("Falling back to original description")
        
        # Use original description directly
        result = self.blender.generate_model(
            description=prompt,
            output_file=output_file,
            **kwargs
        )
        
        result["original_prompt"] = prompt
        return result
    
    def get_output_directory(self) -> str:
        """Get the standardized output directory."""
        return self.registry.get_output_directory()
    
    def resolve_path(self, path: str) -> str:
        """Resolve a path relative to the project root."""
        return self.registry.resolve_path(path)

# Global integrator instance
integrator = ServiceIntegrator()

def get_integrator() -> ServiceIntegrator:
    """Get the global service integrator instance."""
    return integrator
