/**
 * Simple test runner for Jest tests
 */
const { execSync } = require('child_process');

console.log('=== Running Jest Tests ===');

try {
  execSync('npx react-scripts test --watchAll=false', { stdio: 'inherit' });
  console.log('✅ All tests passed!');
  process.exit(0);
} catch (error) {
  console.error('❌ Tests failed with code:', error.status);
  process.exit(1);
}
