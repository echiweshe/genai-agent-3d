"""
External tool integrations package

This package contains adapters for integrating external tools with the GenAI Agent.
"""

# Import integrations
try:
    from genai_agent.integrations.blender_gpt import BlenderGPTIntegration
except ImportError:
    pass

try:
    from genai_agent.integrations.hunyuan_3d import Hunyuan3DIntegration
except ImportError:
    pass

try:
    from genai_agent.integrations.trellis import TrellisIntegration
except ImportError:
    pass
