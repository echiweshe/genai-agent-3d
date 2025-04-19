# GenAI Agent 3D - Complete Setup and Testing Guide

This document provides comprehensive instructions for setting up and testing the GenAI Agent 3D project from scratch. Follow these steps in sequence to ensure a properly functioning system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Core System Setup](#core-system-setup)
3. [External Dependencies Setup](#external-dependencies-setup)
4. [Backend API Setup and Testing](#backend-api-setup-and-testing)
5. [Frontend Setup and Testing](#frontend-setup-and-testing)
6. [End-to-End Testing](#end-to-end-testing)
7. [Complete System Testing](#complete-system-testing)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- Python 3.10+ (Python 3.11 recommended)
- Node.js 16+ (Node.js 18 recommended)
- Redis Server
- Blender 4.x
- Git
- Ollama (for local LLM capabilities)

### Check Prerequisites

```bash
# Verify Python version
python --version

# Verify Node.js version
node --version

# Verify Redis installation
redis-cli ping  # Should return "PONG"

# Verify Blender installation
blender --version

# Verify Git installation
git --version

# Verify Ollama installation (if applicable)
ollama --version
```

## Core System Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/genai-agent-3d.git
cd genai-agent-3d
```

### 2. Python Environment Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

pip uninstall pydantic pydantic-core -y
pip install --no-cache-dir pydantic
```

### 3. Create Required Directories

```bash
# Run the directory creation script
python create_directories.py
```

### 4. Configure the Application

```bash
# Edit the configuration file to match your environment
# Especially update Blender path and any API keys
nano config.yaml  # or use any text editor
```

### 5. Initialize the Core System

```bash
# Run the initialization script
python setup_project.py

# Verify core components
python run.py check
```

## External Dependencies Setup

### 1. Ollama Setup

```bash
# Start Ollama server
python run.py ollama start

# Pull required models
python run.py ollama pull deepseek-coder
python run.py ollama pull llama3   # Optional alternative model

# Verify models
python run.py ollama list
```

### 2. External Integrations Setup

```bash
# Run the integration setup utility
python setup_integrations.py

# Follow the prompts to configure:
# - BlenderGPT
# - Hunyuan-3D
# - TRELLIS

# Verify integrations
python run.py check-integrations
```

### 3. Verify Blender Integration

```bash
# Test Blender script execution
python examples/test_blender_script.py

python .\00_test_blender_integration.py

# You should see Blender launch and create a simple cube
```

## Backend API Setup and Testing

### 1. Set Up Backend API

```bash
# Navigate to the backend directory
cd genai_agent_project/web/backend

# Install backend-specific dependencies
pip install -r requirements.txt
```

### 2. Run Basic Backend Tests

```bash
# Run unit tests for the backend API
python run_tests.py --unit

# Expected output should show all tests passing
```

### 3. Test Extended API Functionality

```bash
# Run extended API tests
python run_tests.py --extended

# These tests verify more complex API functionality
```

### 4. Test WebSocket Functionality

```bash
# Start the server in test mode
cd genai_agent_project/web/backend
python run_server.py --test-mode

# In a separate terminal:
cd genai_agent_project/web/backend/tests
python manual_websocket_test.py

# You should see successful connection and message exchange with detailed test results

# Alternatively, use the convenience scripts from the project root:
cd genai_agent_project
./run_websocket_test.bat  # Windows
# OR
./run_websocket_test.sh   # Linux/macOS
```

### 5. Verify All Backend Tests Together

```bash
# Run all backend tests
python run_tests.py --all

# Expected output should show all tests passing
```

## Frontend Setup and Testing

### 1. Set Up Frontend

```bash
# Navigate to the frontend directory
cd genai_agent_project/web/frontend

# Install frontend dependencies
npm install
```

### 2. Run Service Unit Tests

```bash
# Test API and WebSocket services

cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\web\frontend
.\install_test_deps.bat

node run_tests.js --unit-only

# Expected output should show all service tests passing


# First, run the updated installation script to get all required dependencies:

bashcd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\web\frontend
.\install_test_deps.bat

# Try running the simplified test script that uses the built-in React testing infrastructure:

.\run_react_tests.bat

# If that still doesn't work, we can try a more direct approach:

npx react-scripts test --testMatch="**/simple.test.js" --watchAll=false
```

### 3. Run Component Tests

```bash
# Test React components
node run_tests.js --component-only

# Expected output should show all component tests passing
```

### 4. Run Frontend Tests with Coverage

```bash
# Run all frontend tests with coverage reporting
node run_tests.js --all --coverage

# Review the coverage report in the terminal output

# You can now run the WebSocket tests using either:

node run_tests.js --unit-only 
.\run_simple_tests.bat 

```

## End-to-End Testing

### 1. Start Backend for E2E Tests

```bash
# Navigate to the backend directory
cd genai_agent_project/web/backend

# Start the server
python run_server.py

# Alternatively --- To use these scripts, you can simply run:

# On Windows
.\start_server.bat

# On Linux/Mac
./start_server.sh
If you want to use a different port:
# On Windows
start_server.bat --port 8080

# On Linux/Mac
./start_server.sh --port 8080

python run_server.py --auto-port
```

### 2. Run E2E Tests

```bash


# If necessary, Run the fix_dependencies script
cd genai_agent_project/web/e2e
.\fix_dependencies.bat

# Then you can run the tests with:
.\run_tests.bat

# ----

# EXTRA Setup

Fix for Playwright Test Issues in GenAI Agent 3D
I've identified the problem in your end-to-end (E2E) testing setup. The error message shows that the @playwright/test module is missing, which is required for running the Playwright tests.
Step-by-Step Solution

Install Playwright properly in your e2e directory:
powershell# Navigate to the e2e directory
cd C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\web\e2e

# Make sure you have a package.json file
npm init -y

# Install Playwright as a dev dependency
npm install --save-dev @playwright/test

# Install Playwright browsers
npx playwright install

Verify the installation:
After installing the package, try running the tests again:
powershellnpx playwright test
Or with the UI:
powershellnpx playwright test --ui

Run specific tests if needed:
powershellnpx playwright test workflow.spec.js


What Happened?
This error occurred because:

The Playwright tests are configured to use the @playwright/test package
This package wasn't properly installed in your project
When you run npx playwright test, it tries to use Playwright from a temporary cache, but the test configuration files are looking for a local installation

Updates to Testing Process
For future reference, here's how the E2E testing section of your testing guide should be updated:
End-to-End Testing
1. Start Backend for E2E Tests
bash# Navigate to the backend directory
cd genai_agent_project/web/backend

# Start the server
python run_server.py
2. Install and Set Up Playwright
bash# In a separate terminal, navigate to the e2e directory
cd genai_agent_project/web/e2e

# Make sure package.json exists
npm init -y

# Install Playwright as a dev dependency
npm install --save-dev @playwright/test

# Install Playwright browsers
npx playwright install
3. Run E2E Tests
bash# In the e2e directory
cd genai_agent_project/web/e2e

# Run Playwright tests
npx playwright test

# Expected output should show all tests passing
4. Run E2E Tests with UI (Optional)
bash# For visual debugging, run with UI
npx playwright test --ui

# This will open a visual interface showing the tests
5. Run Specific E2E Workflow Tests
bash# Run just the workflow tests
npx playwright test workflow.spec.js

# These tests verify complete user journeys
Additional Tips

If you're working in a CI/CD environment, make sure to include the Playwright installation steps in your pipeline scripts.
After updating or reinstalling dependencies, you might need to reinstall Playwright.
If you encounter other module-not-found errors, check that all dependencies in your package.json are properly installed.

This fix should resolve your current issue with the Playwright tests and ensure that your end-to-end testing can proceed as expected.



# In a separate terminal, navigate to the e2e directory
cd genai_agent_project/web/e2e

# Run Playwright tests
npx playwright test

# Expected output should show all tests passing
```

### 3. Run E2E Tests with UI (Optional)

```bash
# For visual debugging, run with UI
npx playwright test --ui

# This will open a visual interface showing the tests
```

### 4. Run Specific E2E Workflow Tests

```bash
# Run just the workflow tests
npx playwright test workflow.spec.js

# These tests verify complete user journeys
```

## Complete System Testing

### 1. Run the Cleanup Script

```bash
# Ensure a clean environment
cd genai_agent_project
python cleanup.py
```

### 2. Run All Tests in Sequence

```bash
# Run the comprehensive test script
python run_cleanup_and_test.py

# This script:
# 1. Cleans up the project
# 2. Ensures Ollama server is running
# 3. Runs integration tests for the core system
```

### 3. Run Web Interface Tests

```bash
# Navigate to the web directory
cd genai_agent_project/web

# Run the master test script for web components
python run_all_tests.py --all --start-backend

# The script has been saved to: C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project\run_all_web_tests.py

cd ..
python run_all_web_tests.py --all --start-backend

# This will:
# 1. Start the backend server
# 2. Run all backend tests
# 3. Run all frontend tests
# 4. Run all e2e tests
# 5. Report comprehensive results


$  -----

# How to use the new script:
Run all tests:
python run_all_web_tests.py

#   Skip specific test types:
python run_all_web_tests.py --no-e2e  # Skip end-to-end tests
Specify a different port:
python run_all_web_tests.py --port 8080

#If you want to skip certain tests, you can still use:
python run_all_web_tests.py --no-backend
python run_all_web_tests.py --no-frontend
python run_all_web_tests.py --no-e2e
```

### 4. Run Improved Integration Tests

```bash
# Test the improved JSON generation and extraction
cd genai_agent_project
python run_improved_tests.py

# This verifies the robust LLM parsing and error handling
```

### 5. Run Manual Testing with Interactive Shell

```bash
# Start the interactive shell
python run.py shell

# Try these test commands:
# > Create a scene with a mountain, a forest, and a lake
# > Create a simple scene with a red cube on a blue plane
# > Generate a diagram showing the workflow of a user submitting content
```

### 6. Web Interface Manual Testing

```bash
# Start the backend server
cd genai_agent_project/web/backend
python run_server.py

# In a separate terminal, start the frontend
cd genai_agent_project/web/frontend
npm start

# Navigate to http://localhost:3000 in your browser
# Test the following functionality:
# 1. Dashboard status and overview
# 2. Instructions processing
# 3. Model generation with 3D preview
# 4. Scene creation and editing
# 5. Diagram generation with preview
# 6. Settings configuration
```

## Troubleshooting

### Ollama Issues

```bash
# Check Ollama status
ollama ps

# Restart Ollama service
python run.py ollama restart

# Check available models
python run.py ollama list

# Pull a specific model again if needed
python run.py ollama pull deepseek-coder
```

### Redis Issues

```bash
# Check Redis connection
redis-cli ping

# Restart Redis service
# On Linux:
sudo systemctl restart redis
# On Mac with Homebrew:
brew services restart redis
# On Windows:
net stop Redis
net start Redis
```

### Blender Issues

```bash
# Test Blender directly
blender --python genai_agent_project/examples/simple_blender_test.py

# Verify Blender path in config.yaml
# Make sure to use forward slashes even on Windows: C:/Program Files/Blender Foundation/Blender 4.0/blender.exe
```

### Web Backend Issues

```bash
# Check for available ports
netstat -ano | findstr :8000   # Windows
lsof -i :8000                  # Linux/Mac

# Run server with verbose logging
cd genai_agent_project/web/backend
python run_server.py --debug
```

### Web Frontend Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules
npm install

# Check for TypeScript errors
npm run tsc
```

### Common Test Failures

1. **Backend API Tests**:

   - Ensure Redis is running
   - Verify port 8000 is not in use by another application
   - Check for correct Python dependencies
2. **WebSocket Tests**:

   - These are often timing-sensitive; try increasing timeout values
3. **Frontend Tests**:

   - Jest might need a clean cache: `npx jest --clearCache`
   - Ensure all required npm modules are installed
4. **E2E Tests**:

   - Ensure Playwright is installed: `npx playwright install`
   - Backend server must be running
   - Consider running tests one at a time if encountering race conditions

---

## Quick Reference Commands

### Basic System Testing

```bash
# Core system test
python run.py check

# Improved tests with cleanup
python run_cleanup_and_test.py

# Run with specific model
OLLAMA_MODEL=llama3 python run_improved_tests.py
```

### Web Testing

```bash
# Backend tests only
cd genai_agent_project/web/backend
python run_tests.py --all

# WebSocket tests only
cd genai_agent_project/web/backend
python run_tests.py --websocket

# Manual WebSocket testing
cd genai_agent_project
./run_websocket_test.bat  # Windows
# OR
./run_websocket_test.sh   # Linux/macOS

# Frontend tests only
cd genai_agent_project/web/frontend
node run_tests.js --all

# E2E tests only
cd genai_agent_project/web/e2e
npx playwright test

# All web tests together
cd genai_agent_project/web
python run_all_tests.py --all --start-backend
```

### Running the Application

```bash
# Start the interactive shell
python run.py shell

# Start the web backend
cd genai_agent_project/web/backend
python run_server.py

# Start the web frontend
cd genai_agent_project/web/frontend
npm start
```

This guide provides a comprehensive approach to setting up and testing the GenAI Agent 3D project. By following these steps, you can verify the integrity of the system from the ground up.
