// LLMTester.jsx - Component to test the LLM service
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LLMTester = () => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [models, setModels] = useState([]);
  const [prompt, setPrompt] = useState('Create a 3D model of a mountain landscape');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Fetch providers on component mount
  useEffect(() => {
    fetchProviders();
  }, []);
  
  // Update models when provider changes
  useEffect(() => {
    if (selectedProvider) {
      const provider = providers.find(p => p.name === selectedProvider);
      if (provider) {
        setModels(provider.models);
        if (provider.models.length > 0) {
          setSelectedModel(provider.models[0].id);
        }
      }
    }
  }, [selectedProvider, providers]);
  
  const fetchProviders = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/llm/providers');
      const providersData = response.data || [];
      
      setProviders(providersData);
      
      // Set default provider and model
      if (providersData.length > 0) {
        const defaultProvider = providersData.find(p => p.is_local) || providersData[0];
        setSelectedProvider(defaultProvider.name);
      }
    } catch (err) {
      console.error('Error fetching providers:', err);
      setError('Failed to fetch LLM providers');
    } finally {
      setLoading(false);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedProvider || !selectedModel) {
      setError('Please select a provider and model');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResponse('');
    
    try {
      const response = await axios.post('/api/llm/generate', {
        prompt,
        provider: selectedProvider,
        model: selectedModel,
        parameters: {
          temperature: 0.7,
          max_tokens: 2048
        }
      });
      
      setResponse(response.data.text || JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.error('Error generating text:', err);
      setError(err.response?.data?.detail || 'Failed to generate text');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>LLM Service Tester</h1>
      
      {error && (
        <div style={{ 
          backgroundColor: '#ffebee', 
          color: '#c62828', 
          padding: '10px', 
          borderRadius: '4px',
          marginBottom: '20px' 
        }}>
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Provider:
          </label>
          <select 
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            style={{ 
              width: '100%', 
              padding: '8px', 
              borderRadius: '4px',
              border: '1px solid #ccc' 
            }}
            disabled={loading || providers.length === 0}
          >
            {providers.length === 0 && <option value="">No providers available</option>}
            {providers.map(provider => (
              <option key={provider.name} value={provider.name}>
                {provider.name} {provider.is_local ? "(Local)" : ""}
              </option>
            ))}
          </select>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Model:
          </label>
          <select 
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            style={{ 
              width: '100%', 
              padding: '8px', 
              borderRadius: '4px',
              border: '1px solid #ccc' 
            }}
            disabled={loading || models.length === 0}
          >
            {models.length === 0 && <option value="">No models available</option>}
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Prompt:
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={5}
            style={{ 
              width: '100%', 
              padding: '8px', 
              borderRadius: '4px',
              border: '1px solid #ccc',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
            disabled={loading}
          />
        </div>
        
        <button 
          type="submit" 
          style={{
            backgroundColor: loading ? '#ccc' : '#1976d2',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>
      </form>
      
      {loading && (
        <div style={{ textAlign: 'center', margin: '20px 0' }}>
          <p>Generating response, please wait...</p>
        </div>
      )}
      
      {response && (
        <div style={{ marginTop: '30px' }}>
          <h2>Response:</h2>
          <div style={{
            backgroundColor: '#f5f5f5',
            padding: '15px',
            borderRadius: '4px',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            overflowX: 'auto'
          }}>
            {response}
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMTester;
