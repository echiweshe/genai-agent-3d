import React, { useState } from 'react';
import { 
  Button, 
  Box, 
  Typography, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions,
  TextField,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert
} from '@mui/material';
import { apiUrl } from '../../services/api';

/**
 * Debug helper component for Blender scripts integration
 */
const BlenderDebugHelper = () => {
  const [open, setOpen] = useState(false);
  const [debugLogs, setDebugLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [customPath, setCustomPath] = useState('');
  
  const handleOpen = () => {
    setOpen(true);
    // Clear previous logs
    setDebugLogs([]);
  };
  
  const handleClose = () => {
    setOpen(false);
  };
  
  const addLog = (message, type = 'info') => {
    setDebugLogs(prev => [
      ...prev, 
      { 
        message: typeof message === 'string' ? message : JSON.stringify(message, null, 2),
        type,
        timestamp: new Date().toISOString()
      }
    ]);
  };
  
  const checkDirectoryStructure = async () => {
    try {
      setLoading(true);
      addLog('Checking directory structure...');
      
      // Make a direct fetch to a debug endpoint
      const response = await fetch(`${apiUrl}/debug/paths`);
      
      if (!response.ok) {
        addLog(`Failed to check paths: HTTP ${response.status}`, 'error');
        try {
          const errorData = await response.json();
          addLog(`Error: ${errorData.detail}`, 'error');
        } catch (e) {
          addLog(`Failed to parse error response`, 'error');
        }
        return;
      }
      
      const data = await response.json();
      addLog('Directory structure check completed');
      addLog('Results:', 'info');
      addLog(data);
      
      if (data.missing_directories && data.missing_directories.length > 0) {
        addLog(`Missing directories detected: ${data.missing_directories.join(', ')}`, 'warning');
      } else {
        addLog('All required directories exist', 'success');
      }
      
      if (data.scripts && Object.keys(data.scripts).length > 0) {
        addLog('Found scripts:', 'success');
        Object.entries(data.scripts).forEach(([folder, scripts]) => {
          addLog(`${folder}: ${scripts.length} scripts`);
        });
      } else {
        addLog('No scripts found in any directory', 'warning');
      }
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };
  
  const checkAPIEndpoints = async () => {
    try {
      setLoading(true);
      addLog('Testing API endpoints...');
      
      // Test several endpoints
      const endpoints = [
        '/blender/list-scripts/models',
        '/blender/list-scripts/scenes',
        '/status'
      ];
      
      for (const endpoint of endpoints) {
        addLog(`Testing endpoint: ${endpoint}`);
        
        try {
          const response = await fetch(`${apiUrl}${endpoint}`);
          addLog(`Response status: ${response.status} ${response.statusText}`);
          
          // Try to get the response as text
          const text = await response.text();
          addLog(`Response length: ${text.length} characters`);
          
          try {
            // Try to parse as JSON if possible
            const json = JSON.parse(text);
            addLog(`Response data: ${JSON.stringify(json, null, 2)}`);
          } catch (e) {
            // If not JSON, just show the beginning of the text
            addLog(`Response preview: ${text.substring(0, 100)}...`);
          }
        } catch (endpointError) {
          addLog(`Failed to access endpoint ${endpoint}: ${endpointError.message}`, 'error');
        }
      }
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };
  
  const checkCustomPath = async () => {
    if (!customPath) {
      addLog('Please enter a path to check', 'warning');
      return;
    }
    
    try {
      setLoading(true);
      addLog(`Checking custom path: ${customPath}`);
      
      const response = await fetch(`${apiUrl}/debug/check-path?path=${encodeURIComponent(customPath)}`);
      
      if (!response.ok) {
        addLog(`Failed to check path: HTTP ${response.status}`, 'error');
        try {
          const errorData = await response.json();
          addLog(`Error: ${errorData.detail}`, 'error');
        } catch (e) {
          addLog(`Failed to parse error response`, 'error');
        }
        return;
      }
      
      const data = await response.json();
      addLog('Path check results:');
      addLog(data);
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };
  
  const runDebugScript = async () => {
    try {
      setLoading(true);
      addLog('Attempting to run debug_paths.py script...');
      
      // This will depend on your backend having an endpoint to run the script
      const response = await fetch(`${apiUrl}/debug/run-script`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          script_name: 'debug_paths.py'
        }),
      });
      
      if (!response.ok) {
        addLog(`Failed to run script: HTTP ${response.status}`, 'error');
        try {
          const errorData = await response.json();
          addLog(`Error: ${errorData.detail}`, 'error');
        } catch (e) {
          addLog(`Failed to parse error response`, 'error');
        }
        return;
      }
      
      const data = await response.json();
      addLog('Script execution completed');
      addLog('Output:', 'info');
      addLog(data.output || 'No output returned');
    } catch (error) {
      addLog(`Error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <>
      <Button 
        variant="outlined" 
        color="secondary" 
        onClick={handleOpen}
        sx={{ ml: 1 }}
      >
        Debug Blender Integration
      </Button>
      
      <Dialog
        open={open}
        onClose={handleClose}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Blender Scripts Debug Helper</DialogTitle>
        
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            This tool helps diagnose issues with the Blender script execution feature.
            Run the debug_paths.py script to create required directories and example scripts.
          </Alert>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Diagnostics Tools
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Button 
                variant="contained" 
                onClick={checkDirectoryStructure}
                disabled={loading}
              >
                Check Directory Structure
              </Button>
              
              <Button 
                variant="contained" 
                onClick={checkAPIEndpoints}
                disabled={loading}
              >
                Test API Endpoints
              </Button>
              
              <Button 
                variant="contained" 
                onClick={runDebugScript}
                disabled={loading}
                color="warning"
              >
                Run debug_paths.py
              </Button>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <TextField
                label="Custom Path to Check"
                value={customPath}
                onChange={(e) => setCustomPath(e.target.value)}
                placeholder="models/example_cube.py"
                fullWidth
                size="small"
              />
              
              <Button 
                variant="contained" 
                onClick={checkCustomPath}
                disabled={loading || !customPath}
              >
                Check Path
              </Button>
            </Box>
          </Box>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="subtitle1" gutterBottom>
            Debug Logs
          </Typography>
          
          <Paper 
            elevation={3}
            sx={{ 
              p: 2, 
              height: '300px', 
              overflow: 'auto',
              backgroundColor: '#f5f5f5'
            }}
          >
            {debugLogs.length === 0 ? (
              <Typography color="textSecondary">
                No logs yet. Run a diagnostic tool to see output here.
              </Typography>
            ) : (
              <List dense>
                {debugLogs.map((log, index) => (
                  <ListItem 
                    key={index}
                    sx={{ 
                      py: 0.5,
                      backgroundColor: 
                        log.type === 'error' ? 'rgba(255, 0, 0, 0.1)' :
                        log.type === 'warning' ? 'rgba(255, 255, 0, 0.1)' :
                        log.type === 'success' ? 'rgba(0, 255, 0, 0.1)' :
                        'transparent',
                      borderLeft: 
                        log.type === 'error' ? '3px solid red' :
                        log.type === 'warning' ? '3px solid orange' :
                        log.type === 'success' ? '3px solid green' :
                        '3px solid blue',
                      mb: 0.5
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box component="div" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                          {log.message}
                        </Box>
                      }
                      secondary={log.timestamp}
                      secondaryTypographyProps={{
                        sx: { fontSize: '0.7rem' }
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default BlenderDebugHelper;
