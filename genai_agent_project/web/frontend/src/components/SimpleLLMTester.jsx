import React, { useState, useEffect } from 'react';
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
