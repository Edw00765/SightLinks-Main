from ultralytics import YOLO
import os
import json
from pyproj import Transformer

# Load a model
pathToProgram = "orientedBoundingBox/test/"
def georeferecePoints(x1,y1,x2,y2,x3,y3,x4,y4,imagePath):
    try:
        with open(imagePath.replace('jpg', 'jgw'), 'r') as jgwFile:
            lines = jgwFile.readlines()
        pixelSizeX = float(lines[0].strip())
        pixelSizeY = float(lines[3].strip())
        topLeftXGeo = float(lines[4].strip())
        topLeftYGeo = float(lines[5].strip())
        x1 = topLeftXGeo + pixelSizeX * x1
        y1 = topLeftYGeo + pixelSizeY * y1
        x2 = topLeftXGeo + pixelSizeX * x2
        y2 = topLeftYGeo + pixelSizeY * y2
        x3 = topLeftXGeo + pixelSizeX * x3
        y3 = topLeftYGeo + pixelSizeY * y3
        x4 = topLeftXGeo + pixelSizeX * x4
        y4 = topLeftYGeo + pixelSizeY * y4
        return([(x1,y1),(x2,y2),(x3,y3),(x4,y4)])
    except Exception as e:
        print(f"There was an issue with opening {imagePath.replace('jpg', 'jgw')}: {e}")
        return(None)

def BNGtoLatLong(listOfPoints):
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    longLatList = []
    for xBNG, yBNG in listOfPoints:
        long, lat = transformer.transform(xBNG, yBNG)
        longLatList.append((long, lat))
    return longLatList


def prediction():
    model = YOLO(pathToProgram + "model.pt")  # load an official model

    for image in os.listdir(pathToProgram + "test-data/images"):
        imagePath = f"{pathToProgram}test-data/images/{image}"
        results = model(imagePath, save=True, save_txt=True, conf=0.25, iou=1)  # predict on an image


# def prediction():
#     model = YOLO(pathToProgram + "model.pt")  # load an official model

#     for image in os.listdir(pathToProgram + "test-data/images"):
#         imagePath = f"{pathToProgram}test-data/images/{image}"
#         if imagePath.endswith(('.png', '.jpg', '.jpeg')):
#             try:
#                 allOutput = []
#                 allPointsList = []
#                 results = model(imagePath, save=True, save_txt=True, conf=0.25, iou=1)  # predict on an image
#                 for result in results:
#                     #The xyxyxyxy contains the four edges in pixels, while the xyxyxyxyn contains the percentage
#                     result = result.cpu()

#                     for boxes in result.obb.xyxyxyxy:
#                         x1, y1 = boxes[0]
#                         x2, y2 = boxes[1]
#                         x3, y3 = boxes[2]
#                         x4, y4 = boxes[3]
#                         listOfPoints = georeferecePoints(x1,y1,x2,y2,x3,y3,x4,y4,imagePath)
#                         longLatList = BNGtoLatLong(listOfPoints)
#                         allPointsList.append(longLatList)
#                 allOutput.append({
#                     "image":image,
#                     "coordinates":allPointsList
#                 })
                    
#                 with open("output.json", 'w') as file:
#                     json.dump(allOutput, file)
#             except Exception as e:
#                 print(f"Error opening {imagePath}: {e}")

prediction()