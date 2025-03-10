# Sightlink API Test Suite

This test suite verifies the functionality of the Sightlink API endpoints using both basic API tests and functional tests with real data.

## Prerequisites

- Node.js environment
- npm (Node Package Manager)
- Access to the Sightlink API (base URL: http://api.sightlinks.org)
- Test data files in the correct location:
  - `tests/testInput/digimap-data/small-dataset.zip`
  - **NOTE**: Not uploading digimap test data to Github due to licensincing concerns. Install your own digimap dataset, rename it to "small-dataset", then place the zip in the listed directory above to add your own test data.

## Test Structure

### 1. API Tests (`api.test.js`)

Basic API endpoint tests that verify:
- Direct processing endpoint (`/predict`) accepts POST requests
- Web processing endpoint (`/web/predict`) accepts POST requests
- Status checking endpoint (`/web/status/{task_id}`) is accessible
- Download endpoint (`/download/{task_id}`) requires authentication

### 2. Functional Tests (`functional.test.js`)

End-to-end tests using real Digimap data that verify:
- Complete processing workflow with the small dataset
- Processing with custom detection thresholds
- Error handling for invalid ZIP files

## Running the Tests

1. Install dependencies:
```bash
npm install
```

2. Run all tests:
```bash
npm test
```

## Test Data Requirements

### Small Dataset
- Location: `tests/testInput/digimap-data/small-dataset.zip`
- Contains 9 images for segmentation
- Expected to generate 38 segments for processing
- Used for main processing workflow test

## Test Timeouts

- Main processing test: 15 minutes
- Custom parameters test: 5 minutes
- Invalid ZIP test: 5 minutes

## Expected API Responses

### Processing Endpoints
- POST `/web/predict`: Returns 200 with task_id for valid requests
- POST `/predict`: Returns 400 for invalid requests

### Status Endpoint
- GET `/web/status/{task_id}`: Returns 200 with processing status
- Status includes:
  - `has_detections`: boolean
  - `log`: string (processing stage message)
  - `percentage`: number (0-100)
  - `error`: string (if processing failed)
  - `download_token`: string (when processing completes)

### Download Endpoint
- GET `/download/{task_id}`: Returns 401 for unauthenticated requests

## Processing Stages

The API processes data in the following stages:
1. File extraction (5%)
2. Image segmentation (5-40%)
3. Segment processing (40-100%)

Each stage may show "Unknown" status between progress updates 