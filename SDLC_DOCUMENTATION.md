# Software Development Life Cycle (SDLC) Documentation - GenAI Agent 3D

## 1. Project Inception
- **Project Vision Statement**: GenAI Agent 3D is a comprehensive system for generating 3D content using AI, with the end goal of creating training materials, presentations, animations, and visualizations. The system integrates various Language Models (LLMs), Blender, and other tools to enable the automated generation of 3D models, scenes, diagrams, and SVGs that can be further processed into presentations and videos.
- **Business Case**: 
  - Problem: Creation of 3D content for training and education is time-consuming and requires specialized skills
  - Opportunity: Leverage AI to automate and simplify this process
  - Value: Reduce content creation time, make complex technical concepts more accessible through better visualization
- **Initial Scope Definition**: 
  - AI-driven generation of 3D models, scenes, and diagrams
  - SVG to 3D conversion pipeline
  - Integration with Blender and other 3D tools
  - React-based web UI for controlling the system
  - Support for multiple LLM providers (local and cloud-based)
- **Key Stakeholders**: 
  - Development team
  - Training content creators
  - Technical educators
  - End users of training materials

## 2. Requirements Gathering & Analysis
- **User Requirements**: 
  - Generate 3D visualizations from text descriptions
  - Create technical diagrams as SVG using AI
  - Convert SVG diagrams to 3D scenes automatically
  - Set up animation sequences for 3D scenes
  - Integrate with presentations or videos
  - Support various output formats for different use cases
- **Functional Requirements**: 
  - LLM integration (Ollama, OpenAI, Claude)
  - 3D model generation from text descriptions
  - Scene composition with generated models
  - SVG diagram generation with Claude
  - SVG to 3D conversion
  - Animation system for 3D scenes
  - Blender integration for rendering
  - Asset management system
- **Non-functional Requirements**: 
  - Performance: Responsive UI, efficient rendering
  - Usability: Intuitive interface for non-technical users
  - Reliability: Stable execution of complex generation tasks
  - Scalability: Support for growing asset library
  - Security: Proper handling of API keys and credentials
- **Constraints**: 
  - Local vs. cloud LLM limitations
  - Blender integration complexity
  - Performance limitations on complex scenes
- **Prioritization**: 
  - Must Have: Core LLM integration, model generation, Blender integration
  - Should Have: SVG generation, scene composition, web UI
  - Could Have: Advanced animation, PowerPoint integration
  - Won't Have (initially): Collaborative features, comprehensive CMS

## 3. System Design
- **High-level Architecture**: The system follows a microservices architecture with the following main components:
  - Frontend: React-based web UI for user interactions
  - Backend API: FastAPI service handling requests from the frontend
  - LLM Service: Handles communication with various LLM providers
  - Agent: Orchestrates tool execution and manages generation workflows
  - Redis Message Bus: Facilitates communication between components
  - Tool Registry: Manages the available tools (model generation, scene creation, etc.)
  - External Integrations: Blender, Hunyuan3D, Trellis, etc.
- **Database Design**: 
  - Redis for message bus and caching
  - File-based storage for assets, models, and scenes
  - Metadata storage for asset indexing and retrieval
- **User Interface Design**: 
  - React-based web application with:
    - LLM Tester: For testing LLM providers
    - Model Generator: For creating 3D models
    - Scene Editor: For creating and editing 3D scenes
    - Diagram Generator: For creating diagrams
    - Blender Scripts: For browsing and executing Blender scripts
- **API Specifications**: 
  - LLM API Routes: `/api/llm/*` endpoints for LLM interaction
  - Tool Routes: Endpoints for executing various tools
  - WebSocket Support: For real-time communication
- **Technology Stack**: 
  - Backend: Python, FastAPI
  - Frontend: React, Material-UI
  - Message Bus: Redis
  - 3D: Blender (via Python API)
  - AI: Various LLM providers (Ollama, OpenAI, Claude)
- **Security Architecture**: 
  - API Key Management: Enhanced environment variable loader
  - Secure Storage: Environment variables for sensitive credentials
  - Authentication: API key-based authentication for external services

## 4. Technical Specification
- **Detailed Design Documents**: 
  - Communication Flow:
    - Direct API Flow (simple operations):
      1. User interacts with the frontend UI
      2. Frontend sends a request to the backend API
      3. Backend API processes the request directly
      4. Results are returned to the frontend
    - Agent-based Flow (complex operations):
      1. User submits an instruction via the frontend
      2. Frontend sends the instruction to the backend API
      3. Backend forwards the instruction to the Agent
      4. Agent parses the instruction and identifies required tools
      5. Agent executes tools in sequence, managing dependencies
      6. Results from each tool are collected
      7. Final results are returned to the frontend
    - LLM Service Flow:
      1. Request arrives at LLM API endpoints
      2. LLM Service selects the appropriate provider
      3. Request is sent to the provider (Ollama, OpenAI, Claude, etc.)
      4. Response is received and processed
      5. Result is returned to the requester
- **Algorithm Descriptions**: 
  - SVG to 3D Workflow:
    1. SVG Generation: Create technical diagrams as SVG using AI
    2. Element Extraction: Extract individual elements from the SVG
    3. 3D Conversion: Convert 2D elements to 3D models
    4. Animation Setup: Set up animation sequences
    5. Integration: Integrate with presentations or videos
  - SceneX Animation System:
    - Coordinate system for precise object placement
    - Animation primitives (fade, transition, morph)
    - Animation sequencing system
    - Python API for animation control
- **Error Handling Strategy**: 
  - LLM Integration:
    - Enhanced error messages for missing/invalid API keys
    - Fallback mechanisms for provider failures
  - Service Connections:
    - Retry logic for Redis operations
    - Configurable timeouts for all external operations
  - Blender Integration:
    - Script validation before execution
    - Structured error response format
- **Integration Points**: 
  - LLM Providers (Ollama, OpenAI, Claude)
  - Blender (via Python scripting)
  - Hunyuan3D via fal.ai
  - Redis Message Bus
  - Web UI
- **Performance Specifications**: 
  - Concurrency:
    - FastAPI Backend: Uses asynchronous handlers for concurrent request processing
    - LLM Service: Uses async/await patterns for non-blocking operations
    - Redis Message Bus: Enables concurrent message processing across components
    - Task Queue: Long-running operations are managed as background tasks
  - Timeout Handling:
    - HTTP Requests: httpx client with configurable timeouts
    - Redis Operations: Configurable timeouts for Redis operations
    - LLM Generation: Provider-specific timeout settings
    - Background Tasks: Monitoring and timeout handling for long-running tasks

## 5. Implementation Planning
- **Work Breakdown Structure**: Organized into phases:
  - Phase 1: Fix Current Issues (Immediate Priority)
    - Fix OpenAI integration
    - Fix Ollama integration
    - Complete Claude API integration
    - Complete Hunyuan3D integration
    - Fix output directory linking issue
    - Fix content preview in generator pages
    - Clean up root directory with numerous fix scripts
  - Phase 2: Core Feature Enhancements (Short-term)
    - Enhance model generation with detailed prompting
    - Improve scene generation with environmental details
    - Develop SVG generation and processing workflow
    - Strengthen Blender integration
  - Phase 3: Advanced Features (Medium-term)
    - Develop the SceneX animation system
    - Build PowerPoint integration
    - Create advanced workflow UI
    - Complete third-party tool integrations
  - Phase 4: Production Features (Long-term)
    - Implement video rendering pipeline
    - Build end-to-end training material generation
    - Enhance AI-driven content creation
    - Add collaborative features
- **Resource Allocation**: 
  - Development Team: Core implementation
  - DevOps: Infrastructure and service management
  - Product Management: Feature prioritization and roadmap
  - Design: UI/UX development
- **Development Methodology**: 
  - Hybrid Agile approach 
  - Iterative development with phases
  - Continuous integration for core components
- **Sprint/Release Planning**: 
  - Phase 1 (Immediate): 2-3 sprints to address critical issues
  - Phase 2 (Short-term): 4-6 sprints for core feature enhancements
  - Phase 3 (Medium-term): 6-8 sprints for advanced features
  - Phase 4 (Long-term): 8+ sprints for production features
- **Coding Standards**: 
  - Python: PEP 8
  - JavaScript/React: Airbnb style guide
  - Documentation: Markdown with clear structure

## 6. Development
- **Code Repository Structure**:
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
- **Development Environment Setup**: 
  - Prerequisites:
    - Python 3.10+
    - Redis server (optional, for message bus)
    - Blender 4.x installed
    - Ollama (for local LLM support)
  - Setup Steps:
    1. Clone repository
    2. Create and activate Python virtual environment
    3. Install dependencies
    4. Configure application in config.yaml
    5. Set up API keys using provided utility scripts
- **Version Control Strategy**: 
  - GitHub repository
  - Feature branch workflow
  - Pull requests for code review
  - CI/CD integration
- **Code Review Process**: 
  - Pull request based reviews
  - Automated code quality checks
  - Manual review by at least one team member

## 7. Testing
- **Test Strategy**: 
  - Unit tests for core components
  - Integration tests for service communication
  - End-to-end tests for complete workflows
  - Manual testing for UI and complex interactions
- **Test Plans**: 
  - Core Component Tests: Verify functionality of agent, tools, and services
  - API Tests: Validate API endpoints and responses
  - WebSocket Tests: Test real-time communication
  - UI Tests: Validate frontend functionality
- **Test Cases**: 
  - LLM Service: Test provider selection, request handling, and response processing
  - Tool Registry: Test tool registration, discovery, and execution
  - Agent: Test instruction parsing, tool selection, and execution flow
  - Web UI: Test user interactions and state management
- **Test Data**: 
  - Sample prompts for LLM testing
  - Example SVG files for conversion testing
  - Test 3D models and scenes
- **Test Environment**: 
  - Local development environments
  - Dedicated test environment with isolated services
  - CI/CD pipeline with automated testing

## 8. Deployment
- **Deployment Strategy**: 
  - Initial deployment: Local development setup
  - Production: Containerized microservices with orchestration
- **Infrastructure Requirements**: 
  - Server with GPU support (for local LLMs)
  - Redis server for message bus
  - Storage for assets and 3D models
  - Blender installation
- **Installation Procedures**: 
  ```
  # Clone the repository
  git clone https://github.com/yourusername/genai-agent-3d.git
  cd genai-agent-3d
  
  # Create and activate a virtual environment
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  venv\Scripts\activate     # Windows
  
  # Install dependencies
  pip install -r requirements.txt
  
  # Configure the application
  # Edit config.yaml
  
  # Set up API keys
  python setup_api_keys.py
  
  # Start services
  python genai_agent_project/manage_services.py start all
  ```
- **Rollback Plan**: 
  - Version tracking for all services
  - Snapshot backups before major updates
  - Automated rollback scripts
- **Production Environment Configuration**: 
  - Environment-specific configuration files
  - Secure storage for API keys and credentials
  - Monitoring and logging setup

## 9. Maintenance & Support
- **Monitoring Plan**: 
  - Service status monitoring
  - Performance metrics collection
  - Error rate tracking
  - API usage monitoring
- **Backup & Recovery Procedures**: 
  - Regular backups of configuration and asset files
  - Database snapshots (if applicable)
  - Automated restore procedures
- **Bug Tracking Process**: 
  - GitHub Issues for bug tracking
  - Prioritization based on impact
  - Regular bug fix releases
- **Performance Optimization Strategy**: 
  - Profiling of critical components
  - Cache implementation for frequent operations
  - Optimization of resource-intensive processes (like rendering)
- **Update/Patch Management**: 
  - Regular updates for dependencies
  - Scheduled maintenance windows
  - Transparent communication about changes

## 10. Project Evaluation
- **Success Criteria**: 
  - Functional LLM integration with multiple providers
  - Successful generation of 3D models and scenes
  - Working SVG to 3D conversion pipeline
  - Intuitive user interface
  - Positive user feedback
- **Lessons Learned**: 
  - To be documented throughout development phases
  - Regular retrospectives after major releases
- **User Feedback Collection**: 
  - In-app feedback mechanism
  - User testing sessions
  - Feature request tracking
- **Future Enhancement Roadmap**: 
  - Enhanced animation capabilities
  - Additional LLM provider integrations
  - Advanced rendering options
  - Collaborative features
  - Project templates and presets
