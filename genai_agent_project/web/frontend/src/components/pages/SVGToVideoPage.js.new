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
  IconButton,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Tabs,
  Tab,
  Divider,
  Tooltip,
  Alert
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import GetAppIcon from '@mui/icons-material/GetApp';
import Image3dRotationIcon from '@mui/icons-material/ThreeDRotation';
import MovieIcon from '@mui/icons-material/Movie';
import { executeTool, getDiagrams, deleteDiagram } from '../../services/api';
import DiagramViewer from '../viewers/DiagramViewer';

// Example descriptions for different diagram types
const EXAMPLE_DESCRIPTIONS = {
  flowchart: "A detailed flowchart showing the process of online shopping from a user's perspective, including steps for browsing products, adding items to cart, checkout process, payment options, and order confirmation.",
  network: "A network diagram illustrating a secure enterprise network architecture with multiple security zones, including internet-facing DMZ, internal network segments, firewalls, load balancers, web servers, application servers, and database servers.",
  sequence: "A sequence diagram showing the authentication process for a web application, including the interactions between user, browser, authentication service, user database, and email notification system.",
  class: "A class diagram showing the object-oriented structure of a basic e-commerce system, including classes for customers, products, orders, payment methods, and shipping options. Include appropriate attributes, methods, and relationships.",
  er: "An entity-relationship diagram for a social media platform database, including entities for users, posts, comments, likes, and followers, with appropriate attributes and relationships.",
  mindmap: "A mind map visualizing the main concepts of project management, including initiation, planning, execution, monitoring, and closure, with relevant sub-topics under each main branch.",
  general: "A diagram illustrating the components and flow of a smart home system, showing how various devices connect and interact with each other, the central hub, and the internet."
};

const SVGToVideoPage = ({ addNotification }) => {
  // State for SVG Generation
  const [description, setDescription] = useState('');
  const [diagramType, setDiagramType] = useState('flowchart');
  const [diagramName, setDiagramName] = useState('');
  const [loading, setLoading] = useState(false);
  const [svgContent, setSvgContent] = useState(null);
  const [diagrams, setDiagrams] = useState([]);
  const [loadingDiagrams, setLoadingDiagrams] = useState(true);
  const [viewDiagram, setViewDiagram] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [llmProvider, setLlmProvider] = useState('claude-direct');
  const [providers, setProviders] = useState([]);
  const [loadingProviders, setLoadingProviders] = useState(false);
  
  // State for Pipeline UI
  const [activeStep, setActiveStep] = useState(0);
  const [tabValue, setTabValue] = useState(0);
  const [selectedDiagram, setSelectedDiagram] = useState(null);
  const [converting3D, setConverting3D] = useState(false);
  const [svgTo3DCapabilities, setSvgTo3DCapabilities] = useState({
    available: false,
    loading: true,
    message: 'Checking 3D conversion capabilities...'
  });
  const [model3D, setModel3D] = useState(null);
  const [animating, setAnimating] = useState(false);
  const [animatedModel, setAnimatedModel] = useState(null);
  const [rendering, setRendering] = useState(false);
  const [video, setVideo] = useState(null);
  
  const diagramTypes = [
    { value: 'flowchart', label: 'Flowchart' },
    { value: 'network', label: 'Network Diagram' },
    { value: 'sequence', label: 'Sequence Diagram' },
    { value: 'class', label: 'UML Class Diagram' },
    { value: 'er', label: 'Entity Relationship Diagram' },
    { value: 'mindmap', label: 'Mind Map' },
    { value: 'general', label: 'General Diagram' }
  ];
  
  // Load existing diagrams and providers when component mounts
  useEffect(() => {
    let mounted = true;
    
    const fetchData = async () => {
      try {
        // Fetch diagrams
        setLoadingDiagrams(true);
        const response = await getDiagrams();
        if (!mounted) return;
        
        if (response.status === 'success' && Array.isArray(response.diagrams)) {
          setDiagrams(response.diagrams);
        } else if (Array.isArray(response.diagrams)) {
          setDiagrams(response.diagrams);
        }
        
        // Health check - only once
        try {
          const healthResponse = await fetch('/svg-generator/health');
          if (!mounted) return;
          
          if (healthResponse.ok) {
            const healthData = await healthResponse.json();
            console.log('SVG Generator health:', healthData);
            addNotification({
              type: 'info',
              message: `SVG Generator API Health: ${healthData.message}`,
            });
            
            // Update capabilities
            setSvgTo3DCapabilities({
              available: healthData.svg_to_3d_available,
              loading: false,
              message: healthData.svg_to_3d_available ? 
                'SVG to 3D conversion is available' : 
                'SVG to 3D conversion requires Blender installation'
            });
          } else {
            console.error('SVG Generator health check failed');
            addNotification({
              type: 'warning',
              message: 'SVG Generator health check failed. Some features may not work.',
            });
          }
        } catch (error) {
          console.error('Error checking SVG Generator health:', error);
        }
        
        // Fetch LLM providers - only once
        setLoadingProviders(true);
        try {
          console.log('Fetching providers...');
          const providersResponse = await fetch('/svg-generator/providers');
          if (!mounted) return;
          
          console.log('Providers response status:', providersResponse.status);
          
          if (providersResponse.ok) {
            const data = await providersResponse.json();
            console.log('Providers data:', data);
            
            if (data.status === 'success' && Array.isArray(data.providers)) {
              setProviders(data.providers);
              console.log('Providers set to:', data.providers);
              
              // Set default provider to claude-direct if available
              const claudeDirectProvider = data.providers.find(p => p.id === 'claude-direct');
              if (claudeDirectProvider) {
                setLlmProvider('claude-direct');
                console.log('Default provider set to claude-direct');
              } else if (data.providers.length > 0) {
                setLlmProvider(data.providers[0].id);
                console.log('Default provider set to:', data.providers[0].id);
              }
            } else {
              console.error('Unexpected providers data format:', data);
              addNotification({
                type: 'warning',
                message: 'Failed to load LLM providers. Using mock providers instead.',
              });
              
              // Use mock providers
              const mockProviders = [
                { id: 'mock-claude', name: 'Mock Claude' },
                { id: 'mock-openai', name: 'Mock OpenAI' }
              ];
              setProviders(mockProviders);
              setLlmProvider('mock-claude');
            }
          } else {
            console.error('Failed to fetch providers:', providersResponse.statusText);
            // Use mock providers
            const mockProviders = [
              { id: 'mock-claude', name: 'Mock Claude' },
              { id: 'mock-openai', name: 'Mock OpenAI' }
            ];
            setProviders(mockProviders);
            setLlmProvider('mock-claude');
          }
        } catch (error) {
          console.error('Error fetching providers:', error);
          // Use mock providers
          const mockProviders = [
            { id: 'mock-claude', name: 'Mock Claude' },
            { id: 'mock-openai', name: 'Mock OpenAI' }
          ];
          setProviders(mockProviders);
          setLlmProvider('mock-claude');
        } finally {
          if (mounted) {
            setLoadingProviders(false);
          }
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        if (mounted) {
          addNotification({
            type: 'error',
            message: `Error loading initial data: ${error.message}`,
          });
        }
      } finally {
        if (mounted) {
          setLoadingDiagrams(false);
        }
      }
    };
    
    fetchData();
    
    // Cleanup function
    return () => {
      mounted = false;
    };
  }, []); // Empty dependency array means this effect runs once when component mounts
  
  const handleGenerateSVG = async () => {
    if (!description.trim()) {
      addNotification({
        type: 'warning',
        message: 'Please provide a diagram description',
      });
      return;
    }
    
    try {
      setLoading(true);
      
      // Use our integrated SVG Generator
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
        
        const result = await response.json();
        
        if (result.status === 'success') {
          // Store the SVG content
          setSvgContent(result.code);
          
          // Add the diagram to the list
          const newDiagram = {
            id: result.diagram_id || Date.now().toString(),
            name: result.name || diagramName || `Diagram-${Date.now().toString().slice(-6)}`,
            description,
            type: diagramType,
            format: 'svg',
            path: result.file_path,
            code: result.code,
            date: new Date(),
            result,
          };
          
          setDiagrams(prev => [newDiagram, ...prev]);
          setSelectedDiagram(newDiagram);
          
          // Move to the next step in the pipeline
          setActiveStep(1);
          
          // Show success notification
          addNotification({
            type: 'success',
            message: result.message || 'SVG diagram generated successfully',
          });
        } else {
          // Show error notification
          addNotification({
            type: 'error',
            message: result.error || 'Failed to generate diagram',
          });
        }
      } catch (error) {
        throw new Error(`SVG generation error: ${error.message}`);
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

  const handleConvertTo3D = async () => {
    if (!selectedDiagram) {
      addNotification({
        type: 'warning',
        message: 'Please select an SVG diagram first',
      });
      return;
    }
    
    try {
      setConverting3D(true);
      
      // Call the SVG to 3D conversion API
      const response = await fetch('/svg-generator/convert-to-3d', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          svg_path: selectedDiagram.path,
          name: selectedDiagram.name
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to convert SVG to 3D');
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        // Store the 3D model information
        setModel3D({
          name: result.name,
          path: result.model_path,
          format: 'blend',
          date: new Date()
        });
        
        // Move to the next step in the pipeline
        setActiveStep(2);
        
        // Show success notification
        addNotification({
          type: 'success',
          message: result.message || '3D model created successfully',
        });
      } else {
        // Show error notification
        addNotification({
          type: 'error',
          message: result.error || 'Failed to convert to 3D',
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error converting to 3D: ${error.message}`,
      });
    } finally {
      setConverting3D(false);
    }
  };
  
  const handleAnimateModel = async () => {
    if (!model3D) {
      addNotification({
        type: 'warning',
        message: 'Please convert to 3D model first',
      });
      return;
    }
    
    try {
      setAnimating(true);
      
      // Call the animation API
      const response = await fetch('/svg-generator/animate-model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model_path: model3D.path,
          name: model3D.name,
          animation_type: 'simple', // Default animation type
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to animate 3D model');
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        // Store the animated model information
        setAnimatedModel({
          name: result.name,
          path: result.animated_model_path,
          format: 'blend',
          date: new Date()
        });
        
        // Move to the next step in the pipeline
        setActiveStep(3);
        
        // Show success notification
        addNotification({
          type: 'success',
          message: result.message || 'Model animated successfully',
        });
      } else {
        // Show error notification
        addNotification({
          type: 'error',
          message: result.error || 'Failed to animate model',
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error animating model: ${error.message}`,
      });
    } finally {
      setAnimating(false);
    }
  };
  
  const handleRenderVideo = async () => {
    if (!animatedModel) {
      addNotification({
        type: 'warning',
        message: 'Please animate the 3D model first',
      });
      return;
    }
    
    try {
      setRendering(true);
      
      // Call the rendering API
      const response = await fetch('/svg-generator/render-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          animated_model_path: animatedModel.path,
          name: animatedModel.name,
          quality: 'medium', // Default quality setting
          duration: 10 // Default duration in seconds
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to render video');
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        // Store the video information
        setVideo({
          name: result.name,
          path: result.video_path,
          format: 'mp4',
          date: new Date()
        });
        
        // Mark the process as complete
        setActiveStep(4);
        
        // Show success notification
        addNotification({
          type: 'success',
          message: result.message || 'Video rendered successfully',
        });
      } else {
        // Show error notification
        addNotification({
          type: 'error',
          message: result.error || 'Failed to render video',
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        message: `Error rendering video: ${error.message}`,
      });
    } finally {
      setRendering(false);
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
      
      // If the deleted diagram was selected, clear the selection
      if (selectedDiagram && selectedDiagram.id === id) {
        setSelectedDiagram(null);
      }
      
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
    link.download = `${diagram.name || 'diagram'}.svg`;
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
  
  const handleSelectDiagram = (diagram) => {
    setSelectedDiagram(diagram);
    // Move to the SVG to 3D step
    setActiveStep(1);
  };
  
  const handleExampleClick = (exampleType) => {
    setDiagramType(exampleType);
    setDescription(EXAMPLE_DESCRIPTIONS[exampleType] || '');
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleReset = () => {
    setActiveStep(0);
    setSelectedDiagram(null);
    setModel3D(null);
    setAnimatedModel(null);
    setVideo(null);
  };
  
  // Steps for the SVG to Video pipeline
  const steps = [
    {
      label: 'Generate SVG',
      description: 'Create an SVG diagram from a text description using AI.',
      content: (
        <Box>
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
            
            <Grid item xs={12} sm={6}>
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
              <Typography variant="subtitle2" gutterBottom>
                Example Descriptions
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {diagramTypes.map(type => (
                  <Button 
                    key={type.value}
                    variant="outlined" 
                    size="small"
                    onClick={() => handleExampleClick(type.value)}
                  >
                    {type.label} Example
                  </Button>
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleGenerateSVG}
                  disabled={loading || !description.trim()}
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
                >
                  {loading ? 'Generating...' : 'Generate SVG'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      )
    },
    {
      label: 'SVG to 3D',
      description: 'Convert the SVG diagram to a 3D model.',
      content: (
        <Box>
          {!selectedDiagram ? (
            <Alert severity="info">Please generate or select an SVG diagram first</Alert>
          ) : !svgTo3DCapabilities.available ? (
            <Alert severity="warning">
              {svgTo3DCapabilities.message || 'SVG to 3D conversion requires Blender installation'}
            </Alert>
          ) : (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Selected Diagram: {selectedDiagram.name}
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <DiagramViewer 
                    diagramCode={selectedDiagram.code} 
                    diagramType="svg" 
                    width="100%" 
                    height="300px" 
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleConvertTo3D}
                    disabled={converting3D || !svgTo3DCapabilities.available}
                    startIcon={converting3D ? <CircularProgress size={20} color="inherit" /> : <Image3dRotationIcon />}
                  >
                    {converting3D ? 'Converting...' : 'Convert to 3D'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          )}
        </Box>
      )
    },
    {
      label: 'Animation',
      description: 'Add animation to the 3D model.',
      content: (
        <Box>
          {!model3D ? (
            <Alert severity="info">Please convert an SVG to 3D first</Alert>
          ) : (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  3D Model: {model3D.name}
                </Typography>
                <Alert severity="info">
                  3D model created and saved to {model3D.path}
                </Alert>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleAnimateModel}
                    disabled={animating}
                    startIcon={animating ? <CircularProgress size={20} color="inherit" /> : null}
                  >
                    {animating ? 'Animating...' : 'Animate Model'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          )}
        </Box>
      )
    },
    {
      label: 'Rendering',
      description: 'Render the animated model to video.',
      content: (
        <Box>
          {!animatedModel ? (
            <Alert severity="info">Please animate a 3D model first</Alert>
          ) : (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Animated Model: {animatedModel.name}
                </Typography>
                <Alert severity="info">
                  Animated model created and saved to {animatedModel.path}
                </Alert>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleRenderVideo}
                    disabled={rendering}
                    startIcon={rendering ? <CircularProgress size={20} color="inherit" /> : <MovieIcon />}
                  >
                    {rendering ? 'Rendering...' : 'Render Video'}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          )}
        </Box>
      )
    },
    {
      label: 'Video Output',
      description: 'View and download the final video.',
      content: (
        <Box>
          {!video ? (
            <Alert severity="info">Please render a video first</Alert>
          ) : (
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Video: {video.name}
                </Typography>
                <Alert severity="success">
                  Video rendered successfully! Saved to {video.path}
                </Alert>
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <Button
                    variant="contained"
                    color="primary"
                    href={`/results/${video.name}.mp4`}
                    target="_blank"
                  >
                    View Video
                  </Button>
                  <Button
                    variant="outlined"
                    color="primary"
                    href={`/results/${video.name}.mp4`}
                    download
                    sx={{ ml: 2 }}
                  >
                    Download Video
                  </Button>
                </Box>
              </Grid>
              
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Divider />
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                  <Button 
                    variant="outlined" 
                    color="primary" 
                    onClick={handleReset}
                  >
                    Start New Project
                  </Button>
                </Box>
              </Grid>
            </Grid>
          )}
        </Box>
      )
    }
  ];
  
  return (
    <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        SVG to Video Pipeline
      </Typography>
      
      <Typography variant="body1" paragraph>
        Generate SVG diagrams and convert them to 3D models and videos.
      </Typography>
      
      <Tabs 
        value={tabValue} 
        onChange={handleTabChange} 
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
      >
        <Tab label="Pipeline Process" />
        <Tab label="Generated Diagrams" />
      </Tabs>
      
      {tabValue === 0 && (
        <Paper sx={{ p: 2, flexGrow: 1, overflow: 'auto' }}>
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel>
                  <Typography variant="subtitle1">{step.label}</Typography>
                </StepLabel>
                <StepContent>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {step.description}
                  </Typography>
                  {step.content}
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </Paper>
      )}
      
      {tabValue === 1 && (
        <Paper sx={{ p: 2, flexGrow: 1, overflow: 'auto' }}>
          <Typography variant="h6" gutterBottom>
            Generated SVG Diagrams
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
                        <Tooltip title="View Diagram">
                          <IconButton onClick={() => handleViewDiagram(diagram)}>
                            <VisibilityIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Export Diagram">
                          <IconButton onClick={() => handleExportDiagram(diagram)}>
                            <GetAppIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Convert to 3D">
                          <span>
                            <IconButton 
                              onClick={() => handleSelectDiagram(diagram)}
                              disabled={!svgTo3DCapabilities.available}
                            >
                              <Image3dRotationIcon />
                            </IconButton>
                          </span>
                        </Tooltip>
                        <Tooltip title="Delete Diagram">
                          <IconButton onClick={() => handleDeleteDiagram(diagram.id)}>
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        </Paper>
      )}
      
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

export default SVGToVideoPage;