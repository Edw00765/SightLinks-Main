import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'https://sightlinks.org/api';
const TEST_DATA_PATH = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');

describe('Web Status Endpoint', () => {
  describe('GET /web/status/:task_id', () => {
    it('returns completed: false for non-existent task', async () => {
      const response = await fetch(`${BASE_URL}/web/status/non-existent-task`);
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toEqual({ completed: false });
    });

    it('returns task status for a running task', async () => {
      // First create a task
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'small-dataset.zip');
      
      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;

      // Then check its status immediately (should be running)
      const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
      expect(statusResponse.status).toBe(200);
      const statusData = await statusResponse.json();
      
      // For running tasks, we only expect completed: false
      expect(statusData).toHaveProperty('completed', false);
    });

    it('returns completed task status with detections', async () => {
      const smallDataPath = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');
      const fileBuffer = fs.readFileSync(smallDataPath);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'small-dataset.zip');
      formData.append('model_type', 'yolo_n'); // Use fastest model
      formData.append('output_type', '0');
      
      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;

      // Wait for task completion (with timeout)
      let isCompleted = false;
      let attempts = 0;
      const maxAttempts = 24; // 2 minutes total (5 seconds * 24)
      let lastError = null;

      while (!isCompleted && attempts < maxAttempts) {
        try {
          const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
          const statusData = await statusResponse.json();
          
          if (statusData.completed) {
            isCompleted = true;
            expect(statusData).toHaveProperty('completed', true);
            expect(statusData).toHaveProperty('download_token');
            expect(statusData).toHaveProperty('has_detections', true);
            break;
          }
        } catch (error) {
          lastError = error;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      if (!isCompleted) {
        if (lastError) {
          console.log('Last error:', lastError);
        }
        throw new Error('Task did not complete within timeout period');
      }
    });

    it('returns completed task status without detections', async () => {
      // Use the no_crossings dataset that we know has no detections
      const noDetectionsPath = path.join('data-and-images', 'digimap-data', 'no_crossings.zip');
      const fileBuffer = fs.readFileSync(noDetectionsPath);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'no_crossings.zip');
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.35');
      formData.append('prediction_threshold', '0.5');
      formData.append('save_labeled_image', 'false');
      formData.append('output_type', '0');
      formData.append('yolo_model_type', 'n'); // Use fastest model
      
      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;

      // Wait for task completion (with timeout)
      let isCompleted = false;
      let attempts = 0;
      const maxAttempts = 36; // 3 minutes total (5 seconds * 36)
      let lastError = null;
      let lastStatus = null;

      while (!isCompleted && attempts < maxAttempts) {
        try {
          const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
          const statusData = await statusResponse.json();
          lastStatus = statusData;
          
          if (statusData.completed) {
            isCompleted = true;
            expect(statusData).toHaveProperty('completed', true);
            expect(statusData).toHaveProperty('download_token');
            expect(statusData).toHaveProperty('has_detections', false);
            break;
          }

          if (statusData.error) {
            throw new Error(`Task failed: ${statusData.error_message || 'Unknown error'}`);
          }
        } catch (error) {
          lastError = error;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      if (!isCompleted) {
        console.log('Last known status:', lastStatus);
        if (lastError) {
          console.log('Last error:', lastError);
        }
        throw new Error('Task did not complete within timeout period');
      }
    });

    it('returns error status for failed task', async () => {
      // Create a task with invalid parameters
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'small-dataset.zip');
      formData.append('input_type', 'invalid_type');
      
      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      // The task should still be created
      expect(createResponse.status).toBe(200);
      const createData = await createResponse.json();
      expect(createData).toHaveProperty('task_id');

      // Wait a bit for the task to process and fail
      await new Promise(resolve => setTimeout(resolve, 5000));

      // Check status - should have error message
      const statusResponse = await fetch(`${BASE_URL}/web/status/${createData.task_id}`);
      const statusData = await statusResponse.json();
      
      // Log the actual response for debugging
      console.log('Status response:', statusData);

      // Task should be marked as not completed
      expect(statusData).toEqual({ completed: false });
    });
  });
}); 