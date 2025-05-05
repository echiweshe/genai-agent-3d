# SVG Generator GUI

A graphical user interface for generating SVG diagrams from natural language descriptions using various LLM providers like Claude, OpenAI, and others.

## Features

- **Natural Language Input**: Generate SVG diagrams by describing what you want in plain English
- **Multiple LLM Providers**: Support for Claude Direct, LangChain-based providers, and Redis-based LLM services
- **Specialized Diagram Types**: Create flowcharts, network diagrams, sequence diagrams, and more
- **SVG Preview**: View generated SVGs directly in your browser
- **Save Options**: Save SVGs to any location on your computer
- **3D Conversion** (when available): Convert SVGs to 3D models (requires Blender's mathutils module)

## Requirements

- Python 3.8+
- Tkinter (included with most Python installations)
- Required Python packages (automatically installed with the project)

## Installation

No additional installation is required if you've already set up the SVG to Video pipeline. The GUI uses the same components and dependencies.

## Usage

### Running the GUI

1. Double-click on `run_svg_gui.bat` to start the application
2. Or run from the command line: `python svg_generator_gui.py`

### Generating an SVG

1. **Select an LLM Provider**: Choose from available providers (Claude Direct recommended)
2. **Select a Diagram Type**: Choose the type of diagram you want to create
3. **Enter a Description**: Describe the diagram you want in natural language
   - You can use the example buttons to get started
4. **Click "Generate SVG"**: The application will send your request to the LLM and generate the SVG
5. **View and Save**: After generation, you can view the SVG in your browser and save it to any location

### 3D Conversion (Optional)

If Blender's `mathutils` module is available, you can convert the generated SVG to a 3D model:

1. Generate an SVG as described above
2. Click the "Convert to 3D" button
3. The 3D model will be saved in the output/models directory

## Example Descriptions

### Flowchart Example

```
A detailed flowchart showing the process of online shopping from a user's perspective, including steps for browsing products, adding items to cart, checkout process, payment options, and order confirmation.
```

### Network Diagram Example

```
A network diagram illustrating a secure enterprise network architecture with multiple security zones, including internet-facing DMZ, internal network segments, firewalls, load balancers, web servers, application servers, and database servers.
```

### Sequence Diagram Example

```
A sequence diagram showing the authentication process for a web application, including the interactions between user, browser, authentication service, user database, and email notification system.
```

## Troubleshooting

### LLM Provider Issues

- If Claude Direct is not available, make sure your ANTHROPIC_API_KEY is set in the environment variables
- Check the logs in `svg_generator_gui.log` for detailed error messages

### 3D Conversion Issues

- 3D conversion requires Blender's `mathutils` module
- If the "Convert to 3D" button is disabled, the required dependencies are not available
- Install Blender and set up the Python environment to include Blender's Python modules
