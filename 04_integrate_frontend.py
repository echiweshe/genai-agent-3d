#!/usr/bin/env python
"""
Script to integrate the SimpleLLMTester component into the frontend.
"""

import os
import shutil

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
frontend_dir = os.path.join(project_dir, "web", "frontend")
components_dir = os.path.join(frontend_dir, "src", "components")
pages_dir = os.path.join(frontend_dir, "src", "components", "pages")

# Ensure directories exist
os.makedirs(pages_dir, exist_ok=True)

# Copy SimpleLLMTester to components
source_file = os.path.join(script_dir, "simple_llm_tester.jsx")
destination_file = os.path.join(components_dir, "SimpleLLMTester.jsx")

# Check if source exists
if os.path.exists(source_file):
    # Create a backup if destination already exists
    if os.path.exists(destination_file):
        backup_file = destination_file + ".bak"
        shutil.copy2(destination_file, backup_file)
        print(f"Created backup: {backup_file}")
    
    # Copy the file
    shutil.copy2(source_file, destination_file)
    print(f"Copied: {source_file} -> {destination_file}")
else:
    print(f"Warning: Source file not found: {source_file}")

# Create a test page that includes the SimpleLLMTester
test_page_path = os.path.join(pages_dir, "LLMTestPage.jsx")
test_page_content = """
import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import SimpleLLMTester from '../SimpleLLMTester';

/**
 * Page for testing LLM functionality
 */
function LLMTestPage() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          LLM Testing Page
        </Typography>
        <Typography variant="body1" paragraph align="center">
          Use this page to test the LLM functionality
        </Typography>
        
        <SimpleLLMTester />
      </Box>
    </Container>
  );
}

export default LLMTestPage;
"""

with open(test_page_path, "w") as f:
    f.write(test_page_content)
print(f"Created: {test_page_path}")

# Check for App.js to add the route
app_js_path = os.path.join(frontend_dir, "src", "App.js")

if os.path.exists(app_js_path):
    with open(app_js_path, "r") as f:
        content = f.read()
    
    # Check if we need to add imports and routes
    if "import LLMTestPage from './components/pages/LLMTestPage'" not in content:
        # Add import
        import_lines = []
        route_lines = []
        
        # Find where the imports end
        lines = content.split("\n")
        import_end_index = 0
        for i, line in enumerate(lines):
            if line.startswith("import "):
                import_end_index = i
        
        # Add our import after the last import
        if import_end_index > 0:
            lines.insert(import_end_index + 1, "import LLMTestPage from './components/pages/LLMTestPage';")
        
        # Find the routes section
        for i, line in enumerate(lines):
            if "<Routes>" in line:
                # Find the closing </Routes> tag
                for j in range(i+1, len(lines)):
                    if "</Routes>" in lines[j]:
                        # Add our route before the closing tag
                        lines.insert(j, "          <Route path=\"/llm-test\" element={<LLMTestPage />} />")
                        break
                break
        
        # Write the modified content back
        with open(app_js_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Updated: {app_js_path}")
    else:
        print(f"No changes needed for {app_js_path}, route already exists")
else:
    print(f"Warning: {app_js_path} not found")

# Create a markdown file with instructions
instructions_path = os.path.join(script_dir, "FRONTEND_INTEGRATION.md")
instructions_content = """# Frontend Integration Instructions

The SimpleLLMTester component has been integrated into your frontend.

## How to Access the Tester

1. Make sure all services are running:
   ```
   cd genai_agent_project
   .\venv\Scripts\activate
   python manage_services.py restart all
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3000/llm-test
   ```

## What to Expect

- The LLM Tester page will display a form with:
  - Provider selection dropdown
  - Model selection dropdown
  - Prompt input field
  - Generate button

- When you click Generate, it will send a request to the backend LLM service
  and display the response.

## Troubleshooting

1. If you don't see any providers in the dropdown:
   - Check that the backend is running correctly
   - Look for errors in the browser console
   - Try refreshing the page

2. If you get an error when generating text:
   - Ensure Ollama is running 
   - Check that the model specified is actually available in Ollama
   - Check the backend logs for errors

3. If the page doesn't load:
   - Make sure the frontend service is running
   - Check for any React errors in the console
"""

with open(instructions_path, "w") as f:
    f.write(instructions_content)
print(f"Created: {instructions_path}")

print("\nFrontend integration complete.")
print("\nNext steps:")
print("1. Restart all services: python manage_services.py restart all")
print("2. Open your browser and go to: http://localhost:3000/llm-test")
