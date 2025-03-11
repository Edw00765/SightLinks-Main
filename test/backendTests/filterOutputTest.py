import unittest
import sys
import os
from tqdm import tqdm


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.filterOutput import (
    combineChunksToBaseName,
    checkBoxIntersection,
    extractBaseNameAndCoords,
    removeDuplicateBoxesRC,
)

class TestImageDetectionFunctions(unittest.TestCase):

    def test_extractBaseNameAndCoords_valid(self):
        # Test valid input
        baseNameWithRowCol = "image1__r5__c10"
        baseName, row, col = extractBaseNameAndCoords(baseNameWithRowCol)
        self.assertEqual(baseName, "image1")
        self.assertEqual(row, 5)
        self.assertEqual(col, 10)

    def test_extractBaseNameAndCoords_invalid(self):
        # Test invalid input
        with self.assertRaises(ValueError):
            extractBaseNameAndCoords("invalid_string")

    def test_combineChunksToBaseName(self):
        # Test combining chunks
        imageDetectionsRowCol = {
            "image1__r1__c1": ([["box1"], ["box2"]], [0.9, 0.8]),
            "image1__r1__c2": ([["box3"]], [0.7]),
            "image2__r1__c1": ([["box4"]], [0.6]),
        }
        result = combineChunksToBaseName(imageDetectionsRowCol)
        expected = {
            "image1": [[["box1"], ["box2"], ["box3"]], [0.9, 0.8, 0.7]],
            "image2": [[["box4"]], [0.6]],
        }
        self.assertEqual(result, expected)

    def test_checkBoxIntersection_overlapping(self):
        # Test overlapping boxes
        box1 = [(0, 0), (1, 0), (1, 1), (0, 1)]  # Area = 1
        box2 = [(0, 0), (1, 0), (1, 1), (0, 1)]  # Area = 1
        self.assertTrue(checkBoxIntersection(box1, box2))

    def test_checkBoxIntersection_complete_overlap(self):
        box1 = [(0, 0), (2, 0), (2, 2), (0, 2)]  # Area = 1
        box2 = [(0, 0), (1, 0), (1, 1), (0, 1)]  # Area = 1
        self.assertTrue(checkBoxIntersection(box1, box2))

    def test_checkBoxIntersection_non_overlapping(self):
        # Test non-overlapping boxes
        box1 = [(0, 0), (1, 0), (1, 1), (0, 1)]  # Area = 1
        box2 = [(2, 2), (3, 2), (3, 3), (2, 3)]  # Area = 1
        self.assertFalse(checkBoxIntersection(box1, box2))

    def test_checkBoxIntersection_different_sizes(self):
    # Test boxes of different sizes
        box1 = [(0, 0), (2, 0), (2, 2), (0, 2)]  # Area = 4
        box2 = [(1, 1), (3, 1), (3, 3), (1, 3)]  # Area = 4
        self.assertFalse(checkBoxIntersection(box1, box2))


    def test_removeDuplicateBoxesRC(self):
        # Test filtering boxes across neighboring chunks
        imageDetectionsRowCol = {
            "image1__r1__c1": [
                [[(0, 0), (1, 0), (1, 1), (0, 1)]],
                [0.9],
            ],
            "image1__r1__c2": [
                [[(0, 0), (1, 0), (1, 1), (0, 1)]],
                [0.8],
            ],
        }
        removeDuplicateBoxesRC(imageDetectionsRowCol)
        expected = {
            "image1__r1__c1": [
                [[(0, 0), (1, 0), (1, 1), (0, 1)]],
                [0.9],
            ],
            "image1__r1__c2": [
                [],
                [],
            ],
        }
        self.assertEqual(imageDetectionsRowCol, expected)

if __name__ == '__main__':
    unittest.main()