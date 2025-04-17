/**
 * Global teardown for Playwright end-to-end tests
 * This script stops the backend server after testing
 */

const path = require('path');
const fs = require('fs');

/**
 * Stop the backend server
 */
function stopBackendServer() {
  const pidFile = path.join(__dirname, 'server.pid');
  
  // Check if pid file exists
  if (!fs.existsSync(pidFile)) {
    console.log('⚠️ No server.pid file found, server might not be running');
    return;
  }
  
  try {
    // Read server PID
    const pid = parseInt(fs.readFileSync(pidFile, 'utf8'), 10);
    
    if (isNaN(pid)) {
      console.error('❌ Invalid PID in server.pid file');
      return;
    }
    
    console.log(`🛑 Stopping backend server (PID: ${pid})`);
    
    // Try to kill the process
    if (process.platform === 'win32') {
      // On Windows
      require('child_process').execSync(`taskkill /PID ${pid} /T /F`);
    } else {
      // On Unix-like systems
      process.kill(pid, 'SIGTERM');
    }
    
    console.log('✅ Backend server stopped');
  } catch (error) {
    console.error(`❌ Error stopping backend server: ${error.message}`);
  } finally {
    // Remove pid file
    try {
      fs.unlinkSync(pidFile);
    } catch (error) {
      // Ignore errors on file deletion
    }
  }
}

/**
 * Global teardown function
 */
module.exports = async function globalTeardown() {
  // Stop backend server
  stopBackendServer();
  
  console.log('✅ Global teardown complete');
};
