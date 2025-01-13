from ultralytics import YOLO
import os
import json
import sys
# Load a model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Georeference.Georeference import georeferecePoints
from Georeference.Georeference import BNGtoLatLong


pathToProgram = "orientedBoundingBox/test/"

# def prediction():
#     model = YOLO(pathToProgram + "model.pt")  # load an official model

#     for image in os.listdir(pathToProgram + "test-data/images"):
#         imagePath = f"{pathToProgram}test-data/images/{image}"
#         results = model(imagePath, save=True, save_txt=True, conf=0.25, iou=1)  # predict on an image

def prediction(predictionThreshold=0.25):
    model = YOLO(pathToProgram + "model.pt")  # load an official model
    allOutput = []
    for image in os.listdir(pathToProgram + "test-data/images"):
        imagePath = f"{pathToProgram}test-data/images/{image}"
        if imagePath.endswith(('.png', '.jpg', '.jpeg')):
            try:
                allPointsList = []
                results = model(imagePath, save=False, save_txt=False, conf=predictionThreshold, iou=0.9, project="boundingBoxImages", name="run", exist_ok=True)  # predict on an image, to save an image, set save_txt to true and save to true. If want to override folders instead of creating new ones, set exist_ok to True
                
                print(results)
                for result in results:
                    #The xyxyxyxy contains the four edges in pixels, while the xyxyxyxyn contains the percentage
                    result = result.cpu()
                    for boxes in result.obb.xyxyxyxy:
                        x1, y1 = boxes[0]
                        x2, y2 = boxes[1]
                        x3, y3 = boxes[2]
                        x4, y4 = boxes[3]
                        listOfPoints = georeferecePoints(x1,y1,x2,y2,x3,y3,x4,y4,imagePath)

                        longLatList = BNGtoLatLong(listOfPoints)
                        allPointsList.append(longLatList)
                if allPointsList:
                    allOutput.append({
                        "image":image,
                        "coordinates":allPointsList
                    })
                os.remove(imagePath)
                os.remove(imagePath.replace('jpg', 'jgw'))
            except Exception as e:
                print(f"Error opening {imagePath}: {e}")
    with open("output.json", 'w') as file:
        json.dump(allOutput, file)

prediction()