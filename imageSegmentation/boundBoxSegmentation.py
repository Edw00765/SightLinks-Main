from PIL import Image
from osgeo import gdal
from tqdm import tqdm
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from imageSegmentation.classificationSegmentation import classificationSegmentation

defaultLargeImageDimensions = 4000
boundBoxChunkSize = 1024
classificationChunkSize = 256

def boundBoxSegmentationJGW(classificationThreshold=0.35, extractDir = "run/extract"):
    with tqdm(total=(len(os.listdir(extractDir))//2), desc="Segmenting Images") as pbar:
        imageAndDatas = []
        chunkSeen = set()
        for inputFileName in os.listdir(extractDir):
            if inputFileName.endswith(('.png', '.jpg', '.jpeg')):
                try:
                    imagePath = os.path.join(extractDir, inputFileName)
                    originalImage = Image.open(imagePath)
                    width, height = originalImage.size
                    chunksOfInterest = classificationSegmentation(inputFileName=imagePath, classificationThreshold=classificationThreshold, classificationChunkSize=classificationChunkSize)

                    #data for georeferencing
                    with open(imagePath.replace('jpg', 'jgw'), 'r') as jgwFile:
                        lines = jgwFile.readlines()
                    pixelSizeX = float(lines[0].strip())
                    pixelSizeY = float(lines[3].strip())
                    topLeftXGeo = float(lines[4].strip())
                    topLeftYGeo = float(lines[5].strip())

                    for row, col in chunksOfInterest:
                        #setting cases when point of interest is at the edges
                        topRow = row - 1
                        topCol = col - 1
                        topX = topCol * classificationChunkSize - classificationChunkSize / 2 if topCol > 0 else 0 #This is the top left x
                        topY = topRow * classificationChunkSize - classificationChunkSize / 2 if topRow > 0 else 0 #This is the top left y

                        #setting case if there are overlaps in the image
                        if topX + boundBoxChunkSize > width:
                            topX = width - boundBoxChunkSize
                        if topY + boundBoxChunkSize > height:
                            topY = height - boundBoxChunkSize

                        box = (topX, topY, topX + boundBoxChunkSize, topY + boundBoxChunkSize)
                        imageChunk = f"{inputFileName}{(topX, topY, boundBoxChunkSize)}"
                        if imageChunk in chunkSeen:
                            continue
                        chunkSeen.add(imageChunk)
                        cropped = originalImage.crop(box)
                        
                        topLeftXGeoInterest = topLeftXGeo + topX * pixelSizeX
                        topLeftYGeoInterest = topLeftYGeo + topY * pixelSizeY
                        imageAndDatas.append((inputFileName, cropped, pixelSizeX, pixelSizeY, topLeftXGeoInterest, topLeftYGeoInterest, row, col)) 
                except Exception as e:
                    print(f"Error opening {imagePath}: {e}")
            pbar.update(1)
        return imageAndDatas


def boundBoxSegmentationTIF(classificationThreshold=0.35, extractDir = "run/extract"):
    with tqdm(total=(len(os.listdir(extractDir))), desc="Segmenting Images") as pbar:
        imageAndDatas = []
        chunkSeen = set()
        for inputFileName in os.listdir(extractDir):
            if inputFileName.endswith(('.tif')):
                try:
                    imagePath = os.path.join(extractDir, inputFileName)
                    dataset = gdal.Open(imagePath, gdal.GA_ReadOnly)
                    if dataset is None:
                        raise Exception(f"Failed to open {imagePath}")
                    
                    width = dataset.RasterXSize
                    height = dataset.RasterYSize
                    # Get the georeference data (this will be used to preserve georeferencing)
                    geoTransform = dataset.GetGeoTransform()
                    chunksOfInterest = classificationSegmentation(inputFileName=imagePath, classificationThreshold=classificationThreshold, classificationChunkSize=classificationChunkSize)
                    # Get original filename without extension

                    for col, row in chunksOfInterest:
                        topRow = row - 1
                        topCol = col - 1
                        topX = topCol * classificationChunkSize - classificationChunkSize / 2 if topCol > 0 else 0  # Top left x
                        topY = topRow * classificationChunkSize - classificationChunkSize / 2 if topRow > 0 else 0  # Top left y
                        
                        if topX + boundBoxChunkSize > width:
                            topX = width - boundBoxChunkSize
                        if topY + boundBoxChunkSize > height:
                            topY = height - boundBoxChunkSize
                        # Convert the pixel coordinates to georeferenced coordinates
                        georeferencedTopX = geoTransform[0] + topX * geoTransform[1] + topY * geoTransform[2]
                        georeferencedTopY = geoTransform[3] + topX * geoTransform[4] + topY * geoTransform[5]
                        
                        # Use GDAL to create the cropped image, preserving georeference
                        imageChunk = f"{inputFileName}{(topX, topY, boundBoxChunkSize)}"
                        if imageChunk in chunkSeen:
                            print(col, row, "This has been seen before")
                            print(imageChunk)
                            continue
                        chunkSeen.add(imageChunk)
                        boundBoxInputImage = gdal.Translate("", dataset, srcWin=[topX, topY, boundBoxChunkSize, boundBoxChunkSize], 
                                    projWin=[georeferencedTopX, georeferencedTopY, geoTransform[0] + (topX + boundBoxChunkSize) * geoTransform[1], geoTransform[3] + (topY + boundBoxChunkSize) * geoTransform[5]], 
                                    format="MEM")
                        imageAndDatas.append((inputFileName, boundBoxInputImage, row, col))
                except Exception as e:
                    print(f"Error opening {imagePath}: {e}")
            pbar.update(1)
        return imageAndDatas