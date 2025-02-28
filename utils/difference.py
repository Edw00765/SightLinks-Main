import json
import os
from filterOutput import check_box_intersection



# current Issues for boxes in O(N^2) but not in rowCol Checking:
# for some reason, the O(N^2) solution has extra bounding boxes which should not exist. Consiering it is O(N^2), I dont know how it is there in this filter but not there in the rowcol Checking. Maybe YOLO might change each run?
# 


# Define file paths
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "../input")
nSquared = os.path.join(input_dir, "nSquaredOutput.json")
rowColCheck = os.path.join(input_dir, "rowColOutput.json")
output_file = os.path.join(input_dir, "inRowColNotNSquared.json")  # Output file path

# Load JSON data
with open(nSquared, "r") as f:
    nSquaredData = json.load(f)

with open(rowColCheck, "r") as f:
    rowColCheckData = json.load(f)

# Extract coordinate lists
rowColCheckData = rowColCheckData[0].get("coordinates", [])
nSquaredData = nSquaredData[0].get("coordinates", [])

def getDifference(rowColCheckData, nSquaredData):
    inN2 = []
    
    for boxA in rowColCheckData:
        for boxB in nSquaredData:
            if check_box_intersection(boxA, boxB):
                inN2.append(boxA)
                break  # Stop checking once a match is found

    # Filter out coordinates that exist in inRowColCheck
    difference_data = {
        "coordinates": [box for box in rowColCheckData if box not in inN2]
    }

    # Save to a file
    with open(output_file, "w") as f:
        json.dump(difference_data, f, indent=4)
    
    print(f"Difference saved to {output_file}")

# Run function
getDifference(rowColCheckData, nSquaredData)