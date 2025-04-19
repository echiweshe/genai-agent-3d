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
  CardMedia,
  CardActions,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { executeTool, getModels, deleteModel } from '../../services/api';
import ModelViewer from '../viewers/ModelViewer';

const ModelsPage = ({ addNotification }) => {
  const [description, setDescription] = useState('');
  const [modelType, setModelType] = useState('mesh');
  const [style, setStyle] = useState('realistic');
  const [modelName, setModelName] = useState('');
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState([]);
  const [loadingModels, setLoadingModels] = useState(true);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  
  // Load existing models when component mounts
  useEffect(() => {
    const fetchModels = async () => {
      try {
        setLoadingModels(true);
        const response = await getModels();
        if (response.status === 'success' && Array.isArray(response.models)) {
          setModels(response.models);
        }
      } catch (error) {
        console.error('Error fetching models:', error);
        addNotification({
          type: 'error',
          message: `Error loading models: ${error.message}`,
        });
      } finally {
        setLoadingModels(false);
      }
    };
    
    fetchModels();
  }, [addNotification]);
  
  const handleGenerateModel = async () => {
    if (!description.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please provide a model description',
      });
      return;
    }
    
    try {
      setLoading(true);
      
      // Prepare parameters for model generation
      const parameters = {
        description,
        model_type: modelType,
        style,
        name: modelName || undefined,
        execute: true,
        save_blend: true,
      };
      
      // Execute the model generator tool
      const result = await executeTool('model_generator', parameters);
      
      if (result.status === 'success' || result.status === 'partial_success') {
        // Add the model to the list
        const newModel = {
          id: result.model_id || Date.now().toString(),
          name: result.name || modelName || `Model-${Date.now().toString().slice(-6)}`,
          description,
          type: modelType,
          style,
          path: result.model_path,
          thumbnail: result.thumbnail_path,
          date: new Date(),
          result,
        };
        
        setModels(prev => [newModel, ...prev]);
        
        // Show success notification
        addNotification({
          type: 'success',
          message: result.message || 'Model generated successfully',
        });
        
        // Clear form
        setDescription('');
        setModelName('');
      } else {
        // Show error notification
        addNotification({
          type: 'error',
          message: result.error || 'Failed to generate model',
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error generating model: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async (id) => {
    try {
      // Delete the model via API
      await deleteModel(id);
      
      // Filter out the deleted model
      setModels(prev => prev.filter(model => model.id !== id));
      
      addNotification({
        type: 'success',
        message: 'Model deleted successfully',
      });
    } catch (error) {
      console.error('Error deleting model:', error);
      addNotification({
        type: 'error',
        message: `Error deleting model: ${error.message}`,
      });
    }
  };
  
  const handleView = (model) => {
    setSelectedModel(model);
    setViewDialogOpen(true);
  };
  
  const handleCloseViewDialog = () => {
    setViewDialogOpen(false);
    setSelectedModel(null);
  };
  
  const getModelFileType = (model) => {
    if (!model || !model.path) return 'gltf';
    
    const extension = model.path.split('.').pop()?.toLowerCase();
    return ['gltf', 'glb', 'obj', 'stl', 'ply'].includes(extension) ? extension : 'gltf';
  };
  
  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        3D Model Generator
      </Typography>
      
      <Typography variant="body1" paragraph>
        Generate 3D models from text descriptions using AI.
      </Typography>
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              label="Model Description"
              multiline
              rows={3}
              fullWidth
              variant="outlined"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the 3D model you want to create..."
              disabled={loading}
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Model Type</InputLabel>
              <Select
                value={modelType}
                onChange={(e) => setModelType(e.target.value)}
                label="Model Type"
                disabled={loading}
              >
                <MenuItem value="mesh">Mesh</MenuItem>
                <MenuItem value="curve">Curve</MenuItem>
                <MenuItem value="surface">Surface</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>Style</InputLabel>
              <Select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                label="Style"
                disabled={loading}
              >
                <MenuItem value="realistic">Realistic</MenuItem>
                <MenuItem value="stylized">Stylized</MenuItem>
                <MenuItem value="lowpoly">Low Poly</MenuItem>
                <MenuItem value="cartoon">Cartoon</MenuItem>
                <MenuItem value="abstract">Abstract</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              label="Model Name (optional)"
              fullWidth
              variant="outlined"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              placeholder="Leave blank for auto-generated name"
              disabled={loading}
            />
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleGenerateModel}
                disabled={loading || !description.trim()}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {loading ? 'Generating...' : 'Generate Model'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      <Typography variant="h5" gutterBottom>
        Generated Models
      </Typography>
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {loadingModels ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : models.length === 0 ? (
          <Typography color="text.secondary">
            No models generated yet. Use the form above to create your first model.
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {models.map((model) => (
              <Grid item xs={12} sm={6} md={4} key={model.id}>
                <Card>
                  <CardMedia
                    component="div"
                    sx={{
                      height: 180,
                      backgroundColor: 'grey.200',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                      overflow: 'hidden',
                    }}
                  >
                    {model.thumbnail ? (
                      <img 
                        src={model.thumbnail} 
                        alt={model.name} 
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                      />
                    ) : (
                      <Typography color="text.secondary">
                        [Model Preview]
                      </Typography>
                    )}
                  </CardMedia>
                  <CardContent>
                    <Typography variant="h6" noWrap>
                      {model.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {model.date instanceof Date 
                        ? model.date.toLocaleString() 
                        : new Date(model.date).toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {model.description}
                    </Typography>
                    <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Type: {model.type || modelType}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Style: {model.style || style}
                      </Typography>
                    </Box>
                  </CardContent>
                  <CardActions>
                    <IconButton onClick={() => handleView(model)} title="View Model">
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDelete(model.id)} title="Delete Model">
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
      
      {/* Model Viewer Dialog */}
      <Dialog 
        open={viewDialogOpen} 
        onClose={handleCloseViewDialog} 
        maxWidth="lg" 
        fullWidth
      >
        <DialogTitle>{selectedModel?.name}</DialogTitle>
        <DialogContent sx={{ height: '70vh', p: 0 }}>
          {selectedModel && (
            <ModelViewer 
              modelUrl={selectedModel.path} 
              modelType={getModelFileType(selectedModel)} 
              width="100%" 
              height="100%" 
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseViewDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModelsPage;
