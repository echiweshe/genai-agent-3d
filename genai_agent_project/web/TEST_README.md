# GenAI Agent 3D Web Testing Guide

This document provides information about the testing infrastructure for the GenAI Agent 3D web application.

## Testing Structure

The testing infrastructure is organized into three main categories:

1. **Backend Tests**: Tests for the FastAPI backend endpoints and WebSocket functionality.
2. **Frontend Tests**: Unit and component tests for the React frontend.
3. **End-to-End Tests**: Integration tests that verify the complete application workflow.

## Backend Tests

Backend tests are written using `pytest` and are located in the `web/backend/tests` directory.

### Running Backend Tests

To run backend tests, use the provided script:

```bash..
cd web/backend
python run_tests.py
```

Options:

- `--unit`: Run unit tests only
- `--extended`: Run extended tests only
- `--all`: Run all tests (default)
- `--port PORT`: Port to use for the backend server during tests (default: 8000)

### Backend Test Categories

1. **Unit Tests**: Basic tests for API endpoints and WebSocket functionality.

   - `test_api_endpoints.py`: Tests for basic API endpoints
   - `test_websocket.py`: Tests for basic WebSocket functionality
2. **Extended Tests**: More comprehensive tests for advanced functionality.

   - `test_extended_api.py`: Advanced API endpoint tests including scenes, models, and diagrams
   - `test_extended_websocket.py`: Comprehensive WebSocket tests including connection handling and real-time updates

## Frontend Tests

Frontend tests are written using Jest and React Testing Library and are located in the `web/frontend/src/__tests__` directory.

### Running Frontend Tests

To run frontend tests, use the provided script:

```bash
cd web/frontend
node run_tests.js
```

Options:

- `--unit-only`: Run service and utility tests only
- `--component-only`: Run component tests only
- `--e2e-only`: Run end-to-end tests from the frontend (requires backend to be running)
- `--all`: Run all tests
- `--watch`: Run tests in watch mode
- `--no-coverage`: Skip coverage generation
- `--lint`: Run ESLint checks
- `--start-backend`: Start the backend server for E2E tests (with `--e2e-only`)
- `--continue-on-error`: Continue running tests even if some fail

### Frontend Test Categories

1. **Service Tests**: Tests for API and WebSocket services.

   - `services/api.test.js`: Tests for the API service
   - `services/websocket.test.js`: Tests for the WebSocket service
2. **Component Tests**: Tests for React components.

   - `components/AppHeader.test.js`: Tests for the app header
   - `components/AppSidebar.test.js`: Tests for the sidebar navigation
   - `components/pages/*.test.js`: Tests for page components

## End-to-End Tests

End-to-end tests are written using Playwright and are located in the `web/e2e/tests` directory.

### Running E2E Tests

To run E2E tests, use the following:

```bash
cd web/e2e
npx playwright test
```

For UI mode:

```bash
npx playwright test --ui
```

### E2E Test Files

- `navigation.spec.js`: Tests for application navigation
- `instructions.spec.js`: Tests for the instruction processing workflow
- `tools.spec.js`: Tests for tool execution
- `workflow.spec.js`: Tests for complete application workflows

## Running All Tests

To run all tests in one go, use the master script:

```bash
cd web
python run_all_tests.py
```

Options:

- `--backend`: Run backend tests only
- `--frontend`: Run frontend tests only
- `--e2e`: Run E2E tests only
- `--unit-only`: Run backend unit tests only
- `--extended-only`: Run backend extended tests only
- `--component-only`: Run frontend component tests only
- `--coverage`: Generate coverage reports
- `--watch`: Run tests in watch mode
- `--start-backend`: Start backend server for E2E tests
- `--ui`: Run E2E tests with Playwright UI
- `--debug`: Run E2E tests in debug mode
- `--port PORT`: Port for backend server (default: 8000)

## Continuous Integration

The tests are set up to run in a CI/CD pipeline. The pipeline will:

1. Run backend unit and extended tests
2. Run frontend unit and component tests
3. Generate coverage reports
4. Run end-to-end tests
5. Fail the build if any tests fail

## Best Practices

When writing tests, follow these best practices:

### Backend Tests

- Use fixtures for common setup
- Mock external dependencies
- Test both success and error scenarios
- Test WebSocket connections and disconnections

### Frontend Tests

- Mock API and WebSocket services
- Test component rendering and interactions
- Test form validation and submissions
- Test error handling

### E2E Tests

- Test complete user workflows
- Verify visual elements and interactions
- Test responsive behavior
- Test cross-browser compatibility (using Playwright's multi-browser capabilities)
