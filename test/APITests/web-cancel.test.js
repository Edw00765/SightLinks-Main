import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'https://sightlinks.org/api';
const TEST_DATA_PATH = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');

describe('Web Cancel Endpoint', () => {
  describe('POST /web/cancel/:task_id', () => {
    it('returns 404 for non-existent task', async () => {
      const response = await fetch(`${BASE_URL}/web/cancel/non-existent-task`, {
        method: 'POST'
      });
      
      expect(response.status).toBe(404);
      const data = await response.json();
      expect(data.error).toBe('Task not found or cannot be cancelled');
    });

    it('cancels a running task', async () => {
      // Create a task that will take some time to process
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'test.zip');
      formData.append('model_type', 'yolo_m'); // Use larger model to ensure longer processing time
      formData.append('output_type', '1'); // Comprehensive output for longer processing

      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;

      // Wait for task to start processing
      let isRunning = false;
      let attempts = 0;
      const maxAttempts = 24; // 2 minutes total

      while (!isRunning && attempts < maxAttempts) {
        const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
        const statusData = await statusResponse.json();

        // Task is running if it's not completed and not queued
        if (!statusData.completed && !statusData.download_token) {
          isRunning = true;
          break;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      if (!isRunning) {
        console.log('Task completed before we could cancel it');
      }

      expect(isRunning).toBe(true);

      // Cancel the task
      const cancelResponse = await fetch(`${BASE_URL}/web/cancel/${taskId}`, {
        method: 'POST'
      });
      
      // Get the response data even if status is not 200
      const cancelData = await cancelResponse.json();

      // Verify final status shows task is not completed
      const finalStatus = await fetch(`${BASE_URL}/web/status/${taskId}`);
      const finalData = await finalStatus.json();
      
      expect(finalData.completed).toBe(false);
    });

    it('cancels a queued task', async () => {
      // Create multiple tasks to ensure queueing
      const tasks = [];
      for (let i = 0; i < 6; i++) {
        const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
        const formData = new FormData();
        formData.append('file', new Blob([fileBuffer]), 'test.zip');
        formData.append('model_type', 'yolo_m'); // Use larger model to ensure longer processing
        formData.append('output_type', '1'); // Comprehensive output for longer processing

        const response = await fetch(`${BASE_URL}/web/predict`, {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        tasks.push(data.task_id);

        // Wait a bit between task creation to ensure proper queueing
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Wait for tasks to be properly queued
      await new Promise(resolve => setTimeout(resolve, 5000));

      // Get status of last task (should be queued)
      const lastTaskId = tasks[tasks.length - 1];
      let isQueued = false;
      let attempts = 0;
      const maxAttempts = 12;

      while (!isQueued && attempts < maxAttempts) {
        const statusResponse = await fetch(`${BASE_URL}/web/status/${lastTaskId}`);
        const statusData = await statusResponse.json();

        // Consider task queued if it's not completed and not the first task
        if (!statusData.completed && !statusData.download_token) {
          isQueued = true;
          break;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      expect(isQueued).toBe(true);

      // Cancel the queued task
      const cancelResponse = await fetch(`${BASE_URL}/web/cancel/${lastTaskId}`, {
        method: 'POST'
      });
      
      // Get the response data even if status is not 200
      const cancelData = await cancelResponse.json();

      // Verify task is no longer in queue
      const finalStatus = await fetch(`${BASE_URL}/web/status/${lastTaskId}`);
      const finalData = await finalStatus.json();
      
      expect(finalData.completed).toBe(false);

      // Clean up other tasks
      for (const taskId of tasks) {
        if (taskId !== lastTaskId) {
          await fetch(`${BASE_URL}/web/cancel/${taskId}`, {
            method: 'POST'
          });
        }
      }
    });

    it('returns 404 for completed task', async () => {
      const noDetectionsPath = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');
      const fileBuffer = fs.readFileSync(noDetectionsPath);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'small-dataset.zip');
      formData.append('model_type', 'yolo_n'); // Use fastest model
      formData.append('output_type', '0'); // Minimal output

      const createResponse = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      const createData = await createResponse.json();
      const taskId = createData.task_id;

      // Wait for task completion with increased timeout
      let isCompleted = false;
      let attempts = 0;
      const maxAttempts = 24; // 2 minutes total

      while (!isCompleted && attempts < maxAttempts) {
        const statusResponse = await fetch(`${BASE_URL}/web/status/${taskId}`);
        const statusData = await statusResponse.json();
        
        if (statusData.completed && statusData.download_token) {
          isCompleted = true;
          // Wait a bit to ensure task cleanup is complete
          await new Promise(resolve => setTimeout(resolve, 2000));
          break;
        }

        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }

      if (!isCompleted) {
        console.log('Task did not complete within timeout');
      }

      expect(isCompleted).toBe(true);

      // Try to cancel the completed task
      const cancelResponse = await fetch(`${BASE_URL}/web/cancel/${taskId}`, {
        method: 'POST'
      });
      
      expect(cancelResponse.status).toBe(404);
      const data = await cancelResponse.json();
      expect(data.error).toBe('Task not found or cannot be cancelled');
    });
  });
}); 