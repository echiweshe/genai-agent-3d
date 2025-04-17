/**
 * Global setup for Playwright end-to-end tests
 * This script starts the backend server for testing
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// We'll use the simpler http library to check if the server is ready
const http = require('http');

/**
 * Check if the server is up and running
 * @param {string} url The URL to check
 * @param {number} timeout Timeout in milliseconds
 * @returns {Promise<boolean>} True if server is running
 */
function waitForServer(url, timeout = 60000) {
  const startTime = Date.now();
  
  return new Promise((resolve) => {
    const checkServer = () => {
      const [hostname, port] = url.replace(/^https?:\/\//, '').split(':');
      
      const options = {
        hostname,
        port: port || 80,
        path: '/status', // Use the status endpoint
        method: 'GET',
        timeout: 1000,
      };
      
      const req = http.request(options, (res) => {
        if (res.statusCode === 200) {
          console.log(`✅ Backend server is ready on ${url}`);
          resolve(true);
        } else {
          retry();
        }
      });
      
      req.on('error', () => {
        retry();
      });
      
      req.end();
      
      function retry() {
        // Check timeout
        if (Date.now() - startTime > timeout) {
          console.log(`❌ Timed out waiting for backend server at ${url}`);
          resolve(false);
          return;
        }
        
        // Retry after a short delay
        setTimeout(checkServer, 1000);
      }
    };
    
    checkServer();
  });
}

/**
 * Start the backend server
 * @returns {Promise<import('child_process').ChildProcess|null>} Server process or null
 */
async function startBackendServer() {
  const backendDir = path.resolve(__dirname, '../../backend');
  const serverScript = path.join(backendDir, 'run_server.py');
  
  if (!fs.existsSync(serverScript)) {
    console.error(`❌ Server script not found at ${serverScript}`);
    return null;
  }
  
  console.log(`🚀 Starting backend server from ${serverScript}`);
  
  // Python executable
  const pythonExe = process.platform === 'win32' ? 'python' : 'python3';
  
  // Start the server
  const serverProcess = spawn(pythonExe, [serverScript, '--host', '127.0.0.1', '--port', '8000'], {
    cwd: backendDir,
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: true, // Allow the process to run independently of its parent
  });
  
  // Log output
  serverProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data.toString().trim()}`);
  });
  
  serverProcess.stderr.on('data', (data) => {
    console.error(`Backend (error): ${data.toString().trim()}`);
  });
  
  serverProcess.on('error', (error) => {
    console.error(`❌ Failed to start backend server: ${error.message}`);
    return null;
  });
  
  // Store the pid for clean shutdown
  fs.writeFileSync(path.join(__dirname, 'server.pid'), serverProcess.pid.toString());
  
  // Wait for the server to be ready
  const isReady = await waitForServer('http://127.0.0.1:8000');
  
  if (!isReady) {
    console.error('❌ Backend server failed to start properly');
    if (serverProcess && !serverProcess.killed) {
      serverProcess.kill();
    }
    return null;
  }
  
  return serverProcess;
}

/**
 * Global setup function
 */
module.exports = async function globalSetup() {
  // Start backend server
  const serverProcess = await startBackendServer();
  
  if (!serverProcess) {
    throw new Error('Failed to start backend server for end-to-end tests');
  }
  
  console.log('✅ Global setup complete');
};
