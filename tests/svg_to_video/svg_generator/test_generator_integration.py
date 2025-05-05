"""
Test SVG Generator Integration with LLM Service

This test validates that the SVG Generator properly integrates with the 
project's EnhancedLLMService for generating SVG diagrams.
"""

import os
import sys
import asyncio
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from genai_agent.svg_to_video.svg_generator_new import SVGGenerator

class TestSVGGeneratorIntegration(unittest.TestCase):
    """Tests for the integrated SVG Generator."""
    
    def setUp(self):
        """Set up the test environment."""
        self.svg_generator = SVGGenerator(debug=True)
        
        # Create output directory if it doesn't exist
        self.output_dir = os.path.join(project_root, "output", "test_results", "svg_generator")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_initialization(self):
        """Test that the SVG Generator initializes properly."""
        # Check that the generator was created
        self.assertIsNotNone(self.svg_generator)
        
        # Check that available providers is a list
        providers = self.svg_generator.get_available_providers()
        self.assertIsInstance(providers, list)
        
        # Print available providers
        print(f"Available providers: {providers}")
    
    def test_generate_svg(self):
        """Test SVG generation using the LLM service."""
        test_description = "A simple flowchart showing user login process"
        
        # Run the async test
        result = asyncio.run(self.async_test_generate_svg(test_description))
        self.assertTrue(result)
    
    async def async_test_generate_svg(self, description):
        """Async helper to test SVG generation."""
        try:
            # Get available providers
            providers = self.svg_generator.get_available_providers()
            
            # Skip test if no providers are available
            if not providers:
                print("Skipping test: No LLM providers available")
                return True
            
            # Use the first available provider
            provider = providers[0]
            print(f"Using provider: {provider}")
            
            # Generate SVG
            svg_content = await self.svg_generator.generate_svg(
                concept=description,
                provider=provider
            )
            
            # Check that SVG content was returned
            self.assertIsNotNone(svg_content)
            self.assertIn("<svg", svg_content)
            self.assertIn("</svg>", svg_content)
            
            # Save SVG to file
            output_file = os.path.join(self.output_dir, "test_output.svg")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(svg_content)
            
            print(f"SVG saved to: {output_file}")
            
            return True
        except Exception as e:
            print(f"Error in SVG generation test: {str(e)}")
            return False

if __name__ == "__main__":
    unittest.main()
