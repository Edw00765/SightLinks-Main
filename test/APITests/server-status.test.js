import { describe, it, expect } from 'vitest';

const BASE_URL = 'https://sightlinks.org/api';

describe('Server Status Endpoint', () => {
  describe('GET /server-status', () => {
    it('returns server statistics', async () => {
      const response = await fetch(`${BASE_URL}/server-status`);
      expect(response.status).toBe(200);
      const data = await response.json();
      
      // Task-related properties
      expect(data).toHaveProperty('active_tasks');
      expect(data).toHaveProperty('cancelled_tasks');
      expect(data).toHaveProperty('failed_tasks');
      expect(data).toHaveProperty('current_tasks');
      expect(data).toHaveProperty('processing_tasks');
      expect(data).toHaveProperty('queued_tasks');
      expect(data).toHaveProperty('total_tasks_processed');
      expect(data).toHaveProperty('total_files_processed');
      
      // Queue-related properties
      expect(data).toHaveProperty('max_queue_size');
      expect(data).toHaveProperty('queue_size');
      expect(data).toHaveProperty('max_concurrent_tasks');
      expect(data).toHaveProperty('queued_task_ids');
      expect(data).toHaveProperty('processing_task_ids');
      
      // System metrics
      expect(data).toHaveProperty('cpu_usage_percent');
      expect(data).toHaveProperty('memory_usage_mb');
      expect(data).toHaveProperty('uptime_seconds');
      expect(data).toHaveProperty('start_time');
      
      // Type checks for numeric values
      expect(typeof data.active_tasks).toBe('number');
      expect(typeof data.cancelled_tasks).toBe('number');
      expect(typeof data.failed_tasks).toBe('number');
      expect(typeof data.memory_usage_mb).toBe('number');
      expect(typeof data.cpu_usage_percent).toBe('number');
      expect(typeof data.uptime_seconds).toBe('number');
      
      // Type checks for arrays
      expect(Array.isArray(data.queued_task_ids)).toBe(true);
      expect(Array.isArray(data.processing_task_ids)).toBe(true);
    });
  });
}); 