# Direct Services Architecture

This implementation provides a robust alternative to the Redis-based service discovery mechanism, ensuring that critical services (LLM and Blender) are directly initialized and available without relying on Redis message bus discovery.

## Architecture Overview

The direct services architecture maintains the extensibility of the microservices design while providing more reliability for critical path services:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Interface Layer                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                         Agent Core Layer                         │
└───┬─────────────┬─────────────┬─────────────┬─────────────┬─────┘
    │             │             │             │             │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│  LLM   │     │ Tool   │     │ Scene  │     │ Asset  │     │ Memory │
│Service │     │Registry│     │Manager │     │Manager │     │Service │
└───┬───┘     └───┬───┘     └───┬───┘     └───┬───┘     └───┬───┘
    │             │             │             │             │
┌───▼─────────────▼─────────────▼─────────────▼─────────────▼───┐
│                       Redis Message Bus                        │
└───┬─────────────┬─────────────┬─────────────┬─────────────┬───┘
    │             │             │             │             │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│SceneX  │     │Blender │     │Model  │     │Diagram │     │ SVG    │
│Service │     │Service │     │Service│     │Service │     │Service │
└───────┘     └───────┘     └───────┘     └───────┘     └───────┘
```

### Key Improvements

1. **Critical Service Reliability**
   - LLM and Blender services are directly initialized
   - No dependency on Redis discovery for essential services
   - Proper error handling and retries

2. **Unified Configuration**
   - Merges settings from .env and config.yaml with clear precedence
   - Consistent configuration across all services
   - Runtime config updates with persistence

3. **Standardized Output Directories**
   - Single canonical output location
   - Automatic directory linking for web backend and other components
   - Prevents file path confusion

4. **Backward Compatibility**
   - Works alongside existing Redis-based architecture
   - Optional activation via command line or config
   - Gradual migration path for existing components

## Components

The implementation consists of:

1. **Service Registry** (`service_initialization.py`)
   - Central registry for service instances
   - Unified configuration management
   - Output directory standardization

2. **LLM Service** (`llm_service.py`)
   - Support for multiple providers (Ollama, OpenAI, Anthropic)
   - Robust error handling and retries
   - Streaming capabilities

3. **Blender Service** (`blender_service.py`)
   - Script execution in headless and UI modes
   - Cross-platform path resolution
   - Asynchronous execution support

4. **Service Integrator** (`service_integrator.py`)
   - Unified interface for accessing services
   - Service availability checks
   - Combined LLM-Blender workflows

5. **Agent Integration** (`agent_integration.py`)
   - Compatibility with existing agent code
   - Hook registration system
   - Simplified interfaces for 3D model generation

## Setup Instructions

### Automated Setup

Run the appropriate setup script for your platform:

- **Windows**: `setup_direct_services.bat`
- **Linux/Mac**: `setup_direct_services.sh`

This will:
1. Set up output directories and symlinks
2. Apply patches to main.py
3. Configure the system for direct services

### Manual Setup

If you prefer to set up the components manually:

1. Run `python ensure_output_directories.py` to set up directory structure
2. Run `python apply_direct_services.py` to integrate the direct services

### Running with Direct Services

After setup, you can run the application with direct services:

- **Windows**: `genai_agent_project\run_direct.bat`
- **Linux/Mac**: `./genai_agent_project/run_direct.sh`

Or add the `--direct-services` flag to your existing command:

```
python main.py --direct-services
```

## Configuration

Direct services can be enabled in config.yaml:

```yaml
USE_DIRECT_SERVICES: true
LLM_PROVIDER: "ollama"  # ollama, openai, anthropic
LLM_MODEL: "llama3"
LLM_TIMEOUT: 120.0
BLENDER_PATH: "path/to/blender"  # Optional, will auto-detect if not specified
```

## Developer Notes

### Adding New Critical Services

To add a new critical service to direct initialization:

1. Create a new service module in `genai_agent/core/services/`
2. Add the service to `initialize_essential_services()` in `service_initialization.py`
3. Add accessor methods in `service_integrator.py`

### Migrating Existing Services

To migrate an existing Redis-based service to direct initialization:

1. Identify all message patterns and handlers
2. Create a direct service class that implements the same functionality
3. Add a compatibility layer in `agent_integration.py`
4. Register with the agent using the `register_with_agent` function

## Troubleshooting

### Common Issues

- **Service Not Found**: Check that the service is registered in `initialize_essential_services()`
- **Blender Not Found**: Set `BLENDER_PATH` in config.yaml or .env file
- **LLM Connection Fails**: Verify Ollama is running or API keys are set for OpenAI/Anthropic
- **Output Files Missing**: Check that output directories are properly linked

### Debugging

- Enable debug logging by setting the logging level to DEBUG
- Check service availability with the `/api/services/status` endpoint
- Run the initialization script with `--test` flag to verify services
