#Need to install pillow from pip, to ensure that the images are the required size
from PIL import Image
import os
import re

def classificationSegmentation(inputFileName):
    image = Image.open(inputFileName)
    width, height = image.size
    #kostas required size
    chunkSize = 256

    uniqueImageIdentifier = ''.join(re.findall(r'\d+', inputFileName))
    outputFolder = "imageSegmentation/classificationInput"
    os.makedirs(outputFolder, exist_ok=True)

    # Loop to create and save chunks
    for row in range(0, height, chunkSize):
        for col in range(0, width, chunkSize):
            xDifference = 0
            yDifference = 0
            if col + chunkSize > width:
                xDifference = col + chunkSize - width
            if row + chunkSize > height:
                yDifference = row + chunkSize - height
            box = (col - xDifference, row - yDifference, col - xDifference + chunkSize, row - yDifference + chunkSize)
            cropped = image.crop(box)
            cropped.save(f"{outputFolder}/{uniqueImageIdentifier}chunk_{row // chunkSize}_{col // chunkSize}.jpg")
    print(f"Chunks saved in: {os.path.abspath(outputFolder)}")

classificationSegmentation("imageSegmentation/digimapData/tq2678_rgb_250_09.jpg")