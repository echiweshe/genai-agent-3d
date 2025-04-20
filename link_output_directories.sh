#!/bin/bash

echo "========================================================"
echo "     GenAI Agent 3D - Link Output Directories"
echo "========================================================"
echo
echo "This script will create symbolic links to ensure both"
echo "the web frontend and backend/agent use the same output folders."
echo
echo "Press Enter to continue or Ctrl+C to cancel..."
read

echo
echo "Step 1: Determining directories..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
FRONTEND_OUTPUT="${SCRIPT_DIR}/genai_agent_project/web/backend/output"
AGENT_OUTPUT="${SCRIPT_DIR}/genai_agent_project/output"

echo "Frontend output directory: ${FRONTEND_OUTPUT}"
echo "Agent output directory: ${AGENT_OUTPUT}"

echo
echo "Step 2: Ensuring directories exist..."
if [ ! -d "${AGENT_OUTPUT}" ]; then
    echo "Creating agent output directory..."
    mkdir -p "${AGENT_OUTPUT}"
fi

if [ ! -d "${FRONTEND_OUTPUT}" ]; then
    echo "Creating frontend output directory..."
    mkdir -p "${FRONTEND_OUTPUT}"
fi

echo
echo "Step 3: Creating symbolic links for subdirectories..."

# Models directory
echo "Processing models directory..."
if [ -d "${FRONTEND_OUTPUT}/models" ]; then
    echo "- Backing up existing frontend models..."
    mkdir -p "${FRONTEND_OUTPUT}/models_backup"
    cp -R "${FRONTEND_OUTPUT}/models/"* "${FRONTEND_OUTPUT}/models_backup/" 2>/dev/null
    rm -rf "${FRONTEND_OUTPUT}/models"
fi
mkdir -p "${AGENT_OUTPUT}/models"
ln -sf "${AGENT_OUTPUT}/models" "${FRONTEND_OUTPUT}/models"

# Scenes directory
echo "Processing scenes directory..."
if [ -d "${FRONTEND_OUTPUT}/scenes" ]; then
    echo "- Backing up existing frontend scenes..."
    mkdir -p "${FRONTEND_OUTPUT}/scenes_backup"
    cp -R "${FRONTEND_OUTPUT}/scenes/"* "${FRONTEND_OUTPUT}/scenes_backup/" 2>/dev/null
    rm -rf "${FRONTEND_OUTPUT}/scenes"
fi
mkdir -p "${AGENT_OUTPUT}/scenes"
ln -sf "${AGENT_OUTPUT}/scenes" "${FRONTEND_OUTPUT}/scenes"

# Diagrams directory
echo "Processing diagrams directory..."
if [ -d "${FRONTEND_OUTPUT}/diagrams" ]; then
    echo "- Backing up existing frontend diagrams..."
    mkdir -p "${FRONTEND_OUTPUT}/diagrams_backup"
    cp -R "${FRONTEND_OUTPUT}/diagrams/"* "${FRONTEND_OUTPUT}/diagrams_backup/" 2>/dev/null
    rm -rf "${FRONTEND_OUTPUT}/diagrams"
fi
mkdir -p "${AGENT_OUTPUT}/diagrams"
ln -sf "${AGENT_OUTPUT}/diagrams" "${FRONTEND_OUTPUT}/diagrams"

# Tools directory
echo "Processing tools directory..."
if [ -d "${FRONTEND_OUTPUT}/tools" ]; then
    echo "- Backing up existing frontend tools..."
    mkdir -p "${FRONTEND_OUTPUT}/tools_backup"
    cp -R "${FRONTEND_OUTPUT}/tools/"* "${FRONTEND_OUTPUT}/tools_backup/" 2>/dev/null
    rm -rf "${FRONTEND_OUTPUT}/tools"
fi
mkdir -p "${AGENT_OUTPUT}/tools"
ln -sf "${AGENT_OUTPUT}/tools" "${FRONTEND_OUTPUT}/tools"

# Temp directory
echo "Processing temp directory..."
if [ -d "${FRONTEND_OUTPUT}/temp" ]; then
    echo "- Backing up existing frontend temp files..."
    mkdir -p "${FRONTEND_OUTPUT}/temp_backup"
    cp -R "${FRONTEND_OUTPUT}/temp/"* "${FRONTEND_OUTPUT}/temp_backup/" 2>/dev/null
    rm -rf "${FRONTEND_OUTPUT}/temp"
fi
mkdir -p "${AGENT_OUTPUT}/temp"
ln -sf "${AGENT_OUTPUT}/temp" "${FRONTEND_OUTPUT}/temp"

echo
echo "Step 4: Moving existing model files..."
echo "Copying any files from web backend to agent output..."
cp -R "${FRONTEND_OUTPUT}/models_backup/"* "${AGENT_OUTPUT}/models/" 2>/dev/null
cp -R "${FRONTEND_OUTPUT}/scenes_backup/"* "${AGENT_OUTPUT}/scenes/" 2>/dev/null
cp -R "${FRONTEND_OUTPUT}/diagrams_backup/"* "${AGENT_OUTPUT}/diagrams/" 2>/dev/null
cp -R "${FRONTEND_OUTPUT}/tools_backup/"* "${AGENT_OUTPUT}/tools/" 2>/dev/null
cp -R "${FRONTEND_OUTPUT}/temp_backup/"* "${AGENT_OUTPUT}/temp/" 2>/dev/null

echo
echo "========================================================"
echo "                  DIRECTORIES LINKED"
echo "========================================================"
echo "Symbolic links have been created successfully."
echo
echo "Now both the web frontend and agent will access"
echo "the same files in: ${AGENT_OUTPUT}"
echo
echo "Any existing files have been moved to the agent output directory."
echo "Backups of the original web frontend files are in:"
echo "${FRONTEND_OUTPUT}/*_backup folders"
echo
echo "Please restart your backend server for changes to take effect:"
echo "  python manage_services.py restart backend"
echo "========================================================"
echo
echo "Press Enter to exit..."
read
