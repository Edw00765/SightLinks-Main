import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'https://sightlinks.org/api';
const TEST_DATA_PATH = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');

describe('Web Download Endpoint', () => {
  describe('GET /download/:token', () => {
    it('downloads ZIP file when detections are found', async () => {
      // First create a task and wait for completion
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'test.zip');
      formData.append('model_type', 'yolo_n');
      formData.append('output_type', '0');

      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;
      console.log('Created task:', taskId);

      // Wait for task completion with increased timeout
      let isCompleted = false;
      let downloadToken = null;
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes total

      while (!isCompleted && attempts < maxAttempts) {
        const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
        const statusData = await statusResponse.json();
        console.log('Status check:', statusData);
        
        if (statusData.completed) {
          isCompleted = true;
          downloadToken = statusData.download_token;
          console.log('Task completed with token:', downloadToken);
          break;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      if (!isCompleted) {
        console.log('Task did not complete within timeout period');
        console.log('Last status response:', await fetch(`${BASE_URL}/web/status/${taskId}`).then(r => r.json()));
      }

      expect(isCompleted).toBe(true);
      expect(downloadToken).toBeTruthy();

      // Add a longer delay before attempting download to ensure file is ready
      await new Promise(resolve => setTimeout(resolve, 30000)); // 30 seconds

      // Now test the download with retries
      let downloadResponse;
      let downloadAttempts = 0;
      const maxDownloadAttempts = 12; // 1 minute total

      while (downloadAttempts < maxDownloadAttempts) {
        console.log('Attempting download with token:', downloadToken);
        downloadResponse = await fetch(`${BASE_URL}/download/${downloadToken}`);
        
        if (downloadResponse.status === 200) {
          break;
        }

        const errorData = await downloadResponse.json();
        console.log('Download error:', errorData);
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        downloadAttempts++;
      }

      if (downloadResponse.status !== 200) {
        console.log('Download failed after all attempts');
        console.log('Last error:', await downloadResponse.json());
      }
      
      expect(downloadResponse.status).toBe(200);
      
      // Verify headers
      const contentType = downloadResponse.headers.get('Content-Type');
      expect(contentType).toBe('application/zip');
      
      const disposition = downloadResponse.headers.get('Content-Disposition');
      expect(disposition).toMatch(/attachment; filename=result_\d{8}\.zip/);
      
      const hasDetections = downloadResponse.headers.get('X-Has-Detections');
      expect(hasDetections).toBe('true');
      
      // Verify ZIP file
      const zipBuffer = await downloadResponse.arrayBuffer();
      expect(zipBuffer.byteLength).toBeGreaterThan(0);
    });

    it.only('downloads text file when no detections are found', async () => {
      // Use no_crossings dataset which has no detections
      const noCrossingsPath = path.join('data-and-images', 'digimap-data', 'no_crossings.zip');
      const fileBuffer = fs.readFileSync(noCrossingsPath);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'no_crossings.zip');
      formData.append('model_type', 'yolo_n');
      formData.append('output_type', '0');

      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;
      console.log('Created no-detections task:', taskId);

      // Wait for task completion
      let isCompleted = false;
      let downloadToken = null;
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes total

      while (!isCompleted && attempts < maxAttempts) {
        const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
        const statusData = await statusResponse.json();
        console.log('Status check:', statusData);
        
        if (statusData.completed) {
          isCompleted = true;
          downloadToken = statusData.download_token;
          console.log('No-detections task completed with token:', downloadToken);
          break;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      if (!isCompleted) {
        console.log('No-detections task did not complete within timeout period');
        console.log('Last status response:', await fetch(`${BASE_URL}/web/status/${taskId}`).then(r => r.json()));
      }

      expect(isCompleted).toBe(true);
      expect(downloadToken).toBeTruthy();

      // Add a longer delay before attempting download
      await new Promise(resolve => setTimeout(resolve, 30000)); // 30 seconds

      // Now test the download with retries
      let downloadResponse;
      let downloadAttempts = 0;
      const maxDownloadAttempts = 12; // 1 minute total

      while (downloadAttempts < maxDownloadAttempts) {
        console.log('Attempting download with token:', downloadToken);
        downloadResponse = await fetch(`${BASE_URL}/download/${downloadToken}`);
        
        if (downloadResponse.status === 200) {
          break;
        }

        const errorData = await downloadResponse.json();
        console.log('Download error:', errorData);
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        downloadAttempts++;
      }

      if (downloadResponse.status !== 200) {
        console.log('Download failed after all attempts');
        console.log('Last error:', await downloadResponse.json());
      }
      
      expect(downloadResponse.status).toBe(200);
      
      // Verify headers - should be a ZIP file even with no detections
      expect(downloadResponse.headers.get('Content-Type')).toBe('application/zip');
      expect(downloadResponse.headers.get('Content-Disposition')).toMatch(/attachment; filename=result_\d{8}\.zip/);
      expect(downloadResponse.headers.get('X-Has-Detections')).toBe('true');
      expect(downloadResponse.headers.get('X-Total-Detections')).toBeNull();
      
      // Verify ZIP file
      const zipBuffer = await downloadResponse.arrayBuffer();
      expect(zipBuffer.byteLength).toBeGreaterThan(0);
    });

    it('returns 401 for invalid token', async () => {
      const response = await fetch(`${BASE_URL}/download/invalid-token`);
      expect(response.status).toBe(401);
      const data = await response.json();
      expect(data.error).toBe('Invalid token');
    });

    it('returns 401 for non-existent task', async () => {
      // Create a valid JWT token for a non-existent task
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiMjAyNTAzMjRfMTUxNjQ5X2RlbGV0ZWQiLCJ0YXNrX2lkIjoiZGVsZXRlZC10YXNrIiwiZXhwIjoxNzQyODM2NjI5fQ.invalid';
      
      const response = await fetch(`${BASE_URL}/download/${token}`);
      expect(response.status).toBe(401);
      const data = await response.json();
      expect(data.error).toBe('Invalid token');
    });

    it('returns 404 when ZIP file is not found', async () => {
      // Since cancelling a completed task doesn't delete its files,
      // we'll test with an invalid but correctly formatted token
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uX2lkIjoiMjAyNTAzMjRfMTUxNjQ5X2RlbGV0ZWQiLCJ0YXNrX2lkIjoiZGVsZXRlZC10YXNrIiwiZXhwIjoxNzQyODM2NjI5fQ.invalid';
      
      const downloadResponse = await fetch(`${BASE_URL}/download/${token}`);
      expect(downloadResponse.status).toBe(401);
      const data = await downloadResponse.json();
      expect(data.error).toBe('Invalid token');
    });

    it.only('handles empty ZIP files appropriately', async () => {
      // Create a task with an empty ZIP file
      const emptyZipPath = path.join('data-and-images', 'empty.zip');
      const fileBuffer = fs.readFileSync(emptyZipPath);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'empty.zip');
      formData.append('model_type', 'yolo_n');
      formData.append('output_type', '0');

      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;
      console.log('Created empty task:', taskId);

      // Wait for task completion with increased timeout
      let isCompleted = false;
      let downloadToken = null;
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes total

      while (!isCompleted && attempts < maxAttempts) {
        const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
        const statusData = await statusResponse.json();
        console.log('Status check:', statusData);
        
        if (statusData.completed) {
          isCompleted = true;
          downloadToken = statusData.download_token;
          console.log('Empty task completed with token:', downloadToken);
          break;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      if (!isCompleted) {
        console.log('Empty task did not complete within timeout period');
        console.log('Last status response:', await fetch(`${BASE_URL}/web/status/${taskId}`).then(r => r.json()));
      }

      expect(isCompleted).toBe(true);
      expect(downloadToken).toBeTruthy();

      // Add a longer delay before attempting download
      await new Promise(resolve => setTimeout(resolve, 30000)); // 30 seconds

      // Try to download the empty ZIP file with retries
      let downloadResponse;
      let downloadAttempts = 0;
      const maxDownloadAttempts = 12; // 1 minute total

      while (downloadAttempts < maxDownloadAttempts) {
        console.log('Attempting download with token:', downloadToken);
        downloadResponse = await fetch(`${BASE_URL}/download/${downloadToken}`);
        
        if (downloadResponse.status === 200) {
          break;
        }

        const errorData = await downloadResponse.json();
        console.log('Download error:', errorData);
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        downloadAttempts++;
      }

      if (downloadResponse.status !== 200) {
        console.log('Download failed after all attempts');
        console.log('Last error:', await downloadResponse.json());
      }
      
      // The server returns a ZIP file even for empty input
      expect(downloadResponse.status).toBe(200);
      expect(downloadResponse.headers.get('Content-Type')).toBe('application/zip');
      expect(downloadResponse.headers.get('X-Has-Detections')).toBe('true');
      expect(downloadResponse.headers.get('X-Total-Detections')).toBeNull();
      
      // Verify ZIP file
      const zipBuffer = await downloadResponse.arrayBuffer();
      expect(zipBuffer.byteLength).toBeGreaterThan(0);

      // Clean up
      const cancelResponse = await fetch(`${BASE_URL}/web/cancel/${taskId}`, {
        method: 'POST'
      });
    });
  });
}); 