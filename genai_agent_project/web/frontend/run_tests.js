/**
 * Script to run frontend tests
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const config = {
  unitTests: true,
  componentTests: true,
  e2eTests: false, // Set to true to include e2e tests
  generateCoverage: true,
  watchMode: false
};

// Parse command line arguments
const args = process.argv.slice(2);
if (args.includes('--unit-only')) {
  config.componentTests = false;
  config.e2eTests = false;
}
if (args.includes('--component-only')) {
  config.unitTests = false;
  config.e2eTests = false;
}
if (args.includes('--e2e-only')) {
  config.unitTests = false;
  config.componentTests = false;
  config.e2eTests = true;
}
if (args.includes('--all')) {
  config.unitTests = true;
  config.componentTests = true;
  config.e2eTests = true;
}
if (args.includes('--watch')) {
  config.watchMode = true;
  config.generateCoverage = false;
}
if (args.includes('--no-coverage')) {
  config.generateCoverage = false;
}

/**
 * Run a command and log the output
 * @param {string} command - Command to run
 * @param {string} title - Title for logging
 */
function runCommand(command, title) {
  console.log(`\n=== Running ${title} ===\n`);
  try {
    execSync(command, { stdio: 'inherit' });
    console.log(`\n✅ ${title} completed successfully\n`);
    return true;
  } catch (error) {
    console.error(`\n❌ ${title} failed\n`);
    if (!args.includes('--continue-on-error')) {
      process.exit(1);
    }
    return false;
  }
}

/**
 * Build the test command based on configuration
 * @returns {string} Jest command
 */
function buildTestCommand() {
  let command = 'npx jest';
  
  // Test patterns
  const testPatterns = [];
  if (config.unitTests) {
    testPatterns.push('--testPathPattern=src/__tests__/(?!components)');
  }
  if (config.componentTests) {
    testPatterns.push('--testPathPattern=src/__tests__/components');
  }
  
  if (testPatterns.length > 0) {
    command += ` ${testPatterns.join(' ')}`;
  }
  
  // Options
  if (config.watchMode) {
    command += ' --watch';
  }
  if (config.generateCoverage) {
    command += ' --coverage';
  }
  
  return command;
}

/**
 * Main function to run tests
 */
function runTests() {
  console.log('=== Frontend Test Runner ===');
  console.log('Configuration:');
  console.log(JSON.stringify(config, null, 2));
  
  let allPassed = true;
  
  // Run ESLint
  if (args.includes('--lint') || args.includes('--all')) {
    allPassed = runCommand('npx eslint src', 'ESLint') && allPassed;
  }
  
  // Run unit and component tests
  if (config.unitTests || config.componentTests) {
    const command = buildTestCommand();
    allPassed = runCommand(command, 'Jest Tests') && allPassed;
  }
  
  // Run E2E tests if enabled
  if (config.e2eTests) {
    // Check if we need to start the backend server
    if (args.includes('--start-backend')) {
      console.log('\n=== Starting Backend Server for E2E Tests ===\n');
      
      const backendProcess = require('child_process').spawn(
        'python',
        ['../backend/run_server.py'],
        { stdio: 'pipe' }
      );
      
      // Give the backend server time to start
      console.log('Waiting for backend server to start...');
      execSync('sleep 5');
      
      try {
        // Run the E2E tests
        allPassed = runCommand('cd ../e2e && npx playwright test', 'E2E Tests') && allPassed;
      } finally {
        // Ensure we kill the backend server
        console.log('Stopping backend server...');
        backendProcess.kill();
      }
    } else {
      // Run E2E tests without starting the backend
      allPassed = runCommand('cd ../e2e && npx playwright test', 'E2E Tests') && allPassed;
    }
  }
  
  // Report results
  if (allPassed) {
    console.log('\n✅ All tests passed successfully!\n');
    process.exit(0);
  } else {
    console.error('\n❌ Some tests failed. See above for details.\n');
    process.exit(1);
  }
}

// Run the tests
runTests();
