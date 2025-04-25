#!/usr/bin/env python
"""
Final fixes for the GenAI Agent 3D LLM integration.
This script addresses any remaining issues and ensures everything is working correctly.
"""

import os
import sys
import subprocess
import shutil
import glob
import re

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
frontend_dir = os.path.join(project_dir, "web", "frontend")
backend_dir = os.path.join(project_dir, "genai_agent")

print("=" * 80)
print("GenAI Agent 3D - Final Fixes".center(80))
print("=" * 80)
print()

# Fix 1: Ensure __init__.py files exist
print("Fix 1: Ensuring __init__.py files exist in all directories...")

dirs_to_check = [
    os.path.join(project_dir, "genai_agent"),
    os.path.join(project_dir, "genai_agent", "services"),
    os.path.join(project_dir, "genai_agent", "tools"),
    os.path.join(project_dir, "genai_agent", "api"),
    os.path.join(project_dir, "genai_agent", "integrations"),
]

for directory in dirs_to_check:
    init_file = os.path.join(directory, "__init__.py")
    os.makedirs(directory, exist_ok=True)
    
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Package initialization file\n")
        print(f"✅ Created __init__.py in {directory}")
    else:
        print(f"ℹ️ __init__.py already exists in {directory}")

print()

# Fix 2: Check and fix svg_processor.py
print("Fix 2: Checking and fixing svg_processor.py...")

svg_processor_path = os.path.join(backend_dir, "tools", "svg_processor.py")
if os.path.exists(svg_processor_path):
    with open(svg_processor_path, "r") as f:
        svg_processor_content = f.read()
    
    # Look for f-string with backslash issue (line 371 according to logs)
    matches = re.findall(r'f".*?\\.*?"', svg_processor_content)
    
    if matches:
        print(f"Found {len(matches)} f-strings with backslashes that need fixing:")
        for i, match in enumerate(matches):
            print(f"  {i+1}. {match}")
            
            # Replace backslashes with double backslashes in f-strings
            fixed_match = match.replace("\\", "\\\\")
            svg_processor_content = svg_processor_content.replace(match, fixed_match)
        
        with open(svg_processor_path, "w") as f:
            f.write(svg_processor_content)
        print("✅ Fixed f-string backslash issues in svg_processor.py")
    else:
        print("ℹ️ No f-string issues found in svg_processor.py")
else:
    print("ℹ️ svg_processor.py not found, skipping fix")

print()

# Fix 3: Create a ReactJS SimpleLLMTester component file
print("Fix 3: Creating a standalone SimpleLLMTester component...")

os.makedirs(os.path.join(frontend_dir, "src", "components"), exist_ok=True)
simple_tester_path = os.path.join(frontend_dir, "src", "components", "SimpleLLMTester.jsx")

simple_tester_content = """import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  CircularProgress, 
  TextField, 
  Typography, 
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert
} from '@mui/material';
import axios from 'axios';

/**
 * A simple component to test LLM functionality
 */
function SimpleLLMTester() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prompt, setPrompt] = useState('Create a 3D model of a mountain landscape');
  const [response, setResponse] = useState('');
  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');
  const [providers, setProviders] = useState([]);
  const [models, setModels] = useState([]);

  // Fetch providers on component mount
  useEffect(() => {
    fetchProviders();
  }, []);

  // Update models when provider changes
  useEffect(() => {
    if (provider) {
      const selectedProvider = providers.find(p => p.name.toLowerCase() === provider.toLowerCase());
      if (selectedProvider && selectedProvider.models) {
        setModels(selectedProvider.models);
        if (selectedProvider.models.length > 0) {
          setModel(selectedProvider.models[0].id);
        }
      }
    }
  }, [provider, providers]);

  // Fetch available LLM providers
  const fetchProviders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/api/llm/providers');
      const providersData = response.data || [];
      
      setProviders(providersData);
      
      // Set default provider and model
      if (providersData.length > 0) {
        setProvider(providersData[0].name.toLowerCase());
      }
    } catch (err) {
      console.error('Error fetching providers:', err);
      setError('Failed to fetch LLM providers. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Generate text with the selected model
  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResponse('');
      
      const data = {
        prompt,
        provider, 
        model,
        parameters: {
          temperature: 0.7,
          max_tokens: 2048
        }
      };

      console.log('Sending request to /api/llm/generate:', data);
      
      const response = await axios.post('/api/llm/generate', data);
      
      if (response.data && response.data.text) {
        setResponse(response.data.text);
      } else if (response.data && typeof response.data === 'string') {
        setResponse(response.data);
      } else {
        setResponse(JSON.stringify(response.data, null, 2));
      }
    } catch (err) {
      console.error('Error generating text:', err);
      setError(`Error: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        LLM Tester
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="provider-label">LLM Provider</InputLabel>
          <Select
            labelId="provider-label"
            id="provider-select"
            value={provider}
            label="LLM Provider"
            onChange={(e) => setProvider(e.target.value)}
            disabled={loading || providers.length === 0}
          >
            {providers.map((p) => (
              <MenuItem key={p.name} value={p.name.toLowerCase()}>{p.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel id="model-label">Model</InputLabel>
          <Select
            labelId="model-label"
            id="model-select"
            value={model}
            label="Model"
            onChange={(e) => setModel(e.target.value)}
            disabled={loading || models.length === 0}
          >
            {models.map((m) => (
              <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <TextField
          label="Prompt"
          multiline
          rows={4}
          fullWidth
          variant="outlined"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={loading}
          sx={{ mb: 3 }}
        />
        
        <Button
          variant="contained"
          color="primary"
          onClick={handleGenerate}
          disabled={loading || !prompt.trim()}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
          fullWidth
        >
          {loading ? 'Generating...' : 'Generate'}
        </Button>
      </Paper>
      
      {response && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Response
          </Typography>
          
          <Box sx={{ 
            bgcolor: 'background.paper', 
            p: 2, 
            borderRadius: 1, 
            maxHeight: '400px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace'
          }}>
            {response}
          </Box>
        </Paper>
      )}
    </Box>
  );
}

export default SimpleLLMTester;
"""

with open(simple_tester_path, 'w') as f:
    f.write(simple_tester_content)
print(f"✅ Created SimpleLLMTester component at {simple_tester_path}")

# Fix 4: Create a LLM test page
print("\nFix 4: Creating an LLM Test Page...")

llm_test_page_path = os.path.join(frontend_dir, "src", "components", "pages", "LLMTestPage.jsx")
os.makedirs(os.path.join(frontend_dir, "src", "components", "pages"), exist_ok=True)

llm_test_page_content = """import React from 'react';
import { Box, Typography } from '@mui/material';
import SimpleLLMTester from '../SimpleLLMTester';

const LLMTestPage = () => {
  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        LLM Testing
      </Typography>
      
      <Typography variant="body1" paragraph>
        Test the LLM integration by generating text with different models.
      </Typography>
      
      <SimpleLLMTester />
    </Box>
  );
};

export default LLMTestPage;
"""

with open(llm_test_page_path, 'w') as f:
    f.write(llm_test_page_content)
print(f"✅ Created LLM Test Page at {llm_test_page_path}")

# Fix 5: Update app router to include LLM test page
print("\nFix 5: Updating App Router to include LLM Test page...")

app_router_path = os.path.join(frontend_dir, "src", "AppRouter.jsx")

if os.path.exists(app_router_path):
    with open(app_router_path, 'r') as f:
        app_router_content = f.read()
    
    # Check if LLMTestPage is already imported
    if "import LLMTestPage from './components/pages/LLMTestPage'" not in app_router_content:
        # Add import
        app_router_content = re.sub(
            r'(import .*? from .*?;\n)(?!import)',
            r'\1import LLMTestPage from \'./components/pages/LLMTestPage\';\n',
            app_router_content,
            1
        )
        
        # Add route
        if "<Route path=\"/llm-test\" element={<LLMTestPage />} />" not in app_router_content:
            app_router_content = re.sub(
                r'(<Routes>.*?)(\s*</Routes>)',
                r'\1\n        <Route path="/llm-test" element={<LLMTestPage />} />\2',
                app_router_content,
                1,
                re.DOTALL
            )
    
        with open(app_router_path, 'w') as f:
            f.write(app_router_content)
        print(f"✅ Updated App Router to include LLM Test page")
    else:
        print(f"ℹ️ LLM Test page already included in App Router")
else:
    print(f"❌ Could not find App Router at {app_router_path}")

# Fix 6: Add link to LLM Test page in the sidebar
print("\nFix 6: Adding link to LLM Test page in the sidebar...")

sidebar_path = os.path.join(frontend_dir, "src", "components", "Sidebar.jsx")

if os.path.exists(sidebar_path):
    with open(sidebar_path, 'r') as f:
        sidebar_content = f.read()
    
    # Check if LLM Test link is already added
    if "/llm-test" not in sidebar_content:
        # Add LLM Test to sidebar items
        if "const sidebarItems = [" in sidebar_content:
            sidebar_content = re.sub(
                r'(const sidebarItems = \[\s*{[^}]*},\s*)(\];)',
                r'\1  {\n    name: \'LLM Test\',\n    icon: <ChatIcon />,\n    path: \'/llm-test\'\n  },\n\2',
                sidebar_content,
                1,
                re.DOTALL
            )
        
            # Make sure ChatIcon is imported
            if "ChatIcon" not in sidebar_content:
                sidebar_content = re.sub(
                    r'(import {.*?} from \'@mui/icons-material\';)',
                    r'import { ChatIcon, \1',
                    sidebar_content
                )
        
            with open(sidebar_path, 'w') as f:
                f.write(sidebar_content)
            print(f"✅ Added LLM Test link to sidebar")
        else:
            print(f"❌ Could not find sidebar items array in {sidebar_path}")
    else:
        print(f"ℹ️ LLM Test link already exists in sidebar")
else:
    print(f"❌ Could not find Sidebar component at {sidebar_path}")

print("\nFinal fixes completed! 🎉")
print("1. Restart the application using: python manage_services.py restart all")
print("2. Access the web interface at: http://localhost:3000")
print("3. Navigate to the LLM Test page from the sidebar")
print("\nHappy 3D generating with AI! 🚀")
