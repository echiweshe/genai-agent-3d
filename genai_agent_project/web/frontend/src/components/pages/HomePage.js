import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Button, 
  Card, 
  CardContent, 
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import ViewInArIcon from '@mui/icons-material/ViewInAr';
import SceneIcon from '@mui/icons-material/Landscape';
import SchemaIcon from '@mui/icons-material/Schema';
import BuildIcon from '@mui/icons-material/Build';
import { useNavigate } from 'react-router-dom';
import { getTools } from '../../services/api';

const HomePage = ({ systemStatus, addNotification }) => {
  const navigate = useNavigate();
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  
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
  
  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Welcome to GenAI Agent 3D
      </Typography>
      
      <Typography variant="body1" paragraph>
        A framework for AI-driven 3D scene generation, integrating large language models with Blender and other 3D tools.
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Quick Actions Card */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button 
                  variant="contained" 
                  fullWidth 
                  startIcon={<ViewInArIcon />}
                  onClick={() => navigate('/models')}
                >
                  Create Model
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button 
                  variant="contained" 
                  fullWidth 
                  startIcon={<SceneIcon />}
                  onClick={() => navigate('/scene')}
                >
                  Build Scene
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button 
                  variant="contained" 
                  fullWidth 
                  startIcon={<SchemaIcon />}
                  onClick={() => navigate('/diagrams')}
                >
                  Generate Diagram
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button 
                  variant="contained" 
                  fullWidth 
                  startIcon={<BuildIcon />}
                  onClick={() => navigate('/tools')}
                >
                  Browse Tools
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        {/* System Status Card */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {systemStatus.status === 'loading' ? (
              <Typography>Loading system status...</Typography>
            ) : systemStatus.status === 'error' ? (
              <Typography color="error">
                Error: {systemStatus.error || 'Failed to connect to server'}
              </Typography>
            ) : (
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="Agent Status" 
                    secondary={systemStatus.agent?.initialized ? 'Initialized' : 'Not initialized'} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Redis Connection" 
                    secondary={systemStatus.redis ? 'Connected' : 'Disconnected'} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Available Tools" 
                    secondary={`${systemStatus.agent?.tools || 0} tools registered`} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="System Version" 
                    secondary={systemStatus.version || '0.1.0'} 
                  />
                </ListItem>
              </List>
            )}
          </Paper>
        </Grid>
        
        {/* Available Tools Card */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Available Tools
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Typography>Loading tools...</Typography>
            ) : tools.length === 0 ? (
              <Typography>No tools available</Typography>
            ) : (
              <Grid container spacing={2}>
                {tools.map((tool) => (
                  <Grid item xs={12} sm={6} md={4} key={tool.name}>
                    <Card variant="outlined">
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
                          onClick={() => navigate(`/tools?tool=${tool.name}`)}
                        >
                          Use Tool
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HomePage;
