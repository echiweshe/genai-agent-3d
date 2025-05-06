import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress, 
  Alert,
  Tooltip,
  Snackbar,
  Divider,
  Grid
} from '@mui/material';
import { Boxes, Eye, AlertCircle, CheckCircle, FileSymlink } from 'lucide-react';

/**
 * SVG to 3D Viewer Component
 * 
 * This component provides an interface for users to:
 * 1. Select an SVG diagram they've generated
 * 2. Convert it to a 3D model
 * 3. View the resulting 3D model in Blender
 */
const SVGTo3DViewer = ({ selectedSvg, onConversionComplete }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [modelPath, setModelPath] = useState(null);
  const [blenderAvailable, setBlenderAvailable] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  // Check if Blender is available when the component mounts
  useEffect(() => {
    checkBlenderAvailability();
  }, []);

  // Check if Blender is available
  const checkBlenderAvailability = async () => {
    try {
      const response = await axios.get('/blender/health');
      setBlenderAvailable(response.data?.status === 'available');
    } catch (error) {
      console.error('Error checking Blender availability:', error);
      setBlenderAvailable(false);
    }
  };

  // Convert the selected SVG to a 3D model
  const convertToModel = async () => {
    if (!selectedSvg) {
      setNotification({
        open: true,
        message: 'Please select an SVG diagram first',
        severity: 'warning'
      });
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setModelPath(null);

    try {
      // Make API call to convert SVG to 3D
      const response = await axios.post('/svg-generator/convert-to-3d', {
        svg_path: selectedSvg.file_path,
        name: selectedSvg.name
      });

      if (response.data.status === 'success') {
        setSuccess(true);
        setModelPath(response.data.model_path);
        setNotification({
          open: true,
          message: '3D model created successfully!',
          severity: 'success'
        });
        
        // Callback for parent components
        if (onConversionComplete) {
          onConversionComplete(response.data);
        }
      } else {
        throw new Error('Conversion failed');
      }
    } catch (error) {
      console.error('Error converting SVG to 3D:', error);
      setError(error.response?.data?.detail || 'Failed to convert SVG to 3D model');
      setNotification({
        open: true,
        message: 'SVG to 3D conversion failed',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Open the 3D model in Blender
  const openInBlender = async () => {
    if (!modelPath) {
      setNotification({
        open: true,
        message: 'No 3D model available to view',
        severity: 'warning'
      });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/blender/open-model', {
        model_path: modelPath,
        new_instance: true
      });
      
      setNotification({
        open: true,
        message: 'Opening model in Blender...',
        severity: 'info'
      });
    } catch (error) {
      console.error('Error opening model in Blender:', error);
      setNotification({
        open: true,
        message: 'Failed to open model in Blender',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Download the 3D model
  const downloadModel = () => {
    if (!modelPath) {
      setNotification({
        open: true,
        message: 'No 3D model available to download',
        severity: 'warning'
      });
      return;
    }

    // Create URL for download
    const downloadUrl = `/api/download?path=${encodeURIComponent(modelPath)}`;
    window.open(downloadUrl, '_blank');
  };

  // Close notification
  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3, position: 'relative' }}>
      <Typography variant="h6" gutterBottom>
        SVG to 3D Conversion
      </Typography>
      
      <Divider sx={{ mb: 2 }} />

      {/* Selected SVG info */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Selected Diagram:
        </Typography>
        {selectedSvg ? (
          <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1, bgcolor: '#f5f5f5' }}>
            <Typography>
              <strong>{selectedSvg.name}</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedSvg.file_path}
            </Typography>
          </Box>
        ) : (
          <Alert severity="info" sx={{ mb: 2 }}>
            No SVG diagram selected. Please generate or select an SVG diagram first.
          </Alert>
        )}
      </Box>

      {/* Conversion button */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item>
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <Boxes />}
            onClick={convertToModel}
            disabled={loading || !selectedSvg}
            sx={{ minWidth: '180px' }}
          >
            {loading ? 'Converting...' : 'Convert to 3D Model'}
          </Button>
        </Grid>

        {/* View in Blender button */}
        {modelPath && (
          <Grid item>
            <Tooltip title={blenderAvailable ? 'Open in Blender' : 'Blender not available'}>
              <span>
                <Button
                  variant="outlined"
                  color="secondary"
                  startIcon={<Eye />}
                  onClick={openInBlender}
                  disabled={!blenderAvailable || loading}
                  sx={{ minWidth: '150px' }}
                >
                  View in Blender
                </Button>
              </span>
            </Tooltip>
          </Grid>
        )}
        
        {/* Download model button */}
        {modelPath && (
          <Grid item>
            <Button
              variant="outlined"
              startIcon={<FileSymlink />}
              onClick={downloadModel}
              disabled={loading}
            >
              Download Model
            </Button>
          </Grid>
        )}
      </Grid>

      {/* Error and success messages */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} icon={<AlertCircle />}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircle />}>
          3D model created successfully: {modelPath}
        </Alert>
      )}

      {/* Blender availability warning */}
      {!blenderAvailable && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Blender is not available. You won't be able to view models directly in Blender.
          To enable this feature, make sure Blender is installed and configured in the system.
        </Alert>
      )}

      {/* Notification snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default SVGTo3DViewer;
