# SVG Generator Fix for GenAI Agent 3D

This README explains how to fix the SVG generator module in the GenAI Agent 3D project. The following scripts are provided to address various issues with the SVG generator pipeline.

## Current Issues

1. **SVG Output Directory Issues**: The system tries to create directories that already exist as files.
2. **Missing Dependencies**: The mathutils module is missing, preventing full SVG to 3D conversion functionality.
3. **Claude Provider Error**: The Claude provider fails with a "count_tokens" error.
4. **Missing ModelAnimator Class**: The animation module is missing the ModelAnimator class.
5. **Code Path Duplication**: The SVG generator code is duplicated in multiple locations.

## Available Fix Scripts

### All-in-One Fix Script (Recommended)

This script fixes all the issues in one go:

```
powershell -ExecutionPolicy Bypass -File fix_svg_generator_all_in_one.ps1
```

This script performs the following actions:
- Creates backups of existing files and directories
- Fixes SVG output directory structure
- Copies SVG generator code from backup
- Updates import statements
- Creates mathutils stub module
- Fixes Claude provider integration
- Creates ModelAnimator stub class
- Creates test files and synchronization scripts

### Individual Fix Scripts

If you prefer to fix issues one by one, you can use these individual scripts:

1. **Fix SVG Directory Structure**: 
   ```
   powershell -ExecutionPolicy Bypass -File fix_svg_directory_structure.ps1
   ```

2. **Fix Backend Issues**:
   ```
   powershell -ExecutionPolicy Bypass -File fix_backend_issues.ps1
   ```

3. **Install Required Dependencies**:
   ```
   powershell -ExecutionPolicy Bypass -File install_required_dependencies.ps1
   ```

4. **Restore SVG Generator from Backup**:
   ```
   powershell -ExecutionPolicy Bypass -File restore_svg_generator.ps1
   ```

### Utility Scripts

These scripts provide additional functionality:

1. **Test SVG Generator**:
   ```
   python test_svg_generator.py
   ```

2. **Synchronize SVG Directories**:
   ```
   sync_svg_directories.bat
   ```

3. **Restart Backend Service**:
   ```
   restart_backend.bat
   ```

## Step-by-Step Fix Procedure

### Option 1: Quick Fix (Recommended)

1. Run the all-in-one fix script:
   ```
   powershell -ExecutionPolicy Bypass -File fix_svg_generator_all_in_one.ps1
   ```

2. Test the SVG generator:
   ```
   python test_svg_generator.py
   ```

3. Restart the backend service:
   ```
   restart_backend.bat
   ```

### Option 2: Manual Fix

1. Fix the SVG directory structure:
   ```
   powershell -ExecutionPolicy Bypass -File fix_svg_directory_structure.ps1
   ```

2. Install required dependencies:
   ```
   powershell -ExecutionPolicy Bypass -File install_required_dependencies.ps1
   ```

3. Restore SVG generator from backup:
   ```
   powershell -ExecutionPolicy Bypass -File restore_svg_generator.ps1
   ```

4. Fix backend issues:
   ```
   powershell -ExecutionPolicy Bypass -File fix_backend_issues.ps1
   ```

5. Test the SVG generator:
   ```
   python test_svg_generator.py
   ```

6. Restart the backend service:
   ```
   restart_backend.bat
   ```

## Directory Structure

After fixing the issues, the directory structure will be:

```
genai-agent-3d/
├── output/
│   ├── svg/                     # Consolidated output directory for SVG files
│   └── svg_to_video/
│       ├── animations/          # Directory for animations
│       ├── models/              # Directory for 3D models
│       ├── svg/                 # Mirror of main SVG directory
│       └── videos/              # Directory for rendered videos
├── genai_agent_project/
│   ├── genai_agent/
│   │   └── svg_to_video/        # Main code directory for SVG pipeline
│   └── output/
│       └── svg/                 # Mirror of main SVG directory
└── backups/                     # Backups created during fixes
```

## Troubleshooting

If you encounter issues:

1. **Backend Fails to Start**:
   - Check the logs for specific errors
   - Try running `fix_backend_issues.ps1`
   - Make sure SVG directories exist as directories, not files

2. **SVG Generation Fails**:
   - Try the mock provider first: `python test_svg_generator.py`
   - Check API keys for Claude and OpenAI
   - Verify langchain integration is working

3. **Permission Errors**:
   - Run scripts with administrator privileges
   - Check file permissions on the SVG directories

4. **Directory Structure Issues**:
   - Run `sync_svg_directories.bat` to ensure all directories are synchronized
   - Check for file/directory conflicts using `fix_svg_directory_structure.ps1`

## Restoring from Backup

All fix scripts create backups before making changes. To restore:

1. Check the `backups` directory for timestamped backups
2. Copy the contents back to their original locations

## Additional Notes

- The mathutils module is provided as a stub. For full 3D conversion functionality, the actual Blender mathutils module is required.
- The ModelAnimator class is a stub implementation. For full animation functionality, additional development is needed.
- The code has been updated to use `genai_agent_project.genai_agent.svg_to_video` imports instead of `genai_agent.svg_to_video`.

For any questions, please refer to the documentation or contact the development team.
