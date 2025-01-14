from PIL import Image
from tqdm import tqdm
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ImageSegmentation.ClassificationSegmentation import classificationSegmentation
#Take images which are highly likely from kostas
#assume we get a list of tuples (row, column)

#if the image is in an edge, still keep it in the top right so the georeferencing still works,
#but black out the areas where it should be empty


#At some point will need to update the inputFileName so that the data will be retrieved from a database.
inputFolder = "ImageSegmentation/digimapData"
outputFolder = "OrientedBoundingBox/test/test-data/images"

def boundBoxSegmentation(inputFolder, classificationThreshold=0.35):
    with tqdm(total=(len(os.listdir(inputFolder))//2), desc="Segmenting Images") as pbar:
        for inputFileName in os.listdir(inputFolder):
            if inputFileName.endswith(('.png', '.jpg', '.jpeg')):
                try:
                    imagePath = os.path.join(inputFolder, inputFileName)
                    originalImage = Image.open(imagePath)
                    width, height = originalImage.size
                    #Size of bounding box chunks
                    largeChunkSize = 1024
                    #Size of classification chunks
                    smallChunkSize = 256
                    #chunksOfInterest will be retrieved from kostas' program.
                    chunksOfInterest = classificationSegmentation(imagePath, classificationThreshold)
                    #This unique identifier needs to be kept all the way to the georeferencing stage so that we know which file to open
                    uniqueImageIdentifier = ''.join(re.findall(r'\d+', imagePath))
                    os.makedirs(outputFolder, exist_ok=True)

                    #data for georeferencing
                    with open(imagePath.replace('jpg', 'jgw'), 'r') as jgwFile:
                        lines = jgwFile.readlines()
                    pixelSizeX = float(lines[0].strip())
                    rotationX = float(lines[1].strip())
                    rotationY = float(lines[2].strip())
                    pixelSizeY = float(lines[3].strip())
                    topLeftXGeo = float(lines[4].strip())
                    topLeftYGeo = float(lines[5].strip())

                    for row, col in chunksOfInterest:
                        #setting cases when point of interest is at the edges
                        topRow = row - 1
                        topCol = col - 1
                        topX = topCol * smallChunkSize - smallChunkSize / 2 if topCol > 0 else 0 #This is the top left x
                        topY = topRow * smallChunkSize - smallChunkSize / 2 if topRow > 0 else 0 #This is the top left y

                        #setting case if there are overlaps in the image
                        if topX + largeChunkSize > width:
                            topX = width - largeChunkSize
                        if topY + largeChunkSize > height:
                            topY = height - largeChunkSize

                        box = (topX, topY, topX + largeChunkSize, topY + largeChunkSize)
                        cropped = originalImage.crop(box)
                        cropped.save(f"{outputFolder}/{uniqueImageIdentifier}chunkOfInterest_{row}_{col}.jpg")
                        with open(f"{outputFolder}/{uniqueImageIdentifier}chunkOfInterest_{row}_{col}.jgw", 'w') as file:
                            file.write(f"{pixelSizeX:.10f}\n")
                            file.write(f"{rotationX:.10f}\n")
                            file.write(f"{rotationY:.10f}\n")
                            file.write(f"{pixelSizeY:.10f}\n")
                            file.write(f"{(topLeftXGeo + topX * pixelSizeX):.10f}\n")
                            file.write(f"{(topLeftYGeo + topY * pixelSizeY):.10f}\n")
                        pbar.update(1)
                except Exception as e:
                    print(f"Error opening {imagePath}: {e}")