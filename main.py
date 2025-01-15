from imageSegmentation.boundBoxSegmentation import boundBoxSegmentation
from orientedBoundingBox.predictOBB import prediction
from utils.extract import extract_files
from datetime import datetime
import os
import time
import sys
sys.dont_write_bytecode = True

def create_dir(run_dir):
    """Create and return timestamped output directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    i = 0
    while os.path.exists(run_dir+"/"+timestamp):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+str(i)
        i += 1
    output_dir = os.path.join(run_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def execute(uploadDir = "input", inputType = "0", classificationThreshold = 0.35, predictionThreshold = 0.5, saveLabeledImage = False, outputType = "0", yoloModelType = "n"):
    start_time = time.time()
    outputFolder = create_dir("run/output")
    extractDir = create_dir("run/extract")
    # Extract files if needed
    extract_files(inputType, uploadDir, extractDir)
    # Run segmentation and prediction
    boundBoxSegmentation(classificationThreshold, outputFolder, extractDir)
    prediction(predictionThreshold, saveLabeledImage, outputType, outputFolder, yoloModelType)
    print(f"Output saved to {outputFolder} as {outputType}.")
    print(f"Total time taken: {time.time() - start_time:.2f} seconds")