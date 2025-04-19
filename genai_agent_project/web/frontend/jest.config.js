/**
 * Jest configuration file
 */

module.exports = {
  // Set test environment to jsdom for browser-like environment
  testEnvironment: 'jsdom',
  
  // The testEnvironmentOptions are needed to avoid the error
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  },
  
  // Use setup files to configure Jest environment
  setupFiles: [
    '<rootDir>/src/setupTests.js'
  ],
  
  // Execute after setup files
  setupFilesAfterEnv: [
    '@testing-library/jest-dom'
  ],
  
  // Folder where tests are located
  testMatch: [
    '<rootDir>/src/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}'
  ],
  
  // Configure coverage
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js',
    '!src/reportWebVitals.js',
    '!src/setupTests.js',
  ],
  
  // Transform modules
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  
  // Module name mapper for non-JS modules
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': '<rootDir>/src/__mocks__/styleMock.js',
    '\\.(gif|ttf|eot|svg|png)$': '<rootDir>/src/__mocks__/fileMock.js',
  },
  
  // Transform patterns
  transformIgnorePatterns: [
    '/node_modules/(?!.*\\.mjs$)',
  ],
  
  // Mocks, if needed
  // moduleNameMapper: {},
};
