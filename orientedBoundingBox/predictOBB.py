from ultralytics import YOLO
from tqdm import tqdm
import os
import json
import sys
import re

# Load a model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from georeference.georeference import georeferecePoints
from georeference.georeference import BNGtoLatLong

def get_original_image_name(filename):
    """Extract original image name from segmented filename"""
    # Remove row and column information (e.g., '_r1_c1')
    return re.sub(r'_r\d+_c\d+$', '', filename)

def save_txt_output(outputFolder, image_name, coordinates):
    """Save coordinates to a TXT file with one bounding box per line"""
    txt_path = os.path.join(outputFolder, f"{image_name}.txt")
    
    with open(txt_path, 'w') as file:
        for coord_set in coordinates:
            # Format each point as "lon,lat" and join with spaces
            line = " ".join([f"{point[0]},{point[1]}" for point in coord_set])
            file.write(line + "\n")

def prediction(predictionThreshold=0.25, saveLabeledImage=False, outputType="0", outputFolder="run/output", modelType="n"):
    modelPath = f"models/yolo-{modelType}.pt"
    model = YOLO(modelPath)  # load an official model
    
    # Dictionary to store all detections grouped by original image
    image_detections = {}
    
    # First, process all images and group detections
    with tqdm(total=(len(os.listdir(outputFolder))//2), desc="Creating Oriented Bounding Box") as pbar:
        for image in os.listdir(outputFolder):
            if not image.endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            imagePath = os.path.join(outputFolder, image)
            try:
                allPointsList = []
                results = model(imagePath, save=saveLabeledImage, conf=predictionThreshold, iou=0.9, 
                              project=outputFolder+"/labeledImages", name="run", exist_ok=True, verbose=False)
                
                for result in results:
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
                    # Get original image name
                    original_image = get_original_image_name(os.path.splitext(image)[0])
                    
                    # Add detections to the group
                    if original_image not in image_detections:
                        image_detections[original_image] = []
                    image_detections[original_image].extend(allPointsList)
                
                os.remove(imagePath)
                os.remove(imagePath.replace('jpg', 'jgw'))
                pbar.update(1)
            except Exception as e:
                print(f"Error processing {imagePath}: {e}")
    
    # Now save the grouped detections
    if outputType == "0":
        # Save as JSON
        json_output = []
        for original_image, coordinates in image_detections.items():
            json_output.append({
                "image": f"{original_image}.jpg",
                "coordinates": coordinates
            })
        
        json_path = os.path.join(outputFolder, "output.json")
        with open(json_path, 'w') as file:
            json.dump(json_output, file, indent=2)
        print(f"\nJSON output saved to: {json_path}")
    else:
        # Save as TXT files
        for original_image, coordinates in image_detections.items():
            save_txt_output(outputFolder, original_image, coordinates)
        print(f"\nTXT files saved to: {outputFolder}")
    
    print(f"Processed {len(image_detections)} original images")