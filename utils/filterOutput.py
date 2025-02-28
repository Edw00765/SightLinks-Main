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
        baseName, _, _ = extractBaseNameAndCoords(nameWithRowCol)
        imageDetections.setdefault(baseName, [[], []])
        imageDetections[baseName][0].extend(imageDetectionsRowCol[nameWithRowCol][0])
        imageDetections[baseName][1].extend(imageDetectionsRowCol[nameWithRowCol][1])
    
    return imageDetections

def checkBoxIntersection(box_1, box_2, threshold=0.6):
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
    
def extractBaseNameAndCoords(baseNameWithRowCol):
    match = re.match(r"(.+?)__r(-?\d+)__c(-?\d+)", baseNameWithRowCol)
    if match:
        baseName = match.group(1)
        row = int(match.group(2))
        col = int(match.group(3))
        return baseName, row, col
    else:
        raise ValueError("Input string is not in the expected format.")
    

#This is the O(N^2) solution for the filtering
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
            if checkBoxIntersection(boxA, boxB, threshold=0.7):
                idxToRemove = i if allConfidenceList[i] <= allConfidenceList[j] else j
                toRemove.add(idxToRemove)

        allPointsList[:] = [box for i, box in enumerate(allPointsList) if i not in toRemove]
        allConfidenceList[:] = [conf for i, conf in enumerate(allConfidenceList) if i not in toRemove]


def removeDuplicateBoxesRC(imageDetectionsRowCol):
    with tqdm(total=len(imageDetectionsRowCol), desc="Filtering crosswalks") as pbar:
        for currentKeyToFilter in imageDetectionsRowCol:
            allPointsList, allConfidenceList = imageDetectionsRowCol[currentKeyToFilter]
            toRemove = set()
            baseName, row, col = extractBaseNameAndCoords(currentKeyToFilter)
            toRemoveNeighboringMap = {}

            for dRow in range(-5, 6):  # Check neighboring 11x11 grid
                for dCol in range(-5, 6):
                    if dRow == 0 and dCol == 0:
                        continue

                    newRow, newCol = row + dRow, col + dCol
                    neighboringChunk = f"{baseName}__r{newRow}__c{newCol}"
                    if neighboringChunk not in imageDetectionsRowCol:
                        continue
                    neighboringBoxes, neighboringConf = imageDetectionsRowCol[neighboringChunk]
                    toRemoveNeighboring = set()

                    for i, boxA in enumerate(allPointsList):
                        if i in toRemove:
                            continue
                        for j, boxB in enumerate(neighboringBoxes):
                            if j in toRemoveNeighboring:
                                continue

                            if checkBoxIntersection(boxA, boxB, threshold=0.7):
                                if allConfidenceList[i] <= neighboringConf[j]:
                                    toRemove.add(i)
                                    break
                                else:
                                    toRemoveNeighboring.add(j)
                                    break
                    if toRemoveNeighboring:
                        toRemoveNeighboringMap[neighboringChunk] = toRemoveNeighboringMap.get(neighboringChunk, set()).union(toRemoveNeighboring)

            for chunk, indices in toRemoveNeighboringMap.items():
                imageDetectionsRowCol[chunk][0] = [box for i, box in enumerate(imageDetectionsRowCol[chunk][0]) if i not in indices]
                imageDetectionsRowCol[chunk][1] = [conf for i, conf in enumerate(imageDetectionsRowCol[chunk][1]) if i not in indices]

            imageDetectionsRowCol[currentKeyToFilter][0] = [box for i, box in enumerate(allPointsList) if i not in toRemove]
            imageDetectionsRowCol[currentKeyToFilter][1] = [conf for i, conf in enumerate(allConfidenceList) if i not in toRemove]

            pbar.update(1)
