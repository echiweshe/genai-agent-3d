#!/bin/bash
# Setup Direct Services Architecture
# This script applies all the necessary configurations for direct services

echo "============================================================="
echo "Setting up direct services architecture..."
echo "============================================================="

echo
echo "Step 1: Ensuring output directories are properly linked..."
python ensure_output_directories.py
if [ $? -ne 0 ]; then
    echo "Failed to set up output directories"
    exit 1
fi

echo
echo "Step 2: Applying direct services integration..."
python apply_direct_services.py
if [ $? -ne 0 ]; then
    echo "Failed to apply direct services integration"
    exit 1
fi

echo
echo "============================================================="
echo "Direct services setup completed successfully!"
echo "============================================================="
echo
echo "You can now run the agent with direct services using:"
echo "  ./genai_agent_project/run_direct.sh"
echo
echo "This implementation:"
echo " - Initializes critical services directly without Redis discovery"
echo " - Maintains extensibility of the microservices architecture"
echo " - Provides reliable access to LLM and Blender functionality"
echo " - Standardizes output directories to avoid path confusion"
echo

# Make script executable
chmod +x genai_agent_project/run_direct.sh
