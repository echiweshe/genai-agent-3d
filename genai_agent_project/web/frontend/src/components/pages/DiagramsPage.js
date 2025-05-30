import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  TextField, 
  Button, 
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import GetAppIcon from '@mui/icons-material/GetApp';
import { executeTool, getDiagrams, deleteDiagram } from '../../services/api';
import DiagramViewer from '../viewers/DiagramViewer';

const DiagramsPage = ({ addNotification }) => {
  const [description, setDescription] = useState('');
  const [diagramType, setDiagramType] = useState('flowchart');
  const [format, setFormat] = useState('svg'); // Default to SVG for our implementation
  const [diagramName, setDiagramName] = useState('');
  const [loading, setLoading] = useState(false);
  const [diagrams, setDiagrams] = useState([]);
  const [loadingDiagrams, setLoadingDiagrams] = useState(true);
  const [viewDiagram, setViewDiagram] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [llmProvider, setLlmProvider] = useState('claude-direct');
  const [providers, setProviders] = useState([]);
  const [loadingProviders, setLoadingProviders] = useState(false);
  
  const diagramTypes = [
    { value: 'flowchart', label: 'Flowchart' },
    { value: 'network', label: 'Network Diagram' },
    { value: 'sequence', label: 'Sequence Diagram' },
    { value: 'class', label: 'UML Class Diagram' },
    { value: 'er', label: 'Entity Relationship Diagram' },
    { value: 'mindmap', label: 'Mind Map' },
    { value: 'general', label: 'General Diagram' }
  ];
  
  const formatOptions = [
    { value: 'svg', label: 'SVG' },
    { value: 'mermaid', label: 'Mermaid' },
    { value: 'dot', label: 'DOT (GraphViz)' }
  ];

  // Load existing diagrams and providers when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch diagrams
        setLoadingDiagrams(true);
        const response = await getDiagrams();
        if (response.status === 'success' && Array.isArray(response.diagrams)) {
          setDiagrams(response.diagrams);
        }
        
        // Fetch LLM providers
        setLoadingProviders(true);
        try {
          const providersResponse = await fetch('/svg-generator/providers');
          if (providersResponse.ok) {
            const data = await providersResponse.json();
            if (data.status === 'success' && Array.isArray(data.providers)) {
              setProviders(data.providers);
              
              // Set default provider to claude-direct if available
              const claudeDirectProvider = data.providers.find(p => p.id === 'claude-direct');
              if (claudeDirectProvider) {
                setLlmProvider('claude-direct');
              } else if (data.providers.length > 0) {
                setLlmProvider(data.providers[0].id);
              }
            }
          }
        } catch (error) {
          console.error('Error fetching providers:', error);
          // Don't show notification for this error as it's not critical
        } finally {
          setLoadingProviders(false);
        }
      } catch (error) {
        console.error('Error fetching diagrams:', error);
        addNotification({
          type: 'error',
          message: `Error loading diagrams: ${error.message}`,
        });
      } finally {
        setLoadingDiagrams(false);
      }
    };
    
    fetchData();
  }, [addNotification]);
  
  const handleGenerateDiagram = async () => {
    if (!description.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please provide a diagram description',
      });
      return;
    }
    
    try {
      setLoading(true);
      
      let result;
      
      if (format === 'svg') {
        // For SVG format, use our integrated SVG Generator
        try {
          const response = await fetch('/svg-generator/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              description,
              diagram_type: diagramType,
              provider: llmProvider,
              name: diagramName || undefined
            })
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate SVG');
          }
          
          result = await response.json();
        } catch (error) {
          throw new Error(`SVG generation error: ${error.message}`);
        }
      } else {
        // For other formats, use the existing diagram generator tool
        const parameters = {
          description,
          diagram_type: diagramType,
          format,
          name: diagramName || undefined,
        };
        
        result = await executeTool('diagram_generator', parameters);
      }
      
      if (result.status === 'success') {
        // Add the diagram to the list
        const newDiagram = {
          id: result.diagram_id || Date.now().toString(),
          name: result.name || diagramName || `Diagram-${Date.now().toString().slice(-6)}`,
          description,
          type: diagramType,
          format,
          path: result.file_path,
          code: result.code,
          date: new Date(),
          result,
        };
        
        setDiagrams(prev => [newDiagram, ...prev]);
        
        // Show success notification
        addNotification({
          type: 'success',
          message: result.message || 'Diagram generated successfully',
        });
        
        // Clear form
        setDescription('');
        setDiagramName('');
      } else {
        // Show error notification
        addNotification({
          type: 'error',
          message: result.error || 'Failed to generate diagram',
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error generating diagram: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleViewDiagram = (diagram) => {
    setViewDiagram(diagram);
    setViewDialogOpen(true);
  };
  
  const handleCloseViewDialog = () => {
    setViewDialogOpen(false);
    setViewDiagram(null);
  };
  
  const handleDeleteDiagram = async (id) => {
    try {
      // Delete the diagram via API
      await deleteDiagram(id);
      
      // Filter out the deleted diagram
      setDiagrams(prev => prev.filter(diagram => diagram.id !== id));
      
      addNotification({
        type: 'success',
        message: 'Diagram deleted successfully',
      });
    } catch (error) {
      console.error('Error deleting diagram:', error);
      addNotification({
        type: 'error',
        message: `Error deleting diagram: ${error.message}`,
      });
    }
  };
  
  // Handle diagram export
  const handleExportDiagram = (diagram) => {
    if (!diagram || !diagram.code) {
      addNotification({
        type: 'error',
        message: 'No diagram code available to export',
      });
      return;
    }
    
    // Create a blob from the diagram code
    const blob = new Blob([diagram.code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary link to download the file
    const link = document.createElement('a');
    link.href = url;
    
    // Determine file extension based on format
    let extension = '';
    if (diagram.format === 'mermaid') {
      extension = '.mmd';
    } else if (diagram.format === 'svg') {
      extension = '.svg';
    } else if (diagram.format === 'dot') {
      extension = '.dot';
    } else {
      extension = '.txt';
    }
    
    link.download = `${diagram.name || 'diagram'}${extension}`;
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    addNotification({
      type: 'success',
      message: 'Diagram exported successfully',
    });
  };
  
  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        Diagram Generator
      </Typography>
      
      <Typography variant="body1" paragraph>
        Generate diagrams from text descriptions using AI.
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              label="Diagram Description"
              multiline
              rows={3}
              fullWidth
              variant="outlined"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the diagram you want to create..."
              disabled={loading}
            />
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Diagram Type</InputLabel>
              <Select
                value={diagramType}
                onChange={(e) => setDiagramType(e.target.value)}
                label="Diagram Type"
                disabled={loading}
              >
                {diagramTypes.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Format</InputLabel>
              <Select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                label="Format"
                disabled={loading}
              >
                {formatOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {format === 'svg' && (
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth variant="outlined">
                <InputLabel>LLM Provider</InputLabel>
                <Select
                  value={llmProvider}
                  onChange={(e) => setLlmProvider(e.target.value)}
                  label="LLM Provider"
                  disabled={loading || loadingProviders}
                >
                  {loadingProviders ? (
                    <MenuItem value="">
                      <em>Loading providers...</em>
                    </MenuItem>
                  ) : providers.length === 0 ? (
                    <MenuItem value="">
                      <em>No providers available</em>
                    </MenuItem>
                  ) : (
                    providers.map(provider => (
                      <MenuItem key={provider.id} value={provider.id}>
                        {provider.name || provider.id}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Grid>
          )}
          
          <Grid item xs={12} sm={format === 'svg' ? 3 : 6}>
            <TextField
              label="Diagram Name (optional)"
              fullWidth
              variant="outlined"
              value={diagramName}
              onChange={(e) => setDiagramName(e.target.value)}
              placeholder="Leave blank for auto-generated name"
              disabled={loading}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleGenerateDiagram}
                disabled={loading || !description.trim()}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {loading ? 'Generating...' : 'Generate Diagram'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      <Typography variant="h5" gutterBottom>
        Generated Diagrams
      </Typography>
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {loadingDiagrams ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : diagrams.length === 0 ? (
          <Typography color="text.secondary">
            No diagrams generated yet. Use the form above to create your first diagram.
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {diagrams.map((diagram) => (
              <Grid item xs={12} sm={6} md={4} key={diagram.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" noWrap>
                      {diagram.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {diagram.date instanceof Date 
                        ? diagram.date.toLocaleString() 
                        : new Date(diagram.date).toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {diagram.description}
                    </Typography>
                    <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Type: {diagram.type}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Format: {diagram.format}
                      </Typography>
                    </Box>
                  </CardContent>
                  <CardActions>
                    <IconButton onClick={() => handleViewDiagram(diagram)} title="View Diagram">
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton onClick={() => handleExportDiagram(diagram)} title="Export Diagram">
                      <GetAppIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteDiagram(diagram.id)} title="Delete Diagram">
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
      
      {/* View Diagram Dialog */}
      <Dialog 
        open={viewDialogOpen} 
        onClose={handleCloseViewDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {viewDiagram?.name || 'Diagram'}
        </DialogTitle>
        
        <DialogContent sx={{ minHeight: '60vh', p: 0 }}>
          {viewDiagram && (
            <DiagramViewer 
              diagramCode={viewDiagram.code} 
              diagramType={viewDiagram.format} 
              width="100%" 
              height="100%" 
            />
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => handleExportDiagram(viewDiagram)}>
            Export
          </Button>
          <Button onClick={handleCloseViewDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DiagramsPage;
