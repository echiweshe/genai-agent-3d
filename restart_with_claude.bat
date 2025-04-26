@echo off
echo ===============================================================================
echo                Restart GenAI Agent 3D with Claude as Default LLM
echo ===============================================================================
echo.
echo This batch file will restart all services with Claude as the default LLM provider.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

cd genai_agent_project
python manage_services.py restart all

echo.
echo Services have been restarted with Claude as the default LLM provider.
echo You can now access the web interface at: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
