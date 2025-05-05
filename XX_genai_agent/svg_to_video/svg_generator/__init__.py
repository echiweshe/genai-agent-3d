"""
SVG Generator Package

This package provides functionality to generate SVG diagrams using various LLM providers.
It can be imported independently from the rest of the pipeline.
"""

# Allow importing SVGGenerator directly
try:
    from .svg_generator import SVGGenerator
except ImportError as e:
    # Allow importing even if there are errors with other dependencies
    import sys
    import logging
    logging.warning(f"Could not import SVGGenerator: {e}")
    
    # Define a placeholder SVGGenerator for IDE completion
    class SVGGenerator:
        """Placeholder SVGGenerator class for when imports fail."""
        
        def __init__(self, *args, **kwargs):
            raise ImportError("SVGGenerator could not be imported. Please check the error logs.")

__all__ = ['SVGGenerator']
