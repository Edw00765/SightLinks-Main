from ultralytics import YOLO
from osgeo import gdal, osr
from PIL import Image
from tqdm import tqdm
import numpy as np
import os
import json
import sys
import re


# Load a model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from georeference.georeference import georeferenceTIF, georefereceJGW, BNGtoLatLong

def getOriginalImageName(filename):
    """Extract original image name from segmented filename"""
    # Remove row and column information (e.g., '_r1_c1')
    return re.sub(r'_r\d+_c\d+$', '', filename)

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

def predictionJGW(predictionThreshold=0.25, saveLabeledImage=False, outputType="0", outputFolder="run/output", modelType="n"):
    modelPath = f"models/yolo-{modelType}.pt"
    model = YOLO(modelPath)  # load an official model
    
    # Dictionary to store all detections and their confidence grouped by original image
    imageDetections = {}
    # First, process all images and group detections
    with tqdm(total=(len(os.listdir(outputFolder))//2), desc="Creating Oriented Bounding Box") as pbar:
        for image in os.listdir(outputFolder):
            if not image.endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            imagePath = os.path.join(outputFolder, image)
            try:
                allPointsList = []
                allConfidenceList = []
                results = model(imagePath, save=saveLabeledImage, conf=predictionThreshold, iou=0.9, 
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
                        listOfPoints = georefereceJGW(x1,y1,x2,y2,x3,y3,x4,y4,imagePath)
                        longLatList = BNGtoLatLong(listOfPoints)
                        allPointsList.append(longLatList)
                
                if allPointsList:
                    # Get original image name
                    originalImage = getOriginalImageName(os.path.splitext(image)[0])
                    
                    # Add detections to the group
                    if originalImage not in imageDetections:
                        # Index 0 will contain the coordinates, while index 1 will contain it's confidence. They are related based on their index.
                        imageDetections[originalImage] = [[],[]]
                    imageDetections[originalImage][0].extend(allPointsList)
                    imageDetections[originalImage][1].extend(allConfidenceList)
                
                os.remove(imagePath)
                os.remove(imagePath.replace('jpg', 'jgw'))
                pbar.update(1)
            except Exception as e:
                print(f"Error processing {imagePath}: {e}")
    
    # Now save the grouped detections
    if outputType == "0":
        # Save as JSON
        jsonOutput = []
        for originalImage, coordAndConf in imageDetections.items():
            jsonOutput.append({
                "image": f"{originalImage}.jpg",
                "coordinates": coordAndConf[0],
                "confidence": coordAndConf[1]
            })
        
        jsonPath = os.path.join(outputFolder, "output.json")
        with open(jsonPath, 'w') as file:
            json.dump(jsonOutput, file, indent=2)
        print(f"\nJSON output saved to: {jsonPath}")
    else:
        # Save as TXT files
        for originalImage, coordAndConf in imageDetections.items():
            saveTXTOutput(outputFolder, originalImage, coordAndConf[0], coordAndConf[1])
        print(f"\nTXT files saved to: {outputFolder}")
    
    print(f"Processed {len(imageDetections)} original images")

##########################################################################################################

def predictionTIF(predictionThreshold=0.25, saveLabeledImage=False, outputType="0", outputFolder="run/output", modelType="n"):
    modelPath = f"models/yolo-{modelType}.pt"
    model = YOLO(modelPath)  # load an official model
    
    # Dictionary to store all detections and their confidence grouped by original image
    imageDetections = {}
    # First, process all images and group detections
    with tqdm(total=(len(os.listdir(outputFolder))), desc="Creating Oriented Bounding Box") as pbar:
        for image in os.listdir(outputFolder):
            if not image.endswith(('.tif')):
                continue
            
            imagePath = os.path.join(outputFolder, image)
            try:
                allPointsList = []
                allConfidenceList = []

                pilImage = Image.open(imagePath)

                results = model(pilImage, save=saveLabeledImage, conf=predictionThreshold, iou=0.9, 
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
                        ##################################################################
                        
                        longLatList = georeferenceTIF(imagePath,x1,y1,x2,y2,x3,y3,x4,y4)
                        allPointsList.append(longLatList)
                
                if allPointsList:
                    # Get original image name
                    originalImage = getOriginalImageName(os.path.splitext(image)[0])
                    
                    # Add detections to the group
                    if originalImage not in imageDetections:
                        # Index 0 will contain the coordinates, while index 1 will contain it's confidence. They are related based on their index.
                        imageDetections[originalImage] = [[],[]]
                    imageDetections[originalImage][0].extend(allPointsList)
                    imageDetections[originalImage][1].extend(allConfidenceList)
                
                os.remove(imagePath)
                pbar.update(1)
            except Exception as e:
                print(f"Error processing {imagePath}: {e}")
    
    # Now save the grouped detections
    if outputType == "0":
        # Save as JSON
        jsonOutput = []
        for originalImage, coordAndConf in imageDetections.items():
            jsonOutput.append({
                "image": f"{originalImage}.tif",
                "coordinates": coordAndConf[0],
                "confidence": coordAndConf[1]
            })
        
        jsonPath = os.path.join(outputFolder, "output.json")
        with open(jsonPath, 'w') as file:
            json.dump(jsonOutput, file, indent=2)
        print(f"\nJSON output saved to: {jsonPath}")
    else:
        # Save as TXT files
        for originalImage, coordAndConf in imageDetections.items():
            saveTXTOutput(outputFolder, originalImage, coordAndConf[0], coordAndConf[1])
        print(f"\nTXT files saved to: {outputFolder}")
    
    print(f"Processed {len(imageDetections)} original images")


# print(georeferenceTIF("run/output/m_4007309_sw_18_030_20230820_r4_c1_r0_c2.tif", 100.5, 100.5, 200.5,200.5, 100.5, 200.5, 200, 100))

# predictionTIF(saveLabeledImage=True)