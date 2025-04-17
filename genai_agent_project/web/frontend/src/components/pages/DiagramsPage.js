import React, { useState } from 'react';
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
  Divider,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { executeTool } from '../../services/api';

const DiagramsPage = ({ addNotification }) => {
  const [description, setDescription] = useState('');
  const [diagramType, setDiagramType] = useState('flowchart');
  const [format, setFormat] = useState('mermaid');
  const [diagramName, setDiagramName] = useState('');
  const [loading, setLoading] = useState(false);
  const [diagrams, setDiagrams] = useState([]);
  const [viewDiagram, setViewDiagram] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  
  const diagramTypes = [
    { value: 'flowchart', label: 'Flowchart' },
    { value: 'erd', label: 'Entity Relationship Diagram' },
    { value: 'uml', label: 'UML Class Diagram' },
    { value: 'scene_layout', label: 'Scene Layout' },
    { value: 'hierarchy', label: 'Object Hierarchy' }
  ];
  
  const formatOptions = [
    { value: 'mermaid', label: 'Mermaid' },
    { value: 'svg', label: 'SVG' },
    { value: 'dot', label: 'DOT (GraphViz)' }
  ];
  
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
      
      // Prepare parameters for diagram generation
      const parameters = {
        description,
        diagram_type: diagramType,
        format,
        name: diagramName || undefined,
      };
      
      // Execute the diagram generator tool
      const result = await executeTool('diagram_generator', parameters);
      
      if (result.status === 'success') {
        // Add the diagram to the list
        setDiagrams(prev => [
          {
            id: result.file_path || Date.now().toString(),
            name: result.name,
            description,
            type: diagramType,
            format,
            path: result.file_path,
            code: result.code,
            date: new Date(),
            result,
          },
          ...prev
        ]);
        
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
  
  const handleDeleteDiagram = (id) => {
    setDiagrams(prev => prev.filter(diagram => diagram.id !== id));
    
    addNotification({
      type: 'info',
      message: 'Diagram removed from list',
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
          
          <Grid item xs={12} sm={4}>
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
          
          <Grid item xs={12} sm={4}>
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
          
          <Grid item xs={12} sm={4}>
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
        {diagrams.length === 0 ? (
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
                      {diagram.date.toLocaleString()}
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
                    <Button size="small" onClick={() => handleViewDiagram(diagram)}>
                      View
                    </Button>
                    <Button size="small" onClick={() => handleDeleteDiagram(diagram.id)}>
                      Delete
                    </Button>
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
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {viewDiagram?.name || 'Diagram'}
        </DialogTitle>
        
        <DialogContent dividers>
          {viewDiagram && (
            <Box>
              <Typography variant="body2" paragraph>
                {viewDiagram.description}
              </Typography>
              
              <Box sx={{ p: 2, bgcolor: 'background.paper', borderRadius: 1, maxHeight: '60vh', overflow: 'auto' }}>
                <Typography component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                  {viewDiagram.code}
                </Typography>
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  * Diagram rendering not implemented in this version
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseViewDialog}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DiagramsPage;
