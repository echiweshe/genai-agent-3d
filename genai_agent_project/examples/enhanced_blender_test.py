"""
Enhanced test script for creating a 3D scene with GenAI Agent and Blender integration.
This script:
1. Connects to the GenAI Agent
2. Generates a scene description using LLM
3. Creates the actual scene in Blender
4. Renders a preview image
"""

import os
import sys
import asyncio
import yaml
import json
import tempfile
import bpy
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from genai_agent.agent import GenAIAgent
    from genai_agent.tools.blender_script_tool import BlenderScriptTool
    from env_loader import get_env, get_config
except ImportError as e:
    print(f"Error importing GenAI Agent modules: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# Setup Blender environment
def setup_blender_environment():
    """Set up the Blender environment for our test"""
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Set up rendering
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720
    
    # Create a world with a nice sky
    world = bpy.data.worlds['World']
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs[0].default_value = (0.5, 0.7, 1.0, 1.0)  # Sky blue
    bg_node.inputs[1].default_value = 1.0  # Strength
    
    print("✅ Blender environment set up successfully")

# Function to execute Blender Python code
def execute_blender_code(python_code):
    """Execute Python code in Blender"""
    print(f"Executing Blender code ({len(python_code)} characters)")
    
    # For debugging
    temp_file = os.path.join(project_root, "examples", "output", "last_blender_code.py")
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)
    with open(temp_file, 'w') as f:
        f.write(python_code)
    
    try:
        # Execute the code
        exec(python_code)
        print("✅ Blender code executed successfully")
        return True
    except Exception as e:
        print(f"❌ Error executing Blender code: {e}")
        return False

async def main():
    """Test creating a scene with GenAI Agent and Blender integration"""
    print("\n" + "="*80)
    print("ENHANCED BLENDER TEST - GENAI AGENT 3D INTEGRATION")
    print("="*80 + "\n")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(project_root, "examples", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load configuration
    config_path = os.path.join(project_root, "config.yaml")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            print(f"✅ Loaded configuration from {config_path}")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # Check available Ollama models
    print("\nChecking for available Ollama models...")
    selected_model = None
    
    try:
        from genai_agent.tools.ollama_helper import OllamaHelper
        
        if OllamaHelper.is_ollama_running():
            models = OllamaHelper.list_models()
            if models:
                available_model_names = [model.get('name') for model in models]
                print(f"Available models: {available_model_names}")
                
                # Prioritize lighter and known-working models
                preferred_models = [
                    "deepseek-coder:latest",        # First choice (smallest & most stable)
                    "llama3:latest",                # Second choice (4.7 GB)
                    "deepseek-coder-v2:latest",     # Largest fallback (8.9 GB)
                ]

                # Pick the first available model from preferred list
                for model in preferred_models:
                    if model in available_model_names:
                        selected_model = model
                        break
                
                # If no preferred model is found, use the first available
                if not selected_model and available_model_names:
                    selected_model = available_model_names[0]
                    
                if selected_model:
                    config['llm']['model'] = selected_model
                    print(f"✅ Using model: {selected_model}")
        else:
            print("⚠️ Ollama is not running")
    except Exception as e:
        print(f"❌ Error checking Ollama models: {e}")
    
    # Set up Blender environment
    print("\nSetting up Blender environment...")
    setup_blender_environment()
    
    # Create GenAI Agent
    print("\nInitializing GenAI Agent...")
    try:
        agent = GenAIAgent(config)
        print("✅ GenAI Agent initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing GenAI Agent: {e}")
        return
    
    # Define the scene we want to create
    instruction = "Create a peaceful mountain scene with a lake, pine forest, and a small cabin with smoke coming from the chimney. Use low-poly style."
    
    print(f"\nSending instruction to agent: \"{instruction}\"")
    start_time = time.time()
    
    try:
        # Process the instruction with the agent
        result = await agent.process_instruction(instruction)
        
        # Log the results
        print(f"\n✅ Instruction processed in {time.time() - start_time:.2f} seconds")
        print("\nResult summary:")
        print("-" * 40)
        
        if result.get('status') == 'success':
            print("Status: ✅ Success")
        else:
            print(f"Status: ❌ {result.get('status', 'Unknown')}")
        
        print(f"Steps executed: {result.get('steps_executed', 0)}")
        
        # Extract the Blender code
        blender_code = None
        for step in result.get('results', []):
            if step.get('tool') == 'blender_script_tool' and step.get('result', {}).get('status') == 'success':
                blender_code = step.get('result', {}).get('output')
                break
        
        # Save full result to file
        result_file = os.path.join(output_dir, "agent_result.json")
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Full result saved to: {result_file}")
        
        # Execute the Blender code if available
        if blender_code:
            print("\nExecuting generated Blender code...")
            execute_blender_code(blender_code)
            
            # Render and save the result
            render_path = os.path.join(output_dir, "rendered_scene.png")
            bpy.context.scene.render.filepath = render_path
            bpy.ops.render.render(write_still=True)
            print(f"\n✅ Scene rendered and saved to: {render_path}")
            
            # Save the Blender file
            blend_file = os.path.join(output_dir, "generated_scene.blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend_file)
            print(f"✅ Blend file saved to: {blend_file}")
        else:
            print("\n❌ No Blender code was generated")
    
    except Exception as e:
        print(f"\n❌ Error during scene generation: {e}")
    
    finally:
        # Close agent
        print("\nClosing GenAI Agent...")
        await agent.close()
        print("✅ Test completed")

if __name__ == "__main__":
    # When run directly in Blender
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error in main execution: {e}")
