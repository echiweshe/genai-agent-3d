import React, { useEffect, useState, useRef } from 'react';
import { Box, Typography, CircularProgress, Paper, Button } from '@mui/material';
import mermaid from 'mermaid';

// Initialize mermaid
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  logLevel: 'error',
  securityLevel: 'strict',
  flowchart: { curve: 'basis' },
  gantt: { axisFormat: '%m/%d/%Y' },
  sequence: { actorMargin: 50 },
});

const DiagramViewer = ({ 
  diagramCode, 
  diagramType = 'mermaid', 
  width = '100%', 
  height = '400px' 
}) => {
  const containerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [svgContent, setSvgContent] = useState(null);
  
  useEffect(() => {
    if (!diagramCode) {
      setLoading(false);
      return;
    }

    const renderDiagram = async () => {
      try {
        setLoading(true);
        setError(null);
        
        if (diagramType.toLowerCase() === 'mermaid') {
          try {
            // Generate SVG
            const { svg } = await mermaid.render('diagram-container', diagramCode);
            setSvgContent(svg);
          } catch (e) {
            console.error('Mermaid rendering error:', e);
            setError(`Failed to render Mermaid diagram: ${e.message}`);
          }
        } else if (diagramType.toLowerCase() === 'svg') {
          // Directly use SVG content
          setSvgContent(diagramCode);
        } else if (diagramType.toLowerCase() === 'dot') {
          // For DOT format, we'd typically use a GraphViz renderer
          // Since we don't have a direct GraphViz integration, we'll show an error or placeholder
          setError('DOT format diagrams require server-side rendering with GraphViz. Displaying code instead.');
          // As a fallback we could create a pre-formatted code block
          setSvgContent(`<pre>${diagramCode}</pre>`);
        } else {
          setError(`Unsupported diagram type: ${diagramType}`);
        }
      } catch (error) {
        console.error('Error rendering diagram:', error);
        setError(`Failed to render diagram: ${error.message}`);
      } finally {
        setLoading(false);
      }
    };

    renderDiagram();
  }, [diagramCode, diagramType]);

  // Function to export diagram as SVG
  const handleExportSVG = () => {
    if (!svgContent) return;
    
    // Create a blob from the SVG content
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary link to download the file
    const link = document.createElement('a');
    link.href = url;
    link.download = `diagram-${Date.now()}.svg`;
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };
  
  // Function to export diagram as PNG
  const handleExportPNG = () => {
    if (!svgContent || !containerRef.current) return;
    
    // Create a canvas element
    const canvas = document.createElement('canvas');
    const svgElement = containerRef.current.querySelector('svg');
    
    if (!svgElement) {
      console.error('No SVG element found');
      return;
    }
    
    // Get SVG dimensions
    const svgRect = svgElement.getBoundingClientRect();
    
    // Set canvas size to match SVG size with higher resolution
    const scale = 2; // Increase resolution by 2x
    canvas.width = svgRect.width * scale;
    canvas.height = svgRect.height * scale;
    
    // Get canvas context and scale it
    const ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);
    
    // Create a new Image element
    const img = new Image();
    
    // Convert SVG to data URL
    const xml = new XMLSerializer().serializeToString(svgElement);
    const svg64 = btoa(unescape(encodeURIComponent(xml)));
    const image64 = 'data:image/svg+xml;base64,' + svg64;
    
    // Set up image onload handler
    img.onload = () => {
      // Draw image on canvas
      ctx.drawImage(img, 0, 0);
      
      // Convert canvas to PNG data URL
      const pngData = canvas.toDataURL('image/png');
      
      // Create download link
      const link = document.createElement('a');
      link.download = `diagram-${Date.now()}.png`;
      link.href = pngData;
      link.click();
    };
    
    // Set image source to SVG data URL
    img.src = image64;
  };

  return (
    <Box sx={{ position: 'relative', width, height, display: 'flex', flexDirection: 'column' }}>
      <Paper
        elevation={3}
        sx={{
          flexGrow: 1,
          width: '100%',
          bgcolor: 'background.paper',
          overflow: 'auto',
          position: 'relative',
          p: 2,
        }}
      >
        {/* Diagram container */}
        <Box 
          ref={containerRef}
          sx={{ 
            width: '100%', 
            height: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
          dangerouslySetInnerHTML={svgContent ? { __html: svgContent } : undefined}
        />

        {/* Loading indicator */}
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              zIndex: 10,
            }}
          >
            <CircularProgress />
            <Typography variant="body1" sx={{ mt: 2 }}>
              Rendering Diagram...
            </Typography>
          </Box>
        )}

        {/* Error message */}
        {error && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              zIndex: 10,
              p: 3,
            }}
          >
            <Typography variant="h6" color="error">Error</Typography>
            <Typography variant="body1" color="error" align="center">
              {error}
            </Typography>
            {/* Show diagram code if there's an error */}
            {diagramCode && (
              <Paper
                elevation={1}
                sx={{
                  mt: 2,
                  p: 2,
                  maxHeight: '200px',
                  overflow: 'auto',
                  width: '100%',
                  bgcolor: 'grey.100',
                }}
              >
                <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                  {diagramCode}
                </Typography>
              </Paper>
            )}
          </Box>
        )}

        {/* No diagram message */}
        {!loading && !error && !diagramCode && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              zIndex: 10,
            }}
          >
            <Typography variant="h6">No Diagram</Typography>
            <Typography variant="body1">
              No diagram code provided
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Export buttons */}
      {svgContent && !loading && !error && (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'flex-end', 
          gap: 1, 
          mt: 1 
        }}>
          <Button 
            variant="outlined" 
            size="small" 
            onClick={handleExportSVG}
          >
            Export SVG
          </Button>
          <Button 
            variant="outlined" 
            size="small" 
            onClick={handleExportPNG}
          >
            Export PNG
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default DiagramViewer;
