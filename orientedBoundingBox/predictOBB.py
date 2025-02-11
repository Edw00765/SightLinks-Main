from ultralytics import YOLO
import numpy as np
from osgeo import gdal, osr
from PIL import Image
from tqdm import tqdm
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from georeference.georeference import georeferenceTIF, georefereceJGW, BNGtoLatLong
from utils.filterOutput import removeDuplicateBoxesRC, combineChunksToBaseName

#We could combine these two functions into one, but would that be more difficult for future debugging? We might be able to change everything to JFW format

def predictionJGW(imageAndDatas, predictionThreshold=0.25, saveLabeledImage=False, outputFolder="run/output", modelType="n"):
    modelPath = f"models/yolo-{modelType}.pt"
    model = YOLO(modelPath)  # load an official model
    # Dictionary to store all detections and their confidence grouped by original image
    imageDetections = {}
    numOfSavedImages = 0
    # First, process all images and group detections
    with tqdm(total=(len(imageAndDatas)), desc="Creating Oriented Bounding Box") as pbar:
        for baseName, croppedImage, pixelSizeX, pixelSizeY, topLeftXGeo, topLeftYGeo in imageAndDatas:
            try:
                allPointsList = []
                allConfidenceList = []
                results = model(croppedImage, save=saveLabeledImage, conf=predictionThreshold, iou=0.01, 
                            project=outputFolder+"/labeledImages", name="run", exist_ok=True, verbose=False)
                if saveLabeledImage and os.path.exists(outputFolder+"/labeledImages/run/image0.jpg"):
                    os.rename(outputFolder+"/labeledImages/run/image0.jpg", outputFolder+f"/labeledImages/run/image{numOfSavedImages}.jpg")
                    numOfSavedImages += 1
                for result in results:
                    result = result.cpu()
                    for confidence in result.obb.conf:
                        allConfidenceList.append(confidence.item())
                    for boxes in result.obb.xyxyxyxy:
                        x1, y1 = boxes[0]
                        x2, y2 = boxes[1]
                        x3, y3 = boxes[2]
                        x4, y4 = boxes[3]
                        listOfPoints = georefereceJGW(x1,y1,x2,y2,x3,y3,x4,y4,pixelSizeX,pixelSizeY,topLeftXGeo,topLeftYGeo)
                        longLatList = BNGtoLatLong(listOfPoints)
                        allPointsList.append(longLatList)
                    if allPointsList:
                        if baseName not in imageDetections:
                            imageDetections[baseName] = [[],[]]
                        imageDetections[baseName][0].extend(allPointsList)
                        imageDetections[baseName][1].extend(allConfidenceList)
            except Exception as e:
                print(f"Error processing {croppedImage}: {e}")
            pbar.update(1)
    return imageDetections

def predictionTIF(imageAndDatas, predictionThreshold=0.25, saveLabeledImage=False, outputFolder="run/output", modelType="n"):
    modelPath = f"models/yolo-{modelType}.pt"
    model = YOLO(modelPath)  # load an official model
    # Dictionary to store all detections and their confidence grouped by original image
    imageDetections = {}
    numOfSavedImages = 1
    # First, process all images and group detections
    with tqdm(total=(len(imageAndDatas)), desc="Creating Oriented Bounding Box") as pbar:
        for baseName, croppedImage, _, _ in imageAndDatas:
            try:
                allPointsList = []
                allConfidenceList = []
                croppedImageArray = croppedImage.ReadAsArray()
                if croppedImageArray.ndim == 3:
                    croppedImageArray = np.moveaxis(croppedImageArray, 0, -1)
                PILImage = Image.fromarray(croppedImageArray)
                results = model(PILImage, save=saveLabeledImage, conf=predictionThreshold, iou=0.9, 
                              project=outputFolder+"/labeledImages", name="run", exist_ok=True, verbose=False)
                if saveLabeledImage and os.path.exists(outputFolder+"/labeledImages/run/image0.jpg"):
                    os.rename(outputFolder+"/labeledImages/run/image0.jpg", outputFolder+f"/labeledImages/run/image{numOfSavedImages}.jpg")
                    numOfSavedImages += 1
                for result in results:
                    result = result.cpu()
                    for confidence in result.obb.conf:
                        allConfidenceList.append(confidence.item())
                    for boxes in result.obb.xyxyxyxy:
                        x1, y1 = boxes[0].tolist()
                        x2, y2 = boxes[1].tolist()
                        x3, y3 = boxes[2].tolist()
                        x4, y4 = boxes[3].tolist()
                        longLatList = georeferenceTIF(croppedImage,x1,y1,x2,y2,x3,y3,x4,y4)
                        allPointsList.append(longLatList)                

                    if baseName not in imageDetections:
                        imageDetections[baseName] = [[],[]]
                    imageDetections[baseName][0].extend(allPointsList)
                    imageDetections[baseName][1].extend(allConfidenceList)
            except Exception as e:
                print(f"Error processing {baseName}: {e}")
            pbar.update(1)
    return imageDetections



#############################
# These versions have filtering built in
# def predictionJGW(imageAndDatas, predictionThreshold=0.25, saveLabeledImage=False, outputFolder="run/output", modelType="n"):
#     modelPath = f"models/yolo-{modelType}.pt"
#     model = YOLO(modelPath)  # load an official model
#     # Dictionary to store all detections and their confidence grouped by original image
#     imageDetectionsRowCol = {}
#     numOfSavedImages = 1
#     # First, process all images and group detections
#     with tqdm(total=(len(imageAndDatas)), desc="Creating Oriented Bounding Box") as pbar:
#         for baseName, croppedImage, pixelSizeX, pixelSizeY, topLeftXGeo, topLeftYGeo, row, col in imageAndDatas:
#             try:
#                 allPointsList = []
#                 allConfidenceList = []
#                 results = model(croppedImage, save=saveLabeledImage, conf=predictionThreshold, iou=0.01, 
#                             project=outputFolder+"/labeledImages", name="run", exist_ok=True, verbose=False)
#                 if saveLabeledImage and os.path.exists(outputFolder+"/labeledImages/run/image0.jpg"):
#                     os.rename(outputFolder+"/labeledImages/run/image0.jpg", outputFolder+f"/labeledImages/run/image{numOfSavedImages}.jpg")
#                     numOfSavedImages += 1
#                 for result in results:
#                     result = result.cpu()
#                     for confidence in result.obb.conf:
#                         allConfidenceList.append(confidence.item())
#                     for boxes in result.obb.xyxyxyxy:
#                         x1, y1 = boxes[0]
#                         x2, y2 = boxes[1]
#                         x3, y3 = boxes[2]
#                         x4, y4 = boxes[3]
#                         listOfPoints = georefereceJGW(x1,y1,x2,y2,x3,y3,x4,y4,pixelSizeX,pixelSizeY,topLeftXGeo,topLeftYGeo)
#                         longLatList = BNGtoLatLong(listOfPoints)
#                         allPointsList.append(longLatList)
#                     if allPointsList:
#                         baseNameWithRowCol = f"{baseName}_r{row}_c{col}"
#                         imageDetectionsRowCol[baseNameWithRowCol] = [allPointsList,allConfidenceList]
#                         removeDuplicateBoxesRC(imageDetectionsRowCol=imageDetectionsRowCol, baseName=baseName, row=row, col=col)
#             except Exception as e:
#                 print(f"Error processing {croppedImage}: {e}")
#             pbar.update(1)
#     imageDetections = combineChunksToBaseName(imageDetectionsRowCol=imageDetectionsRowCol)
#     return imageDetections

# # This version of predictionTIF has filtering
# def predictionTIF(imageAndDatas, predictionThreshold=0.25, saveLabeledImage=False, outputFolder="run/output", modelType="n"):
#     modelPath = f"models/yolo-{modelType}.pt"
#     model = YOLO(modelPath)  # load an official model
#     # Dictionary to store all detections and their confidence grouped by image, row, and column
#     imageDetectionsRowCol = {}
#     numOfSavedImages = 1
#     # First, process all images and group detections
#     with tqdm(total=(len(imageAndDatas)), desc="Creating Oriented Bounding Box") as pbar:
#         for baseName, croppedImage, row, col in imageAndDatas:
#             try:
#                 allPointsList = []
#                 allConfidenceList = []
#                 croppedImageArray = croppedImage.ReadAsArray()
#                 if croppedImageArray.ndim == 3:
#                     croppedImageArray = np.moveaxis(croppedImageArray, 0, -1)
#                 PILImage = Image.fromarray(croppedImageArray)
#                 results = model(PILImage, save=saveLabeledImage, conf=predictionThreshold, iou=0.9, 
#                               project=outputFolder+"/labeledImages", name="run", exist_ok=True, verbose=False)
#                 if saveLabeledImage and os.path.exists(outputFolder+"/labeledImages/run/image0.jpg"):
#                     os.rename(outputFolder+"/labeledImages/run/image0.jpg", outputFolder+f"/labeledImages/run/image{numOfSavedImages}.jpg")
#                     numOfSavedImages += 1
#                 for result in results:
#                     result = result.cpu()
#                     for confidence in result.obb.conf:
#                         allConfidenceList.append(confidence.item())
#                     for boxes in result.obb.xyxyxyxy:
#                         x1, y1 = boxes[0].tolist()
#                         x2, y2 = boxes[1].tolist()
#                         x3, y3 = boxes[2].tolist()
#                         x4, y4 = boxes[3].tolist()
#                         longLatList = georeferenceTIF(croppedImage,x1,y1,x2,y2,x3,y3,x4,y4)
#                         allPointsList.append(longLatList)
                
#                 if allPointsList:
#                     baseNameWithRowCol = f"{baseName}__r{row}__c{col}"
#                     imageDetectionsRowCol[baseNameWithRowCol] = [allPointsList,allConfidenceList]
                    
#             except Exception as e:
#                 print(f"Error processing {baseName}: {e}")
#             pbar.update(1)
#     removeDuplicateBoxesRC(imageDetectionsRowCol=imageDetectionsRowCol)
#     imageDetections = combineChunksToBaseName(imageDetectionsRowCol=imageDetectionsRowCol)
#     return imageDetections