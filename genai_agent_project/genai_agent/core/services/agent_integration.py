"""
Agent Integration Module
--------------------
Provides compatibility layer for integrating the direct service architecture 
with the existing agent code.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple, Generator, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("AgentIntegration")

class AgentIntegration:
    """
    Provides compatibility between the direct service architecture
    and the existing agent code.
    """
    
    def __init__(self):
        """Initialize the agent integration."""
        from genai_agent.core.services.service_integrator import get_integrator
        
        self.integrator = get_integrator()
        self.output_dir = self.integrator.get_output_directory()
        
        # Keep track of agent hooks we've registered
        self.registered_hooks = set()
        
        logger.info("Agent Integration initialized")
    
    def register_with_agent(self, agent):
        """
        Register direct services with an agent instance.
        
        Args:
            agent: The agent instance to register with
        """
        # Store agent reference
        self.agent = agent
        
        # Register direct LLM handling
        if hasattr(agent, 'register_llm_handler') and 'llm' not in self.registered_hooks:
            agent.register_llm_handler(self.handle_llm_request)
            self.registered_hooks.add('llm')
            logger.info("Registered direct LLM handler with agent")
        
        # Register direct Blender handling
        if hasattr(agent, 'register_blender_handler') and 'blender' not in self.registered_hooks:
            agent.register_blender_handler(self.handle_blender_request)
            self.registered_hooks.add('blender')
            logger.info("Registered direct Blender handler with agent")
        
        # Register model generation handling
        if hasattr(agent, 'register_model_handler') and 'model' not in self.registered_hooks:
            agent.register_model_handler(self.handle_model_request)
            self.registered_hooks.add('model')
            logger.info("Registered direct model handler with agent")
    
    def handle_llm_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an LLM request from the agent.
        
        Args:
            request_data: The request data from the agent
            
        Returns:
            Dictionary with the LLM response
        """
        prompt = request_data.get('prompt', '')
        model = request_data.get('model', None)
        provider = request_data.get('provider', None)
        max_tokens = request_data.get('max_tokens', 2048)
        temperature = request_data.get('temperature', 0.7)
        stream = request_data.get('stream', False)
        output_file = request_data.get('output_file', None)
        
        try:
            # Handle streaming vs. non-streaming
            if stream:
                # For streaming, we need to collect all chunks
                full_response = ""
                for chunk in self.integrator.stream_text(
                    prompt=prompt,
                    model=model,
                    provider=provider,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    output_file=output_file
                ):
                    full_response += chunk
                    # If agent has streaming callback, use it
                    if hasattr(self.agent, 'on_llm_chunk') and callable(self.agent.on_llm_chunk):
                        self.agent.on_llm_chunk(chunk)
                
                response = full_response
            else:
                # Non-streaming is simpler
                response = self.integrator.generate_text(
                    prompt=prompt,
                    model=model,
                    provider=provider,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    output_file=output_file
                )
            
            logger.info(f"LLM request handled successfully: {len(response)} chars")
            
            return {
                'success': True,
                'response': response,
                'output_file': output_file if output_file else None
            }
        
        except Exception as e:
            logger.error(f"Error handling LLM request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_blender_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a Blender request from the agent.
        
        Args:
            request_data: The request data from the agent
            
        Returns:
            Dictionary with the Blender execution results
        """
        script_path = request_data.get('script_path', '')
        params = request_data.get('params', {})
        output_file = request_data.get('output_file', None)
        headless = request_data.get('headless', None)
        
        try:
            # Execute the Blender script
            result = self.integrator.execute_blender_script(
                script_path=script_path,
                params=params,
                output_file=output_file,
                headless=headless
            )
            
            logger.info(f"Blender request handled: {script_path}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error handling Blender request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_model_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a model generation request from the agent.
        
        Args:
            request_data: The request data from the agent
            
        Returns:
            Dictionary with the model generation results
        """
        description = request_data.get('description', '')
        use_llm_enhancement = request_data.get('enhance_description', True)
        output_file = request_data.get('output_file', 'model.glb')
        model_type = request_data.get('model_type', 'basic')
        
        try:
            # Generate the 3D model
            if use_llm_enhancement:
                result = self.integrator.generate_3d_model_from_llm(
                    prompt=description,
                    output_file=output_file,
                    enhanced_description=True,
                    model_type=model_type
                )
            else:
                result = self.integrator.generate_3d_model(
                    description=description,
                    output_file=output_file,
                    model_type=model_type
                )
            
            logger.info(f"Model generation request handled: {output_file}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error handling model generation request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_description_to_model(self, description: str, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a 3D model from a description, with simplified interface for agent tools.
        
        Args:
            description: Text description of the model to generate
            output_file: Name of the output file
            
        Returns:
            Dictionary with the model generation results
        """
        # Generate a default output filename if not provided
        if not output_file:
            import hashlib
            # Create a hash from the description for a unique filename
            hash_obj = hashlib.md5(description.encode())
            file_hash = hash_obj.hexdigest()[:8]
            output_file = f"model_{file_hash}.glb"
        
        # Ensure output file has the correct extension
        if not output_file.endswith('.glb'):
            output_file += '.glb'
        
        # Ensure output file is in the output directory
        if not os.path.isabs(output_file):
            output_file = os.path.join(self.output_dir, output_file)
        
        # Request the model generation
        result = self.handle_model_request({
            'description': description,
            'enhance_description': True,
            'output_file': output_file,
            'model_type': 'detailed'  # Use detailed model by default
        })
        
        return result
    
    def get_output_directory(self) -> str:
        """Get the standardized output directory."""
        return self.output_dir

# Create a global instance
agent_integration = AgentIntegration()

def get_agent_integration() -> AgentIntegration:
    """Get the global agent integration instance."""
    return agent_integration

def register_with_agent(agent) -> AgentIntegration:
    """
    Register direct services with an agent instance.
    
    Args:
        agent: The agent instance to register with
        
    Returns:
        The agent integration instance
    """
    agent_integration.register_with_agent(agent)
    return agent_integration
