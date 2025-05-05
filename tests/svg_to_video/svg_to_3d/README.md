# SVG to 3D Converter Test Suite

This directory contains comprehensive tests for the SVG to 3D converter module located at `genai_agent/svg_to_video/svg_to_3d/`.

## Current Status

### ✅ Working Features
- Basic shape conversion (rectangles, circles, ellipses, lines, polygons, paths)
- Text rendering with proper 3D extrusion
- Fill colors correctly applied
- Scene setup with camera and lighting
- Modular architecture with separate components

### ❌ Known Issues
- Transparency/opacity not working (all materials appear solid)
- Strokes on mesh objects (circles) not rendering
- Stroke-only shapes (fill="none") have rendering issues

### 🚧 Work in Progress
- Material system refinement for transparency
- Stroke implementation for mesh objects
- Comprehensive test coverage

For detailed status, see [CURRENT_STATUS.md](./CURRENT_STATUS.md)

## Important: Blender Requirement

The SVG to 3D converter uses Blender's Python modules (like `mathutils` and `bpy`), so all tests must be run with Blender's Python interpreter.

## Quick Start

1. Make sure Blender is installed on your system
2. Navigate to the project root directory
3. Use the PowerShell test runner:
   ```powershell
   .\run_svg_to_3d_tests.ps1
   ```
   Or manually run tests from the test directory:
   ```bash
   cd tests/svg_to_video/svg_to_3d
   python run_quick_test.py  # For quick test
   python test_suite.py      # For full test suite
   ```

## Test Scripts

### 1. Check Imports
Verify that all modules can be imported correctly:
```bash
python check_imports.py
```

### 2. Run Tests
Run specific tests using the test runner:
```bash
# Run basic test
python run_tests.py --test basic

# Run debug test
python run_tests.py --test debug

# Run batch test
python run_tests.py --test batch

# Run visual test (opens Blender GUI)
python run_tests.py --test visual --no-background
```

### 3. Complete Test Suite
Run all tests and generate a comprehensive report:
```bash
python test_suite.py
```

## Individual Test Scripts

### test_converter.py
Basic functionality test with simple shapes.
```bash
blender --background --python test_converter.py
```

### debug_converter.py
Detailed debug test with edge cases and verbose output.
```bash
blender --background --python debug_converter.py
```

### batch_test.py
Tests multiple SVG files to ensure robustness.
```bash
blender --background --python batch_test.py
```

### visual_test.py
Visual test with complex SVG elements (runs in Blender GUI).
```bash
blender --python visual_test.py
```

### convert_svg.py
Command-line interface for converting individual SVG files:
```bash
blender --background --python convert_svg.py -- input.svg output.blend
```

## Test Results

After running the test suite, you'll find:
- Log files in `test_results/` (created in this test directory)
- Generated .blend files in `test_output/` (created in this test directory)
- JSON and HTML reports in `test_results/`
- SVG outputs will be saved to the project's `output/svg/` directory

## Troubleshooting

1. **Blender not found**: Specify the path to Blender:
   ```bash
   python run_tests.py --blender /path/to/blender
   ```

2. **Import errors**: Run the import check:
   ```bash
   python check_imports.py
   ```

3. **Detailed debugging**: Run with debug flag:
   ```bash
   blender --background --python convert_svg.py -- input.svg output.blend --debug
   ```

## Test Coverage

The test suite covers:
- Basic shapes (rectangles, circles, ellipses)
- Complex paths with curves and arcs
- Text elements
- Grouped elements with transforms
- Edge cases (empty paths, very small elements)
- Material and color handling
- Scene setup and camera positioning

## Next Steps

After verifying all tests pass:
1. Integrate the converter into the main SVG to video pipeline
2. Add UI integration in the main project
3. Implement animation capabilities
4. Test with production SVG files
