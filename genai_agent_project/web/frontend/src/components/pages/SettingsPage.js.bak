import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  TextField, 
  Button, 
  Switch,
  FormControlLabel,
  CircularProgress,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Snackbar
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { getConfig, updateConfig } from '../../services/api';

const SettingsPage = ({ addNotification, darkMode, toggleDarkMode }) => {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [modelConfig, setModelConfig] = useState({
    provider: '',
    model: ''
  });
  const [blenderConfig, setBlenderConfig] = useState({
    path: ''
  });
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  // Fetch configuration on mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const response = await getConfig();
        if (response.status === 'success') {
          setConfig(response.config);
          
          // Extract relevant configs
          if (response.config.llm) {
            setModelConfig({
              provider: response.config.llm.provider || '',
              model: response.config.llm.model || ''
            });
          }
          
          if (response.config.blender) {
            setBlenderConfig({
              path: response.config.blender.path || ''
            });
          }
        } else {
          addNotification({
            type: 'error',
            message: response.message || 'Failed to load configuration',
          });
        }
      } catch (error) {
        addNotification({
          type: 'error',
          message: `Error loading configuration: ${error.message}`,
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchConfig();
  }, [addNotification]);
  
  const handleSaveModelConfig = async () => {
    try {
      setSaving(true);
      
      // Update provider
      await updateConfig('llm', 'provider', modelConfig.provider);
      
      // Update model
      await updateConfig('llm', 'model', modelConfig.model);
      
      addNotification({
        type: 'success',
        message: 'Model configuration saved successfully',
      });
      
      setSaveSuccess(true);
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error saving model configuration: ${error.message}`,
      });
    } finally {
      setSaving(false);
    }
  };
  
  const handleSaveBlenderConfig = async () => {
    try {
      setSaving(true);
      
      // Update blender path
      await updateConfig('blender', 'path', blenderConfig.path);
      
      // Also update the blender path in the tools configuration
      await updateConfig('tools', 'blender_script', {
        ...config?.tools?.blender_script,
        config: {
          ...config?.tools?.blender_script?.config,
          blender_path: blenderConfig.path
        }
      });
      
      addNotification({
        type: 'success',
        message: 'Blender configuration saved successfully',
      });
      
      setSaveSuccess(true);
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error saving Blender configuration: ${error.message}`,
      });
    } finally {
      setSaving(false);
    }
  };
  
  const handleBlenderPathChange = (e) => {
    setBlenderConfig({
      ...blenderConfig,
      path: e.target.value
    });
  };
  
  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      
      <Typography variant="body1" paragraph>
        Configure your GenAI Agent 3D installation.
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {/* UI Settings */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                UI Settings
              </Typography>
              
              <Divider sx={{ mb: 2 }} />
              
              <FormControlLabel
                control={
                  <Switch 
                    checked={darkMode} 
                    onChange={toggleDarkMode} 
                  />
                }
                label="Dark Mode"
              />
            </Paper>
          </Grid>
          
          {/* Model Settings */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Language Model Settings
              </Typography>
              
              <Divider sx={{ mb: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Provider"
                    fullWidth
                    variant="outlined"
                    value={modelConfig.provider}
                    onChange={(e) => setModelConfig({ ...modelConfig, provider: e.target.value })}
                    helperText="e.g., ollama, openai"
                  />
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Model"
                    fullWidth
                    variant="outlined"
                    value={modelConfig.model}
                    onChange={(e) => setModelConfig({ ...modelConfig, model: e.target.value })}
                    helperText="e.g., deepseek-coder:latest, llama3:latest"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleSaveModelConfig}
                      disabled={saving}
                      startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}
                    >
                      {saving ? 'Saving...' : 'Save Model Settings'}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
          
          {/* Blender Settings */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Blender Settings
              </Typography>
              
              <Divider sx={{ mb: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    label="Blender Path"
                    fullWidth
                    variant="outlined"
                    value={blenderConfig.path}
                    onChange={handleBlenderPathChange}
                    helperText="Path to Blender executable"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleSaveBlenderConfig}
                      disabled={saving}
                      startIcon={saving ? <CircularProgress size={20} color="inherit" /> : null}
                    >
                      {saving ? 'Saving...' : 'Save Blender Settings'}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
          
          {/* Advanced Configuration */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Advanced Configuration</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" paragraph>
                  The complete configuration is shown below. Edit the configuration file directly for advanced settings.
                </Typography>
                
                <Box sx={{ 
                  bgcolor: 'background.paper', 
                  p: 2, 
                  borderRadius: 1, 
                  maxHeight: '400px',
                  overflow: 'auto'
                }}>
                  <Typography component="pre" sx={{ 
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'monospace'
                  }}>
                    {JSON.stringify(config, null, 2)}
                  </Typography>
                </Box>
              </AccordionDetails>
            </Accordion>
          </Grid>
        </Grid>
      )}
      
      <Snackbar
        open={saveSuccess}
        autoHideDuration={3000}
        onClose={() => setSaveSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={() => setSaveSuccess(false)}>
          Settings saved successfully
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SettingsPage;
