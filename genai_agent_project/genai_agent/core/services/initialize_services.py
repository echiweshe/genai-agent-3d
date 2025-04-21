"""
Service Initialization Script
--------------------------
Command-line script to initialize services with configuration override capability
and service testing functionality.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("ServiceInitialization")

def initialize_with_config(config_overrides: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize services with optional configuration overrides.
    
    Args:
        config_overrides: Dictionary of configuration values to override
    """
    from genai_agent.core.services.service_initialization import get_registry
    
    # Get the registry
    registry = get_registry()
    
    # Apply any configuration overrides
    if config_overrides:
        for key, value in config_overrides.items():
            registry.set_config(key, value)
            logger.info(f"Overriding config: {key} = {value}")
    
    # Initialize all essential services
    from genai_agent.core.services.service_initialization import initialize_services
    initialize_services()
    
    logger.info("Services initialized successfully")
    logger.info(f"Available services: {registry.list_services()}")

def test_llm_service() -> bool:
    """
    Test the LLM service by generating a simple response.
    
    Returns:
        True if test passes, False otherwise
    """
    from genai_agent.core.services.service_integrator import get_integrator
    
    integrator = get_integrator()
    
    try:
        # Simple test prompt
        test_prompt = "Respond with a single word: Hello"
        
        # Test generation
        response = integrator.generate_text(test_prompt, max_tokens=10)
        
        logger.info(f"LLM test response: {response}")
        
        if response and len(response.strip()) > 0:
            logger.info("LLM service test: PASSED")
            return True
        else:
            logger.error("LLM service test: FAILED (empty response)")
            return False
    
    except Exception as e:
        logger.error(f"LLM service test: FAILED with error: {str(e)}")
        return False

def test_blender_service() -> bool:
    """
    Test the Blender service by running a simple script.
    
    Returns:
        True if test passes, False otherwise
    """
    from genai_agent.core.services.service_integrator import get_integrator
    import tempfile
    
    integrator = get_integrator()
    
    try:
        # Create a simple test script
        test_script_content = """
import bpy
import sys
import json

# Simple test - create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Save test info
test_info = {
    "blender_version": bpy.app.version_string,
    "objects_created": len(bpy.context.scene.objects),
    "success": True
}

# Print result for subprocess capture
print(json.dumps(test_info))
"""
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w') as f:
            f.write(test_script_content)
            test_script_path = f.name
        
        try:
            # Run the test script
            result = integrator.execute_blender_script(test_script_path)
            
            if result["success"]:
                # Try to parse the output for more information
                try:
                    for line in result["output"].splitlines():
                        if line.strip().startswith("{") and line.strip().endswith("}"):
                            test_info = json.loads(line.strip())
                            logger.info(f"Blender version: {test_info.get('blender_version')}")
                            logger.info(f"Objects created: {test_info.get('objects_created')}")
                            break
                except Exception as e:
                    logger.warning(f"Could not parse Blender output: {str(e)}")
                
                logger.info("Blender service test: PASSED")
                return True
            else:
                logger.error(f"Blender service test: FAILED - {result.get('error', 'Unknown error')}")
                return False
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(test_script_path)
            except Exception:
                pass
    
    except Exception as e:
        logger.error(f"Blender service test: FAILED with error: {str(e)}")
        return False

def run_tests() -> bool:
    """
    Run tests for all services.
    
    Returns:
        True if all tests pass, False otherwise
    """
    logger.info("Running service tests...")
    
    # Test LLM service
    llm_test_result = test_llm_service()
    
    # Test Blender service
    blender_test_result = test_blender_service()
    
    # Overall test result
    all_passed = llm_test_result and blender_test_result
    
    if all_passed:
        logger.info("All service tests PASSED")
    else:
        logger.error("Some service tests FAILED")
    
    return all_passed

def main():
    """Main function for command-line execution."""
    parser = argparse.ArgumentParser(description="Initialize and test services")
    
    parser.add_argument("--config", help="JSON file with configuration overrides")
    parser.add_argument("--test", action="store_true", help="Test services after initialization")
    parser.add_argument("--llm-provider", help="Override LLM provider (ollama, openai, anthropic)")
    parser.add_argument("--llm-model", help="Override LLM model")
    parser.add_argument("--blender-path", help="Override Blender executable path")
    parser.add_argument("--output-dir", help="Override output directory")
    
    args = parser.parse_args()
    
    # Prepare configuration overrides
    config_overrides = {}
    
    # Load from JSON file if provided
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config_overrides.update(json.load(f))
        except Exception as e:
            logger.error(f"Error loading config file: {str(e)}")
            return 1
    
    # Apply command-line overrides
    if args.llm_provider:
        config_overrides["LLM_PROVIDER"] = args.llm_provider
    
    if args.llm_model:
        config_overrides["LLM_MODEL"] = args.llm_model
    
    if args.blender_path:
        config_overrides["BLENDER_PATH"] = args.blender_path
    
    if args.output_dir:
        config_overrides["OUTPUT_DIRECTORY"] = args.output_dir
    
    # Initialize services with any overrides
    initialize_with_config(config_overrides)
    
    # Run tests if requested
    if args.test:
        all_passed = run_tests()
        return 0 if all_passed else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
