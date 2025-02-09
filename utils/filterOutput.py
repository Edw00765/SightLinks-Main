import math
from itertools import combinations

#To find the radius, I chose to use an eucliean approximation as it is alot faster than other methods like vincenty's formula

def isWithinRadius(lat1, lon1, lat2, lon2, radius=1.5):
    R = 6371000  # Earth radius in meters

    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Compute deltas
    delta_x = (lon2 - lon1) * math.cos((lat1 + lat2) / 2) * R
    delta_y = (lat2 - lat1) * R

    # Compute distance
    distance = math.sqrt(delta_x**2 + delta_y**2)

    return distance <= radius

def isBoxTheSameCrossing(boxA, boxB, radius):
    #if box1 is within box2, we return box1 so we know which to remove
    def checkBoxInside(box1, box2):
        min_lat2 = min(lat for lat, lon in box2)
        max_lat2 = max(lat for lat, lon in box2)
        min_lon2 = min(lon for lat, lon in box2)
        max_lon2 = max(lon for lat, lon in box2)

        near_count = 0  # Count of points near box2 corners
        inside_count = 0  # Count of points inside box2 bounding box

        for lat1, lon1 in box1:
            # Check if the point is within 2m of any corner in box2
            if any(isWithinRadius(lat1, lon1, lat2, lon2, radius) for lat2, lon2 in box2):
                near_count += 1
            # Check if the point is inside the bounding box of box2
            elif min_lat2 <= lat1 <= max_lat2 and min_lon2 <= lon1 <= max_lon2:
                inside_count += 1

    
        if near_count >= 3 or inside_count >= 3:
            print("redundant box:", box1)
            return box1
        return None
    
    return checkBoxInside(boxA, boxB) or checkBoxInside(boxB, boxA)


def removeDuplicateBoxes(imageDetections, radius=1.5):
    for baseName in imageDetections:
        allPointsList = imageDetections[baseName][0]
        allConfidenceList = imageDetections[baseName][1]
        while True:
            toRemove = set()
            foundRemoval = False
            for i, j in combinations(range(len(allPointsList)), 2):
                if i in toRemove or j in toRemove:
                    continue
                boxA = allPointsList[i]
                boxB = allPointsList[j]

                redundantBox = isBoxTheSameCrossing(boxA, boxB, radius=radius)
                if redundantBox:
                    idxToRemove = i if redundantBox == boxA else j
                    toRemove.add(idxToRemove)
                    foundRemoval = True

            # If no boxes were removed, break the loop
            if not foundRemoval:
                break

            allPointsList[:] = [box for i, box in enumerate(allPointsList) if i not in toRemove]
            allConfidenceList[:] = [conf for i, conf in enumerate(allConfidenceList) if i not in toRemove]
    

