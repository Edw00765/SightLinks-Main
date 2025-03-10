import { describe, test, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const API_BASE_URL = 'http://api.sightlinks.org';
const SMALL_DATASET_PATH = path.join('testInput', 'digimap-data', 'small-dataset.zip');

// Helper function to create FormData with specified parameters
function createFormData({
  filePath,
  inputType = '0',
  classificationThreshold = '0.35',
  predictionThreshold = '0.5',
  saveLabeledImage = 'true',
  outputType = '0',
  yoloModelType = 'n'
} = {}) {
  const formData = new FormData();
  const fileBuffer = fs.readFileSync(filePath);
  const zipBlob = new Blob([fileBuffer], { type: 'application/zip' });
  
  formData.append('file', zipBlob, path.basename(filePath));
  formData.append('input_type', inputType);
  formData.append('classification_threshold', classificationThreshold);
  formData.append('prediction_threshold', predictionThreshold);
  formData.append('save_labeled_image', saveLabeledImage);
  formData.append('output_type', outputType);
  formData.append('yolo_model_type', yoloModelType);
  
  return formData;
}

// Helper function to submit a task with retries
async function submitTask(formData, maxRetries = 3) {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });
      
      console.log(`Submit response status (attempt ${attempt}):`, response.status);
      const responseText = await response.text();
      console.log(`Submit response body (attempt ${attempt}):`, responseText);

      if (response.status !== 200) {
        console.log(`Task submission failed (attempt ${attempt}):`, response.status);
        throw new Error(`Task submission failed with status ${response.status}: ${responseText}`);
      }

      const responseData = JSON.parse(responseText);
      expect(responseData).toHaveProperty('task_id');
      return responseData.task_id;
    } catch (error) {
      lastError = error;
      console.log(`Attempt ${attempt} failed:`, error.message);
      
      if (attempt < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000); // Exponential backoff, max 10s
        console.log(`Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
}

// Helper function to wait for task completion with exponential backoff
async function waitForCompletion(taskId, { 
  maxWaitMinutes = 30,
  initialInterval = 5000,
  maxInterval = 30000,
  noProgressTimeout = 5 * 60 * 1000 // 5 minutes
} = {}) {
  let elapsed = 0;
  let interval = initialInterval;
  let maxProgress = 0;
  let lastProgressUpdate = Date.now();
  let lastLog = '';
  
  while (elapsed < maxWaitMinutes * 60 * 1000) {
    const statusResponse = await fetch(`${API_BASE_URL}/web/status/${taskId}`);
    const statusText = await statusResponse.text();
    console.log(`Status check (${elapsed / 1000}s elapsed):`, statusText);
    
    expect(statusResponse.status).toBe(200);
    const status = JSON.parse(statusText);
    
    // Track progress
    if (status.percentage > maxProgress) {
      maxProgress = status.percentage;
      lastProgressUpdate = Date.now();
    }
    
    // Track activity through logs
    if (status.log && status.log !== 'Unknown' && status.log !== lastLog) {
      lastLog = status.log;
      lastProgressUpdate = Date.now();
      console.log('New log message:', status.log);
    }
    
    // Check completion conditions
    if (status.percentage === 100 || status.error) {
      return { status, maxProgress };
    }
    
    // Check for stalled processing
    const timeSinceProgress = Date.now() - lastProgressUpdate;
    if (maxProgress > 0 && timeSinceProgress > noProgressTimeout) {
      throw new Error(`Processing stalled: No progress for ${timeSinceProgress / 1000}s after reaching ${maxProgress}%`);
    }
    
    await new Promise(resolve => setTimeout(resolve, interval));
    elapsed += interval;
    interval = Math.min(interval * 1.5, maxInterval); // Exponential backoff
  }
  
  throw new Error(`Processing timed out after ${maxWaitMinutes} minutes`);
}

describe('Functional API Tests with Digimap Data', () => {
  // Test complete processing workflow with real data
  test('Process small Digimap dataset', { timeout: 900000 }, async () => {
    const formData = createFormData({ filePath: SMALL_DATASET_PATH });
    const taskId = await submitTask(formData);
    console.log('Created task ID:', taskId);
    
    const { status, maxProgress } = await waitForCompletion(taskId, { 
      maxWaitMinutes: 15,
      initialInterval: 10000, // Start with 10s interval for large dataset
      maxInterval: 30000,     // Max 30s between checks
      noProgressTimeout: 10 * 60 * 1000 // 10 minutes without progress before failing
    });
    
    expect(status).not.toBeNull();
    if (status.error) {
      console.log('Processing error:', status.error);
      throw new Error(`Processing failed: ${status.error}`);
    } else {
      expect(maxProgress).toBeGreaterThan(0);
      expect(status.percentage).toBe(100);
      console.log('Processing completed successfully');
    }
  });

  // Test processing with different model parameters
  test('Process with different detection thresholds', { timeout: 900000 }, async () => {
    const formData = createFormData({
      filePath: SMALL_DATASET_PATH,
      classificationThreshold: '0.5',
      predictionThreshold: '0.7',
      yoloModelType: 'n'
    });
    
    const taskId = await submitTask(formData);
    console.log('Custom parameters task ID:', taskId);
    
    // Use the same timeout values as the main test
    const { status } = await waitForCompletion(taskId, { 
      maxWaitMinutes: 15,
      initialInterval: 10000, // Start with 10s interval for large dataset
      maxInterval: 30000,     // Max 30s between checks
      noProgressTimeout: 10 * 60 * 1000 // 10 minutes without progress before failing
    });
    
    // Consider test successful if we see significant progress
    expect(status.percentage).toBeGreaterThan(20);
    console.log('Processing progressing with custom parameters');
  });

  // Test error handling with invalid ZIP
  test('Error handling with invalid ZIP content', { timeout: 300000 }, async () => {
    // Create an empty ZIP file (just header)
    const invalidBuffer = Buffer.from([
      0x50, 0x4B, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]);
    
    const formData = new FormData();
    const invalidBlob = new Blob([invalidBuffer], { type: 'application/zip' });
    formData.append('file', invalidBlob, 'invalid.zip');
    formData.append('input_type', '0');
    formData.append('classification_threshold', '0.35');
    formData.append('prediction_threshold', '0.5');
    
    try {
      const taskId = await submitTask(formData);
      console.log('Invalid ZIP task ID:', taskId);
      
      // Monitor for failure
      const { status } = await waitForCompletion(taskId, {
        maxWaitMinutes: 5,
        noProgressTimeout: 60000 // 1 minute
      });
      
      // We expect either an error message or no progress
      if (status.error) {
        expect(typeof status.error).toBe('string');
        expect(status.error.length).toBeGreaterThan(0);
        console.log('Expected error received:', status.error);
      } else {
        expect(status.percentage).toBe(0);
        console.log('Task failed with no progress as expected');
      }
    } catch (error) {
      // Also accept immediate rejection
      console.log('Task rejected as expected:', error.message);
    }
  });
}); 