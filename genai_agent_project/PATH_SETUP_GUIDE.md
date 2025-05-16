# GenAI Agent 3D - Path and Directory Setup Guide

This guide helps you resolve issues with file paths and directory access in the GenAI Agent 3D application.

## Common Issues

1. **Error: "Model file not found"** - This occurs when the application can't locate model files because different parts of the system are looking in different directories.

2. **Error: "Access outside of base directory is not allowed"** - This happens when the web server tries to access files outside its allowed directory structure.

3. **Error loading models in viewers** - Models don't appear in viewers because the front-end and back-end are using different paths.

## Non-Admin Fix (Recommended)

Since creating symbolic links requires administrator privileges, we've created alternative scripts that work without admin rights:

```
# Run diagnostics to check the current state
python diagnostics_nonadmin.py

# Set up directory structure (without symbolic links)
python setup_directory_links_nonadmin.py

# After setup, whenever you add or modify files, run:
python sync_output_dirs.py
```

This approach creates reference directories with file copying rather than symbolic links.

## Admin Fix (Optional)

If you have administrator privileges, you can use the original scripts:

```
# Run diagnostics only
python diagnostics.py

# Run diagnostics and fix issues (requires administrator privileges)
python diagnostics.py --fix
```

## Manual Fix

If you prefer to fix the issues manually, follow these steps:

### 1. Update the Configuration

Edit `config.yaml` to ensure all paths use the same base directory:

```yaml
paths:
  output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output
  models_output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/models
  scenes_output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/scenes
  svg_output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg
  diagrams_output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/diagrams
  svg_to_video_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video
  svg_to_video_svg_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/svg
  svg_to_video_models_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/models
  blendergpt_output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/blendergpt
  hunyuan_output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/hunyuan
  trellis_output_dir: C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/trellis
```

### 2. Create Required Directories

Make sure all the necessary directories exist:

```
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/models
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/scenes
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/diagrams
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/svg
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/svg_to_video/models
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/blendergpt
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/hunyuan
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/trellis
```

### 3. Setup Reference Directories

Create the same directory structure in these locations:

```
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/output
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/web/backend/output
C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/genai_agent_project/web/frontend/public/output
```

### 4. Restart Services

After making these changes, restart all services:

1. Stop the web backend server
2. Stop the web frontend server
3. Start the web backend server
4. Start the web frontend server

## Using the Non-Admin Solution

When using the non-admin solution with file copying:

1. **Main Output Directory**: Always use `C:/ZB_Share/Labs/src/CluadeMCP/genai-agent-3d/output/` as your primary location for adding files
   
2. **Synchronization**: Run `python sync_output_dirs.py` whenever:
   - You add new files to any output directory
   - You modify files in any output directory
   - You encounter "file not found" errors

3. **Checking Status**: Run `python diagnostics_nonadmin.py` to verify your setup is working correctly

## Troubleshooting

If you're still experiencing issues:

1. **Check web server logs** - Look for file path errors in the web server logs
2. **Check file permissions** - Ensure the output directories are readable and writable
3. **Run manual synchronization** - Run `python sync_output_dirs.py` to ensure files are synchronized
4. **Use the diagnostic tool** - Run `python diagnostics_nonadmin.py` to identify issues

## Need Help?

If you continue to experience issues, please file a bug report with:

1. The exact error message
2. The output of the diagnostics script
3. The steps you've taken to try to resolve the issue
