import math
from itertools import combinations
import re
from shapely.geometry import Polygon
import yaml
from pathlib import Path
from torchvision.ops import nms
from torch import is_tensor, tensor
from tqdm import tqdm

def combineChunksToBaseName(imageDetectionsRowCol):
    imageDetections = {}
    for nameWithRowCol in imageDetectionsRowCol:
        baseName, _, _ = extract_base_name_and_coords(nameWithRowCol)
        imageDetections.setdefault(baseName, [[], []])
        imageDetections[baseName][0].extend(imageDetectionsRowCol[nameWithRowCol][0])
        imageDetections[baseName][1].extend(imageDetectionsRowCol[nameWithRowCol][1])
    
    return imageDetections

def check_box_intersection(box_1, box_2, threshold=0.6):
    poly_1 = Polygon(box_1)
    poly_2 = Polygon(box_2)
    try:
        intersection_area = poly_1.intersection(poly_2).area
        union_area = poly_1.union(poly_2).area
        iou = intersection_area / union_area if union_area > 0 else 0

        scaled_iou = iou * (max(poly_1.area, poly_2.area) / min(poly_1.area, poly_2.area))
        return scaled_iou > threshold
    except:
        return False  # Return False if the intersection computation fails
    
def extract_base_name_and_coords(baseNameWithRowCol):
    match = re.match(r"(.+?)__r(-?\d+)__c(-?\d+)", baseNameWithRowCol)
    if match:
        baseName = match.group(1)
        row = int(match.group(2))
        col = int(match.group(3))
        return baseName, row, col
    else:
        raise ValueError("Input string is not in the expected format.")
    
def removeDuplicateBoxes(imageDetections):
    for baseName in imageDetections:
        allPointsList = imageDetections[baseName][0]
        allConfidenceList = imageDetections[baseName][1]
        toRemove = set()

        for i, j in combinations(range(len(allPointsList)), 2):
            if i in toRemove or j in toRemove:
                continue
            boxA = allPointsList[i]
            boxB = allPointsList[j]
            if check_box_intersection(boxA, boxB, threshold=0.7):
                idxToRemove = i if allConfidenceList[i] <= allConfidenceList[j] else j
                toRemove.add(idxToRemove)

        allPointsList[:] = [box for i, box in enumerate(allPointsList) if i not in toRemove]
        allConfidenceList[:] = [conf for i, conf in enumerate(allConfidenceList) if i not in toRemove]



def removeDuplicateBoxesRC(imageDetectionsRowCol):
    with tqdm(total=(len(imageDetectionsRowCol)), desc="Filtering crosswalks") as pbar:
        for currentKeyToFilter in imageDetectionsRowCol:
            allPointsList = imageDetectionsRowCol[currentKeyToFilter][0]
            allConfidenceList = imageDetectionsRowCol[currentKeyToFilter][1]
            toRemove = set()
            baseName, row, col = extract_base_name_and_coords(currentKeyToFilter)
            for i in range(len(allPointsList)): #Iterates through every single box within that row and column, then iterates through all possible intersections
                if i in toRemove:
                    continue
                boxA = allPointsList[len(allPointsList) - 1 - i]
                try:
                    for d_row in range(-4,5):  # row shifts, it needs to check an extra to 5 in the edge case that the segmentation still produces a duplicate at the edges
                        for d_col in range(-4,5):  # col shifts
                            if d_row == 0 and d_col == 0:
                                continue
                            new_row = int(row) + d_row
                            new_col = int(col) + d_col
                            neighboringChunk = f"{baseName}__r{new_row}__c{new_col}"
                            
                            if neighboringChunk not in imageDetectionsRowCol:
                                continue
                            neighboringBoxes, neighboringConf = imageDetectionsRowCol[neighboringChunk]
                            toRemoveNeighboring = set()
                            
                            for j in range(len(neighboringBoxes)):
                                boxB = neighboringBoxes[j]
                                if check_box_intersection(boxA, boxB, threshold=0.7):
                                    # I really dont know why changing this from <= to < solved it
                                    if allConfidenceList[i] < neighboringConf[j]:
                                        toRemove.add(i)
                                    else:
                                        toRemoveNeighboring.add(j)
                            
                            # Remove neighbor boxes outside the loop to prevent index shifting
                            if toRemoveNeighboring:
                                neighboringBoxes[:] = [box for x, box in enumerate(neighboringBoxes) if x not in toRemoveNeighboring]
                                neighboringConf[:] = [conf for x, conf in enumerate(neighboringConf) if x not in toRemoveNeighboring]
                except Exception as e:
                    print(f"there was an error in removeDuplicateBoxesRC: {e}")

            allPointsList[:] = [box for i, box in enumerate(allPointsList) if i not in toRemove]
            allConfidenceList[:] = [conf for i, conf in enumerate(allConfidenceList) if i not in toRemove]
            pbar.update(1)