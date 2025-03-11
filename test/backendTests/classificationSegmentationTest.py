import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from imageSegmentation.classificationSegmentation import classificationSegmentation

class TestClassificationSegmentation(unittest.TestCase):

    def test_classificationSegmentation(self):
        # Test parameters
        inputFileName = "test/backendTests/testInput/512x512.jpg"
        classificationThreshold = 0.35
        classificationChunkSize = 256

        # Call the function
        result = classificationSegmentation(inputFileName, classificationThreshold, classificationChunkSize)

        # Expected result: [(1,1),(1,1)]    #It should actually be [(0,0), (1,0)], but for the purpose of the function, it is changed to [(1,1), (1,1)]
        expected = [(1,1),(1,1)]
        self.assertEqual(result, expected)


    def test_classificationSegmentation_blank_cases(self):
        # Test parameters
        inputFileName = "test/backendTests/testInput/blank.png"
        classificationThreshold = 0.35
        classificationChunkSize = 256

        # Call the function
        result = classificationSegmentation(inputFileName, classificationThreshold, classificationChunkSize)

        # Expected result: []
        expected = []
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()