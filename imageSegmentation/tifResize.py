from osgeo import gdal
from PIL import Image
import os

def tile_resize(input_file, outputFolder, tile_width, tile_height):
    # Check if the file is accessible
    print(f"The file {input_file} is too large, segmenting it to smaller images.")
    baseName = os.path.splitext(input_file)[0]
    input_file = os.path.join(outputFolder, input_file)
    dataset = gdal.Open(input_file, gdal.GA_ReadOnly)
    if not dataset:
        raise FileNotFoundError(f"Failed to open file: {input_file}")

    width = dataset.RasterXSize
    height = dataset.RasterYSize
    band_count = dataset.RasterCount

    print(f"Image dimensions: {width} x {height}, Bands: {band_count}")

    # Ensure output directory exists
    os.makedirs(outputFolder, exist_ok=True)

    # Loop through tiles
    for row in range(0, height, tile_height):
        for col in range(0, width, tile_width):
            # Define the output tile path
            output_file = f"{outputFolder}/{baseName}_r{row // tile_height}_c{col // tile_width}.tif"
            current_path = os.getcwd()

            print(f"Current directory: {current_path}")
            # Compute the dimensions of the tile
            xDifference = 0
            yDifference = 0
            if col + tile_width > width:
                xDifference = col + tile_width - width
            if row + tile_height > height:
                yDifference = row + tile_height - height

            # Use gdal.Translate to extract tiles
            gdal.Translate(
                output_file,
                input_file,
                srcWin=[col - xDifference, row - yDifference, tile_width, tile_height],
                format="GTiff"  # Output format
            )

            print(f"Created tile: {output_file}")

    # Close the dataset
    dataset = None
    os.remove(input_file)

def get_pixel_count(image_path):
    # Open the image using Pillow
    Image.MAX_IMAGE_PIXELS = None

    with Image.open(image_path) as img:
        width, height = img.size  # Get the width and height of the image
        pixel_count = width * height
        return pixel_count
    
# print(get_pixel_count("input/m_4007309_sw_18_030_20230820.tif"))