#!/bin/bash
# Fix Claude API Key in GenAI Agent 3D

echo "========================================================================"
echo "              Fix Claude API Key for GenAI Agent 3D"
echo "========================================================================"
echo
echo "This script will help you set up your Claude (Anthropic) API key."
echo "You'll need a valid API key from Anthropic to use Claude in the application."
echo

# Activate the Python virtual environment if it exists
if [ -f "./genai_agent_project/venv/bin/activate" ]; then
    source ./genai_agent_project/venv/bin/activate
fi

# Run the Python script to fix the API key
python fix_claude_api_key.py

echo
echo "If the key was set successfully, you can now restart the application to use Claude."
echo "To restart the application, use: python manage_services.py restart all"
echo
