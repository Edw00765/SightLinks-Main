#Need to install pillow from pip, to ensure that the images are the required size
from PIL import Image
import math
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classificationScreening.classify import PIL_infer

def classificationSegmentation(inputFileName, classificationThreshold, classificationChunkSize):
    image = Image.open(inputFileName)
    width, height = image.size
    print("width and height in classificationSegmentation",width, height)
    listOfColRow = []
    # Loop to create and save chunks
    for row in range(0, height, classificationChunkSize):
        for col in range(0, width, classificationChunkSize):
            xDifference = 0
            yDifference = 0
            if col + classificationChunkSize > width:
                xDifference = col + classificationChunkSize - width
            if row + classificationChunkSize > height:
                yDifference = row + classificationChunkSize - height
            box = (col - xDifference, row - yDifference, col - xDifference + classificationChunkSize, row - yDifference + classificationChunkSize)
            cropped = image.crop(box)
            containsCrossing = PIL_infer(cropped, threshold=classificationThreshold)
            if containsCrossing:
                rowToAdd = row // classificationChunkSize
                colToAdd = col // classificationChunkSize
                if xDifference:
                    colToAdd = math.ceil(width / classificationChunkSize) - 2 #make it -2 to accomodate for 0 index
                elif col == 0:
                    colToAdd = 1
                if yDifference:
                    rowToAdd = math.ceil(height / classificationChunkSize) - 2
                elif row == 0:
                    rowToAdd = 1
                listOfColRow.append((colToAdd, rowToAdd))

    print(listOfColRow)
    return listOfColRow