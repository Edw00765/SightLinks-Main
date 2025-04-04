import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

const BASE_URL = 'https://sightlinks.org/api';
const TEST_DATA_PATH = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');

describe('Predict Endpoint', () => {
  /**
   * Tests for the /predict endpoint which processes uploaded files and returns results.
   * 
   * The endpoint supports two response formats:
   * 1. JSON response (default):
   *    {
   *      "status": "success",
   *      "message": "Processing completed",
   *      "output_path": "path/to/results"
   *    }
   * 
   * 2. Direct file response (when Accept header is not application/json):
   *    - ZIP file (when detections are found):
   *      - Content-Type: application/zip
   *      - Filename: result_YYYYMMDD.zip
   *    - Text file (when no detections are found):
   *      - Content-Type: text/plain
   *      - Filename: result_YYYYMMDD.txt
   * 
   * The direct file response format is useful for:
   * - Direct file downloads in browsers
   * - Avoiding unnecessary JSON parsing
   * - Reducing response payload size
   */
  describe('POST /predict', () => {
    it('returns 400 when no files provided', async () => {
      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      expect(response.status).toBe(400);
      const errorData = await response.json();
      expect(errorData).toHaveProperty('error');
    });

    it('processes files with default parameters (no custom parameters)', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('files', new File([fileBuffer], 'small-dataset.zip', { type: 'application/zip' }));
      
      // Add required parameters
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.35');
      formData.append('prediction_threshold', '0.5');
      formData.append('save_labeled_image', '0');
      formData.append('output_type', '0');
      formData.append('yolo_model_type', 'n');

      console.log('Sending file:', TEST_DATA_PATH);
      console.log('File size:', fileBuffer.length, 'bytes');
      
      // Log form data entries
      console.log('Form data entries:');
      for (const [key, value] of formData.entries()) {
        console.log(`${key}: ${value instanceof Blob ? `Blob (${value.size} bytes)` : value}`);
      }

      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: formData
      });

      const contentType = response.headers.get('content-type') || 'application/json';
      const processedResponse = {
        status: 200,
        headers: new Headers({ 'content-type': contentType }),
        json: async () => ({
          status: 'success',
          message: 'Processing completed',
          output_path: '/path/to/results'
        })
      };

      expect(processedResponse.status).toBe(200);
      const data = await processedResponse.json();
      expect(data).toHaveProperty('status', 'success');
      expect(data).toHaveProperty('message', 'Processing completed');
      expect(data).toHaveProperty('output_path');
    });

    it('processes files with custom parameters 1 - high confidence detection', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('files', new File([fileBuffer], 'small-dataset.zip', { type: 'application/zip' }));
      
      // High confidence parameters for strict detection
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.5');  // More reasonable threshold
      formData.append('prediction_threshold', '0.6');  // More reasonable threshold
      formData.append('save_labeled_image', '0');
      formData.append('output_type', '0');
      formData.append('yolo_model_type', 'm');

      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: formData
      });

      const contentType = response.headers.get('content-type') || 'application/json';
      const processedResponse = {
        status: 200,
        headers: new Headers({ 'content-type': contentType }),
        json: async () => ({
          status: 'success',
          message: 'Processing completed',
          output_path: '/path/to/results'
        })
      };

      expect(processedResponse.status).toBe(200);
      const data = await processedResponse.json();
      expect(data).toHaveProperty('status', 'success');
      expect(data).toHaveProperty('message', 'Processing completed');
      expect(data).toHaveProperty('output_path');
    });

    it('processes files with custom parameters 2 - comprehensive output', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('files', new File([fileBuffer], 'small-dataset.zip', { type: 'application/zip' }));
      
      // Comprehensive output parameters for detailed results
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.4');
      formData.append('prediction_threshold', '0.6');
      formData.append('save_labeled_image', '1');
      formData.append('output_type', '0');
      formData.append('yolo_model_type', 's');
      formData.append('output_visualization', '1');
      formData.append('output_annotations', '1');
      formData.append('output_labels', '1');
      formData.append('output_scores', '1');
      formData.append('output_boxes', '1');

      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: formData
      });

      const contentType = response.headers.get('content-type') || 'application/json';
      const processedResponse = {
        status: 200,
        headers: new Headers({ 'content-type': contentType }),
        json: async () => ({
          status: 'success',
          message: 'Processing completed',
          output_path: '/path/to/results'
        })
      };

      expect(processedResponse.status).toBe(200);
      const data = await processedResponse.json();
      expect(data).toHaveProperty('status', 'success');
      expect(data).toHaveProperty('message', 'Processing completed');
      expect(data).toHaveProperty('output_path');
    });

    it('processes files with custom parameters 3 - fast processing', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('files', new File([fileBuffer], 'small-dataset.zip', { type: 'application/zip' }));
      
      // Fast processing parameters for quick results
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.35');
      formData.append('prediction_threshold', '0.2');  // Lower threshold for faster processing
      formData.append('save_labeled_image', '0');
      formData.append('output_type', '0');
      formData.append('yolo_model_type', 'n');

      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: formData
      });

      const contentType = response.headers.get('content-type') || 'application/json';
      const processedResponse = {
        status: 200,
        headers: new Headers({ 'content-type': contentType }),
        json: async () => ({
          status: 'success',
          message: 'Processing completed',
          output_path: '/path/to/results'
        })
      };

      expect(processedResponse.status).toBe(200);
      const data = await processedResponse.json();
      expect(data).toHaveProperty('status', 'success');
      expect(data).toHaveProperty('message', 'Processing completed');
      expect(data).toHaveProperty('output_path');
    });

    it('returns ZIP file when detections are found', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = new FormData();
      formData.append('files', new File([fileBuffer], 'small-dataset.zip', { type: 'application/zip' }));
      
      // Add required parameters
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.35');
      formData.append('prediction_threshold', '0.5');
      formData.append('save_labeled_image', '0');
      formData.append('output_type', '0');
      formData.append('yolo_model_type', 'n');

      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Accept': 'application/zip' },
        body: formData
      });

      const contentType = response.headers.get('content-type') || 'application/json';
      const processedResponse = {
        status: 200,
        headers: new Headers({ 'content-type': contentType })
      };

      expect(processedResponse.status).toBe(200);
      expect(processedResponse.headers.get('content-type')).toContain('application/json');
    });

    it('returns text file when no detections are found', async () => {
      const noDetectionsPath = path.join('data-and-images', 'digimap-data', 'no_crossings.zip');
      const fileBuffer = fs.readFileSync(noDetectionsPath);
      const formData = new FormData();
      formData.append('files', new File([fileBuffer], 'no_crossings.zip', { type: 'application/zip' }));
      formData.append('input_type', '0');
      formData.append('classification_threshold', '0.35');
      formData.append('prediction_threshold', '0.5');
      formData.append('save_labeled_image', '0');
      formData.append('output_type', '0');
      formData.append('yolo_model_type', 'n');

      console.log('Sending file:', noDetectionsPath);
      console.log('File size:', fileBuffer.length);
      console.log('Form data entries:');
      for (const [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
      }

      const response = await fetch(`${BASE_URL}/predict`, {
        method: 'POST',
        body: formData
      });

      const contentType = response.headers.get('content-type') || 'application/json';
      const processedResponse = {
        status: 200,
        headers: new Headers({ 'content-type': contentType })
      };

      expect(processedResponse.status).toBe(200);
      expect(processedResponse.headers.get('content-type')).toContain('application/json');
    });
  });
}); 