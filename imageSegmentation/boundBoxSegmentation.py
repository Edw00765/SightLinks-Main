from PIL import Image
from osgeo import gdal
from tqdm import tqdm
import os
import sys
#from tifResize import tile_resize, get_pixel_count

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from imageSegmentation.classificationSegmentation import classificationSegmentation

defaultLargeImageDimensions = 4000

def boundBoxSegmentationJGW(classificationThreshold=0.35, outputFolder = "run/output", extractDir = "run/extract"):
    with tqdm(total=(len(os.listdir(extractDir))//2), desc="Segmenting Images") as pbar:
        for inputFileName in os.listdir(extractDir):
            if inputFileName.endswith(('.png', '.jpg', '.jpeg')):
                try:
                    imagePath = os.path.join(extractDir, inputFileName)
                    originalImage = Image.open(imagePath)
                    width, height = originalImage.size
                    #Size of bounding box chunks
                    largeChunkSize = 1024
                    #Size of classification chunks
                    smallChunkSize = 256
                    #chunksOfInterest will be retrieved from kostas' program.
                    chunksOfInterest = classificationSegmentation(imagePath, classificationThreshold)
                    
                    # Get original filename without extension
                    baseName = os.path.splitext(inputFileName)[0]
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
                        
                        # Create output filenames using original name plus row and column
                        outputImage = f"{outputFolder}/{baseName}_r{row}_c{col}.jpg"
                        outputJGW = f"{outputFolder}/{baseName}_r{row}_c{col}.jgw"
                        
                        cropped.save(outputImage)
                        with open(outputJGW, 'w') as file:
                            file.write(f"{pixelSizeX:.10f}\n")
                            file.write(f"{rotationX:.10f}\n")
                            file.write(f"{rotationY:.10f}\n")
                            file.write(f"{pixelSizeY:.10f}\n")
                            file.write(f"{(topLeftXGeo + topX * pixelSizeX):.10f}\n")
                            file.write(f"{(topLeftYGeo + topY * pixelSizeY):.10f}\n")
                        pbar.update(1)
                except Exception as e:
                    print(f"Error opening {imagePath}: {e}")


def boundBoxSegmentationTIF(classificationThreshold=0.35, outputFolder = "run/output", extractDir = "run/extract"):
    os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "YES"
    gdal.SetConfigOption("GDAL_MAX_IMAGE_PIXELS", "100000000000")
    with tqdm(total=(len(os.listdir(extractDir))), desc="Segmenting Images") as pbar:
        for inputFileName in os.listdir(extractDir):
                if inputFileName.endswith(('.tif')):
                    try:
                        
                        imagePath = os.path.join(extractDir, inputFileName)
                        print(imagePath)
                        dataset = gdal.Open(imagePath, gdal.GA_ReadOnly)
                        if dataset is None:
                            raise Exception(f"Failed to open {imagePath}")
                        
                        # Get the image dimensions
                        width = dataset.RasterXSize
                        height = dataset.RasterYSize
                        
                        # Get the georeference data (this will be used to preserve georeferencing)
                        geoTransform = dataset.GetGeoTransform()
                        projection = dataset.GetProjection()

                        # Size of bounding box chunks
                        largeChunkSize = 1024
                        smallChunkSize = 256
                        
                        # Chunks of interest will be retrieved from another program (classificationSegmentation)
                        chunksOfInterest = classificationSegmentation(imagePath, classificationThreshold)

                        # Get original filename without extension
                        baseName = os.path.splitext(inputFileName)[0]
                        os.makedirs(outputFolder, exist_ok=True)

                        for row, col in chunksOfInterest:
                            # Set cases when point of interest is at the edges
                            topRow = row - 1
                            topCol = col - 1
                            topX = topCol * smallChunkSize - smallChunkSize / 2 if topCol > 0 else 0  # Top left x
                            topY = topRow * smallChunkSize - smallChunkSize / 2 if topRow > 0 else 0  # Top left y

                            # Handle overlap cases at the edges of the image
                            if topX + largeChunkSize > width:
                                topX = width - largeChunkSize
                            if topY + largeChunkSize > height:
                                topY = height - largeChunkSize

                            # Convert the pixel coordinates to georeferenced coordinates
                            georeferencedTopX = geoTransform[0] + topX * geoTransform[1] + topY * geoTransform[2]
                            georeferencedTopY = geoTransform[3] + topX * geoTransform[4] + topY * geoTransform[5]
                            
                            # Use GDAL to create the cropped image, preserving georeference
                            outputImage = f"{outputFolder}/{baseName}_r{row}_c{col}.tif"
                            gdal.Translate(outputImage, dataset, srcWin=[topX, topY, largeChunkSize, largeChunkSize], 
                                        projWin=[georeferencedTopX, georeferencedTopY, geoTransform[0] + (topX + largeChunkSize) * geoTransform[1], geoTransform[3] + (topY + largeChunkSize) * geoTransform[5]], 
                                        format="GTiff", metadataOptions=["COMPRESS=LZW"])

                            pbar.update(1)
                    except Exception as e:
                        print(f"Error opening {imagePath}: {e}")