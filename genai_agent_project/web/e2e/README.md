# End-to-End (E2E) Tests for GenAI Agent 3D

This directory contains end-to-end tests for the GenAI Agent 3D web interface using Playwright.

## Setting Up the Tests

1. Install dependencies:

```bash
# Run fix_dependencies script
# On Windows
.\fix_dependencies.bat

# On Linux/macOS
./fix_dependencies.sh
```

The script will:
- Clean npm cache
- Remove existing node_modules and package-lock.json
- Install all dependencies
- Install Playwright browsers

## Running the Tests

### Running All Tests

```bash
npm test
```

### Running Tests with UI

```bash
npm run test:ui
```

### Running Tests in Headed Mode

```bash
npm run test:headed
```

### Viewing Test Reports

```bash
npm run report
```

## Test Structure

- `tests/` - Contains all test files
- `setup/` - Contains global setup and teardown scripts
- `playwright.config.js` - Playwright configuration
- `.env` - Environment variables for tests

## Troubleshooting

If you encounter issues with Playwright, try:

1. Reinstalling dependencies:
   ```bash
   npm cache clean --force
   rm -rf node_modules
   npm install
   npx playwright install
   ```

2. Check that both frontend and backend servers are running:
   ```bash
   # Start backend server (in backend directory)
   cd ../backend
   python start_server.py
   
   # Start frontend server (in frontend directory)
   cd ../frontend
   npm start
   ```

3. Verify the BASE_URL in .env matches your frontend server address

## Adding New Tests

Add new test files in the `tests/` directory with the `.spec.js` extension.
