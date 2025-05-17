import React, { useState, useEffect } from 'react';
import { 
  Button, 
  Grid, 
  Typography, 
  TextField, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  FormControlLabel,
  Checkbox,
  Slider,
  Box,
  Alert,
  Paper,
  Divider,
  Tooltip,
  IconButton
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

// This component provides SVG to 3D conversion options with clarity preservation
const ConversionOptions = ({ onConvert, svgPath, onShowProgress }) => {
  // Conversion options with improved defaults for professional quality
  const [extrudeDepth, setExtrudeDepth] = useState(0.0005);  // Reduced default extrusion to 0.0005
  const [showInBlender, setShowInBlender] = useState(false);
  const [useEnhanced, setUseEnhanced] = useState(true);
  const [preserveClarity, setPreserveClarity] = useState(true);
  const [stylePreset, setStylePreset] = useState('professional');  // New default professional preset
  const [stylePresets, setStylePresets] = useState([]);
  const [customElements, setCustomElements] = useState(false);  // New option for element-specific treatment
  
  // Load style presets from API
  useEffect(() => {
    fetch('/api/svg-generator/style-presets')
      .then(response => response.json())
      .then(data => setStylePresets(data.style_presets || []))
      .catch(error => console.error('Error fetching style presets:', error));
  }, []);
  
  const handleExtrudeDepthChange = (event, newValue) => {
    setExtrudeDepth(newValue);
  };
  
  const handleConvert = () => {
    // Show progress indicator
    onShowProgress(true);
    
    // Prepare options
    const options = {
      extrude_depth: preserveClarity ? Math.min(extrudeDepth * 0.5, 0.005) : extrudeDepth,
      show_in_blender: showInBlender,
      use_enhanced: useEnhanced,
      preserve_clarity: preserveClarity,
      style_preset: stylePreset,
      custom_elements: customElements
    };
    
    // Call parent handler with options
    fetch('/api/svg-generator/convert-to-3d', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        svg_path: svgPath,
        options: options
      })
    })
    .then(response => response.json())
    .then(data => {
      // Hide progress indicator
      onShowProgress(false);
      
      // Call parent handler with result
      onConvert(data);
    })
    .catch(error => {
      console.error('Error converting SVG to 3D:', error);
      onShowProgress(false);
    });
  };
  
  const handleImportToBlender = () => {
    // Show progress indicator
    onShowProgress(true);
    
    // Prepare options
    const options = {
      extrude_depth: preserveClarity ? Math.min(extrudeDepth * 0.5, 0.005) : extrudeDepth,
      preserve_clarity: preserveClarity,
      style_preset: stylePreset,
      custom_elements: customElements
    };
    
    // Call import API
    fetch('/api/svg-generator/import-to-blender', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        svg_path: svgPath,
        options: options
      })
    })
    .then(response => response.json())
    .then(data => {
      // Hide progress indicator
      onShowProgress(false);
    })
    .catch(error => {
      console.error('Error importing SVG to Blender:', error);
      onShowProgress(false);
    });
  };
  
  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Typography variant="h6" gutterBottom>
        Convert SVG to 3D
      </Typography>
      
      <Grid container spacing={2}>
        {/* Extrusion Depth Slider */}
        <Grid item xs={12}>
          <Typography id="extrude-depth-slider" gutterBottom>
            Extrusion Depth
            <Tooltip title="Controls how much the 2D elements are extruded into 3D. Lower values (0.0001-0.001) maintain better diagram clarity, while higher values (0.005-0.05) create more pronounced 3D effects.">
              <IconButton size="small" sx={{ ml: 1 }}>
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs>
              <Slider
                value={extrudeDepth}
                onChange={handleExtrudeDepthChange}
                aria-labelledby="extrude-depth-slider"
                step={0.0001}
                marks={[
                  { value: 0.0001, label: 'Min' },
                  { value: 0.001, label: 'Low' },
                  { value: 0.01, label: 'Med' },
                  { value: 0.05, label: 'High' }
                ]}
                min={0.0001}
                max={0.05}
                valueLabelDisplay="auto"
                disabled={preserveClarity}
              />
            </Grid>
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                {preserveClarity ? Math.min(extrudeDepth * 0.5, 0.005).toFixed(4) : extrudeDepth.toFixed(4)}
              </Typography>
            </Grid>
          </Grid>
        </Grid>
        
        {/* Style Preset Selector */}
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel id="style-preset-label">Style Preset</InputLabel>
            <Select
              labelId="style-preset-label"
              id="style-preset"
              value={stylePreset}
              label="Style Preset"
              onChange={(e) => setStylePreset(e.target.value)}
            >
              {stylePresets.map(preset => (
                <MenuItem key={preset.id} value={preset.id}>
                  {preset.name} - {preset.description}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        {/* Checkboxes */}
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={useEnhanced}
                onChange={(e) => setUseEnhanced(e.target.checked)}
              />
            }
            label="Use enhanced materials and lighting"
          />
        </Grid>
        
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={preserveClarity}
                onChange={(e) => setPreserveClarity(e.target.checked)}
              />
            }
            label={
              <Box display="flex" alignItems="center">
                Preserve diagram clarity (recommended for training materials)
                <Tooltip title="Uses minimal extrusion and preserves the diagram's original 2D appearance while adding subtle 3D effects. Perfect for educational content.">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
          />
        </Grid>
        
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={customElements}
                onChange={(e) => setCustomElements(e.target.checked)}
              />
            }
            label={
              <Box display="flex" alignItems="center">
                Use element-specific treatment
                <Tooltip title="Intelligently applies different extrusion depths and effects to different types of elements (text, nodes, connectors) for optimal visual hierarchy.">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            }
          />
        </Grid>
        
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={showInBlender}
                onChange={(e) => setShowInBlender(e.target.checked)}
              />
            }
            label="Show in Blender after conversion"
          />
        </Grid>
        
        {preserveClarity && (
          <Grid item xs={12}>
            <Alert severity="info">
              Clarity preservation is enabled. Extrusion depth will be optimized to maintain diagram readability.
              Current value: {Math.min(extrudeDepth * 0.5, 0.005).toFixed(4)}
            </Alert>
          </Grid>
        )}
        
        {/* Action Buttons */}
        <Grid item xs={12}>
          <Divider sx={{ my: 1 }} />
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Button 
              variant="contained"
              color="primary"
              onClick={handleConvert}
            >
              Convert to 3D
            </Button>
            
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleImportToBlender}
            >
              Import to Blender
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ConversionOptions;