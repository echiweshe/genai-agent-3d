"""
Core Services Package
------------------
Provides direct service initialization and robust service infrastructure
for reliable LLM and 3D model generation.
"""

from genai_agent.core.services.service_initialization import (
    get_registry,
    get_service,
    initialize_services
)

from genai_agent.core.services.service_integrator import (
    get_integrator
)

from genai_agent.core.services.agent_integration import (
    get_agent_integration,
    register_with_agent
)

# For convenience, expose the main entry points
registry = get_registry()
integrator = get_integrator()
agent_integration = get_agent_integration()

__all__ = [
    'registry',
    'integrator',
    'agent_integration',
    'get_registry',
    'get_service',
    'initialize_services',
    'get_integrator',
    'get_agent_integration',
    'register_with_agent'
]
