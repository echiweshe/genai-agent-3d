# SVG to Video Pipeline: Cleanup Plan

## Overview

This document outlines the plan for cleaning up and reorganizing the SVG to Video pipeline files to ensure a consistent and maintainable directory structure.

## Current State

The SVG to Video pipeline currently has several issues:

1. **Duplicated Files**: There are multiple versions of some components (e.g., `svg_generator.py` and `svg_generator_new.py`)
2. **Inconsistent Directory Structure**: Some files are in the module root while others are in subdirectories
3. **Scattered Scripts**: Run and test scripts are scattered across the repository
4. **Root Directory Clutter**: Many scripts and documentation files in the root directory

## Cleanup Tasks

### 1. SVG to Video Module Cleanup

#### Move Standalone Files to Their Module Directories

- Move `animation_system.py` → `animation/animation_system.py`
- Move `svg_generator.py` and `svg_generator_new.py` → Keep only the latest in `svg_generator/svg_generator.py`
- Move `video_renderer.py` → `rendering/video_renderer.py`
- Move `utils.py` → `svg_to_3d/svg_utils.py` (if related to SVG to 3D)

#### Remove Deprecated Files

- Remove `convert_svg_to_3d.py` (replaced by modular implementation)
- Remove `svg_to_3d_converter.py` (replaced by modular implementation)
- Remove `pipeline.py` (replaced by `pipeline_integrated.py`)

#### Update __init__.py Files

- Update the main `__init__.py` to import from the correct module paths
- Create/update `__init__.py` files in each module directory

### 2. Scripts Reorganization

#### Create Organized Script Directories

```
scripts/
└── svg_to_video/
    ├── run/                      # Run scripts
    ├── test/                     # Test scripts
    └── utils/                    # Utility scripts
```

#### Move SVG to Video Scripts

- Move root scripts to appropriate directories:
  - `run_svg_to_video.ps1` → `scripts/svg_to_video/run/`
  - `run_svg_video_demo.ps1` → `scripts/svg_to_video/run/`
  - `run_svg_video_demo.py` → `scripts/svg_to_video/run/`
  - `test_svg_to_video.ps1` → `scripts/svg_to_video/test/`
  - `run_svg_to_3d_tests.ps1` → `scripts/svg_to_video/test/`
  - `run_svg_generator_test.ps1` → `scripts/svg_to_video/test/`

### 3. Tests Reorganization

#### Create Organized Test Directory Structure

```
tests/
└── svg_to_video/
    ├── svg_generator/
    ├── svg_to_3d/
    ├── animation/
    ├── rendering/
    └── pipeline/
```

#### Move and Update Test Files

- Ensure test files are in their appropriate directories
- Update test imports to match the new module structure

### 4. Documentation Reorganization

#### Create Comprehensive Documentation Structure

```
docs/
└── svg_to_video/
    ├── README.md                 # Main documentation
    ├── API.md                    # API reference
    ├── ARCHITECTURE.md           # Architecture overview
    ├── DIRECTORY_STRUCTURE.md    # Directory structure
    ├── CLEANUP_PLAN.md           # This document
    └── components/               # Component documentation
        ├── svg_generator.md
        ├── svg_to_3d.md
        ├── animation.md
        └── rendering.md
```

#### Move and Update Documentation Files

- Move `README-SVG-TO-VIDEO.md` → `docs/svg_to_video/README.md`
- Move component-specific documentation to their appropriate files

### 5. Output Directory Standardization

#### Create Standard Output Directory Structure

```
output/
└── svg_to_video/
    ├── svg/                      # Generated SVG files
    ├── models/                   # 3D model files
    ├── animations/               # Animation files
    └── videos/                   # Rendered videos
```

#### Update Code to Use Standard Paths

- Ensure all components use the standard output paths
- Update environment variables or configuration as needed

## Implementation Steps

1. **Backup First**: Create a backup of the current state
2. **Module Cleanup**: Clean up the SVG to Video module first
3. **Scripts Reorganization**: Move scripts to their proper locations
4. **Tests Reorganization**: Reorganize test files
5. **Documentation Reorganization**: Move and update documentation
6. **Output Directory Standardization**: Set up standard output directories
7. **Update Imports**: Fix any broken imports across the codebase
8. **Test Everything**: Run tests to ensure everything works properly

## Post-Cleanup Verification

After completing the cleanup tasks, verify that:

1. All components work correctly
2. All scripts can be run from their new locations
3. Documentation is complete and up-to-date
4. Output directories are correctly structured and used by the code
5. No deprecated files or imports remain
