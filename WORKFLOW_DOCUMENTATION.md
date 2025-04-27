# GenAI Agent 3D - Workflow and Use Cases Documentation

## Overview

This document describes the key workflows and use cases for the GenAI Agent 3D project, based on the workflow diagram. The system is structured in three primary layers:

1. **User Interface Layer** - Frontend interfaces and user interaction points
2. **Agent Layer** - Middleware services that process requests and coordinate tools
3. **Tool Layer** - Backend tools and services that perform specialized tasks

## 1. User Interface Layer

### Web Page UI
- **Purpose**: Provides frontend interface for user interactions
- **Components**:
  - React-based web application
  - Script management interface
  - Asset browser and viewer
- **Outputs To**: Selenium API for website processing

### Third Party Integrations
- **Purpose**: Connects to external AI and 3D modeling services
- **Components**:
  - Hunyuan3D for AI-based 3D model generation
  - Blender integration for 3D modeling and rendering
  - GPT models for text-based instructions and code generation
- **Outputs To**: SceneX API for scene generation

### SVG Diagram Generation
- **Purpose**: Creates technical diagrams in SVG format
- **Components**:
  - Claude LLM for diagram generation
  - SVG optimization and processing
  - Element extraction and classification
- **Outputs To**: SceneX API for animation and scene composition

### Network Diagram to 3D
- **Purpose**: Converts network topology diagrams to 3D visualizations
- **Components**:
  - Network component recognition
  - Topology mapping to 3D space
  - Connection visualization
- **Outputs To**: Selenium API for capturing website content

### SVG to 3D Conversion
- **Purpose**: Transforms SVG diagrams into 3D models and scenes
- **Components**:
  - SVG parsing and element extraction
  - Element classification (nodes, connectors, labels)
  - 3D representation mapping
- **Outputs To**: SceneX API for scene composition

### NLP to 3D
- **Purpose**: Generates 3D content from natural language descriptions
- **Components**:
  - Natural language processing
  - Scene description interpretation
  - Object and relationship extraction
- **Outputs To**: SceneX API for scene generation

## 2. Agent Layer

### Selenium API
- **Purpose**: Captures website content for visualization
- **Components**:
  - Automated browser control
  - Screenshot capture
  - Content extraction
- **Outputs To**: Redis MQ for communication with tools

### SceneX API
- **Purpose**: Handles advanced scene generation and animation
- **Components**:
  - Scene composition engine
  - Animation sequencing
  - Camera and lighting control
- **Outputs To**: Redis MQ for communication with tools

### Redis MQ
- **Purpose**: Communication bus between components
- **Components**:
  - Message queue
  - Pub/sub system
  - Request/response pattern handler
- **Outputs To**: Various tools in the Tool Layer

## 3. Tool Layer

### Anthropic
- **Purpose**: Advanced language processing and understanding
- **Components**:
  - Claude API integration
  - Prompt engineering for SVG generation
  - Instruction parsing

### AWS Bedrock
- **Purpose**: Cloud-based AI service integration
- **Components**:
  - Model hosting
  - API management
  - Scaling and resource allocation

### 8hrs Reduced To
- **Purpose**: Performance optimization for time-intensive tasks
- **Components**:
  - Processing time reduction
  - Workflow optimization
  - Resource allocation

### Alerts/IrisTool
- **Purpose**: Monitoring and notification system
- **Components**:
  - Process monitoring
  - Error detection and alerting
  - Status reporting

### Scene Generation API
- **Purpose**: Comprehensive scene generation and management
- **Components**:
  - Composite Scene Creation
  - Advanced Animation Library
  - Camera Control System
  - Scene Lighting Management
  - Material System for realistic rendering

## Workflow Examples

### 1. Network Visualization Workflow
1. User submits network diagram through Web UI
2. Selenium API captures the diagram
3. SVG to 3D conversion processes the diagram
4. Redis MQ routes the request to Scene Generation API
5. Scene Generation API creates a 3D representation with proper positioning
6. Animation sequences are added for data flow visualization
7. Final scene is rendered and returned to the user

### 2. Technical Diagram Workflow
1. User provides text description of desired technical diagram
2. Claude LLM generates an SVG diagram
3. SVG is processed and elements are extracted
4. SceneX API converts elements to 3D representations
5. Scene Generation API composes the complete scene
6. Advanced animation is applied to illustrate component relationships
7. Final visualization is rendered with professional lighting and materials

### 3. Natural Language to 3D Scene Workflow
1. User provides natural language description of desired scene
2. NLP processing extracts objects, relationships, and attributes
3. SceneX API plans the scene composition
4. Elements are positioned according to described relationships
5. Redis MQ coordinates with appropriate tools
6. Scene Generation API creates the complete scene with materials and lighting
7. Animation sequences are added as specified in the description
8. Final scene is rendered and delivered to the user

## Integration Points

- **Web UI to Agent Layer**: HTTP/WebSocket communication
- **Agent Layer to Redis MQ**: Asynchronous message passing
- **Redis MQ to Tools**: Structured message protocol
- **Tool Layer to Output**: Standardized file formats and metadata

This modular architecture allows for flexible workflow definition and component replacement while maintaining a consistent user experience and processing pipeline.
