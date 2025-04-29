# Troubleshooting Guide for SVG to Video Pipeline

This document provides solutions for common issues encountered when setting up and running the SVG to Video Pipeline.

## Setup Issues

### Virtual Environment Creation Fails

**Problem**: The `setup_svg_to_video.bat` script fails when creating the virtual environment.

**Solution**:
1. Make sure Python 3.9+ is installed and in your PATH
2. Try creating the virtual environment manually:
   ```
   python -m venv venv
   ```
3. If that fails, try installing the virtualenv package:
   ```
   pip install virtualenv
   virtualenv venv
   ```

### Dependency Installation Fails

**Problem**: The installation of dependencies fails with error messages.

**Solution**:
1. Make sure you have an internet connection
2. Try upgrading pip:
   ```
   venv\Scripts\activate
   pip install --upgrade pip
   ```
3. Install dependencies one by one to identify the problematic package:
   ```
   pip install fastapi uvicorn python-multipart langchain
   ```

## Runtime Issues

### ImportError: cannot import name 'ChatOllama' from 'langchain.chat_models'

**Problem**: The backend server fails to start with this error.

**Solution**:
1. This error occurs because the installed version of LangChain doesn't include ChatOllama
2. Use the simplified server which handles this case gracefully:
   ```
   run_simple_dev.bat
   ```
3. Alternatively, test just the SVG generator without the full pipeline:
   ```
   run_svg_generator_test.bat
   ```

### No LLM Providers Available

**Problem**: When running the application, it shows "No LLM providers available".

**Solution**:
1. Make sure you've added your API keys to the `.env` file
2. At least one of the following should be uncommented and have a valid API key:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```
3. Verify the API keys are correct and not expired
4. Try testing the API keys with the specific provider's tools

### Proxy error: Could not proxy request from localhost:3000 to http://localhost:8000/

**Problem**: The frontend is running but can't connect to the backend.

**Solution**:
1. Make sure the backend server is running
2. Check if there are any error messages in the backend server window
3. Try running the backend server separately:
   ```
   call venv\Scripts\activate
   cd web\backend
   python simple_server.py
   ```
4. If the backend is having issues, use the troubleshooting tips above

## API Key Issues

### Claude API Not Working

**Problem**: You've added your Claude API key but get authentication errors.

**Solution**:
1. Make sure your API key is correct
2. Check if your API key is still active
3. The API key should be in the format `sk-ant-apiXXX-...`
4. Try testing the key using the Anthropic documentation

### OpenAI API Not Working

**Problem**: You've added your OpenAI API key but get authentication errors.

**Solution**:
1. Verify your API key is correct
2. Check if your account has credit available
3. Make sure your API key has permissions for the models being used
4. Try testing the key using the OpenAI playground

## Blender Issues

### Blender Not Found

**Problem**: The system can't find or run Blender.

**Solution**:
1. Make sure Blender is installed
2. Add Blender to your system PATH, or
3. Add the full path to Blender in your `.env` file:
   ```
   BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 3.3\blender.exe
   ```

### Blender Script Errors

**Problem**: Blender fails when running the conversion scripts.

**Solution**:
1. Make sure you're using Blender 3.0 or newer
2. Try running Blender manually to ensure it works
3. Check that there are no issues with your GPU drivers
4. If problems persist, try falling back to CPU rendering:
   ```
   BLENDER_USE_GPU=0
   ```

## Other Issues

### Web Frontend Not Building

**Problem**: The frontend fails to build with Node.js errors.

**Solution**:
1. Make sure you have Node.js 14 or newer installed
2. Try clearing the npm cache:
   ```
   npm cache clean --force
   ```
3. Try reinstalling the dependencies:
   ```
   cd web\frontend
   rm -rf node_modules
   npm install
   ```

### Backend Server Not Starting

**Problem**: The backend server doesn't start or crashes immediately.

**Solution**:
1. Make sure all dependencies are installed
2. Try the simplified server with `run_simple_dev.bat`
3. Check for port conflicts - something else might be using port 8000
4. Look for error messages in the console output

If you encounter an issue not covered in this document, please check the log files for more detailed error messages.
