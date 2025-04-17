import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card,
  CardContent,
  CardActions,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Tab,
  Tabs,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { getTools, executeTool } from '../../services/api';
import { useLocation } from 'react-router-dom';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tool-tabpanel-${index}`}
      aria-labelledby={`tool-tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && (
        <Box sx={{ p: 3, height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const ToolsPage = ({ addNotification }) => {
  const location = useLocation();
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTool, setSelectedTool] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [parameters, setParameters] = useState({});
  const [executing, setExecuting] = useState(false);
  const [results, setResults] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  
  // Parse the query parameter for a specific tool
  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const toolName = query.get('tool');
    
    if (toolName) {
      // If a tool is specified in the URL, load it
      const found = tools.find(tool => tool.name === toolName);
      if (found) {
        setSelectedTool(found);
        setDialogOpen(true);
      }
    }
  }, [location, tools]);
  
  // Fetch available tools
  useEffect(() => {
    const fetchTools = async () => {
      try {
        setLoading(true);
        const response = await getTools();
        if (response.status === 'success') {
          setTools(response.tools);
        } else {
          addNotification({
            type: 'error',
            message: response.message || 'Failed to get tools',
          });
        }
      } catch (error) {
        addNotification({
          type: 'error',
          message: `Error fetching tools: ${error.message}`,
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchTools();
  }, [addNotification]);
  
  const handleToolSelect = (tool) => {
    setSelectedTool(tool);
    setParameters({});
    setDialogOpen(true);
  };
  
  const handleDialogClose = () => {
    setDialogOpen(false);
    setSelectedTool(null);
    setParameters({});
  };
  
  const handleParameterChange = (name, value) => {
    setParameters(prev => ({
      ...prev,
      [name]: value,
    }));
  };
  
  const handleToolExecution = async () => {
    if (!selectedTool) return;
    
    try {
      setExecuting(true);
      
      const result = await executeTool(selectedTool.name, parameters);
      
      // Add to results
      setResults(prev => [...prev, {
        tool: selectedTool.name,
        parameters: { ...parameters },
        result,
        timestamp: new Date(),
      }]);
      
      // Show notification
      if (result.status === 'success') {
        addNotification({
          type: 'success',
          message: `Tool ${selectedTool.name} executed successfully`,
        });
      } else {
        addNotification({
          type: 'error',
          message: `Tool execution failed: ${result.error || 'Unknown error'}`,
        });
      }
      
      // Close dialog
      setDialogOpen(false);
      setSelectedTool(null);
      setParameters({});
      
      // Switch to results tab
      setTabValue(1);
      
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error executing tool: ${error.message}`,
      });
    } finally {
      setExecuting(false);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="tool tabs">
          <Tab label="Available Tools" />
          <Tab label="Results" />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0} sx={{ flexGrow: 1, overflow: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          Available Tools
        </Typography>
        
        <Typography variant="body1" paragraph>
          Select a tool to execute specific operations.
        </Typography>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : tools.length === 0 ? (
          <Typography>No tools available</Typography>
        ) : (
          <Grid container spacing={3}>
            {tools.map((tool) => (
              <Grid item xs={12} sm={6} md={4} key={tool.name}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {tool.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {tool.description}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      color="primary"
                      onClick={() => handleToolSelect(tool)}
                    >
                      Use Tool
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={1} sx={{ flexGrow: 1, overflow: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          Tool Execution Results
        </Typography>
        
        {results.length === 0 ? (
          <Typography color="text.secondary">
            No results yet. Execute a tool to see results here.
          </Typography>
        ) : (
          <Box>
            {results.map((result, index) => (
              <Paper sx={{ p: 2, mb: 2 }} key={index}>
                <Box sx={{ mb: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    Tool: {result.tool}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {result.timestamp.toLocaleString()}
                  </Typography>
                </Box>
                
                <Divider sx={{ my: 1 }} />
                
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Parameters</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography component="pre" sx={{ 
                      whiteSpace: 'pre-wrap',
                      fontSize: '0.875rem',
                      bgcolor: 'background.paper',
                      p: 1,
                      borderRadius: 1,
                    }}>
                      {JSON.stringify(result.parameters, null, 2)}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
                
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography>Result</Typography>
                      <Chip 
                        label={result.result.status} 
                        color={result.result.status === 'success' ? 'success' : result.result.status === 'error' ? 'error' : 'default'} 
                        size="small" 
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {result.result.error && (
                      <Typography color="error" sx={{ mb: 1 }}>
                        Error: {result.result.error}
                      </Typography>
                    )}
                    <Typography component="pre" sx={{ 
                      whiteSpace: 'pre-wrap',
                      fontSize: '0.875rem',
                      bgcolor: 'background.paper',
                      p: 1,
                      borderRadius: 1,
                      maxHeight: 400,
                      overflow: 'auto',
                    }}>
                      {JSON.stringify(result.result, null, 2)}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              </Paper>
            ))}
          </Box>
        )}
      </TabPanel>
      
      {/* Tool Execution Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTool?.name || 'Tool Execution'}
        </DialogTitle>
        
        <DialogContent dividers>
          {selectedTool && (
            <Box>
              <Typography paragraph>
                {selectedTool.description}
              </Typography>
              
              <Typography variant="subtitle1" gutterBottom>
                Parameters
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <TextField
                  label="Parameters (JSON)"
                  multiline
                  rows={8}
                  fullWidth
                  variant="outlined"
                  placeholder='{"key": "value"}'
                  value={JSON.stringify(parameters, null, 2)}
                  onChange={(e) => {
                    try {
                      const parsed = JSON.parse(e.target.value);
                      setParameters(parsed);
                    } catch (error) {
                      // Ignore JSON parse errors while typing
                    }
                  }}
                  disabled={executing}
                />
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleDialogClose} disabled={executing}>
            Cancel
          </Button>
          <Button 
            onClick={handleToolExecution} 
            variant="contained" 
            color="primary"
            disabled={executing}
            startIcon={executing && <CircularProgress size={20} color="inherit" />}
          >
            {executing ? 'Executing...' : 'Execute Tool'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ToolsPage;
