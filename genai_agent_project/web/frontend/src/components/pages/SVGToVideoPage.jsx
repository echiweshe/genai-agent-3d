import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Divider,
  Button,
  Grid,
  useTheme
} from '@mui/material';
import { FileSymlink, Video, Settings, FileCheck } from 'lucide-react';

// Import components
import Header from '../common/Header';
import SVGGeneratorForm from '../svg/SVGGeneratorForm';
import SVGDisplay from '../svg/SVGDisplay';
import SVGList from '../svg/SVGList';
import SVGTo3DViewer from '../svg/SVGTo3DViewer';

/**
 * Enhanced SVG to Video Pipeline Page
 * 
 * This component provides an interface for users to:
 * 1. Generate SVG diagrams using natural language descriptions
 * 2. View and manage generated SVGs
 * 3. Convert SVGs to 3D models and view them in Blender
 * 4. Create animations and videos from 3D models
 */
const SVGToVideoPage = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  
  // State
  const [tabIndex, setTabIndex] = useState(0);
  const [diagrams, setDiagrams] = useState([]);
  const [selectedDiagram, setSelectedDiagram] = useState(null);
  const [loading, setLoading] = useState(false);
  const [providers, setProviders] = useState([]);
  const [capabilities, setCapabilities] = useState({
    svg_generator_available: false,
    svg_to_3d_available: false,
    animation_available: false,
    rendering_available: false
  });

  // Fetch capabilities and diagrams on component mount
  useEffect(() => {
    fetchCapabilities();
    fetchDiagrams();
    fetchProviders();
  }, []);

  // Fetch SVG to Video pipeline capabilities
  const fetchCapabilities = async () => {
    try {
      const response = await axios.get('/svg-generator/capabilities');
      if (response.data.status === 'success') {
        setCapabilities(response.data);
      }
    } catch (error) {
      console.error('Error fetching capabilities:', error);
    }
  };

  // Fetch list of generated diagrams
  const fetchDiagrams = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/diagrams');
      setDiagrams(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching diagrams:', error);
      setLoading(false);
    }
  };

  // Fetch available LLM providers
  const fetchProviders = async () => {
    try {
      const response = await axios.get('/svg-generator/providers');
      if (response.data.status === 'success') {
        setProviders(response.data.providers);
      }
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  // Handle SVG generation success
  const handleSVGGenerated = (newDiagram) => {
    setDiagrams([newDiagram, ...diagrams]);
    setSelectedDiagram(newDiagram);
    setTabIndex(1); // Switch to the "Generated Diagrams" tab
  };

  // Handle diagram selection
  const handleDiagramSelect = (diagram) => {
    setSelectedDiagram(diagram);
  };

  // Handle diagram deletion
  const handleDiagramDelete = async (diagramId) => {
    try {
      await axios.delete(`/diagrams/${diagramId}`);
      setDiagrams(diagrams.filter(d => d.diagram_id !== diagramId));
      if (selectedDiagram && selectedDiagram.diagram_id === diagramId) {
        setSelectedDiagram(null);
      }
    } catch (error) {
      console.error('Error deleting diagram:', error);
    }
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };

  // Handle 3D model conversion completion
  const handleModelConversionComplete = (modelData) => {
    console.log('Model conversion complete:', modelData);
    // Could update state here if needed for further pipeline steps
  };

  return (
    <Container maxWidth="lg">
      <Header title="SVG to Video Pipeline" />
      
      <Typography variant="h4" gutterBottom>
        SVG to Video Pipeline
      </Typography>
      
      <Typography variant="body1" paragraph>
        Generate SVG diagrams and convert them to 3D models and videos.
      </Typography>

      {/* Pipeline status indicators */}
      <Paper elevation={2} sx={{ p: 2, mb: 3, bgcolor: theme.palette.background.default }}>
        <Typography variant="subtitle1" gutterBottom>
          Pipeline Status:
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={3}>
            <Box 
              sx={{ 
                p: 1, 
                borderRadius: 1, 
                bgcolor: capabilities.svg_generator_available ? 'success.light' : 'error.light',
                color: 'white',
                textAlign: 'center'
              }}
            >
              <Typography variant="body2">SVG Generation</Typography>
              <Typography variant="caption">{capabilities.svg_generator_available ? 'Available' : 'Unavailable'}</Typography>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box 
              sx={{ 
                p: 1, 
                borderRadius: 1, 
                bgcolor: capabilities.svg_to_3d_available ? 'success.light' : 'error.light',
                color: 'white',
                textAlign: 'center'
              }}
            >
              <Typography variant="body2">SVG to 3D</Typography>
              <Typography variant="caption">{capabilities.svg_to_3d_available ? 'Available' : 'Unavailable'}</Typography>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box 
              sx={{ 
                p: 1, 
                borderRadius: 1, 
                bgcolor: capabilities.animation_available ? 'success.light' : 'warning.light',
                color: 'white',
                textAlign: 'center'
              }}
            >
              <Typography variant="body2">Animation</Typography>
              <Typography variant="caption">{capabilities.animation_available ? 'Available' : 'Limited'}</Typography>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box 
              sx={{ 
                p: 1, 
                borderRadius: 1, 
                bgcolor: capabilities.rendering_available ? 'success.light' : 'warning.light',
                color: 'white',
                textAlign: 'center'
              }}
            >
              <Typography variant="body2">Rendering</Typography>
              <Typography variant="caption">{capabilities.rendering_available ? 'Available' : 'Limited'}</Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs for pipeline stages */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs
          value={tabIndex}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Generate SVG" icon={<FileSymlink />} iconPosition="start" />
          <Tab label="Generated Diagrams" icon={<FileCheck />} iconPosition="start" />
          <Tab label="3D Conversion" icon={<Settings />} iconPosition="start" />
          <Tab label="Animation & Video" icon={<Video />} iconPosition="start" />
        </Tabs>
        
        <Divider />
        
        {/* Tab content */}
        <Box p={3}>
          {/* Tab 1: SVG Generation */}
          {tabIndex === 0 && (
            <SVGGeneratorForm 
              onSuccess={handleSVGGenerated} 
              providers={providers} 
            />
          )}
          
          {/* Tab 2: Generated Diagrams */}
          {tabIndex === 1 && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  {loading ? (
                    <Box display="flex" justifyContent="center" p={3}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <SVGList 
                      diagrams={diagrams} 
                      onSelect={handleDiagramSelect} 
                      onDelete={handleDiagramDelete}
                      selectedDiagram={selectedDiagram}
                    />
                  )}
                </Grid>
                <Grid item xs={12} md={8}>
                  {selectedDiagram ? (
                    <SVGDisplay diagram={selectedDiagram} />
                  ) : (
                    <Paper sx={{ p: 3, textAlign: 'center' }}>
                      <Typography variant="body1" color="textSecondary">
                        Select a diagram to view or generate a new one.
                      </Typography>
                      <Button 
                        variant="contained" 
                        color="primary"
                        onClick={() => setTabIndex(0)}
                        sx={{ mt: 2 }}
                      >
                        Generate New SVG
                      </Button>
                    </Paper>
                  )}
                </Grid>
              </Grid>
            </Box>
          )}
          
          {/* Tab 3: 3D Conversion */}
          {tabIndex === 2 && (
            <Box>
              {selectedDiagram ? (
                <SVGTo3DViewer 
                  selectedSvg={selectedDiagram}
                  onConversionComplete={handleModelConversionComplete}
                />
              ) : (
                <Paper sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="body1" color="textSecondary">
                    Please select an SVG diagram to convert to 3D.
                  </Typography>
                  <Button 
                    variant="contained" 
                    color="primary"
                    onClick={() => setTabIndex(1)}
                    sx={{ mt: 2 }}
                  >
                    Select Diagram
                  </Button>
                </Paper>
              )}
            </Box>
          )}
          
          {/* Tab 4: Animation & Video */}
          {tabIndex === 3 && (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Animation & Video
              </Typography>
              <Typography variant="body1" color="textSecondary" paragraph>
                Animation and video rendering are under development.
              </Typography>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => setTabIndex(2)}
              >
                Go to 3D Conversion
              </Button>
            </Paper>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default SVGToVideoPage;
