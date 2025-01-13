To execute:
    1. setup the virtual environment by first installing it in SightLink-Main
    2. install all of the requirements in requirements.txt into the venv
    3. run the venv
    4. execute main.py
    
SIGHTLINK-MAIN consists of four segments:
    classificationScreening:
        This folder should contain vgg16_binary_classifier_duo.pth, and if it isn't there, please download it first and place it in this folder.

        The only file of interest for now is Classify.py, as this is the file which contains the methods to determine the classification. This file contains the method which receives a PIL image, and checks if it contains any crossing or not. If it does contain a crossing, it will simply return True, False otherwise.
    
    georeference:
        Simply contains one file which is used to georeference the output of orientedBoundingBox.

    imageSegmentation:
        Contains the original data input, and two files to segment images to the needs of our classification model and YOLO model.

        ClassificationSegmentation.py contains a method which takes the raw input files and segments the images into 256x256 images, it then calls the classification model into all of these smaller chunks and saves which row and column it was in. It then returns all of them once the image is done being processed

        BoundBoxSegmentation.py contains a method which calls classificationSegmentation(), then after retrieving the row and column of interest, it segments the original image to 1024x1024, with that small 256x256 chunk in the center. It saves this to be used as an input for orientedBoundingBox, and it also saves a corresponding jgw file for each new segment.

    orientedBoundingBox:
        in test/test.py, it contains the prediction method which will load a YOLO model and retrieve all of the bounding box from an image. It will receive the 4 corners of a crossing and store it into a list, where each item contains the image filename, and all of the coordinates of a bounding box. This list is then written to output.json.

in main.py:
    set the inputFolder, classificationThreshold, and boundingBoxThreshold. The higher these threshold, the less likely that it will make a wrong bounding box, but it is more likely for it to miss some crossings. To improve, we need the improve the YOLO model by having even more training data.
