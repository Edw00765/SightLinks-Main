# Sightlink API Test Suite

This test suite verifies the functionality of the Sightlink API endpoints using automated tests with real data.

## Prerequisites

- Node.js environment
- npm (Node Package Manager)
- Access to the Sightlink API (base URL: https://sightlinks.org/api)
- Test data files in the correct location:
  - `data-and-images/digimap-data/small-dataset.zip`


## Test Structure

### API Tests

1. **Predict Endpoint Tests** (`api-predict.test.js`)
   - Tests the `/predict` endpoint
   - Verifies file processing with default parameters
   - Tests custom parameter handling
   - Includes error handling for invalid requests

2. **Web Status Tests** (`web-status.test.js`)
   - Tests the `/web/status/{task_id}` endpoint
   - Verifies task status retrieval
   - Validates response format and fields

3. **Server Status Tests** (`server-status.test.js`)
   - Tests server health and configuration
   - Verifies available models and directories
   - Monitors system resource usage

## Running the Tests

1. Install dependencies:
```bash
npm install
```

2. Run all tests serially (recommended):
```bash
npm run test:serial
```

3. Run specific test files:
```bash
npm run test:api-predict    # Run predict endpoint tests
npm run test:web-status     # Run web status tests
npm run test:server-status  # Run server status tests
```

## Test Data Requirements

### Small Dataset
- Location: `data-and-images/digimap-data/small-dataset.zip`
- Used for testing the processing workflow
- Ensure the dataset is properly formatted and contains valid images

## Error Handling

The test suite includes robust error handling:
- Automatic retries for transient server errors
- Exponential backoff between retry attempts
- Detailed logging of server responses
- Specific handling for server restart scenarios

## Expected API Responses

### Predict Endpoint
- POST `/predict`
  - Success: 200 with `{ status: 'success', message: 'Processing completed', output_path: string }`
  - Error: 400 for invalid requests, 500 for server errors

### Web Status Endpoint
- GET `/web/status/{task_id}`
  - Returns processing status and progress information
  - Includes error details if processing failed

### Server Status
- GET `/api/test`
  - Returns server configuration and health metrics
  - Includes model availability and system resource usage

## Development

### Git Configuration
The repository includes a `.gitignore` file that excludes:
- `node_modules/` directory
- `package-lock.json`

This ensures that only essential code is tracked in version control. 