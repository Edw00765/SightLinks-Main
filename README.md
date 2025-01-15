# SightLink

SightLink is a computer vision system designed to detect and georeference buildings in aerial imagery. It processes both Digimap and custom aerial imagery, providing oriented bounding boxes with geographical coordinates. The system uses a combination of image segmentation, YOLO-based detection, and georeferencing to accurately identify and locate buildings in aerial photographs.

## Features

- Supports both Digimap and custom aerial imagery
- Automatic extraction and handling of zip archives
- Building detection using YOLO-based model with oriented bounding boxes (OBB)
- Automatic georeferencing of detected buildings
- Multiple output formats (JSON/TXT)
- Progress tracking with detailed progress bars
- Organized output with timestamped directories
- Handles both single files and batch processing
- Automatic cleanup of temporary files

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Required Python packages (see requirements.txt)
- Sufficient disk space for image processing
- CUDA-capable GPU recommended for faster processing

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd SightLink-Main
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure the model file is present:
- Place `model.pt` in the `orientedBoundingBox/` directory

## Project Structure

```
SightLink-Main/
├── imageSegmentation/           # Image segmentation modules
│   ├── boundBoxSegmentation.py  # Segmentation for bounding box detection
│   └── classificationSegmentation.py  # Image classification segmentation
├── orientedBoundingBox/         # Building detection components
│   ├── model.pt                # YOLO model weights
│   └── predictOBB.py           # Prediction and output generation
├── georeference/               # Georeferencing utilities
│   └── georeference.py         # Coordinate conversion functions
├── utils/                      # Utility functions
│   └── extract.py             # File extraction and handling
├── run/                        # Runtime directories
│   └── output/                # Timestamped output directories
├── upload/                    # Input file directory
└── requirements.txt           # Python dependencies
```

## Usage

### Directory Setup

1. Create required directories if they don't exist:
```bash
mkdir -p upload run/output
```

2. Place input files in the upload directory:
   - For Digimap data (input_type="0"): Place zip files containing .jpg and .jgw files
   - For custom data (input_type="1"): Place either:
     - Individual .jpg and .jgw files
     - Zip files containing image data

### Running the Program

```python
from main import execute

# Required parameters
upload_dir = "upload"              # Directory containing input files
input_type = "0"                   # "0" for Digimap, "1" for custom data
classification_threshold = 0.35     # Threshold for building classification (0.0-1.0)
prediction_threshold = 0.5         # Threshold for bounding box detection (0.0-1.0)
save_labeled_image = False         # Save images with visualized bounding boxes
output_type = "0"                  # "0" for JSON output, "1" for TXT output

# Execute processing
execute(upload_dir, input_type, classification_threshold, 
        prediction_threshold, save_labeled_image, output_type)
```

### Output Formats

1. JSON Format (outputType="0")
   ```json
   [
     {
       "image": "image_name.jpg",
       "coordinates": [
         [[lon1,lat1], [lon2,lat2], [lon3,lat3], [lon4,lat4]],  # Building 1
         [[lon1,lat1], [lon2,lat2], [lon3,lat3], [lon4,lat4]]   # Building 2
       ]
     }
   ]
   ```

2. TXT Format (outputType="1")
   - Each line represents one building's coordinates:
   ```
   lon1,lat1 lon2,lat2 lon3,lat3 lon4,lat4
   lon1,lat1 lon2,lat2 lon3,lat3 lon4,lat4
   ```

### Output Directory Structure

```
run/output/YYYYMMDD_HHMMSS/  # Timestamp-based directory
├── output.json              # If JSON output selected
└── image_name.txt          # If TXT output selected (one per image)
```

## Processing Pipeline

1. File Extraction
   - Handles zip files and individual images
   - Filters out system files and unsupported formats
   - Organizes files for processing

2. Image Segmentation
   - Processes large aerial images
   - Prepares images for building detection

3. Building Detection
   - Uses YOLO model for oriented bounding box detection
   - Applies confidence thresholds for accurate detection

4. Georeferencing
   - Converts pixel coordinates to geographical coordinates
   - Uses .jgw files for accurate coordinate mapping

5. Output Generation
   - Creates timestamped output directory
   - Generates selected output format (JSON/TXT)
   - Cleans up temporary files

## Error Handling

- Skips incompatible files with warnings
- Handles missing or corrupt files gracefully
- Provides detailed error messages for troubleshooting
- Maintains processing state during batch operations

## Performance Considerations

- GPU acceleration recommended for faster processing
- Memory usage scales with image size
- Batch processing optimized for large datasets
- Progress bars provide estimated completion times

## License

[Add License Information]

## Contributors

[Add Contributors Information]

## Acknowledgments

- YOLO for object detection framework
- Ultralytics for YOLOv8 implementation
- [Add other acknowledgments]
