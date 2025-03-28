import fs from 'fs';
import path from 'path';
import { describe, it, expect } from 'vitest';

export const BASE_URL = 'https://sightlinks.org/api';
export const TEST_DATA_PATH = path.join('data-and-images', 'digimap-data', 'small-dataset.zip');

// Common utility functions
export const readTestFile = (filePath) => {
    return fs.readFileSync(filePath);
};

export const createFormData = (buffer, filename) => {
    const formData = new FormData();
    formData.append('file', new Blob([buffer]), filename);
    return formData;
};

describe('Test Endpoint', () => {
  describe('GET /test', () => {
    it('returns complete server status and configuration', async () => {
      const response = await fetch(`${BASE_URL}/test`);
      expect(response.status).toBe(200);
      const data = await response.json();
      
      // Basic status
      expect(data).toHaveProperty('status', 'operational');
      expect(data).toHaveProperty('version');
      expect(data).toHaveProperty('timestamp');
      
      // Endpoints configuration
      expect(data).toHaveProperty('endpoints');
      expect(data.endpoints).toHaveProperty('test');
      expect(data.endpoints).toHaveProperty('predict');
      expect(data.endpoints).toHaveProperty('web_predict');
      expect(data.endpoints).toHaveProperty('status');
      expect(data.endpoints).toHaveProperty('download');
      
      // Available models
      expect(data).toHaveProperty('models');
      expect(data.models).toHaveProperty('yolo_n');
      expect(data.models).toHaveProperty('yolo_s');
      expect(data.models).toHaveProperty('yolo_m');
      expect(data.models).toHaveProperty('mobilenet');
      expect(data.models).toHaveProperty('vgg16');
      
      // Directory status
      expect(data).toHaveProperty('directories');
      expect(data.directories).toHaveProperty('run_output');
      expect(data.directories).toHaveProperty('run_extract');
      expect(data.directories).toHaveProperty('input');
      expect(data.directories).toHaveProperty('models');
      
      // CUDA information
      expect(data).toHaveProperty('cuda');
      expect(data.cuda).toHaveProperty('available');
      expect(data.cuda).toHaveProperty('device_count');
      expect(data.cuda).toHaveProperty('device_name');
      
      // System status
      expect(data).toHaveProperty('system');
      expect(data.system).toHaveProperty('cpu_percent');
      expect(data.system).toHaveProperty('memory_percent');
      expect(data.system).toHaveProperty('disk_percent');
    });
  });

  describe('POST /test', () => {
    it('returns configuration with echo of POSTed data when no files are uploaded', async () => {
      const testData = { message: 'test message' };
      const response = await fetch(`${BASE_URL}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData)
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      // Verify all standard configuration is present
      expect(data).toHaveProperty('status', 'operational');
      expect(data).toHaveProperty('version');
      expect(data).toHaveProperty('timestamp');
      
      // Verify POST-specific fields
      expect(data).toHaveProperty('echo');
      expect(data.echo).toEqual(testData);
      expect(data).not.toHaveProperty('files');
    });

    it('returns configuration with uploaded files information when a file is uploaded', async () => {
      const fileBuffer = fs.readFileSync(TEST_DATA_PATH);
      const formData = createFormData(fileBuffer, 'small-dataset.zip');

      const response = await fetch(`${BASE_URL}/test`, {
        method: 'POST',
        body: formData
      });

      expect(response.status).toBe(200);
      const data = await response.json();
      
      // Verify all standard configuration is present
      expect(data).toHaveProperty('status', 'operational');
      expect(data).toHaveProperty('version');
      expect(data).toHaveProperty('timestamp');
      
      // Verify files information
      expect(data).toHaveProperty('files');
      expect(Array.isArray(data.files)).toBe(true);
      expect(data.files.length).toBeGreaterThan(0);
      
      // Specific file checks from report
      expect(data.files[0]).toHaveProperty('filename', 'small-dataset.zip');
      expect(data.files[0]).toHaveProperty('size');
      expect(data.files[0].size).toBeGreaterThan(0);
    });
  });
}); 