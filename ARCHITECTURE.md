# GenAI Agent 3D - Architecture Documentation

This document describes the architecture, file structure, and component interactions of the GenAI Agent 3D project. It serves as a guide for understanding the current implementation and planning future development.

## Project Overview

GenAI Agent 3D is a comprehensive system for generating 3D content using AI, with the end goal of creating training materials, presentations, animations, and visualizations. The system integrates various Language Models (LLMs), Blender, and other tools to enable the automated generation of 3D models, scenes, diagrams, and SVGs that can be further processed into presentations and videos.

## Architecture Overview

The system follows a microservices architecture with the following main components:

1. **Frontend**: React-based web UI for user interactions
2. **Backend API**: FastAPI service handling requests from the frontend
3. **LLM Service**: Handles communication with various LLM providers
4. **Agent**: Orchestrates tool execution and manages generation workflows
5. **Redis Message Bus**: Facilitates communication between components
6. **Tool Registry**: Manages the available tools (model generation, scene creation, etc.)
7. **External Integrations**: Blender, Hunyuan3D, Trellis, etc.

### Architecture Diagram

```
┌───────────┐        ┌───────────┐       ┌───────────────┐
│           │        │           │       │               │
│  Frontend │◄─────▶│  Backend  │◄─────▶│  Agent        │
│  (React)  │        │  (FastAPI)│       │               │
│           │        │           │       └───────┬───────┘
└───────────┘        └───────────┘               │
                                                 ▼
                                       ┌─────────────────────┐
                                       │                     │
┌───────────┐        ┌───────────┐     │    Tool Registry    │
│           │        │           │     │                     │
│  Blender  │◄───────│  Tools    │◄────┘                     │
│           │        │           │                           │
└───────────┘        └───────────┘                           │
                                                             │
                      ┌───────────┐                          │
                      │           │                          │
                      │  Redis    │◄─────────────────────────┘
                      │ Message   │
                      │   Bus     │◄───────┐
                      │           │        │
                      └───────────┘        │
                                           │
                                 ┌─────────▼───────┐
                                 │                 │
                                 │   LLM Service   │
                                 │                 │
                                 └──┬───────┬───┬──┘
                                    │       │   │
                       ┌────────────┘       │   └────────────┐
                       │                    │                │
                 ┌─────▼─────┐        ┌─────▼─────┐    ┌─────▼─────┐
                 │           │        │           │    │           │
                 │  Ollama   │        │  OpenAI   │    │  Claude   │
                 │           │        │           │    │           │
                 └───────────┘        └───────────┘    └───────────┘
```

## Component Details

### Frontend

- **Technology**: React
- **Location**: `genai_agent_project/web/frontend/`
- **Function**: Provides the user interface for interacting with the system
- **Key Components**:
  - LLM Tester: For testing LLM providers
  - Model Generator: For creating 3D models
  - Scene Editor: For creating and editing 3D scenes
  - Diagram Generator: For creating diagrams
  - Blender Scripts: For browsing and executing Blender scripts

### Backend API

- **Technology**: FastAPI
- **Location**: `genai_agent_project/web/backend/`
- **Function**: Handles HTTP requests from the frontend and routes them to the appropriate service
- **Key Components**:
  - LLM API Routes: `/api/llm/*` endpoints for LLM interaction
  - Tool Routes: Endpoints for executing various tools
  - WebSocket Support: For real-time communication

### LLM Service

- **Technology**: Python
- **Location**: `genai_agent_project/genai_agent/services/llm.py`
- **Function**: Provides a unified interface to multiple LLM providers
- **Key Components**:
  - Provider Discovery: Detects available LLM providers
  - Provider-specific Handlers: Custom logic for each LLM provider
  - API Key Management: Loads and manages API keys from environment variables

### Agent

- **Technology**: Python
- **Location**: `genai_agent_project/genai_agent/agent.py`
- **Function**: Orchestrates tool execution and manages generation workflows
- **Key Components**:
  - Instruction Processing: Parses user instructions
  - Tool Selection: Chooses appropriate tools for tasks
  - Execution Flow: Manages the workflow of generation tasks

### Redis Message Bus

- **Technology**: Redis, Python
- **Location**: `genai_agent_project/genai_agent/services/redis_bus.py`
- **Function**: Provides asynchronous communication between components
- **Key Components**:
  - Message Publishing: Sends messages to channels
  - Message Subscription: Receives messages from channels
  - Request/Response Pattern: For synchronous-like communication over Redis

### Tool Registry

- **Technology**: Python
- **Location**: `genai_agent_project/genai_agent/tools/registry.py`
- **Function**: Manages the available tools and their execution
- **Key Components**:
  - Tool Registration: Registers tools with the system
  - Tool Discovery: Finds available tools
  - Tool Execution: Runs tools with given parameters

### External Integrations

- **Blender**: Integration with Blender for 3D modeling and animation
- **Hunyuan3D**: Integration with Hunyuan3D for 3D model generation
- **Trellis**: Integration with Trellis for additional capabilities
- **BlenderGPT**: Integration with BlenderGPT for AI-assisted Blender operations

## File Structure

```
genai-agent-3d/
├── genai_agent_project/
│   ├── config.yaml              # Main configuration file
│   ├── .env                     # Environment variables
│   ├── manage_services.py       # Service management script
│   ├── genai_agent/             # Core agent code
│   │   ├── agent.py             # Main agent implementation
│   │   ├── config.py            # Configuration utilities
│   │   ├── services/            # Service implementations
│   │   │   ├── llm.py           # LLM service
│   │   │   ├── llm_api_routes.py # LLM API endpoints
│   │   │   ├── enhanced_env_loader.py # Environment variable loader
│   │   │   ├── redis_bus.py     # Redis message bus
│   │   │   └── settings_api.py  # Settings API
│   │   ├── tools/               # Tool implementations
│   │   │   ├── registry.py      # Tool registry
│   │   │   ├── model_generator.py # 3D model generator
│   │   │   ├── scene_generator.py # Scene generator
│   │   │   ├── diagram_generator.py # Diagram generator
│   │   │   ├── blender_script.py # Blender script tool
│   │   │   └── ... other tools
│   │   └── integrations/        # External integrations
│   │       ├── blender/         # Blender integration
│   │       ├── hunyuan3d/       # Hunyuan3D integration
│   │       └── trellis/         # Trellis integration
│   ├── web/                     # Web interface
│   │   ├── frontend/            # React frontend
│   │   │   ├── src/             # Frontend source code
│   │   │   │   ├── components/  # React components
│   │   │   │   ├── pages/       # Page implementations
│   │   │   │   └── ... other React files
│   │   └── backend/             # FastAPI backend
│   │       ├── main.py          # Main FastAPI application
│   │       ├── routes/          # API route definitions
│   │       └── ... other backend files
│   └── output/                  # Generated output
│       ├── models/              # Generated 3D models
│       ├── scenes/              # Generated scenes
│       └── diagrams/            # Generated diagrams
├── setup_api_keys.py            # Script to set up API keys
├── fix_claude_api_key.py        # Fix for Claude API key
└── ... other utility scripts
```

## Communication Flow

### Direct API Flow

For simple operations that don't require complex tool orchestration:

1. User interacts with the frontend UI
2. Frontend sends a request to the backend API
3. Backend API processes the request directly
4. Results are returned to the frontend

### Agent-based Flow

For complex operations requiring tool orchestration:

1. User submits an instruction via the frontend
2. Frontend sends the instruction to the backend API
3. Backend forwards the instruction to the Agent
4. Agent parses the instruction and identifies required tools
5. Agent executes tools in sequence, managing dependencies
6. Results from each tool are collected
7. Final results are returned to the frontend

### LLM Service Flow

For operations requiring LLM generation:

1. Request arrives at LLM API endpoints
2. LLM Service selects the appropriate provider
3. Request is sent to the provider (Ollama, OpenAI, Claude, etc.)
4. Response is received and processed
5. Result is returned to the requester

## Concurrency and Timeout Handling

### Concurrency

- **FastAPI Backend**: Uses asynchronous handlers for concurrent request processing
- **LLM Service**: Uses async/await patterns for non-blocking operations
- **Redis Message Bus**: Enables concurrent message processing across components
- **Task Queue**: Long-running operations are managed as background tasks

### Timeout Handling

- **HTTP Requests**: httpx client with configurable timeouts
- **Redis Operations**: Configurable timeouts for Redis operations
- **LLM Generation**: Provider-specific timeout settings
- **Background Tasks**: Monitoring and timeout handling for long-running tasks

## Design Decisions

### Why Redis Message Bus?

1. **Decoupling**: Allows components to communicate without direct dependencies
2. **Scalability**: Enables horizontal scaling of services
3. **Reliability**: Provides message persistence and delivery guarantees
4. **Pub/Sub Pattern**: Natural fit for event-driven architecture

### Direct vs. Agent-based Processing

- **Direct Processing**: Used for simple, well-defined operations
  - Advantages: Lower latency, simpler implementation
  - Use cases: LLM testing, direct tool execution

- **Agent-based Processing**: Used for complex, multi-step operations
  - Advantages: Better orchestration, can handle complex instructions
  - Use cases: Converting natural language instructions to tool sequences

### Local vs. Cloud LLM Providers

- **Local (Ollama)**: 
  - Advantages: No API costs, can work offline, better privacy
  - Disadvantages: Limited by local hardware, potentially lower quality

- **Cloud (OpenAI, Claude)**:
  - Advantages: Higher quality, more capabilities, no local resource usage
  - Disadvantages: API costs, requires internet, potential privacy concerns

### Output Directory Structure

The system uses a unified output directory structure at `genai_agent_project/output/` with symbolic links to ensure both the agent and web frontend access the same files.

### Error Handling and Logging

- Comprehensive error handling at each layer
- Detailed logging for debugging and monitoring
- User-friendly error messages in the UI

## Future Development Considerations

Based on the current architecture, future development should focus on:

1. Fixing the output directory linking issue
2. Enhancing model and scene generation capabilities
3. Implementing SVG generation and processing
4. Creating animation workflows and PowerPoint integration
5. Developing the SceneX animation system
6. Improving Blender addon integration
7. Building presentation generation tools

## Best Practices

- Follow PEP 8 for Python code style
- Use async/await for non-blocking operations
- Implement comprehensive error handling
- Include detailed logging
- Write unit and integration tests
- Document code and features
- Use type hints for better IDE support and code quality

## Conclusion

The GenAI Agent 3D project has a solid foundation with a flexible architecture that can be extended to support various content generation workflows. The microservices approach with Redis-based communication allows for scalability and modularity, while the agent-based orchestration enables complex, multi-step operations.

By continuing to build on this architecture, the project can realize its vision of automated generation of 3D content, animations, and presentations for training and educational purposes.
