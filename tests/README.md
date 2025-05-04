# GenAI Agent 3D Test Suite

This directory contains all tests for the GenAI Agent 3D project.

## Directory Structure

```
tests/
├── svg_to_video/              # SVG to Video pipeline tests
│   ├── svg_to_3d/             # SVG to 3D converter tests
│   ├── svg_generator/         # SVG generator tests
│   └── animation/             # Animation system tests (coming soon)
├── integrations/              # Integration tests (coming soon)
└── README.md                  # This file
```

## Running Tests

Each subdirectory contains its own test suite with specific instructions. In general:

1. **SVG to 3D Converter Tests**: See `svg_to_video/svg_to_3d/README.md`
2. **SVG Generator Tests**: (Coming soon)
3. **Animation Tests**: (Coming soon)

## Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test how components work together
- **Visual Tests**: Tests that require Blender UI to verify results
- **Performance Tests**: Measure performance metrics (coming soon)

## Quick Start

To run all SVG to 3D converter tests:

```bash
cd tests/svg_to_video/svg_to_3d
python test_suite.py
```

## Adding New Tests

When adding new tests:

1. Create test files in the appropriate subdirectory
2. Use consistent naming: `test_*.py` for test files
3. Update the relevant README with instructions
4. Ensure proper import paths for modules being tested
