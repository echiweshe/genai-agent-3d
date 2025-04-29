"""
LLM Integrations for SVG Generation

This package contains direct integrations with various LLM providers
for generating SVG diagrams from text descriptions without using LangChain.
"""

from .claude_direct import ClaudeDirectSVGGenerator

__all__ = ['ClaudeDirectSVGGenerator']
