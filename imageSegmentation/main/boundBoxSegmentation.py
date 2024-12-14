from PIL import Image
import os

#Take images which are highly likely from kostas
#assume we get a list of tuples (row, column)

#take the row, column, and take it as a center of an image which is a (3 chunk x 3 chunk), the top left of the new image
#will be row - 1, column - 1

#if the image is in an edge, still keep it in the top right so the georeferencing still works,
#but black out the areas where it should be empty


#At some point will need to update the inputFileName so that the data will be retrieved from a database.
inputFileName = "SightLink-Main/imageSegmentation/digimapData/tq2779_rgb_250_09.jpg"
originalImage = Image.open(inputFileName)
width, height = originalImage.size

#Aiden's required size
largeChunkSize = 1024
smallChunkSize = 342
#chunksOfInterest will be retrieved from kostas' program.
chunksOfInterest = [(0,0), (0,11), (11,11), (11,0), (5, 0), (0,5), (5,11), (11,5)]
outputFolder = "SightLink-Main/imageSegmentation/boundingBoxInput"
os.makedirs(outputFolder, exist_ok=True)

#data for georeferencing
with open(inputFileName.replace('jpg', 'jgw'), 'r') as jgwFile:
    lines = jgwFile.readlines()
pixelSizeX = float(lines[0].strip())
rotationX = float(lines[1].strip())
rotationY = float(lines[2].strip())
pixelSizeY = float(lines[3].strip())
topLeftXGeo = float(lines[4].strip())
topLeftYGeo = float(lines[5].strip())

for row, col in chunksOfInterest:
    xDifference = 0
    yDifference = 0
    #setting cases when point of interest is at the edges
    if row == 0:
        topRow = 0
    else:
        topRow = row - 1
    if col == 0:
        topCol = 0
    else:
        topCol = col - 1
    topX = topCol * smallChunkSize
    topY = topRow * smallChunkSize

    #setting case if there are overlaps in the image
    if topX + largeChunkSize > width:
        topX = width - largeChunkSize
    if topY + largeChunkSize > height:
        topY = height - largeChunkSize

    box = (topX, topY, topX + largeChunkSize, topY + largeChunkSize)
    cropped = originalImage.crop(box)
    cropped.save(f"{outputFolder}/chunkOfInterest_{row}_{col}.jpg")
    with open(f"{outputFolder}/chunkOfInterest_{row}_{col}.jgw", 'w') as jgwFile:
        jgwFile.write(f"{pixelSizeX:.10f}\n")
        jgwFile.write(f"{rotationX:.10f}\n")
        jgwFile.write(f"{rotationY:.10f}\n")
        jgwFile.write(f"{pixelSizeY:.10f}\n")
        jgwFile.write(f"{(topLeftXGeo + topX * pixelSizeX):.10f}\n")
        jgwFile.write(f"{(topLeftYGeo + topY * pixelSizeY):.10f}\n")

print(f"Chunks saved in: {os.path.abspath(outputFolder)}")