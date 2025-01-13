from ImageSegmentation.BoundBoxSegmentation import boundBoxSegmentation
from OrientedBoundingBox.test.test import prediction

# inputFolder is needed by boundBoxSegmentation
inputFolder = "imageSegmentation/digimapData"
# classification threshold is used by boundBoxSegmentation to modify the threshold for the classification
classificationThreshold = 0.35
# predictionThreshold is used by prediction as a parameter to set a custom threshold for the bounding box model
predictionThreshold = 0.5

boundBoxSegmentation(inputFolder)
prediction(predictionThreshold)

# subprocess.run(["python3", "imageSegmentation/BoundBoxSegmentation.py"])
# subprocess.run(["python3", "orientedBoundingBox/test/test.py"])