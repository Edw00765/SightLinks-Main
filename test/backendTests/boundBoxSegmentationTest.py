import unittest
from PIL import Image
import os
import sys
from osgeo import gdal

# Import the functions to be tested

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from imageSegmentation.boundBoxSegmentation import boundBoxSegmentationJGW, boundBoxSegmentationTIF

class TestBoundBoxSegmentation(unittest.TestCase):
   
    def test_boundBoxSegmentationJGW(self):
        testImageFileName = "4000x4000.jpg"
        # Call the function
        result = boundBoxSegmentationJGW(extractDir="test/backendTests/testInput/BBSegInput")

        # Verify the result
        for item in result:
            self.assertEqual(item[0], testImageFileName)  # Verify the filename
            self.assertIsInstance(item[1], Image.Image)  # Verify the cropped image
            self.assertEqual(item[1].size, (1024, 1024))  # Verify the size of the cropped image

    def test_boundBoxSegmentationTIF(self):
        testImageFileName = "4000x4000TIF.tif"

        # Call the function
        result = boundBoxSegmentationTIF(extractDir="test/backendTests/testInput/BBSegInput")

        for item in result:
            self.assertEqual(item[0], testImageFileName)  # Verify the filename
            self.assertIsInstance(item[1], gdal.Dataset)  # Verify the cropped dataset
            self.assertEqual(item[1].RasterXSize, 1024)  # Verify the width of the cropped dataset
            self.assertEqual(item[1].RasterYSize, 1024)  # Verify the height of the cropped dataset

if __name__ == '__main__':
    unittest.main()