/**
 * Global teardown for Playwright tests
 */

async function globalTeardown() {
  console.log('Running global teardown...');
  
  // Clean up any resources created during setup
  // For example:
  // - Close database connections
  // - Remove temporary files
  // - Clear any test data
  
  console.log('Global teardown complete');
}

module.exports = globalTeardown;
