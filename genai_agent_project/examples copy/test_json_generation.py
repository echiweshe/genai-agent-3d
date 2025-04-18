"""
Test script to verify improved JSON generation and extraction
"""

import os
import sys
import asyncio
import yaml
import json
import logging
from typing import List, Dict, Any

# Configure logging - use DEBUG level to see detailed logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.llm import LLMService
from genai_agent.tools.scene_generator import SceneGeneratorTool
from genai_agent.tools.ollama_helper import OllamaHelper
from env_loader import get_env, get_config


def get_effective_llm_model(config: Dict[str, Any]) -> str:
    """Determine the effective LLM model from env or config"""
    env_model = get_env("LLM_MODEL")
    yaml_model = config.get("llm", {}).get("model")
    llm_model = env_model or yaml_model or "llama3"

    # Validate against Ollama
    models = OllamaHelper.list_models()
    available = [m.get("name") for m in models]
    if llm_model not in available:
        logger.warning(f"Model '{llm_model}' not found in Ollama. Available models: {available}")
    else:
        logger.info(f"Using LLM model: {llm_model}")
        config["llm"]["model"] = llm_model

    return llm_model


async def test_direct_json_generation():
    """Test direct JSON generation with optimized prompt"""
    print("\n=== Testing Direct JSON Generation ===")

    # Load config
    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    get_effective_llm_model(config)

    # Initialize LLM service
    llm_service = LLMService(config.get("llm", {}))

    prompt = """Your task is to output ONLY a valid JSON object to define a 3D scene. No explanations or comments, just the JSON.

Description: A simple mountain landscape with a lake and trees
Style: realistic
Name: TestJSON

The JSON object must have this structure:
{
  "name": "TestJSON",
  "description": "A simple mountain landscape with a lake and trees",
  "objects": [
    {
      "id": "uuid-here",
      "type": "cube",
      "name": "Object Name",
      "position": [0, 0, 0],
      "rotation": [0, 0, 0],
      "scale": [1, 1, 1],
      "properties": {
        "material": {
          "name": "Material Name",
          "color": [1, 0, 0, 1]
        }
      }
    }
  ]
}

Include:
- A camera (position at distance to view the scene)
- At least one light source
- 2-3 objects related to the scene description

IMPORTANT: Your response must be ONLY valid JSON with NO comments or explanations. Don't include backticks (```) or 'json' text.
"""

    print("Generating JSON...")
    response = await llm_service.generate(prompt)

    truncated = response if len(response) < 500 else response[:500] + "..."
    print(f"\nLLM Response: {truncated}")

    try:
        json_data = json.loads(response)
        print("\n✅ Successfully parsed direct JSON response!")
        print(f"JSON contains {len(json_data.get('objects', []))} objects")
        return True
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse direct JSON: {str(e)}")

        # Try fallback extraction
        scene_generator = SceneGeneratorTool(None, {})
        extracted_json = scene_generator._extract_json_from_response(response)

        if extracted_json:
            print("\n✅ Successfully extracted JSON using advanced methods!")
            print(f"Extracted JSON contains {len(extracted_json.get('objects', []))} objects")
            return True
        else:
            print("\n❌ All JSON extraction methods failed")
            return False


async def test_scene_generator_with_improved_prompt():
    """Test scene generator with improved prompting"""
    print("\n=== Testing Scene Generator with Improved Prompt ===")

    config_path = os.path.join(project_root, "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    get_effective_llm_model(config)

    redis_bus = RedisMessageBus(config.get("redis", {}))
    await redis_bus.connect()

    try:
        llm_service = LLMService(config.get("llm", {}))
        scene_gen_tool = SceneGeneratorTool(redis_bus, {})
        scene_gen_tool.llm_service = llm_service

        print("Generating scene with improved prompt...")
        result = await scene_gen_tool.execute({
            "description": "A small village nestled between mountains with a river running through it",
            "style": "cartoon",
            "name": "CartoonVillage"
        })

        if result.get("status") == "success":
            print("\n✅ Scene generation successful!")
            print(f"Scene name: {result.get('scene_name')}")
            print(f"Object count: {result.get('object_count')}")

            if "with 4 objects" in result.get("message", "") and result.get("object_count") == 4:
                print("Note: Used fallback scene data (shows exactly 4 objects)")
            else:
                print("Successfully used LLM-generated scene data!")
            return True
        else:
            print(f"\n❌ Scene generation failed: {result.get('error')}")
            return False
    finally:
        await redis_bus.disconnect()


async def main():
    print("Starting JSON generation and extraction tests...")

    if not OllamaHelper.is_ollama_running():
        print("Starting Ollama server...")
        OllamaHelper.start_ollama()
        await asyncio.sleep(5)

    results = [
        await test_direct_json_generation(),
        await test_scene_generator_with_improved_prompt()
    ]

    print("\n=== Test Summary ===")
    tests = ["Direct JSON Generation", "Scene Generator with Improved Prompt"]
    all_passed = True

    for test, result in zip(tests, results):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test}: {status}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! JSON generation and extraction is working correctly.")
    else:
        print("\n⚠️ Some tests failed. The system will still work using fallback data.")


if __name__ == "__main__":
    asyncio.run(main())
