// @ts-check
const { defineConfig, devices } = require('@playwright/test');
require('dotenv').config();

/**
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: false, // Don't run tests in parallel
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1, // Retry once for greater stability
  workers: 1, // Only use 1 worker to avoid overloading the system
  reporter: 'html',

  // Global setup for web server
  globalSetup: require.resolve('./setup/global-setup'),
  globalTeardown: require.resolve('./setup/global-teardown'),

  use: {
    // Base URL to use in navigation
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // Browser trace on failure
    trace: 'on-first-retry',

    // Take screenshots on failure
    screenshot: 'only-on-failure',

    // Record video on failure
    video: 'on-first-retry',
  },

  // Increase timeout for tests since we need to wait for servers
  timeout: 120000, // 2 minutes

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },

    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Comment out webServer to use our own server management
  // webServer: {
  //   command: 'cd ../frontend && npm run start',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120 * 1000,
  // },
});
