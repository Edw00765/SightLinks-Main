import { describe, test, expect } from 'vitest';

const API_BASE_URL = 'http://api.sightlinks.org';

describe('API Tests', () => {
  // Test direct processing endpoint
  test('Direct processing endpoint accepts POST requests', async () => {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: new FormData()
    });
    console.log('Direct processing endpoint status:', response.status);
    // Should return 400 (Bad Request) when no file is provided
    expect(response.status).toBe(400);
  });

  // Test web processing endpoint
  test('Web processing endpoint accepts POST requests', async () => {
    const response = await fetch(`${API_BASE_URL}/web/predict`, {
      method: 'POST',
      body: new FormData()
    });
    console.log('Web processing endpoint status:', response.status);
    // Should return 400 (Bad Request) when no file is provided
    expect(response.status).toBe(400);
  });

  // Test status checking endpoint
  test('Status checking endpoint is accessible', async () => {
    const response = await fetch(`${API_BASE_URL}/web/status/test`);
    console.log('Status checking endpoint status:', response.status);
    expect(response.status).toBe(200);
  });

  // Test download endpoint
  test('Download endpoint requires authentication', async () => {
    const response = await fetch(`${API_BASE_URL}/download/test`);
    console.log('Download endpoint status:', response.status);
    // Should return 401 (Unauthorized) when no token is provided
    expect(response.status).toBe(401);
  });
}); 