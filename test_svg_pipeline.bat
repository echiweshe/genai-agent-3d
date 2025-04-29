@echo off
echo Testing SVG to Video Pipeline components
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_svg_to_video.bat first.
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

echo Testing SVG Generator component...
python -c "from genai_agent.svg_to_video.svg_generator import SVGGenerator; print('SVG Generator imported successfully'); print('Available providers:', SVGGenerator().get_available_providers())"

echo.
echo Testing Blender installation...
python -c "from genai_agent.svg_to_video.utils import check_blender_installation; available, info = check_blender_installation(); print(f'Blender available: {available}'); print(f'Blender info: {info}')"

echo.
echo Testing pipeline module...
python -c "from genai_agent.svg_to_video.pipeline import SVGToVideoPipeline; print('Pipeline module imported successfully')"

echo.
if %ERRORLEVEL% == 0 (
    echo All tests passed!
    echo The SVG to Video Pipeline components are working correctly.
) else (
    echo Some tests failed.
    echo Please check the error messages above.
)
