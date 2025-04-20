/**
 * Fix Frontend Paths for GenAI Agent 3D
 * This script updates frontend API URLs to work properly
 */

// Update the following URLs according to your setup
const API_URL = 'http://localhost:8000';
const WEBSOCKET_URL = 'ws://localhost:8000';

// Don't modify below this line
console.log('Fixing frontend API URLs for GenAI Agent 3D...');

const fs = require('fs');
const path = require('path');

// Define the expected path to the .env file
const envPath = path.join(__dirname, 'genai_agent_project', 'web', 'frontend', '.env');
const envLocalPath = path.join(__dirname, 'genai_agent_project', 'web', 'frontend', '.env.local');

function updateEnvFile(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      console.log(`Updating ${filePath}`);
      let content = fs.readFileSync(filePath, 'utf8');
      
      // Update/set API URL
      if (content.includes('REACT_APP_API_URL=')) {
        content = content.replace(/REACT_APP_API_URL=.*/g, `REACT_APP_API_URL=${API_URL}`);
      } else {
        content += `\nREACT_APP_API_URL=${API_URL}`;
      }
      
      // Update/set WebSocket URL
      if (content.includes('REACT_APP_WS_URL=')) {
        content = content.replace(/REACT_APP_WS_URL=.*/g, `REACT_APP_WS_URL=${WEBSOCKET_URL}`);
      } else {
        content += `\nREACT_APP_WS_URL=${WEBSOCKET_URL}`;
      }
      
      fs.writeFileSync(filePath, content);
      console.log(`✅ Successfully updated ${filePath}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error updating ${filePath}:`, error);
    return false;
  }
}

// Try to update .env file
let updated = updateEnvFile(envPath);

// If .env doesn't exist, try .env.local
if (!updated) {
  updated = updateEnvFile(envLocalPath);
}

// If neither exists, create .env
if (!updated) {
  try {
    const parentDir = path.dirname(envPath);
    if (!fs.existsSync(parentDir)) {
      console.log(`Creating directory: ${parentDir}`);
      fs.mkdirSync(parentDir, { recursive: true });
    }
    
    const content = `REACT_APP_API_URL=${API_URL}\nREACT_APP_WS_URL=${WEBSOCKET_URL}`;
    fs.writeFileSync(envPath, content);
    console.log(`✅ Created new .env file at ${envPath}`);
  } catch (error) {
    console.error('Error creating .env file:', error);
  }
}

console.log('\nFrontend URLs have been fixed. Please restart your frontend server.');
