# SVG Pipeline Consolidation

This directory contains scripts to verify and consolidate the SVG to Video pipeline in the GenAI Agent 3D project.

## Problem Statement

The project currently has duplicate code paths for the SVG to Video pipeline:

1. **Main codebase location**: 
   - `C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent\svg_to_video`

2. **Project codebase location**: 
   - `C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\genai_agent\svg_to_video`

3. **Different SVG output paths**:
   - Test output: `C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\output\svg`
   - Web UI output: `C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg_to_video\svg`

## Current Status

Initial testing has revealed:
- The main SVG directory (`genai_agent/svg_to_video`) appears to already be removed
- The project SVG directory structure is modular with subdirectories instead of monolithic files 
- Some of the output directories may already be symlinked together

## Solution

The solution consists of two scripts:

1. **svg_pipeline_verification.py**: Verifies that the SVG pipeline is working correctly in the main project directory
2. **consolidate_svg_pipeline.py**: Consolidates the code and output paths to eliminate duplication

These scripts have been designed to be idempotent - they can be run multiple times without causing harm, and will detect and handle cases where consolidation has already been partially completed.

## Usage

### Step 1: Verify the SVG Pipeline

```bash
python svg_pipeline_verification.py
```

This script will:
- Check if all required directories exist
- Verify that essential files are present
- Check if output directories are already symlinked
- Test module files for content
- Create a basic SVG file to test the output directory

### Step 2: Consolidate the SVG Pipeline

```bash
python consolidate_svg_pipeline.py
```

This script will:
- Check if output directories are already symlinks and handle appropriately
- Consolidate output directories into a single path
- Update file paths in code to reference the consolidated output directory
- Update API routes and configuration
- Remove duplicate code directory (if it exists)
- Create symlinks for backward compatibility
- Verify that SVG files can be created in the consolidated output directory

## Backup

Both scripts automatically create backups before making changes:
- The consolidation script creates backups of directories before removing them
- It also preserves different versions of files with .bak extensions

## After Consolidation

After running the consolidation script:
1. All SVG files will be stored in: `C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\output\svg`
2. Symlinks will be created for the old paths to maintain backward compatibility
3. Code references will be updated to use the consolidated path

## Troubleshooting

If you encounter any issues:
1. Check the logs for details on what went wrong
2. Restore from backups if necessary (look for directories with "_backup" suffix)
3. Manually update any missed file paths to reference the consolidated output directory

## Directory Structure After Consolidation

```
genai-agent-3d/
├── output/
│   ├── svg/                     # Consolidated output directory for SVG files
│   └── svg_to_video/
│       ├── animations/
│       ├── models/
│       ├── svg -> ../../output/svg   # Symlink to consolidated SVG directory
│       └── videos/
├── genai_agent_project/
│   ├── genai_agent/
│   │   └── svg_to_video/        # Main code directory for SVG pipeline
│   └── output/
│       └── svg -> ../../output/svg   # Symlink to consolidated SVG directory
└── XX_genai_agent/              # Backup of original redundant directory
```
