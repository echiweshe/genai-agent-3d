@echo off
echo ========================================================
echo     GenAI Agent 3D - Fix All Backend Issues
echo ========================================================
echo.
echo This script will fix multiple issues:
echo 1. Add missing ping method to RedisMessageBus
echo 2. Add /api/health endpoint for service monitoring
echo 3. Fix any indentation errors
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Step 1: Fixing missing ping method in RedisMessageBus...
python fix_redis_ping.py

echo.
echo Step 2: Adding health endpoint to main.py...
python add_health_endpoint.py

echo.
echo Step 3: Fixing any indentation errors...
python fix_indentation.py

echo.
echo ========================================================
echo                      NEXT STEPS
echo ========================================================
echo 1. Restart your backend server:
echo    cd genai_agent_project
echo    python manage_services.py restart backend
echo.
echo 2. Your service manager should now be able to successfully
echo    start all services without health check failures.
echo.
echo If you're still having issues, check the manual_fix_instructions.txt
echo file for additional help.
echo ========================================================
echo.
pause
