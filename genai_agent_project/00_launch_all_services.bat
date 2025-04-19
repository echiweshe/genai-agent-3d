@echo off
echo Launching GenAI Agent 3D services...

start "Redis Server" cmd /k "cd /d C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project && redis-server"
timeout /t 2 > nul
start "Redis Monitor" cmd /k "cd /d C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project && redis-cli monitor"
timeout /t 1 > nul
start "Ollama Server" cmd /k "cd /d C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project && ollama serve"
timeout /t 1 > nul
start "Backend Server" cmd /k "cd /d C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\web\backend && python run_server.py"
timeout /t 1 > nul
start "Frontend Server" cmd /k "cd /d C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\web\frontend && npm start"
timeout /t 1 > nul
start "Agent Core" cmd /k "cd /d C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project && python run.py shell"
timeout /t 1 > nul
