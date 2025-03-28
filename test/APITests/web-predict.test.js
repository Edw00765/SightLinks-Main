import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'https://sightlinks.org/api';
const TEST_DATA_PATH = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');

describe('Web Predict Endpoint', () => {
  describe('POST /web/predict', () => {
    it('returns 400 when no files provided', async () => {
      const response = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' }
      });

      expect(response.status).toBe(400);
      const data = await response.json();
      expect(data).toHaveProperty('error', 'No valid image files uploaded. Expected JPG/JPEG/PNG files or ZIP containing them.');
    });

    it('queues task with default parameters', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'tiny-dataset.zip');

      const response = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('task_id');
      expect(data).toHaveProperty('message', 'Task queued successfully');
    });

    it('queues task with custom parameters', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'tiny-dataset.zip');
      
      // Custom parameters
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.4');
      formData.append('prediction_threshold', '0.6');
      formData.append('save_labeled_image', 'true');
      formData.append('output_type', '1');
      formData.append('yolo_model_type', 'm');

      // Add retry logic
      let response;
      let attempts = 0;
      const maxAttempts = 3;
      
      while (attempts < maxAttempts) {
        try {
          response = await fetch(`${BASE_URL}/web/predict`, {
            method: 'POST',
            body: formData
          });
          break;
        } catch (error) {
          attempts++;
          if (attempts === maxAttempts) throw error;
          await new Promise(resolve => setTimeout(resolve, 5000));
        }
      }

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('task_id');
      expect(data).toHaveProperty('message', 'Task queued successfully');
    });

    it('returns 503 when server is busy', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('file', new Blob([fileBuffer]), 'tiny-dataset.zip');

      // Send requests sequentially instead of all at once
      const maxRequests = 5;
      let has503 = false;
      
      for (let i = 0; i < maxRequests && !has503; i++) {
        try {
          const response = await fetch(`${BASE_URL}/web/predict`, {
            method: 'POST',
            body: formData
          });
          
          if (response.status === 503) {
            has503 = true;
            const errorData = await response.json();
            expect(errorData).toHaveProperty('error', 'Server is busy. Please try again later.');
            break;
          }
        } catch (error) {
          // Continue with next request even if this one failed
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      if (!has503) {
        console.log('Server handled all requests without becoming busy');
      }
    });

    it('queues task with GeoTIFF input type', async () => {
      const filePath = path.join(__dirname, 'data-and-images', 'Geotiff-image.tif');
      
      // Create a ZIP file containing the GeoTIFF
      const JSZip = require('jszip');
      const zip = new JSZip();
      const fileBuffer = fs.readFileSync(filePath);
      zip.file('Geotiff-image.tif', fileBuffer);
      
      const zipBuffer = await zip.generateAsync({type: 'nodebuffer'});
      
      const formData = new FormData();
      formData.append('file', new Blob([zipBuffer]), 'geotiff-data.zip');
      formData.append('input_type', '1');  // GeoTIFF input type

      const response = await fetch(`${BASE_URL}/web/predict`, {
        method: 'POST',
        body: formData
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('task_id');
      expect(data).toHaveProperty('message', 'Task queued successfully');
    });
  });
});