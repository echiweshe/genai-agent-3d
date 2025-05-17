@echo off
REM Script to find Blender executable
echo Blender Locator Script
echo ---------------------

REM Check registry for Blender installation
echo Checking Windows Registry...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\BlenderFoundation" /s 2>nul

REM Checking program files
echo.
echo Checking Program Files...
dir /b /s "C:\Program Files\*blender.exe" 2>nul
dir /b /s "C:\Program Files (x86)\*blender.exe" 2>nul

REM Checking ZB_Share path based on current working directory
echo.
echo Checking ZB_Share paths...
dir /b /s "C:\ZB_Share\*blender.exe" 2>nul

REM Search PATH environment variable
echo.
echo Checking PATH environment variable...
for %%i in (blender.exe) do @echo %%~$PATH:i

REM Check for Blender executable anywhere on C:
echo.
echo Performing system-wide search (this may take several minutes)...
echo Searching common paths first...

REM Search common paths first to avoid a full search if possible
for %%D in (Tools Apps 3D Programs Software Portable Downloads Desktop Applications) do (
  dir /b /s "C:\*%%D*\*blender.exe" 2>nul
)

REM Search other likely locations
dir /b /s "C:\blender\blender.exe" 2>nul
dir /b /s "D:\blender\blender.exe" 2>nul
dir /b /s "%USERPROFILE%\Desktop\blender\blender.exe" 2>nul
dir /b /s "%USERPROFILE%\Downloads\blender\blender.exe" 2>nul

echo.
echo If Blender was found, please set the BLENDER_PATH environment variable to the full path above.
echo Example: set BLENDER_PATH=C:\path\to\blender.exe
echo.
echo You can also edit the test_clarity_convert.bat script and add your Blender path directly.
echo.
pause
