# SVG Generator Web UI Integration

This document explains how the SVG Generator has been integrated into the GenAI Agent 3D web UI, allowing users to generate SVG diagrams directly through the web interface using various LLM providers.

## Overview

The SVG Generator has been integrated into the existing Diagrams page of the GenAI Agent 3D web UI. This integration allows users to:

1. Create SVG diagrams from natural language descriptions
2. Choose from different LLM providers (Claude, OpenAI, etc.)
3. Select diagram types (flowchart, network, sequence, etc.)
4. View, export and manage generated diagrams

## Components 

The integration consists of the following components:

### Backend

1. **SVG Generator Routes** (`routes/svg_generator_routes.py`):
   - API endpoints for SVG generation
   - Endpoints for listing available providers and diagram types
   - Saves generated SVGs to the appropriate output directories

2. **SVG Generator Tool** (`genai_agent/tools/svg_generator_tool.py`):
   - Tool implementation for the agent's tool registry
   - Handles SVG generation using the LLM factory
   - Provides a standardized interface for execution

### Frontend

1. **Enhanced DiagramsPage** (`components/pages/DiagramsPage.js`):
   - Updated UI with support for SVG generation
   - Provider selection dropdown for SVG format
   - Integration with new backend endpoints

## Usage

1. **Start the Integrated UI**:
   ```
   start_integrated_ui.bat
   ```

2. **Navigate to the Diagrams Page**:
   - Open a web browser and go to `http://localhost:3000`
   - Click on "Diagrams" in the sidebar

3. **Generate an SVG Diagram**:
   - Enter a description of the diagram you want to create
   - Select "SVG" as the format (should be the default)
   - Choose a diagram type (flowchart, network, etc.)
   - Select an LLM provider (Claude Direct recommended)
   - Click "Generate Diagram"

4. **View and Export Diagrams**:
   - Generated diagrams will appear in the "Generated Diagrams" section
   - Click the eye icon to view a diagram
   - Click the download icon to export a diagram
   - Click the trash icon to delete a diagram

## Example Descriptions

### Flowchart
```
A detailed flowchart showing the process of online shopping from a user's perspective, including steps for browsing products, adding items to cart, checkout process, payment options, and order confirmation.
```

### Network Diagram
```
A network diagram illustrating a secure enterprise network architecture with multiple security zones, including internet-facing DMZ, internal network segments, firewalls, load balancers, web servers, application servers, and database servers.
```

### Sequence Diagram
```
A sequence diagram showing the authentication process for a web application, including the interactions between user, browser, authentication service, user database, and email notification system.
```

## Troubleshooting

1. **No LLM Providers Available**:
   - Make sure the necessary API keys are set in the environment variables
   - For Claude, set `ANTHROPIC_API_KEY`
   - For OpenAI, set `OPENAI_API_KEY`

2. **SVG Generation Fails**:
   - Check the backend logs for detailed error messages
   - Verify that the LLM providers are available and configured correctly

3. **Frontend Not Loading**:
   - Make sure the backend server is running properly
   - Check the browser console for errors
   - Try refreshing the page

## Technical Notes

- The integration uses the LLM factory from the SVG to Video pipeline
- Generated SVGs are stored in both `output/svg` and `output/diagrams` directories
- The frontend uses the Material-UI library for components
- The DiagramViewer component has been extended to handle SVG rendering

## Extending the Integration

To add support for additional diagram types or LLM providers:

1. Update the `get_diagram_types` endpoint in `svg_generator_routes.py`
2. Modify the LLM factory to support new providers
3. Update the frontend DiagramsPage component to display the new options
