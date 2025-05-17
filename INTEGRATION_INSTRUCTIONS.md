# Integrating Enhanced SVG to 3D Conversion

This document explains how to integrate the enhanced SVG to 3D conversion system into the backend API.

## Overview

The enhanced SVG to 3D conversion system provides professional-grade 3D models from SVG diagrams with improved materials, geometry, and scene organization. This integration adds new API endpoints and replaces existing ones with enhanced functionality.

## Integration Steps

1. **Add the Enhanced Routes to the Backend**

   In your main FastAPI application file (`main.py`), add the following import and include it in your app:

   ```python
   from .routes.enhanced_svg_generator_routes import router as enhanced_svg_router
   
   # Include the enhanced SVG generator routes
   app.include_router(enhanced_svg_router)
   ```

   This will add the enhanced endpoints to your API at the `/svg-generator` prefix.

2. **Update Frontend to Use New Endpoints**

   The frontend should be updated to use the new style presets and enhanced options. Add the following to your SVG to 3D conversion component:

   ```javascript
   // Fetch available style presets
   useEffect(() => {
     fetch('/api/svg-generator/style-presets')
       .then(response => response.json())
       .then(data => setStylePresets(data.style_presets))
       .catch(error => console.error('Error fetching style presets:', error));
   }, []);
   
   // Add style preset selector to your form
   <FormControl fullWidth margin="normal">
     <InputLabel>Style Preset</InputLabel>
     <Select
       value={stylePreset}
       onChange={(e) => setStylePreset(e.target.value)}
     >
       {stylePresets.map(preset => (
         <MenuItem key={preset.id} value={preset.id}>
           {preset.name} - {preset.description}
         </MenuItem>
       ))}
     </Select>
   </FormControl>
   
   // Add enhanced toggle to your form
   <FormControlLabel
     control={
       <Checkbox
         checked={useEnhanced}
         onChange={(e) => setUseEnhanced(e.target.checked)}
       />
     }
     label="Use enhanced conversion (professional materials and lighting)"
   />
   
   // Update your conversion request
   const handleConvert = () => {
     fetch('/api/svg-generator/convert-to-3d', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json'
       },
       body: JSON.stringify({
         svg_path: selectedDiagram.path,
         options: {
           extrude_depth: extrudeDepth,
           show_in_blender: showInBlender,
           style_preset: stylePreset,
           use_enhanced: useEnhanced,
           debug: false
         }
       })
     })
     .then(response => response.json())
     .then(data => {
       // Handle response
     })
     .catch(error => {
       // Handle error
     });
   };
   ```

3. **Test the Integration**

   After integrating the enhanced routes, test the system with the following:

   - Generate an SVG diagram using the existing UI
   - Try converting with different style presets
   - Compare enhanced vs. non-enhanced results
   - Test direct import to Blender
   - Verify that proper error handling occurs when Blender is not available

## New API Endpoints

The enhanced integration adds the following new endpoints:

- `GET /svg-generator/style-presets` - Get available style presets for 3D conversion
- `POST /svg-generator/convert-to-3d` - Convert SVG to 3D with enhanced options
- `POST /svg-generator/import-to-blender` - Import SVG directly to Blender

It also modifies existing endpoints to report enhanced capabilities:

- `GET /svg-generator/health` - Now always reports SVG to 3D as available, even if Blender isn't found
- `POST /svg-generator/generate` - Same functionality but prepared for integration with enhanced conversion

## Configuration

The enhanced conversion system uses the same configuration settings as the existing system:

- `svg_output_dir` - Directory for SVG output
- `models_output_dir` - Directory for 3D model output
- `diagrams_output_dir` - Directory for diagram output

Make sure these are properly configured in your settings file.

## Customization

You can customize the enhanced conversion by modifying the style presets or adding new ones:

1. Add new style presets in `enhanced_materials.py` in the `get_material_preset` method
2. Update the `get_style_presets` function in `enhanced_svg_generator_routes.py` to include new presets

## Troubleshooting

If you encounter issues with the integration:

1. Check that Blender is properly installed and available in one of the common paths
2. Verify that all required Python modules are installed
3. Check for errors in the API logs
4. Try the standalone `enhanced_convert_svg_to_3d.bat` script to test outside the web interface

## Conclusion

The enhanced SVG to 3D conversion system provides a significant upgrade to the visual quality and organization of 3D models created from SVG diagrams. This integration makes these enhancements available through the web UI while maintaining compatibility with the existing workflow.
