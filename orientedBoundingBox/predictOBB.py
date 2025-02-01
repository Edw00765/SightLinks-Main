from ultralytics import YOLO
import numpy as np
from osgeo import gdal, osr
from PIL import Image
from tqdm import tqdm
import os
import json
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from georeference.georeference import georeferenceTIF, georefereceJGW, BNGtoLatLong

def saveTXTOutput(outputFolder, imageName, coordinates, confidences=None):
    """Save coordinates and optional confidence scores to a TXT file with one bounding box per line"""
    txtPath = os.path.join(outputFolder, f"{imageName}.txt")
    
    with open(txtPath, 'w') as file:
        for i, coordSet in enumerate(coordinates):
            # Format each point as "lon,lat" and join with spaces
            line = " ".join([f"{point[0]},{point[1]}" for point in coordSet])
            # Add confidence score if available
            if confidences is not None and i < len(confidences):
                line += f" {confidences[i]}"
            file.write(line + "\n")

def predictionJGW(imageAndDatas, predictionThreshold=0.25, saveLabeledImage=False, outputFolder="run/output", modelType="n"):
    modelPath = f"models/yolo-{modelType}.pt"
    model = YOLO(modelPath)  # load an official model
    
    # Dictionary to store all detections and their confidence grouped by original image
    imageDetections = {}
    # First, process all images and group detections
    with tqdm(total=(len(imageAndDatas)), desc="Creating Oriented Bounding Box") as pbar:
        for baseName, croppedImage, pixelSizeX, pixelSizeY, topLeftXGeo, topLeftYGeo in imageAndDatas:
            try:
                allPointsList = []
                allConfidenceList = []
                results = model(croppedImage, save=saveLabeledImage, conf=predictionThreshold, iou=0.9, 
                            project=outputFolder+"/labeledImages", name="run", exist_ok=True, verbose=False)
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
                pbar.update(1)
            except Exception as e:
                print(f"Error processing {croppedImage}: {e}")
                pbar.update(1)
    return imageDetections



def predictionTIF(imageAndDatas, predictionThreshold=0.25, saveLabeledImage=False, outputFolder="run/output", modelType="n"):
    modelPath = f"models/yolo-{modelType}.pt"
    model = YOLO(modelPath)  # load an official model
    # Dictionary to store all detections and their confidence grouped by original image
    imageDetections = {}
    # First, process all images and group detections
    with tqdm(total=(len(imageAndDatas)), desc="Creating Oriented Bounding Box") as pbar:
        for baseName, croppedImage in imageAndDatas:
            try:
                allPointsList = []
                allConfidenceList = []

                #########################################################################################
                #There is a potential for big improvements here, but currently we have to convert to numpy, then PIL as the model does not support numpy array for some reason
                #This also does not save the images properly now, since now the file in memory does not have a specific name, therefore overriding the same name over and over again
                croppedImageArray = croppedImage.ReadAsArray()
                if croppedImageArray.ndim == 3:
                    croppedImageArray = np.moveaxis(croppedImageArray, 0, -1)
                PILImage = Image.fromarray(croppedImageArray)
                results = model(PILImage, save=saveLabeledImage, conf=predictionThreshold, iou=0.9, 
                              project=outputFolder+"/labeledImages", name="run", exist_ok=True, verbose=False)
                
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
                
                if allPointsList:
                    if baseName not in imageDetections:
                        # Index 0 will contain the coordinates, while index 1 will contain it's confidence. They are related based on their index.
                        imageDetections[baseName] = [[],[]]
                    imageDetections[baseName][0].extend(allPointsList)
                    imageDetections[baseName][1].extend(allConfidenceList)
                pbar.update(1)
            except Exception as e:
                print(f"Error processing {baseName}: {e}")
    return imageDetections