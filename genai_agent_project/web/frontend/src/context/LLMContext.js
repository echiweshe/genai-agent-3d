// src/context/LLMContext.js
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import websocketService, { WS_STATUS } from '../services/websocket';

// Create context
const LLMContext = createContext();

// Default LLM parameters
const DEFAULT_TEMPERATURE = 0.7;
const DEFAULT_MAX_TOKENS = 2048;
const DEFAULT_TOP_P = 0.95;

/**
 * Provider component for LLM context
 */
export const LLMProvider = ({ children }) => {
  // State for available providers
  const [providers, setProviders] = useState([]);
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [providersError, setProvidersError] = useState(null);
  
  // State for selected provider and model
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  
  // State for model parameters
  const [temperature, setTemperature] = useState(DEFAULT_TEMPERATURE);
  const [maxTokens, setMaxTokens] = useState(DEFAULT_MAX_TOKENS);
  const [topP, setTopP] = useState(DEFAULT_TOP_P);
  
  // State for WebSocket connection
  const [wsStatus, setWsStatus] = useState(WS_STATUS.CLOSED);
  
  // State for ongoing requests
  const [ongoingRequests, setOngoingRequests] = useState({});
  
  // Fetch available providers when component mounts
  useEffect(() => {
    fetchProviders();
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Add WebSocket status listener
    const removeStatusListener = websocketService.onStatusChange(status => {
      setWsStatus(status);
      
      // If disconnected, try to reconnect
      if (status === WS_STATUS.CLOSED || status === WS_STATUS.ERROR) {
        setTimeout(connectWebSocket, 3000);
      }
    });
    
    // Add message listener for LLM responses
    const removeMessageListener = websocketService.onMessage('result', handleLLMResponse);
    
    // Clean up on unmount
    return () => {
      removeStatusListener();
      removeMessageListener();
      websocketService.disconnect();
    };
  }, []);
  
  // Connect to WebSocket
  const connectWebSocket = useCallback(async () => {
    try {
      await websocketService.connect();
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
    }
  }, []);
  
  // Handle LLM response from WebSocket
  const handleLLMResponse = useCallback((data) => {
    const { request_id, status, result, error } = data;
    
    // Check if we have a callback for this request
    if (request_id && ongoingRequests[request_id]) {
      const { onComplete, onError } = ongoingRequests[request_id];
      
      if (status === 'error' && onError) {
        onError(error || 'Unknown error');
      } else if (onComplete) {
        onComplete(result);
      }
      
      // Remove from ongoing requests
      setOngoingRequests(prev => {
        const updated = { ...prev };
        delete updated[request_id];
        return updated;
      });
    }
  }, [ongoingRequests]);
  
  // Fetch available providers
  const fetchProviders = async () => {
    setLoadingProviders(true);
    setProvidersError(null);
    
    try {
      const response = await api.get('/api/llm/providers');
      const providersData = response.data || [];
      
      setProviders(providersData);
      
      // Set default provider and model if available
      if (providersData.length > 0) {
        // Prefer local providers
        const defaultProvider = providersData.find(p => p.is_local) || providersData[0];
        setSelectedProvider(defaultProvider.name);
        
        if (defaultProvider.models && defaultProvider.models.length > 0) {
          setSelectedModel(defaultProvider.models[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching LLM providers:', error);
      setProvidersError('Failed to load LLM providers');
    } finally {
      setLoadingProviders(false);
    }
  };
  
  // Generate text using the selected model
  const generateText = async (prompt, options = {}) => {
    // Check if provider and model are selected
    if (!selectedProvider || !selectedModel) {
      throw new Error('No LLM provider or model selected');
    }
    
    // Generate a unique request ID
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    
    // If WebSocket is connected, use it for real-time processing
    if (wsStatus === WS_STATUS.OPEN) {
      return new Promise((resolve, reject) => {
        // Add to ongoing requests
        setOngoingRequests(prev => ({
          ...prev,
          [requestId]: {
            prompt,
            timestamp: Date.now(),
            onComplete: resolve,
            onError: reject
          }
        }));
        
        // Send request via WebSocket
        websocketService.send({
          type: 'generate',
          request_id: requestId,
          prompt,
          provider: selectedProvider,
          model: selectedModel,
          parameters: {
            temperature: options.temperature || temperature,
            max_tokens: options.maxTokens || maxTokens,
            top_p: options.topP || topP,
            ...options.parameters
          }
        });
      });
    } else {
      // Fall back to REST API if WebSocket is not connected
      const response = await api.post('/api/llm/generate', {
        prompt,
        provider: selectedProvider,
        model: selectedModel,
        parameters: {
          temperature: options.temperature || temperature,
          max_tokens: options.maxTokens || maxTokens,
          top_p: options.topP || topP,
          ...options.parameters
        },
        timeout: options.timeout || 120
      });
      
      return response.data;
    }
  };
  
  // Classify a user instruction into a structured task
  const classifyTask = async (instruction, options = {}) => {
    // Check if provider and model are selected
    if (!selectedProvider || !selectedModel) {
      throw new Error('No LLM provider or model selected');
    }
    
    try {
      const response = await api.post('/api/llm/classify-task', {
        instruction,
        provider: options.provider || selectedProvider,
        model: options.model || selectedModel
      });
      
      return response.data;
    } catch (error) {
      console.error('Error classifying task:', error);
      throw error;
    }
  };
  
  // Plan the execution of a task
  const planTaskExecution = async (task, availableTools, options = {}) => {
    // Check if provider and model are selected
    if (!selectedProvider || !selectedModel) {
      throw new Error('No LLM provider or model selected');
    }
    
    try {
      const response = await api.post('/api/llm/plan-task', {
        task,
        available_tools: availableTools,
        provider: options.provider || selectedProvider,
        model: options.model || selectedModel
      });
      
      return response.data;
    } catch (error) {
      console.error('Error planning task execution:', error);
      throw error;
    }
  };
  
  // Update model configuration
  const updateModelConfig = useCallback((config) => {
    if (config.provider) {
      setSelectedProvider(config.provider);
    }
    
    if (config.model) {
      setSelectedModel(config.model);
    }
    
    if (config.parameters) {
      const { temperature: temp, max_tokens: tokens, top_p: p } = config.parameters;
      
      if (temp !== undefined) {
        setTemperature(temp);
      }
      
      if (tokens !== undefined) {
        setMaxTokens(tokens);
      }
      
      if (p !== undefined) {
        setTopP(p);
      }
    }
  }, []);
  
  // Get current model configuration
  const getModelConfig = useCallback(() => {
    return {
      provider: selectedProvider,
      model: selectedModel,
      parameters: {
        temperature,
        max_tokens: maxTokens,
        top_p: topP
      }
    };
  }, [selectedProvider, selectedModel, temperature, maxTokens, topP]);
  
  // Get information about the selected model
  const getSelectedModelInfo = useCallback(() => {
    if (!selectedProvider || !selectedModel) return null;
    
    const provider = providers.find(p => p.name === selectedProvider);
    if (!provider) return null;
    
    return provider.models.find(m => m.id === selectedModel);
  }, [providers, selectedProvider, selectedModel]);
  
  // Create context value
  const contextValue = {
    // Providers data
    providers,
    loadingProviders,
    providersError,
    refreshProviders: fetchProviders,
    
    // Selected provider and model
    selectedProvider,
    selectedModel,
    setSelectedProvider,
    setSelectedModel,
    
    // Model parameters
    temperature,
    maxTokens,
    topP,
    setTemperature,
    setMaxTokens,
    setTopP,
    
    // WebSocket status
    wsStatus,
    
    // Methods
    generateText,
    classifyTask,
    planTaskExecution,
    updateModelConfig,
    getModelConfig,
    getSelectedModelInfo
  };
  
  return (
    <LLMContext.Provider value={contextValue}>
      {children}
    </LLMContext.Provider>
  );
};

/**
 * Hook to use LLM context
 */
export const useLLM = () => {
  const context = useContext(LLMContext);
  
  if (!context) {
    throw new Error('useLLM must be used within an LLMProvider');
  }
  
  return context;
};