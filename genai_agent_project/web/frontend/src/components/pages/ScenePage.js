import React, { useState } from 'react';
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
  CardActions
} from '@mui/material';
import { executeTool } from '../../services/api';

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
  const [loading, setLoading] = useState(false);
  const [scenes, setScenes] = useState([]);
  const [currentScene, setCurrentScene] = useState(null);
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleCreateScene = async () => {
    if (!description.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please provide a scene description',
      });
      return;
    }
    
    try {
      setLoading(true);
      
      // Execute scene generator tool
      const result = await executeTool('scene_generator', {
        description,
      });
      
      if (result.status === 'success') {
        // Create a new scene object
        const newScene = {
          id: Date.now().toString(),
          description,
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
        
        // Clear description
        setDescription('');
        
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
  
  const handleSceneSelect = (scene) => {
    setCurrentScene(scene);
    setTabValue(1);
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
          <Tab label="Scene Editor" />
          <Tab label="Scene Library" />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0} sx={{ flexGrow: 1 }}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Create New Scene
          </Typography>
          
          <Divider sx={{ mb: 2 }} />
          
          <TextField
            label="Scene Description"
            multiline
            rows={4}
            fullWidth
            variant="outlined"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the scene you want to create..."
            disabled={loading}
          />
          
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleCreateScene}
              disabled={loading || !description.trim()}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {loading ? 'Creating...' : 'Create Scene'}
            </Button>
          </Box>
        </Paper>
        
        <Typography variant="h6" gutterBottom>
          Recent Scenes
        </Typography>
        
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {scenes.length === 0 ? (
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
                        Scene {scene.id.substring(scene.id.length - 6)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {scene.date.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {scene.description}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button size="small" onClick={() => handleSceneSelect(scene)}>
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
        {currentScene ? (
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6">
                Scene {currentScene.id.substring(currentScene.id.length - 6)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {currentScene.description}
              </Typography>
            </Paper>
            
            <Box sx={{ flexGrow: 1, bgcolor: 'grey.100', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="h5" color="text.secondary">
                3D Scene Viewer (Not yet implemented)
              </Typography>
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
      
      <TabPanel value={tabValue} index={2} sx={{ flexGrow: 1 }}>
        <Typography variant="h6" gutterBottom>
          Scene Library
        </Typography>
        
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {scenes.length === 0 ? (
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
                        Scene {scene.id.substring(scene.id.length - 6)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {scene.date.toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {scene.description}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button size="small" onClick={() => handleSceneSelect(scene)}>
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
    </Box>
  );
};

export default ScenePage;
