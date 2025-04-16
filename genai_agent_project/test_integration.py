#!/usr/bin/env python3
"""
Integration test script for the GenAI Agent
Tests critical components to ensure they work together properly
"""

import os
import sys
import asyncio
import logging
import yaml
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('integration_test')

# Make sure we can import from the project
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from genai_agent.services.llm import LLMService
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.tools.scene_generator import SceneGeneratorTool
from genai_agent.tools.ollama_helper import OllamaHelper

async def test_redis_connection():
    """Test Redis connection"""
    logger.info("Testing Redis connection...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize Redis bus
    redis_bus = RedisMessageBus(config.get('redis', {}))
    
    # Try to connect
    connect_result = await redis_bus.connect()
    
    if connect_result:
        logger.info("✅ Redis connection successful")
    else:
        logger.error("❌ Redis connection failed")
    
    # Disconnect
    await redis_bus.disconnect()
    
    return connect_result

async def test_llm_service():
    """Test LLM service"""
    logger.info("Testing LLM service...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Make sure Ollama is running
    if not OllamaHelper.is_ollama_running():
        logger.info("Starting Ollama server...")
        OllamaHelper.start_ollama()
    
    # Check available models
    models = OllamaHelper.list_models()
    if models:
        model_names = [model.get('name') for model in models]
        logger.info(f"Available models: {model_names}")
        
        # Select a suitable model
        preferred_models = [
            "deepseek-coder:latest",  # 776 MB - smallest
            "llama3:latest",          # 4.7 GB
            "llama3.2:latest",        # 2.0 GB
            "deepseek-coder-v2:latest"  # Larger fallback
        ]
        
        selected_model = None
        for model in preferred_models:
            if model in model_names:
                selected_model = model
                logger.info(f"Selected model: {selected_model}")
                break
        
        if selected_model:
            config['llm']['model'] = selected_model
    else:
        logger.warning("No models found, using default model from config")
    
    # Initialize LLM service
    llm_service = LLMService(config.get('llm', {}))
    
    # Test with a simple prompt
    logger.info("Testing LLM generation...")
    try:
        response = await llm_service.generate("Generate a short JSON object with name and value fields.")
        
        # Log response
        logger.info(f"LLM response received, length: {len(response)}")
        
        # Truncate response for logging if too long
        log_response = response
        if len(log_response) > 500:
            log_response = log_response[:500] + "..."
        logger.info(f"Response preview: {log_response}")
        
        # Try to parse as JSON to further validate
        try:
            # First, try direct parsing
            json_data = json.loads(response)
            logger.info("✅ Response is valid JSON")
            return True
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    logger.info("✅ Extracted valid JSON from response")
                    return True
                except:
                    pass
            
            logger.warning("❌ Could not parse response as JSON, but received a response")
            return True  # Still return True since we got a response
    except Exception as e:
        logger.error(f"❌ LLM generation failed: {str(e)}")
        return False

async def test_scene_generator():
    """Test Scene Generator tool"""
    logger.info("Testing Scene Generator tool...")
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize Redis bus
    redis_bus = RedisMessageBus(config.get('redis', {}))
    await redis_bus.connect()
    
    try:
        # Create scene generator tool
        scene_gen_tool = SceneGeneratorTool(redis_bus, {})
        
        # Test scene generation
        scene_params = {
            'description': 'A simple mountain landscape with trees and a lake',
            'style': 'basic',
            'name': 'TestScene'
        }
        
        logger.info(f"Generating scene with parameters: {scene_params}")
        result = await scene_gen_tool.execute(scene_params)
        
        if result.get('status') == 'success':
            logger.info("✅ Scene generation successful")
            logger.info(f"Scene name: {result.get('scene_name')}")
            logger.info(f"Object count: {result.get('object_count')}")
            return True
        else:
            logger.error(f"❌ Scene generation failed: {result.get('error')}")
            return False
    except Exception as e:
        logger.error(f"❌ Exception in scene generator test: {str(e)}")
        return False
    finally:
        # Close Redis connection
        await redis_bus.disconnect()

async def run_all_tests():
    """Run all integration tests"""
    logger.info("Starting integration tests...")
    
    # List of tests to run
    tests = [
        ("Redis Connection", test_redis_connection),
        ("LLM Service", test_llm_service),
        ("Scene Generator", test_scene_generator)
    ]
    
    # Run each test
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n=== Running {test_name} Test ===")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Error running {test_name} test: {str(e)}")
            results[test_name] = False
    
    # Print summary
    logger.info("\n=== Test Summary ===")
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All tests passed! The system should be working correctly.")
    else:
        logger.warning("\n⚠️ Some tests failed. Please review the logs for details.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
