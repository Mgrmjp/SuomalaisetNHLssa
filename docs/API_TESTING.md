# API Testing Documentation

This document provides comprehensive information about the API testing suite for the Finnish NHL Player Tracker application.

## Overview

The API testing suite ensures that all API endpoints function correctly, handle errors gracefully, and maintain data integrity. The tests cover:

- **Finnish Players API** (`/api/finnish-players`)
- **Scores API** (`/api/scores`)
- **Static Data Serving** (`/data/{date}.json`)
- **Data Validation** and error handling

## Test Structure

```
src/lib/tests/
├── apiTestUtils.js          # Shared utilities and mocks
├── apiSetup.js              # API test environment setup
├── api/
│   └── finnish-players.test.js  # Finnish players API tests
├── scores.test.js            # Scores API tests
├── static-data.test.js       # Static data serving tests
└── data-validation.test.js   # Data validation tests
```

## Running Tests

### Quick Start

```bash
# Run all API tests
npm run test:api

# Or use the custom test runner
node scripts/run-api-tests.js

# Run with coverage
node scripts/run-api-tests.js --coverage

# Run in watch mode
node scripts/run-api-tests.js --watch
```

### Individual Test Categories

```bash
# Run specific test categories
node scripts/run-api-tests.js --category=finnish-players
node scripts/run-api-tests.js --category=scores
node scripts/run-api-tests.js --category=static-data
node scripts/run-api-tests.js --category=validation
```

### Using Vitest Directly

```bash
# Run with custom config
npx vitest run --config vitest.api.config.js

# Run specific test file
npx vitest run src/lib/tests/api/finnish-players.test.js

# Run with coverage
npx vitest run --coverage --config vitest.api.config.js
```

## Test Categories

### 1. Finnish Players API Tests (`/api/finnish-players`)

**Purpose**: Test the endpoint that returns Finnish NHL players data.

**Test Coverage**:
- ✅ Successful data retrieval
- ✅ Different format parameters (`full`, `simple`, `names`)
- ✅ Empty player lists
- ✅ API error handling
- ✅ Malformed API responses
- ✅ Network errors and timeouts
- ✅ Rate limiting
- ✅ Concurrent request handling
- ✅ Response time validation
- ✅ Data structure validation
- ✅ Finnish player filtering
- ✅ Large dataset performance

**Key Test Cases**:
```javascript
// Test successful retrieval
GET /api/finnish-players → 200 + Finnish players array

// Test different formats
GET /api/finnish-players?format=simple → 200 + simplified data
GET /api/finnish-players?format=names → 200 + player names array

// Test error handling
API failure → 500 + error message
```

### 2. Scores API Tests (`/api/scores`)

**Purpose**: Test the endpoint that retrieves NHL game scores.

**Test Coverage**:
- ✅ Valid date range requests
- ✅ Date format validation
- ✅ Required parameter validation
- ✅ Maximum date range enforcement (7 days)
- ✅ Single date requests
- ✅ Empty response handling
- ✅ Metadata accuracy
- ✅ Network error handling
- ✅ API rate limiting
- ✅ Retry logic (rate limits, network errors)
- ✅ Performance benchmarks
- ✅ Concurrent request handling
- ✅ Edge cases (leap years, year boundaries)
- ✅ Integration scenarios

**Key Test Cases**:
```javascript
// Valid request
GET /api/scores?startDate=2025-10-24&endDate=2025-10-25 → 200 + scores + metadata

// Validation failures
GET /api/scores?startDate=invalid → 400 + validation error
GET /api/scores?startDate=2025-10-01&endDate=2025-10-15 → 400 + range error

// Rate limiting
429 response → retry up to 3 times
```

### 3. Static Data Serving Tests

**Purpose**: Test the serving of static JSON data files.

**Test Coverage**:
- ✅ Directory structure validation
- ✅ Data consistency between directories
- ✅ JSON file format validation
- ✅ File reading operations
- ✅ Non-existent file handling
- ✅ Corrupted JSON handling
- ✅ Date format validation in filenames
- ✅ Performance benchmarks
- ✅ Concurrent file access
- ✅ Data integrity checks
- ✅ Permission error handling
- ✅ Empty data files

**Key Test Cases**:
```javascript
// File validation
/static/data/2025-10-25.json exists + valid JSON
/data/games/2025-10-25.json matches static version

// Error handling
Non-existent file → graceful error handling
Corrupted JSON → error detection
```

### 4. Data Validation Tests

**Purpose**: Comprehensive validation of data structures and business logic.

**Test Coverage**:
- ✅ Date validation functions
- ✅ Player data structure validation
- ✅ Field type validation
- ✅ Business logic validation (points calculation, etc.)
- ✅ Finnish player identification
- ✅ Data consistency checks
- ✅ Edge cases and boundary conditions
- ✅ Performance with large datasets
- ✅ Data transformation validation

**Key Test Cases**:
```javascript
// Date validation
isValidDateFormat('2025-10-25') → true
isValidDateFormat('invalid-date') → false

// Player validation
Required fields present + correct types + business logic
```

## Test Utilities

### Mock Data

The test suite includes comprehensive mock data:

```javascript
// Mock Finnish players
mockFinnishPlayers = [
  {
    name: 'Artturi Lehkonen',
    position: 'L',
    team: 'COL',
    nationality: 'FIN'
  }
  // ... more players
]

// Mock game scores
mockGameScores = [
  {
    game_id: 789012,
    date: '2025-10-25',
    homeTeam: { ... },
    awayTeam: { ... }
  }
  // ... more games
]
```

### Helper Functions

Key utility functions for testing:

```javascript
// Create mock fetch responses
createMockResponse(data, options)

// Create error responses
createMockErrorResponse(message, status)

// Measure execution time
measureTime(asyncFunction)

// Validate data structures
validatePlayer(playerData)
validateGameScore(gameData)
```

### Mock Configuration

- **Global fetch**: Mocked for all API calls
- **Node.js modules**: Mocked for file system and process operations
- **Console methods**: Mocked for clean test output
- **Environment**: Test environment configuration

## Configuration Files

### vitest.api.config.js

Specialized configuration for API tests:
- Node environment
- API-specific include patterns
- Extended timeout values
- Coverage configuration
- Custom reporters

### apiSetup.js

Global setup for API tests:
- Mock implementations
- Test utilities
- Environment configuration
- Error simulation helpers

## Coverage Requirements

The test suite maintains high code coverage:

- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

Coverage reports are generated in:
- Console output
- JSON format
- HTML report (detailed)

## Performance Benchmarks

### Response Time Requirements

- **API endpoints**: < 3 seconds
- **Static file reads**: < 100ms
- **Large datasets (100+ items)**: < 2 seconds
- **Concurrent requests**: < 5 seconds total

### Memory Usage

- **Single test suite**: < 50MB peak memory
- **All tests combined**: < 200MB peak memory

## Error Handling Tests

### Network Errors

```javascript
// Simulated network failures
mockNetworkError → 500 + error message

// Timeouts
mockTimeoutError → 500 + error message
```

### API Errors

```javascript
// Rate limiting
429 response → retry logic + eventual failure

// Server errors
5xx response → 500 + error message

// Invalid responses
Malformed JSON → 500 + error message
```

## Continuous Integration

### GitHub Actions (if configured)

```yaml
- name: Run API Tests
  run: |
    npm run test:api
    npm run test:coverage
```

### Pre-commit Hooks

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "npm run test:api"
    }
  }
}
```

## Best Practices

### Test Organization

1. **Descriptive test names**: Clearly indicate what is being tested
2. **Arrange-Act-Assert pattern**: Structure tests consistently
3. **Isolation**: Tests should not depend on each other
4. **Cleanup**: Properly clean up after each test

### Mock Management

1. **Consistent mocks**: Use the same mock data across tests
2. **Reset mocks**: Clean up mocks between tests
3. **Realistic data**: Mock data should resemble real API responses

### Error Testing

1. **Happy path**: Test normal operation
2. **Error cases**: Test failure scenarios
3. **Edge cases**: Test boundary conditions
4. **Performance**: Test with various data sizes

## Troubleshooting

### Common Issues

1. **Test timeouts**: Increase timeout values in config
2. **Mock failures**: Check mock implementation
3. **File not found**: Verify file paths and permissions
4. **Import errors**: Check module resolution

### Debug Mode

```bash
# Run with verbose output
DEBUG=* node scripts/run-api-tests.js

# Run specific test with debugging
npx vitest run src/lib/tests/api/finnish-players.test.js --no-coverage
```

## Contributing

When adding new API tests:

1. **Follow existing patterns**: Use established test structure
2. **Add utilities**: Reuse existing mock data and helpers
3. **Update documentation**: Keep this file current
4. **Maintain coverage**: Ensure new tests meet coverage requirements
5. **Test both success and failure**: Comprehensive error handling

### Test Template

```javascript
describe('New Feature API', () => {
  beforeEach(() => {
    // Setup
  })

  it('should handle successful request', async () => {
    // Test implementation
  })

  it('should handle errors gracefully', async () => {
    // Error handling test
  })
})
```

## References

- [Vitest Documentation](https://vitest.dev/)
- [SvelteKit Testing](https://kit.svelte.dev/docs/testing)
- [Node.js Testing Best Practices](https://github.com/goldbergyoni/nodebestpractices#-4-testing)
- [API Testing Guidelines](https://martinfowler.com/articles/integrationTestExample.html)