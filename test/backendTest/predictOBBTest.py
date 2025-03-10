import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np
import torch
import os
import tempfile
import sys
from tqdm import tqdm

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the functions to be tested
from orientedBoundingBox.predictOBB import predictionJGW, predictionTIF

class TestPredictionFunctions(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_folder = self.temp_dir.name

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()


    def mock_yolo_model(self):
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.cpu.return_value = mock_result
        mock_result.obb.conf = [torch.tensor(0.9), torch.tensor(0.8)]  # Confidence scores
        mock_result.obb.xyxyxyxy = [
            torch.tensor([[0, 0], [1, 0], [1, 1], [0, 1]]),
            torch.tensor([[0.5, 0.5], [1.5, 0.5], [1.5, 1.5], [0.5, 1.5]]),
        ]
        mock_model.return_value = [mock_result]  # Mock the __call__ method
        return mock_model


    @patch('orientedBoundingBox.predictOBB.YOLO')  # Mock the YOLO class
    def test_predictionJGW(self, mock_yolo):
        # Mock the YOLO instance
        mock_model = self.mock_yolo_model()
        mock_yolo.return_value = mock_model

        # Mock input data
        imageAndDatas = [
            ("image1__r1__c1", Image.new('RGB', (256, 256)), 0.1, -0.1, 530000, 180000, 1, 1)
        ]

        # Call the function
        result = predictionJGW(imageAndDatas, saveLabeledImage=False, outputFolder=self.output_folder)

        # Verify the result
        self.assertIn("image1", result)
        self.assertEqual(len(result["image1"][0]), 2)  # Two bounding boxes
        self.assertEqual(len(result["image1"][1]), 2)  # Two confidence scores

    @patch('orientedBoundingBox.predictOBB.YOLO')  # Mock the YOLO class
    @patch('orientedBoundingBox.predictOBB.georeferenceTIF')
    def test_predictionTIF(self, mock_georef_tif, mock_yolo):
        mock_model = self.mock_yolo_model()
        mock_yolo.return_value = mock_model

        # Mock georeferenceTIF to return a valid list of points
        mock_georef_tif.return_value = [(0, 0), (1, 0), (1, 1), (0, 1)]

        # Mock input data
        mock_gdal_image = MagicMock()
        mock_gdal_image.ReadAsArray.return_value = np.random.randint(0, 256, (3, 256, 256), dtype=np.uint8)
        imageAndDatas = [
            ("image1", mock_gdal_image, 1, 1)
        ]

        # Call the function
        result = predictionTIF(imageAndDatas, saveLabeledImage=False, outputFolder=self.output_folder)

        # Verify the result
        self.assertIn("image1", result)
        self.assertEqual(len(result["image1"][0]), 2)  # Two bounding boxes
        self.assertEqual(len(result["image1"][1]), 2)  # Two confidence scores

    @patch('orientedBoundingBox.predictOBB.YOLO')  # Mock the YOLO class
    def test_predictionJGW_empty_input(self, mock_yolo):
        # Mock the YOLO instance
        mock_model = self.mock_yolo_model()
        mock_yolo.return_value = mock_model

        # Mock input data (empty)
        imageAndDatas = []

        # Call the function
        result = predictionJGW(imageAndDatas, saveLabeledImage=False, outputFolder=self.output_folder)

        # Verify the result
        self.assertEqual(result, {})

    @patch('orientedBoundingBox.predictOBB.YOLO')  # Mock the YOLO class
    def test_predictionTIF_empty_input(self, mock_yolo):
        # Mock the YOLO instance
        mock_model = self.mock_yolo_model()
        mock_yolo.return_value = mock_model

        # Mock input data (empty)
        imageAndDatas = []

        # Call the function
        result = predictionTIF(imageAndDatas, saveLabeledImage=False, outputFolder=self.output_folder)

        # Verify the result
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()