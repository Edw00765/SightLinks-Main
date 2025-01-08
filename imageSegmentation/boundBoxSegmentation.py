from PIL import Image
import os
import re

#Take images which are highly likely from kostas
#assume we get a list of tuples (row, column)

#take the row, column, and take it as a center of an image which is a (3 chunk x 3 chunk), the top left of the new image
#will be row - 1, column - 1

#if the image is in an edge, still keep it in the top right so the georeferencing still works,
#but black out the areas where it should be empty


#At some point will need to update the inputFileName so that the data will be retrieved from a database.
inputFolder = "imageSegmentation/digimapData"

def boundBoxSegmentation(inputFolder):
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
                chunksOfInterest = [(0,0), (1,1), (5,5)]
                #This unique identifier needs to be kept all the way to the georeferencing stage so that we know which file to open
                uniqueImageIdentifier = ''.join(re.findall(r'\d+', imagePath))
                outputFolder = "orientedBoundingBox/test/test-data/images"
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
                    with open(f"{outputFolder}/{uniqueImageIdentifier}chunkOfInterest_{row}_{col}.jgw", 'w') as jgwFile:
                        jgwFile.write(f"{pixelSizeX:.10f}\n")
                        jgwFile.write(f"{rotationX:.10f}\n")
                        jgwFile.write(f"{rotationY:.10f}\n")
                        jgwFile.write(f"{pixelSizeY:.10f}\n")
                        jgwFile.write(f"{(topLeftXGeo + topX * pixelSizeX):.10f}\n")
                        jgwFile.write(f"{(topLeftYGeo + topY * pixelSizeY):.10f}\n")

                print(f"Chunks saved in: {os.path.abspath(outputFolder)}")
            except Exception as e:
                print(f"Error opening {imagePath}: {e}")


boundBoxSegmentation(inputFolder)







# inputFolder = "imageSegmentation/digimapData"

# def boundBoxSegmentation(inputFolder):
#     for inputFileName in os.listdir(inputFolder):
#         if inputFileName.endswith(('.png', '.jpg', '.jpeg')):
#             try:
#                 imagePath = os.path.join(inputFolder, inputFileName)
#                 originalImage = Image.open(imagePath)
#                 width, height = originalImage.size
#                 #Size of bounding box chunks
#                 largeChunkSize = 1024
#                 #Size of classification chunks
#                 smallChunkSize = 342
#                 #chunksOfInterest will be retrieved from kostas' program.
#                 chunksOfInterest = [(1,1), (1,4), (1,7), (1,10), (4,1), (4,4), (4,7), (4,10), (7,1), (7,4), (7,7), (7,10), (10,1), (10,4), (10,7), (10,10)]
#                 #This unique identifier needs to be kept all the way to the georeferencing stage so that we know which file to open
#                 uniqueImageIdentifier = ''.join(re.findall(r'\d+', imagePath))
#                 outputFolder = "orientedBoundingBox/test/test-data/images"
#                 os.makedirs(outputFolder, exist_ok=True)

#                 #data for georeferencing
#                 with open(imagePath.replace('jpg', 'jgw'), 'r') as jgwFile:
#                     lines = jgwFile.readlines()
#                 pixelSizeX = float(lines[0].strip())
#                 rotationX = float(lines[1].strip())
#                 rotationY = float(lines[2].strip())
#                 pixelSizeY = float(lines[3].strip())
#                 topLeftXGeo = float(lines[4].strip())
#                 topLeftYGeo = float(lines[5].strip())

#                 for row, col in chunksOfInterest:
#                     #setting cases when point of interest is at the edges
#                     if row == 0:
#                         topRow = 0
#                     else:
#                         topRow = row - 1
#                     if col == 0:
#                         topCol = 0
#                     else:
#                         topCol = col - 1
#                     topX = topCol * smallChunkSize
#                     topY = topRow * smallChunkSize

#                     #setting case if there are overlaps in the image
#                     if topX + largeChunkSize > width:
#                         topX = width - largeChunkSize
#                     if topY + largeChunkSize > height:
#                         topY = height - largeChunkSize

#                     box = (topX, topY, topX + largeChunkSize, topY + largeChunkSize)
#                     cropped = originalImage.crop(box)
#                     cropped.save(f"{outputFolder}/{uniqueImageIdentifier}chunkOfInterest_{row}_{col}.jpg")
#                     with open(f"{outputFolder}/{uniqueImageIdentifier}chunkOfInterest_{row}_{col}.jgw", 'w') as jgwFile:
#                         jgwFile.write(f"{pixelSizeX:.10f}\n")
#                         jgwFile.write(f"{rotationX:.10f}\n")
#                         jgwFile.write(f"{rotationY:.10f}\n")
#                         jgwFile.write(f"{pixelSizeY:.10f}\n")
#                         jgwFile.write(f"{(topLeftXGeo + topX * pixelSizeX):.10f}\n")
#                         jgwFile.write(f"{(topLeftYGeo + topY * pixelSizeY):.10f}\n")

#                 print(f"Chunks saved in: {os.path.abspath(outputFolder)}")
#             except Exception as e:
#                 print(f"Error opening {imagePath}: {e}")


# boundBoxSegmentation(inputFolder)