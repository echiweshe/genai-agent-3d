#!/usr/bin/env python
"""
Script to enhance the settings page to display all LLM providers.
"""

import os
import glob
import re

# Get project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, "genai_agent_project")
frontend_dir = os.path.join(project_dir, "web", "frontend")

# Look for the settings page component
settings_files = glob.glob(os.path.join(frontend_dir, "src", "components", "pages", "*Settings*.jsx"))
settings_files.extend(glob.glob(os.path.join(frontend_dir, "src", "components", "pages", "*Settings*.js")))
settings_files.extend(glob.glob(os.path.join(frontend_dir, "src", "pages", "*Settings*.jsx")))
settings_files.extend(glob.glob(os.path.join(frontend_dir, "src", "pages", "*Settings*.js")))

if settings_files:
    settings_file = settings_files[0]
    print(f"Found settings file: {settings_file}")
    
    # Read the settings file
    with open(settings_file, "r") as f:
        content = f.read()
    
    # Create a backup
    backup_file = settings_file + ".bak"
    with open(backup_file, "w") as f:
        f.write(content)
    print(f"Created backup: {backup_file}")
    
    # Check if we need to enhance the LLM model settings section
    if "Language Model Settings" in content and "Provider" in content:
        # If we already have a component that fetches providers from API, no need to modify
        if "api.get('/api/llm/providers')" in content or "axios.get('/api/llm/providers')" in content:
            print("Settings file already contains code to fetch providers from API.")
        else:
            # Make required modifications based on the structure of the file
            # This is a simplified example and may need adjustment for your specific file structure
            
            # Create LLM model fetcher
            llm_fetcher_code = """
  // Fetch LLM providers from API
  const [providers, setProviders] = useState([]);
  const [loadingProviders, setLoadingProviders] = useState(false);
  
  // Fetch providers
  const fetchProviders = async () => {
    try {
      setLoadingProviders(true);
      const response = await axios.get('/api/llm/providers');
      setProviders(response.data);
    } catch (error) {
      console.error('Failed to fetch LLM providers:', error);
    } finally {
      setLoadingProviders(false);
    }
  };
  
  // Fetch providers on mount
  useEffect(() => {
    fetchProviders();
  }, []);
"""
            
            # Check if we need to add axios import
            if "import axios from 'axios'" not in content:
                content = re.sub(r'(import React.*?\n)', r'\1import axios from \'axios\';\n', content)
            
            # Add the fetcher code after useState declarations
            content = re.sub(r'(const \[.*?, set.*?\] = useState\([^;]*\);(?:\s+)?(?:\/\/.*?\n)?(?:\s+)?)+', r'\g<0>\n' + llm_fetcher_code, content, count=1)
            
            # Replace hardcoded provider options with dynamic ones
            select_section = re.search(r'<(Select|select)[^>]*id="provider-select"[^>]*>[\s\S]*?<\/(Select|select)>', content)
            if select_section:
                provider_select = select_section.group(0)
                
                # Create dynamic provider options
                dynamic_options = """
                {loadingProviders ? (
                  <MenuItem disabled>Loading providers...</MenuItem>
                ) : providers.length === 0 ? (
                  <MenuItem disabled>No providers available</MenuItem>
                ) : (
                  providers.map((provider) => (
                    <MenuItem key={provider.name} value={provider.name.toLowerCase()}>
                      {provider.name} {provider.is_local ? "(Local)" : ""}
                    </MenuItem>
                  ))
                )}
"""
                
                # Replace static options with dynamic ones
                new_provider_select = re.sub(r'<MenuItem[^>]*>.*?<\/MenuItem>(\s*<MenuItem[^>]*>.*?<\/MenuItem>)*', dynamic_options, provider_select)
                
                # Update the content
                content = content.replace(provider_select, new_provider_select)
            
            # Replace hardcoded model options with dynamic ones
            model_select = re.search(r'<(Select|select)[^>]*id="model-select"[^>]*>[\s\S]*?<\/(Select|select)>', content)
            if model_select:
                model_select_section = model_select.group(0)
                
                # Create dynamic model options
                dynamic_model_options = """
                {loadingProviders ? (
                  <MenuItem disabled>Loading models...</MenuItem>
                ) : !provider ? (
                  <MenuItem disabled>Select a provider first</MenuItem>
                ) : (
                  providers
                    .find(p => p.name.toLowerCase() === provider.toLowerCase())
                    ?.models.map((model) => (
                      <MenuItem key={model.id} value={model.id}>
                        {model.name}
                      </MenuItem>
                    )) || (
                      <MenuItem disabled>No models available</MenuItem>
                    )
                )}
"""
                
                # Replace static options with dynamic ones
                new_model_select = re.sub(r'<MenuItem[^>]*>.*?<\/MenuItem>(\s*<MenuItem[^>]*>.*?<\/MenuItem>)*', dynamic_model_options, model_select_section)
                
                # Update the content
                content = content.replace(model_select_section, new_model_select)
            
            # Write the modified content back
            with open(settings_file, "w") as f:
                f.write(content)
            print(f"Enhanced LLM provider selection in {settings_file}")
    else:
        print("Could not find Language Model Settings section in the settings file.")
        
        # Create a new LLM settings component that can be imported
        llm_settings_component_path = os.path.join(frontend_dir, "src", "components", "settings", "LLMSettings.jsx")
        os.makedirs(os.path.dirname(llm_settings_component_path), exist_ok=True)
        
        llm_settings_component = """import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  Button,
  CircularProgress,
  Alert
} from '@mui/material';
import axios from 'axios';

/**
 * LLM Settings component for configuring language model settings
 */
const LLMSettings = () => {
  // State for current settings
  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState(null);
  
  // State for available providers and models
  const [providers, setProviders] = useState([]);
  const [loadingProviders, setLoadingProviders] = useState(false);
  
  // Fetch current settings on mount
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await axios.get('/api/settings');
        const settings = response.data;
        
        if (settings.llm) {
          if (settings.llm.provider) {
            setProvider(settings.llm.provider.toLowerCase());
          }
          
          if (settings.llm.model) {
            setModel(settings.llm.model);
          }
        }
      } catch (error) {
        console.error('Failed to fetch settings:', error);
      }
    };
    
    fetchSettings();
  }, []);
  
  // Fetch available providers and models
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setLoadingProviders(true);
        const response = await axios.get('/api/llm/providers');
        setProviders(response.data);
      } catch (error) {
        console.error('Failed to fetch providers:', error);
        setError('Failed to fetch LLM providers. Make sure the backend is running.');
      } finally {
        setLoadingProviders(false);
      }
    };
    
    fetchProviders();
  }, []);
  
  // Get models for the selected provider
  const getModelsForProvider = () => {
    if (!provider) return [];
    
    const selectedProvider = providers.find(p => p.name.toLowerCase() === provider.toLowerCase());
    return selectedProvider?.models || [];
  };
  
  // Handle save
  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSaveSuccess(false);
      
      // Save settings
      await axios.post('/api/settings', {
        section: 'llm',
        settings: {
          provider,
          model
        }
      });
      
      setSaveSuccess(true);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
      setError('Failed to save settings: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };
  
  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Language Model Settings
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully!
        </Alert>
      )}
      
      <Box sx={{ mb: 2 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="provider-label">Provider</InputLabel>
          <Select
            labelId="provider-label"
            id="provider-select"
            value={provider}
            label="Provider"
            onChange={(e) => {
              setProvider(e.target.value);
              setModel(''); // Reset model when provider changes
            }}
            disabled={loadingProviders || saving}
          >
            {loadingProviders ? (
              <MenuItem disabled>Loading providers...</MenuItem>
            ) : providers.length === 0 ? (
              <MenuItem disabled>No providers available</MenuItem>
            ) : (
              providers.map((provider) => (
                <MenuItem key={provider.name} value={provider.name.toLowerCase()}>
                  {provider.name} {provider.is_local ? "(Local)" : ""}
                </MenuItem>
              ))
            )}
          </Select>
        </FormControl>
        
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="model-label">Model</InputLabel>
          <Select
            labelId="model-label"
            id="model-select"
            value={model}
            label="Model"
            onChange={(e) => setModel(e.target.value)}
            disabled={!provider || loadingProviders || saving}
          >
            {loadingProviders ? (
              <MenuItem disabled>Loading models...</MenuItem>
            ) : !provider ? (
              <MenuItem disabled>Select a provider first</MenuItem>
            ) : (
              getModelsForProvider().map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name}
                </MenuItem>
              ))
            )}
          </Select>
        </FormControl>
        
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
          Choose the language model provider and specific model to use for text generation.
          Local providers like Ollama run on your machine, while cloud providers require API keys.
        </Typography>
        
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={!provider || !model || saving}
          startIcon={saving && <CircularProgress size={20} color="inherit" />}
        >
          {saving ? 'Saving...' : 'Save Model Settings'}
        </Button>
      </Box>
    </Paper>
  );
};

export default LLMSettings;
"""
        
        with open(llm_settings_component_path, "w") as f:
            f.write(llm_settings_component)
        print(f"Created new LLM Settings component: {llm_settings_component_path}")
        
        # Add instructions for importing the component
        print("\nYou can import the LLM Settings component in your Settings page with:")
        print("import LLMSettings from '../components/settings/LLMSettings';")
        print("And then use it in your JSX with: <LLMSettings />")
else:
    print("Could not find Settings page component.")
    
    # Create an API endpoint for settings in the backend
    backend_dir = os.path.join(project_dir, "genai_agent", "services")
    settings_api_path = os.path.join(backend_dir, "settings_api.py")
    
    settings_api_content = """
\"\"\"
API for settings management
\"\"\"

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/settings", tags=["settings"])

# Settings file path
SETTINGS_FILE = "settings.json"

# Get settings file path
def get_settings_file():
    # Get project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(project_dir, SETTINGS_FILE)

# Models
class UpdateSettingsRequest(BaseModel):
    section: str
    settings: Dict[str, Any]

# Utility to load settings
def load_settings():
    try:
        settings_file = get_settings_file()
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return {}

# Utility to save settings
def save_settings(settings):
    try:
        settings_file = get_settings_file()
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return False

@router.get("")
async def get_settings():
    \"\"\"
    Get all settings
    \"\"\"
    try:
        settings = load_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")

@router.post("")
async def update_settings(request: UpdateSettingsRequest):
    \"\"\"
    Update settings
    \"\"\"
    try:
        settings = load_settings()
        
        # Update the specified section
        if request.section not in settings:
            settings[request.section] = {}
        
        # Update settings
        settings[request.section].update(request.settings)
        
        # Save settings
        if save_settings(settings):
            return {"status": "success", "message": "Settings updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save settings")
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

# Define function to add settings routes to the main application
def add_settings_routes(app):
    \"\"\"
    Add settings routes to the FastAPI application
    \"\"\"
    app.include_router(router)
"""
    
    with open(settings_api_path, "w") as f:
        f.write(settings_api_content)
    print(f"Created settings API: {settings_api_path}")
    
    # Add instructions for integrating the settings API
    print("\nYou need to add the settings API routes to main.py:")
    print("from genai_agent.services.settings_api import add_settings_routes")
    print("# After creating the FastAPI app")
    print("add_settings_routes(app)")

print("\nNext steps:")
print("1. Restart the backend: python manage_services.py restart backend")
print("2. Restart the frontend: python manage_services.py restart frontend")
print("3. Navigate to the settings page in your application")
