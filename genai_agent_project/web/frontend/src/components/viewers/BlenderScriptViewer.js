import React, { useState, useEffect, useRef } from 'react';
import { Button, Card, CardContent, Typography, Box, CircularProgress, Snackbar, Alert,
         TextField, FormControlLabel, Switch, Grid, Paper, Divider, List, ListItem, ListItemText, Chip } from '@mui/material';
import { PlayArrow, Code, Refresh, FolderOpen } from '@mui/icons-material';
import { apiUrl } from '../../services/api';
import blenderScriptService from '../../services/blenderScriptService';

/**
 * BlenderScriptViewer - Component for viewing and executing Blender scripts
 * 
 * This component allows users to:
 * 1. View a list of available Blender scripts
 * 2. View script details and content
 * 3. Execute scripts and see real-time output
 */
const BlenderScriptViewer = ({ scriptPath, onScriptSelected, folder: initialFolder }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scriptList, setScriptList] = useState([]);
  const [selectedScript, setSelectedScript] = useState(null);
  const [scriptContent, setScriptContent] = useState('');
  const [executionStatus, setExecutionStatus] = useState(null);
  const [executionOutput, setExecutionOutput] = useState('');
  const [showUI, setShowUI] = useState(false);
  const [folder, setFolder] = useState(initialFolder || 'models'); // Default folder
  
  const outputRef = useRef(null);
  const ws = useRef(null);

  // Load script list on component mount or when folder changes
  useEffect(() => {
    loadScriptList();
  }, [folder]);

  // Update folder state when initialFolder prop changes
  useEffect(() => {
    if (initialFolder) {
      setFolder(initialFolder);
    }
  }, [initialFolder]);

  // If a script path is provided via props, select it
  useEffect(() => {
    if (scriptPath) {
      loadScriptContent(scriptPath);
    }
  }, [scriptPath]);

  // Auto-scroll the output to the bottom when it changes
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [executionOutput]);

  // Clean up WebSocket on unmount
  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
        ws.current = null;
      }
    };
  }, []);

  const loadScriptList = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log(`Attempting to load scripts from folder: ${folder}`);
      console.log(`API URL: ${apiUrl}/blender/list-scripts/${folder}`);
      
      // Use direct fetch for debugging purposes
      const response = await fetch(`${apiUrl}/blender/list-scripts/${folder}`);
      const responseText = await response.text();
      
      console.log(`Response status: ${response.status}`);
      console.log(`Response text:`, responseText);
      
      let data;
      try {
        data = JSON.parse(responseText);
        console.log("Parsed data:", data);
        setScriptList(data.scripts || []);
      } catch (parseErr) {
        console.error("Error parsing JSON:", parseErr);
        setError(`Invalid response format: ${responseText.substring(0, 100)}...`);
        return;
      }

      // If we got an empty array, set a more informative message
      if (data.scripts && data.scripts.length === 0) {
        console.log(`No scripts found in folder: ${folder}`);
      }
    } catch (err) {
      console.error('Error loading script list:', err);
      setError(`Failed to load script list: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadScriptContent = async (path) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log(`Attempting to load script content for: ${path}`);
      
      // Find the script in the list
      const script = scriptList.find(s => s.path === path);
      
      if (script) {
        console.log('Found script in list:', script);
        setSelectedScript(script);
        
        // Try to load from API's blender/script endpoint first
        const contentUrl = `${apiUrl}/blender/script/${encodeURIComponent(script.path)}`;
        console.log(`Trying to load script content from: ${contentUrl}`);
        
        try {
          const response = await fetch(contentUrl);
          console.log(`Content response status: ${response.status}`);
          
          if (response.ok) {
            const content = await response.text();
            console.log(`Received content length: ${content.length} characters`);
            setScriptContent(content);
            return;
          }
        } catch (contentErr) {
          console.warn(`Error loading from blender/script endpoint: ${contentErr.message}. Trying fallback...`);
        }
        
        // Fallback to results endpoint
        const fallbackUrl = `${apiUrl}/results/${encodeURIComponent(script.name)}`;
        console.log(`Trying fallback URL: ${fallbackUrl}`);
        
        const fallbackResponse = await fetch(fallbackUrl);
        console.log(`Fallback response status: ${fallbackResponse.status}`);
        
        if (fallbackResponse.ok) {
          const content = await fallbackResponse.text();
          console.log(`Received content length from fallback: ${content.length} characters`);
          setScriptContent(content);
        } else {
          try {
            const errorData = await fallbackResponse.json();
            throw new Error(errorData.detail || 'Failed to load script content');
          } catch (jsonErr) {
            throw new Error(`Failed to load script content (HTTP ${fallbackResponse.status})`);
          }
        }
      } else {
        console.error(`Script ${path} not found in the list of ${scriptList.length} scripts`);
        throw new Error(`Script ${path} not found in the list`);
      }
    } catch (err) {
      console.error('Error loading script content:', err);
      setError(`Failed to load script content: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const executeScript = async () => {
    if (!selectedScript) return;
    
    try {
      setLoading(true);
      setError(null);
      setExecutionStatus('queued');
      setExecutionOutput('Queuing script execution...\n');
      
      // Call the API to execute the script
      const data = await blenderScriptService.executeScript(selectedScript.path, showUI);
      
      setExecutionStatus(data.status);
      setExecutionOutput(prev => prev + `Script execution ${data.status}. ID: ${data.execution_id}\n`);
      
      // Open WebSocket connection to get real-time updates
      openWebSocketConnection(data.execution_id);
    } catch (err) {
      console.error('Error executing script:', err);
      setError(`Failed to execute script: ${err.message}`);
      setExecutionStatus('failed');
    } finally {
      setLoading(false);
    }
  };

  const openWebSocketConnection = (executionId) => {
    // Close existing connection if any
    if (ws.current) {
      ws.current.close();
    }
    
    // Create new WebSocket connection
    try {
      ws.current = blenderScriptService.createWebSocketConnection(executionId);
      
      ws.current.onopen = () => {
        console.log('WebSocket connection opened');
        setExecutionOutput(prev => prev + 'WebSocket connection established. Waiting for updates...\n');
      };
      
      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Handle different message types
        if (data.type === 'blender_script_status') {
          setExecutionStatus(data.data.status);
          setExecutionOutput(prev => prev + `Status update: ${data.data.message}\n`);
        } else if (data.type === 'blender_script_output') {
          setExecutionOutput(prev => prev + data.data.line);
        } else if (data.type === 'blender_script_full_output') {
          setExecutionOutput(data.data.output);
        } else if (data.type === 'blender_script_update') {
          setExecutionStatus(data.data.status);
          setExecutionOutput(prev => prev + `Update: ${data.data.message}\n`);
        }
      };
      
      ws.current.onclose = () => {
        console.log('WebSocket connection closed');
        setExecutionOutput(prev => prev + 'WebSocket connection closed.\n');
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setExecutionOutput(prev => prev + `WebSocket error: ${error}\n`);
        setError('WebSocket connection error');
      };
    } catch (err) {
      console.error('Failed to open WebSocket connection:', err);
      setError(`Failed to open WebSocket connection: ${err.message}`);
    }
  };

  const handleScriptClick = (script) => {
    if (onScriptSelected) {
      onScriptSelected(script.path);
    }
    loadScriptContent(script.path);
  };

  const handleFolderChange = (event) => {
    setFolder(event.target.value);
  };

  const handleRefresh = () => {
    loadScriptList();
  };

  return (
    <Grid container spacing={2}>
      {/* Left panel - Script List */}
      <Grid item xs={12} md={3}>
        <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">Blender Scripts</Typography>
            <Button 
              size="small" 
              startIcon={<Refresh />} 
              onClick={handleRefresh} 
              disabled={loading}
            >
              Refresh
            </Button>
          </Box>
          
          <Box mb={2}>
            <TextField
              fullWidth
              label="Folder"
              value={folder}
              onChange={handleFolderChange}
              size="small"
              helperText="e.g. models, scenes"
              InputProps={{
                endAdornment: (
                  <Button 
                    size="small" 
                    startIcon={<FolderOpen />} 
                    onClick={handleRefresh}
                    disabled={loading}
                  >
                    Load
                  </Button>
                ),
              }}
            />
          </Box>
          
          {loading && <CircularProgress size={24} />}
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Divider sx={{ mb: 2 }} />
          
          <List dense sx={{ maxHeight: 400, overflow: 'auto' }}>
            {scriptList.length === 0 ? (
              <ListItem>
                <ListItemText 
                  primary="No scripts found" 
                  secondary={
                    <>
                      <div>{`Folder: ${folder}`}</div>
                      <Button 
                        size="small" 
                        onClick={() => {
                          // Run our debug script
                          alert('To fix directory issues, make sure to run the debug_paths.py script first!');
                        }}
                      >
                        Debug Path Issues
                      </Button>
                    </>
                  } 
                />
              </ListItem>
            ) : (
              scriptList.map(script => (
                <ListItem 
                  key={script.path} 
                  button 
                  onClick={() => handleScriptClick(script)}
                  selected={selectedScript?.path === script.path}
                >
                  <ListItemText 
                    primary={script.name} 
                    secondary={
                      <>
                        {`Modified: ${new Date(script.modified * 1000).toLocaleString()}`}
                        <br />
                        {`Path: ${script.path}`}
                      </>
                    } 
                  />
                </ListItem>
              ))
            )}
          </List>
        </Paper>
      </Grid>
      
      {/* Middle panel - Script Content */}
      <Grid item xs={12} md={4}>
        <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            Script Content
          </Typography>
          
          {selectedScript ? (
            <>
              <Typography variant="subtitle1" gutterBottom>
                {selectedScript.name}
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={showUI}
                      onChange={() => setShowUI(!showUI)}
                    />
                  }
                  label="Show Blender UI"
                />
                
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<PlayArrow />}
                  onClick={executeScript}
                  disabled={loading || !selectedScript}
                  sx={{ ml: 2 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Execute'}
                </Button>
              </Box>
              
              <Box
                sx={{
                  backgroundColor: '#f5f5f5',
                  p: 2,
                  borderRadius: 1,
                  height: 400,
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {scriptContent}
              </Box>
            </>
          ) : (
            <Typography variant="body2" color="textSecondary">
              Select a script from the list to view its content
            </Typography>
          )}
        </Paper>
      </Grid>
      
      {/* Right panel - Execution Output */}
      <Grid item xs={12} md={5}>
        <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            Execution Output
            {executionStatus && (
              <Box component="span" ml={2}>
                <Chip 
                  label={executionStatus.toUpperCase()} 
                  color={
                    executionStatus === 'completed' ? 'success' :
                    executionStatus === 'failed' ? 'error' :
                    executionStatus === 'running' ? 'primary' : 'default'
                  }
                  size="small"
                />
              </Box>
            )}
          </Typography>
          
          <Box
            ref={outputRef}
            sx={{
              backgroundColor: '#000',
              color: '#fff',
              p: 2,
              borderRadius: 1,
              height: 450,
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              whiteSpace: 'pre-wrap',
            }}
          >
            {executionOutput || 'No execution output yet. Execute a script to see output here.'}
          </Box>
        </Paper>
      </Grid>
      
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Grid>
  );
};

export default BlenderScriptViewer;
