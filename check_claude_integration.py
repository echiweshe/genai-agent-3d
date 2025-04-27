#!/usr/bin/env python3
"""
Check Claude Integration in GenAI Agent 3D

This script checks if the Claude API integration is working correctly within the project.
It tests the LLM service implementation without requiring external API calls.
"""

import os
import sys
import asyncio
import json
import importlib.util
import inspect
from pathlib import Path
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationChecker:
    """Checks the Claude API integration in the project"""
    
    def __init__(self, project_root):
        """Initialize the checker"""
        self.project_root = project_root
        self.services_path = project_root / "genai_agent_project" / "genai_agent" / "services"
        self.llm_module = None
        self.llm_service = None
        self.env_loader_module = None
    
    def check_file_structure(self):
        """Check if the required files exist"""
        print("\nChecking file structure...")
        
        # Check LLM service file
        llm_path = self.services_path / "llm.py"
        if llm_path.exists():
            print(f"✅ Found LLM service file: {llm_path}")
        else:
            print(f"❌ LLM service file not found: {llm_path}")
            return False
        
        # Check environment loader file
        env_loader_path = self.services_path / "enhanced_env_loader.py"
        if env_loader_path.exists():
            print(f"✅ Found environment loader file: {env_loader_path}")
        else:
            print(f"❌ Environment loader file not found: {env_loader_path}")
            return False
        
        # Check .env file
        env_file_path = self.project_root / "genai_agent_project" / ".env"
        if env_file_path.exists():
            print(f"✅ Found .env file: {env_file_path}")
        else:
            print(f"❌ .env file not found: {env_file_path}")
            return False
        
        return True
    
    def load_modules(self):
        """Load the required modules for testing"""
        print("\nLoading modules...")
        
        try:
            # Add project_root to sys.path to enable imports
            if str(self.project_root) not in sys.path:
                sys.path.append(str(self.project_root))
            
            # Load enhanced_env_loader module
            env_loader_path = self.services_path / "enhanced_env_loader.py"
            spec = importlib.util.spec_from_file_location("enhanced_env_loader", env_loader_path)
            self.env_loader_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.env_loader_module)
            print("✅ Loaded enhanced_env_loader module")
            
            # Load LLM service module
            llm_service_path = self.services_path / "llm.py"
            spec = importlib.util.spec_from_file_location("llm", llm_service_path)
            self.llm_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.llm_module)
            print("✅ Loaded LLM service module")
            
            return True
        except Exception as e:
            print(f"❌ Error loading modules: {str(e)}")
            traceback.print_exc()
            return False
    
    def check_api_key_loading(self):
        """Check if the API key loading is implemented correctly"""
        print("\nChecking API key loading...")
        
        try:
            # Check if get_api_key_for_provider function exists
            if hasattr(self.env_loader_module, 'get_api_key_for_provider'):
                get_api_key_func = getattr(self.env_loader_module, 'get_api_key_for_provider')
                
                # Check if the function accepts a provider parameter
                sig = inspect.signature(get_api_key_func)
                if 'provider' in sig.parameters:
                    print("✅ Found get_api_key_for_provider function with correct signature")
                    
                    # Check if the function handles anthropic provider
                    provider_env_map = None
                    for name, obj in inspect.getmembers(self.env_loader_module):
                        if name == 'provider_env_map':
                            provider_env_map = obj
                            break
                    
                    if provider_env_map and 'anthropic' in provider_env_map:
                        print("✅ The provider_env_map contains an entry for anthropic")
                        print(f"Anthropic API key environment variable: {provider_env_map['anthropic']}")
                    else:
                        print("❌ The provider_env_map does not contain an entry for anthropic")
                else:
                    print("❌ The get_api_key_for_provider function has an incorrect signature")
            else:
                print("❌ Could not find get_api_key_for_provider function")
                return False
            
            # Try to load the anthropic API key
            api_key = get_api_key_func('anthropic')
            if api_key:
                print(f"✅ Successfully loaded Anthropic API key: {api_key[:5]}...")
            else:
                print("⚠️ Anthropic API key not found in environment")
            
            return True
        except Exception as e:
            print(f"❌ Error checking API key loading: {str(e)}")
            return False
    
    def check_anthropic_method(self):
        """Check if the _generate_anthropic method is implemented correctly"""
        print("\nChecking _generate_anthropic method...")
        
        try:
            # Check if LLMService class exists
            if hasattr(self.llm_module, 'LLMService'):
                LLMService = getattr(self.llm_module, 'LLMService')
                
                # Create an instance of LLMService
                self.llm_service = LLMService()
                
                # Check if _generate_anthropic method exists
                if hasattr(self.llm_service, '_generate_anthropic'):
                    generate_anthropic = getattr(self.llm_service, '_generate_anthropic')
                    
                    # Check if the method is async
                    if asyncio.iscoroutinefunction(generate_anthropic):
                        print("✅ Found _generate_anthropic async method")
                        
                        # Check method signature
                        sig = inspect.signature(generate_anthropic)
                        expected_params = ['self', 'prompt', 'model', 'parameters']
                        if all(param in sig.parameters for param in expected_params):
                            print("✅ _generate_anthropic method has the correct signature")
                        else:
                            print("❌ _generate_anthropic method has an incorrect signature")
                            return False
                        
                        # Get the method source code to check for issues
                        source = inspect.getsource(generate_anthropic)
                        
                        # Check if the correct header is used
                        if '"X-API-Key":' in source:
                            print("✅ _generate_anthropic method uses the correct X-API-Key header")
                        else:
                            print("❌ _generate_anthropic method does not use the correct X-API-Key header")
                            return False
                        
                        # Check if anthropic-version header is included
                        if '"anthropic-version":' in source:
                            print("✅ _generate_anthropic method includes the anthropic-version header")
                        else:
                            print("❌ _generate_anthropic method does not include the anthropic-version header")
                            return False
                        
                        # Check content extraction logic
                        if 'content_blocks = data["content"]' in source or 'content_blocks = data.get("content")' in source:
                            print("✅ _generate_anthropic method correctly handles content extraction")
                        else:
                            print("❌ _generate_anthropic method may not correctly handle content extraction")
                            return False
                        
                        return True
                    else:
                        print("❌ _generate_anthropic method is not async")
                        return False
                else:
                    print("❌ Could not find _generate_anthropic method")
                    return False
            else:
                print("❌ Could not find LLMService class")
                return False
        except Exception as e:
            print(f"❌ Error checking _generate_anthropic method: {str(e)}")
            traceback.print_exc()
            return False
    
    def check_provider_discovery(self):
        """Check if Claude models are included in provider discovery"""
        print("\nChecking provider discovery...")
        
        try:
            # Check if the initialize method exists and can be called
            if hasattr(self.llm_service, 'initialize'):
                # Call the initialize method
                asyncio.run(self.llm_service.initialize())
                
                # Check if providers were discovered
                if hasattr(self.llm_service, 'providers'):
                    providers = self.llm_service.providers
                    
                    # Check if anthropic is in providers
                    if 'anthropic' in providers:
                        print("✅ Anthropic provider is included in provider discovery")
                        
                        # Check if Claude models are included
                        models = providers['anthropic'].get('models', [])
                        model_ids = [model.get('id') for model in models]
                        
                        expected_models = [
                            'claude-3-sonnet-20240229',
                            'claude-3-opus-20240229',
                            'claude-3-haiku-20240307',
                            'claude-3.5-sonnet-20250626'
                        ]
                        
                        found_models = [model for model in expected_models if model in str(model_ids)]
                        
                        if found_models:
                            print(f"✅ Found Claude models: {', '.join(found_models)}")
                        else:
                            print("❌ No Claude models found in provider discovery")
                            return False
                    else:
                        print("❌ Anthropic provider is not included in provider discovery")
                        return False
                else:
                    print("❌ Could not find providers attribute")
                    return False
            else:
                print("❌ Could not find initialize method")
                return False
            
            return True
        except Exception as e:
            print(f"❌ Error checking provider discovery: {str(e)}")
            traceback.print_exc()
            return False
    
    def generate_report(self):
        """Generate a report of the checks"""
        print("\n===== Claude API Integration Report =====")
        
        # Run checks
        file_structure_ok = self.check_file_structure()
        if not file_structure_ok:
            print("\n❌ File structure check failed. Please ensure all required files exist.")
            print("Run fix_claude_integration.py to create missing files.")
            return False
        
        modules_loaded = self.load_modules()
        if not modules_loaded:
            print("\n❌ Module loading failed. Please check the error messages above.")
            return False
        
        api_key_loading_ok = self.check_api_key_loading()
        anthropic_method_ok = self.check_anthropic_method()
        provider_discovery_ok = self.check_provider_discovery()
        
        # Generate summary
        print("\n===== Summary =====")
        print(f"File Structure: {'✅' if file_structure_ok else '❌'}")
        print(f"Module Loading: {'✅' if modules_loaded else '❌'}")
        print(f"API Key Loading: {'✅' if api_key_loading_ok else '❌'}")
        print(f"Anthropic Method: {'✅' if anthropic_method_ok else '❌'}")
        print(f"Provider Discovery: {'✅' if provider_discovery_ok else '❌'}")
        
        # Overall result
        all_ok = all([
            file_structure_ok,
            modules_loaded,
            api_key_loading_ok,
            anthropic_method_ok,
            provider_discovery_ok
        ])
        
        if all_ok:
            print("\n✅ Claude API integration checks passed!")
            print("The code seems to be correctly implemented.")
            print("You can now proceed to test the API connection with test_claude_api.py")
        else:
            print("\n❌ Some checks failed. Please fix the issues before proceeding.")
            print("Run fix_claude_integration.py to fix common issues.")
        
        return all_ok

def main():
    """Main function"""
    # Get project root path
    project_root = Path(__file__).parent.absolute()
    
    print("===========================================")
    print("  Claude API Integration Check - GenAI Agent 3D")
    print("===========================================")
    print(f"Project root: {project_root}")
    
    # Create and run the checker
    checker = IntegrationChecker(project_root)
    result = checker.generate_report()
    
    return 0 if result else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
