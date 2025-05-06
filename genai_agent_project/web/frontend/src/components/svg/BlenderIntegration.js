import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Typography, Alert, Tooltip, Box, CircularProgress } from '@mui/material';
import { Boxes, AlertTriangle, Check } from 'lucide-react';

/**
 * Component for Blender integration in the SVG to Video pipeline.
 * Provides functionality to open 3D models in Blender.
 */
const BlenderIntegration = ({ modelPath }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [blenderStatus, setBlenderStatus] = useState('unknown');
  const [blenderPath, setBlenderPath] = useState(null);

  // Check Blender availability on component mount
  useEffect(() => {
    checkBlenderAvailability();
  }, []);

  const checkBlenderAvailability = async () => {
    try {
      const response = await axios.get('/blender/health');
      if (response.data.status === 'available') {
        setBlenderStatus('available');
        setBlenderPath(response.data.blender_path);
      } else {
        setBlenderStatus('unavailable');
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Error checking Blender availability:', err);
      setBlenderStatus('error');
      setError('Failed to check Blender availability');
    }
  };

  const openInBlender = async () => {
    if (!modelPath) {
      setError('No model selected');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await axios.post('/blender/open-model', {
        model_path: modelPath,
        new_instance: true
      });
      setLoading(false);
    } catch (err) {
      console.error('Error opening model in Blender:', err);
      setLoading(false);
      setError(err.response?.data?.detail || 'Failed to open model in Blender');
    }
  };

  const debugBlenderIssues = async () => {
    try {
      const response = await axios.get('/blender/debug-path-issues');
      console.log('Blender debug info:', response.data);
      alert('Blender debug information has been logged to the console');
    } catch (err) {
      console.error('Error debugging Blender issues:', err);
      setError('Failed to debug Blender issues');
    }
  };

  // Render different content based on Blender status
  const renderContent = () => {
    if (blenderStatus === 'unknown') {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CircularProgress size={20} sx={{ mr: 1 }} />
          <Typography>Checking Blender availability...</Typography>
        </Box>
      );
    }

    if (blenderStatus === 'unavailable') {
      return (
        <>
          <Alert 
            severity="warning" 
            icon={<AlertTriangle />}
            sx={{ mb: 2 }}
          >
            Blender is not available. Please make sure Blender is installed and the path is set in the configuration.
          </Alert>
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={debugBlenderIssues}
            startIcon={<AlertTriangle />}
          >
            Debug Blender Issues
          </Button>
        </>
      );
    }

    return (
      <>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            <Check size={16} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
            Blender is available at: {blenderPath}
          </Typography>
        </Box>
        
        <Tooltip title={!modelPath ? 'No model selected' : 'Open this model in Blender'}>
          <span>
            <Button
              variant="contained"
              color="primary"
              onClick={openInBlender}
              disabled={!modelPath || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <Boxes />}
            >
              {loading ? 'Opening...' : 'View in Blender'}
            </Button>
          </span>
        </Tooltip>
      </>
    );
  };

  return (
    <Box sx={{ mt: 2, mb: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>Blender Integration</Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {renderContent()}
    </Box>
  );
};

export default BlenderIntegration;
