import fs from 'fs';
import path from 'path';

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