import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  TextField, 
  Button, 
  CircularProgress,
  Divider,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Collapse
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { 
  executeTool, 
  getScenes, 
  createScene, 
  updateScene, 
  deleteScene, 
  getScene,
  getModels
} from '../../services/api';
import ModelViewer from '../viewers/ModelViewer';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`scene-tabpanel-${index}`}
      aria-labelledby={`scene-tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && (
        <Box sx={{ pt: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const ScenePage = ({ addNotification }) => {
  const [tabValue, setTabValue] = useState(0);
  const [description, setDescription] = useState('');
  const [sceneName, setSceneName] = useState('');
  const [nlDescription, setNlDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingScenes, setLoadingScenes] = useState(true);
  const [scenes, setScenes] = useState([]);
  const [currentScene, setCurrentScene] = useState(null);
  const [selectedSceneId, setSelectedSceneId] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModels, setSelectedModels] = useState([]);
  const [expandedModelsList, setExpandedModelsList] = useState(false);
  const [sceneObjects, setSceneObjects] = useState([]);
  const [showAddObjectDialog, setShowAddObjectDialog] = useState(false);
  const [newObject, setNewObject] = useState({
    type: 'cube',
    name: '',
    position: [0, 0, 0],
    rotation: [0, 0, 0],
    scale: [1, 1, 1],
    color: '#FF0000'
  });
  const [previewModel, setPreviewModel] = useState(null);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  
  // Load scenes and models when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoadingScenes(true);
        
        // Get scenes
        const scenesResponse = await getScenes();
        if (scenesResponse.status === 'success' && Array.isArray(scenesResponse.scenes)) {
          setScenes(scenesResponse.scenes);
        }
        
        // Get models for use in scene creation
        const modelsResponse = await getModels();
        if (modelsResponse.status === 'success' && Array.isArray(modelsResponse.models)) {
          setAvailableModels(modelsResponse.models);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        addNotification({
          type: 'error',
          message: `Error loading data: ${error.message}`,
        });
      } finally {
        setLoadingScenes(false);
      }
    };
    
    fetchData();
  }, [addNotification]);
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const toggleModelsList = () => {
    setExpandedModelsList(!expandedModelsList);
  };
  
  const handleModelSelect = (modelId) => {
    setSelectedModels(prev => {
      if (prev.includes(modelId)) {
        return prev.filter(id => id !== modelId);
      } else {
        return [...prev, modelId];
      }
    });
  };
  
  const handleCreateScene = async () => {
    if (!sceneName.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please provide a scene name',
      });
      return;
    }
    
    if (!description.trim() && !nlDescription.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please provide a scene description',
      });
      return;
    }
    
    try {
      setLoading(true);
      
      let result;
      
      if (nlDescription.trim()) {
        // Use natural language description to generate scene
        result = await executeTool('scene_generator', {
          description: nlDescription,
          name: sceneName,
          models: selectedModels.length > 0 ? selectedModels : undefined
        });
      } else {
        // Create a basic scene with the specified properties
        result = await createScene({
          name: sceneName,
          description,
          objects: [{
            type: 'cube',
            position: [0, 0, 0],
            scale: [1, 1, 1],
            rotation: [0, 0, 0],
            color: '#FF0000'
          }]
        });
      }
      
      if (result.status === 'success') {
        // Create a new scene object
        const newScene = {
          id: result.scene_id,
          name: sceneName,
          description: description || nlDescription,
          date: new Date(),
          result,
        };
        
        // Add to scenes list
        setScenes(prev => [newScene, ...prev]);
        
        // Set as current scene
        setCurrentScene(newScene);
        
        // Show success notification
        addNotification({
          type: 'success',
          message: result.message || 'Scene created successfully',
        });
        
        // Clear inputs
        setSceneName('');
        setDescription('');
        setNlDescription('');
        setSelectedModels([]);
        
        // Switch to editor tab
        setTabValue(1);
      } else {
        // Show error notification
        addNotification({
          type: 'error',
          message: result.error || 'Failed to create scene',
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error creating scene: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleSceneSelect = async (sceneId) => {
    if (!sceneId) {
      setCurrentScene(null);
      setSceneObjects([]);
      return;
    }
    
    try {
      // Get scene details
      const response = await getScene(sceneId);
      
      if (response.status === 'success') {
        setCurrentScene(response.scene);
        setSceneObjects(response.scene.objects || []);
        addNotification({
          type: 'info',
          message: 'Scene loaded',
        });
      } else {
        addNotification({
          type: 'error',
          message: response.error || 'Failed to load scene',
        });
      }
    } catch (error) {
      console.error('Error loading scene:', error);
      addNotification({
        type: 'error',
        message: `Error loading scene: ${error.message}`,
      });
    }
  };
  
  const handleShowAddObjectDialog = () => {
    setNewObject({
      type: 'cube',
      name: '',
      position: [0, 0, 0],
      rotation: [0, 0, 0],
      scale: [1, 1, 1],
      color: '#FF0000'
    });
    setShowAddObjectDialog(true);
  };
  
  const handleCloseAddObjectDialog = () => {
    setShowAddObjectDialog(false);
  };
  
  const handleAddObject = () => {
    // Validate the new object
    if (!newObject.name.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please provide an object name',
      });
      return;
    }
    
    // Add the new object to the scene
    setSceneObjects(prev => [...prev, { ...newObject, id: Date.now().toString() }]);
    
    // Close the dialog
    handleCloseAddObjectDialog();
    
    // Show notification
    addNotification({
      type: 'success',
      message: 'Object added to scene',
    });
  };
  
  const handleRemoveObject = (objectId) => {
    setSceneObjects(prev => prev.filter(obj => obj.id !== objectId));
    
    addNotification({
      type: 'info',
      message: 'Object removed from scene',
    });
  };
  
  const handleSaveScene = async () => {
    if (!currentScene) {
      addNotification({
        type: 'warning',
        message: 'No scene selected',
      });
      return;
    }
    
    try {
      // Update the scene with current objects
      const response = await updateScene(currentScene.id, {
        ...currentScene,
        objects: sceneObjects
      });
      
      if (response.status === 'success') {
        // Update the scenes list
        setScenes(prev => prev.map(scene => 
          scene.id === currentScene.id ? { ...scene, objects: sceneObjects } : scene
        ));
        
        addNotification({
          type: 'success',
          message: 'Scene saved successfully',
        });
      } else {
        addNotification({
          type: 'error',
          message: response.error || 'Failed to save scene',
        });
      }
    } catch (error) {
      console.error('Error saving scene:', error);
      addNotification({
        type: 'error',
        message: `Error saving scene: ${error.message}`,
      });
    }
  };
  
  const handleDeleteScene = async (sceneId) => {
    try {
      // Delete the scene
      const response = await deleteScene(sceneId);
      
      if (response.status === 'success') {
        // Remove from the scenes list
        setScenes(prev => prev.filter(scene => scene.id !== sceneId));
        
        // If this was the current scene, clear it
        if (currentScene && currentScene.id === sceneId) {
          setCurrentScene(null);
          setSceneObjects([]);
        }
        
        addNotification({
          type: 'success',
          message: 'Scene deleted successfully',
        });
      } else {
        addNotification({
          type: 'error',
          message: response.error || 'Failed to delete scene',
        });
      }
    } catch (error) {
      console.error('Error deleting scene:', error);
      addNotification({
        type: 'error',
        message: `Error deleting scene: ${error.message}`,
      });
    }
  };
  
  const handleClosePreviewDialog = () => {
    setShowPreviewDialog(false);
    setPreviewModel(null);
  };
  
  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        Scene Editor
      </Typography>
      
      <Typography variant="body1" paragraph>
        Create and edit 3D scenes from descriptions.
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="scene tabs">
          <Tab label="Create Scene" />
          <Tab label="Edit Scene" />
          <Tab label="Preview Scene" />
          <Tab label="Scene Library" />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0} sx={{ flexGrow: 1 }}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Create New Scene
          </Typography>
          
          <Divider sx={{ mb: 2 }} />
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="Scene Name"
                fullWidth
                variant="outlined"
                value={sceneName}
                onChange={(e) => setSceneName(e.target.value)}
                placeholder="Enter a name for your scene"
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Scene Description"
                multiline
                rows={2}
                fullWidth
                variant="outlined"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your scene..."
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Scene Description (Natural Language)"
                multiline
                rows={3}
                fullWidth
                variant="outlined"
                value={nlDescription}
                onChange={(e) => setNlDescription(e.target.value)}
                placeholder="Or describe the scene in natural language for AI generation..."
                disabled={loading}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Paper
                variant="outlined"
                sx={{ p: 2, mt: 1, mb: 2, bgcolor: 'background.default' }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                  }}
                  onClick={toggleModelsList}
                >
                  <Typography variant="subtitle1">
                    Use Existing Models
                  </Typography>
                  {expandedModelsList ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </Box>
                
                <Collapse in={expandedModelsList}>
                  <List dense sx={{ mt: 1 }}>
                    {availableModels.length === 0 ? (
                      <ListItem>
                        <ListItemText primary="No models available" />
                      </ListItem>
                    ) : (
                      availableModels.map((model) => (
                        <ListItem key={model.id}>
                          <ListItemIcon>
                            <Checkbox
                              edge="start"
                              checked={selectedModels.includes(model.id)}
                              onChange={() => handleModelSelect(model.id)}
                            />
                          </ListItemIcon>
                          <ListItemText
                            primary={model.name}
                            secondary={model.description}
                          />
                        </ListItem>
                      ))
                    )}
                  </List>
                </Collapse>
              </Paper>
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleCreateScene}
              disabled={loading || (!sceneName.trim() || (!description.trim() && !nlDescription.trim()))}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {loading ? 'Generating...' : 'Generate Scene'}
            </Button>
          </Box>
        </Paper>
        
        <Typography variant="h6" gutterBottom>
          Recent Scenes
        </Typography>
        
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {loadingScenes ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : scenes.length === 0 ? (
            <Typography color="text.secondary">
              No scenes created yet. Use the form above to create your first scene.
            </Typography>
          ) : (
            <Grid container spacing={2}>
              {scenes.slice(0, 3).map((scene) => (
                <Grid item xs={12} sm={4} key={scene.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" noWrap>
                        {scene.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {scene.date instanceof Date 
                          ? scene.date.toLocaleString() 
                          : new Date(scene.date).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {scene.description}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button size="small" onClick={() => {
                        setSelectedSceneId(scene.id);
                        handleSceneSelect(scene.id);
                        setTabValue(1);
                      }}>
                        Open
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </TabPanel>
      
      <TabPanel value={tabValue} index={1} sx={{ flexGrow: 1 }}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth variant="outlined">
                <InputLabel>Select Scene</InputLabel>
                <Select
                  value={selectedSceneId}
                  onChange={(e) => {
                    setSelectedSceneId(e.target.value);
                    handleSceneSelect(e.target.value);
                  }}
                  label="Select Scene"
                >
                  <MenuItem value="">None</MenuItem>
                  {scenes.map((scene) => (
                    <MenuItem key={scene.id} value={scene.id}>
                      {scene.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                <Button
                  variant="outlined"
                  onClick={handleShowAddObjectDialog}
                  startIcon={<AddIcon />}
                  disabled={!currentScene}
                >
                  Add Object
                </Button>
                <Button
                  variant="contained"
                  onClick={handleSaveScene}
                  startIcon={<SaveIcon />}
                  disabled={!currentScene}
                >
                  Save Scene
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
        
        {currentScene ? (
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Scene Objects
            </Typography>
            
            <Paper sx={{ p: 2, flexGrow: 1, overflow: 'auto' }}>
              {sceneObjects.length === 0 ? (
                <Typography color="text.secondary">
                  No objects in this scene yet. Click 'Add Object' to start building your scene.
                </Typography>
              ) : (
                <List>
                  {sceneObjects.map((object) => (
                    <ListItem
                      key={object.id || object.name}
                      secondaryAction={
                        <IconButton onClick={() => handleRemoveObject(object.id || object.name)}>
                          <DeleteIcon />
                        </IconButton>
                      }
                    >
                      <ListItemText
                        primary={object.name || object.type}
                        secondary={
                          <>
                            <Typography variant="caption" component="span" color="text.secondary">
                              Type: {object.type} | 
                              Pos: [{object.position.join(', ')}] | 
                              Scale: [{object.scale.join(', ')}] | 
                              Color: {object.color || 'N/A'}
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Paper>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Scene Selected
            </Typography>
            <Button variant="contained" onClick={() => setTabValue(0)}>
              Create New Scene
            </Button>
          </Box>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={2} sx={{ flexGrow: 1 }}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <FormControl fullWidth variant="outlined">
            <InputLabel>Select Scene</InputLabel>
            <Select
              value={selectedSceneId}
              onChange={(e) => {
                setSelectedSceneId(e.target.value);
                handleSceneSelect(e.target.value);
              }}
              label="Select Scene"
            >
              <MenuItem value="">None</MenuItem>
              {scenes.map((scene) => (
                <MenuItem key={scene.id} value={scene.id}>
                  {scene.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Paper>
        
        {currentScene ? (
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Scene Preview
            </Typography>
            
            <Box sx={{ flexGrow: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
              <ModelViewer 
                modelUrl={currentScene.model_path || null} 
                modelType="gltf" 
                width="100%" 
                height="100%" 
              />
            </Box>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Scene Selected
            </Typography>
            <Button variant="contained" onClick={() => setTabValue(0)}>
              Create New Scene
            </Button>
          </Box>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={3} sx={{ flexGrow: 1 }}>
        <Typography variant="h6" gutterBottom>
          Scene Library
        </Typography>
        
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {loadingScenes ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : scenes.length === 0 ? (
            <Typography color="text.secondary">
              No scenes created yet.
            </Typography>
          ) : (
            <Grid container spacing={2}>
              {scenes.map((scene) => (
                <Grid item xs={12} sm={6} md={4} key={scene.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" noWrap>
                        {scene.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {scene.date instanceof Date 
                          ? scene.date.toLocaleString() 
                          : new Date(scene.date).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {scene.description}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <IconButton onClick={() => {
                        setSelectedSceneId(scene.id);
                        handleSceneSelect(scene.id);
                        setTabValue(1);
                      }} title="Edit Scene">
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDeleteScene(scene.id)} title="Delete Scene">
                        <DeleteIcon />
                      </IconButton>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </TabPanel>
      
      {/* Add Object Dialog */}
      <Dialog open={showAddObjectDialog} onClose={handleCloseAddObjectDialog}>
        <DialogTitle>Add Object to Scene</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ pt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth variant="outlined">
                <InputLabel>Object Type</InputLabel>
                <Select
                  value={newObject.type}
                  onChange={(e) => setNewObject(prev => ({ ...prev, type: e.target.value }))}
                  label="Object Type"
                >
                  <MenuItem value="cube">Cube</MenuItem>
                  <MenuItem value="sphere">Sphere</MenuItem>
                  <MenuItem value="cylinder">Cylinder</MenuItem>
                  <MenuItem value="plane">Plane</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Object Name"
                fullWidth
                variant="outlined"
                value={newObject.name}
                onChange={(e) => setNewObject(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter a name for this object"
              />
            </Grid>
            
            <Grid item xs={4}>
              <TextField
                label="Position X"
                fullWidth
                variant="outlined"
                type="number"
                value={newObject.position[0]}
                onChange={(e) => setNewObject(prev => ({
                  ...prev,
                  position: [
                    parseFloat(e.target.value) || 0,
                    prev.position[1],
                    prev.position[2]
                  ]
                }))}
              />
            </Grid>
            
            <Grid item xs={4}>
              <TextField
                label="Position Y"
                fullWidth
                variant="outlined"
                type="number"
                value={newObject.position[1]}
                onChange={(e) => setNewObject(prev => ({
                  ...prev,
                  position: [
                    prev.position[0],
                    parseFloat(e.target.value) || 0,
                    prev.position[2]
                  ]
                }))}
              />
            </Grid>
            
            <Grid item xs={4}>
              <TextField
                label="Position Z"
                fullWidth
                variant="outlined"
                type="number"
                value={newObject.position[2]}
                onChange={(e) => setNewObject(prev => ({
                  ...prev,
                  position: [
                    prev.position[0],
                    prev.position[1],
                    parseFloat(e.target.value) || 0
                  ]
                }))}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Color"
                fullWidth
                variant="outlined"
                type="color"
                value={newObject.color}
                onChange={(e) => setNewObject(prev => ({ ...prev, color: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAddObjectDialog}>Cancel</Button>
          <Button onClick={handleAddObject} variant="contained" color="primary">
            Add to Scene
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Preview Dialog */}
      <Dialog 
        open={showPreviewDialog} 
        onClose={handleClosePreviewDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>{previewModel?.name || 'Scene Preview'}</DialogTitle>
        <DialogContent sx={{ height: '70vh', p: 0 }}>
          <ModelViewer 
            modelUrl={previewModel?.model_path || null} 
            modelType="gltf" 
            width="100%" 
            height="100%" 
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePreviewDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScenePage;