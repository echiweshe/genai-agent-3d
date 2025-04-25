// src/components/settings/LLMModelSelector.js
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Slider, 
  TextField,
  Paper, 
  Divider,
  CircularProgress,
  Alert,
  Collapse,
  IconButton,
  Tooltip
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import SettingsIcon from '@mui/icons-material/Settings';
import CloseIcon from '@mui/icons-material/Close';
import SpeedIcon from '@mui/icons-material/Speed';
import { api } from '../../services/api';

/**
 * LLM Model Selector component for selecting and configuring language models
 */
const LLMModelSelector = ({ onModelChange }) => {
  // State for providers and models
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for selected provider and model
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [models, setModels] = useState([]);
  
  // State for model parameters
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [topP, setTopP] = useState(0.95);
  
  // State for advanced settings visibility
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Fetch available providers and models
  useEffect(() => {
    const fetchProviders = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get('/llm/providers');
        const providersData = response.data || [];
        
        setProviders(providersData);
        
        // Set default provider and model if available
        if (providersData.length > 0) {
          const defaultProvider = providersData.find(p => p.is_local) || providersData[0];
          setSelectedProvider(defaultProvider.name);
          
          if (defaultProvider.models && defaultProvider.models.length > 0) {
            setModels(defaultProvider.models);
            setSelectedModel(defaultProvider.models[0].id);
          }
        }
      } catch (err) {
        console.error('Error fetching LLM providers:', err);
        setError('Failed to load LLM providers. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchProviders();
  }, []);
  
  // Update models when provider changes
  useEffect(() => {
    if (selectedProvider) {
      const provider = providers.find(p => p.name === selectedProvider);
      
      if (provider && provider.models) {
        setModels(provider.models);
        
        // Set first model as default
        if (provider.models.length > 0 && !provider.models.some(m => m.id === selectedModel)) {
          setSelectedModel(provider.models[0].id);
        }
      } else {
        setModels([]);
        setSelectedModel('');
      }
    }
  }, [selectedProvider, providers]);
  
  // Notify parent component when selection changes
  useEffect(() => {
    if (selectedProvider && selectedModel) {
      const modelParams = {
        provider: selectedProvider,
        model: selectedModel,
        parameters: {
          temperature,
          max_tokens: maxTokens,
          top_p: topP
        }
      };
      
      onModelChange && onModelChange(modelParams);
    }
  }, [selectedProvider, selectedModel, temperature, maxTokens, topP, onModelChange]);
  
  // Get selected model information
  const getSelectedModelInfo = () => {
    if (!selectedProvider || !selectedModel) return null;
    
    const provider = providers.find(p => p.name === selectedProvider);
    if (!provider) return null;
    
    return provider.models.find(m => m.id === selectedModel);
  };
  
  // Render loading state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }
  
  // Get model info
  const modelInfo = getSelectedModelInfo();
  
  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Model Selection</Typography>
        <Tooltip title="Advanced Settings">
          <IconButton onClick={() => setShowAdvanced(!showAdvanced)}>
            <SettingsIcon />
          </IconButton>
        </Tooltip>
      </Box>
      
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="provider-select-label">Provider</InputLabel>
          <Select
            labelId="provider-select-label"
            id="provider-select"
            value={selectedProvider}
            label="Provider"
            onChange={(e) => setSelectedProvider(e.target.value)}
          >
            {providers.map((provider) => (
              <MenuItem key={provider.name} value={provider.name}>
                {provider.name} {provider.is_local ? "(Local)" : ""}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <FormControl fullWidth>
          <InputLabel id="model-select-label">Model</InputLabel>
          <Select
            labelId="model-select-label"
            id="model-select"
            value={selectedModel}
            label="Model"
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={models.length === 0}
          >
            {models.map((model) => (
              <MenuItem key={model.id} value={model.id}>
                {model.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
      
      {/* Model information */}
      {modelInfo && (
        <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Model Information
          </Typography>
          <Typography variant="body2">
            Context Length: {modelInfo.context_length.toLocaleString()} tokens
          </Typography>
          {!providers.find(p => p.name === selectedProvider)?.is_local && (
            <Typography variant="body2">
              Cost: ${modelInfo.input_cost.toFixed(6)}/1K input tokens, 
              ${modelInfo.output_cost.toFixed(6)}/1K output tokens
            </Typography>
          )}
        </Box>
      )}
      
      {/* Basic parameter - Temperature */}
      <Box sx={{ mb: 3 }}>
        <Typography id="temperature-slider-label" gutterBottom>
          Temperature: {temperature}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Tooltip title="More precise, deterministic responses">
            <Box sx={{ mr: 1 }}>0</Box>
          </Tooltip>
          <Slider
            value={temperature}
            onChange={(e, newValue) => setTemperature(newValue)}
            aria-labelledby="temperature-slider-label"
            min={0}
            max={1}
            step={0.1}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => value.toFixed(1)}
          />
          <Tooltip title="More creative, varied responses">
            <Box sx={{ ml: 1 }}>1</Box>
          </Tooltip>
        </Box>
      </Box>
      
      {/* Advanced settings */}
      <Collapse in={showAdvanced}>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>
          Advanced Settings
        </Typography>
        
        {/* Max Tokens */}
        <Box sx={{ mb: 3 }}>
          <Typography id="max-tokens-slider-label" gutterBottom>
            Max Tokens: {maxTokens}
          </Typography>
          <Slider
            value={maxTokens}
            onChange={(e, newValue) => setMaxTokens(newValue)}
            aria-labelledby="max-tokens-slider-label"
            min={256}
            max={4096}
            step={256}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => value.toLocaleString()}
          />
        </Box>
        
        {/* Top P */}
        <Box sx={{ mb: 3 }}>
          <Typography id="top-p-slider-label" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            Top P: {topP}
            <Tooltip title="Controls diversity by limiting to top X% of token probability mass">
              <IconButton size="small">
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Typography>
          <Slider
            value={topP}
            onChange={(e, newValue) => setTopP(newValue)}
            aria-labelledby="top-p-slider-label"
            min={0.1}
            max={1}
            step={0.05}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => value.toFixed(2)}
          />
        </Box>
      </Collapse>
    </Paper>
  );
};

export default LLMModelSelector;