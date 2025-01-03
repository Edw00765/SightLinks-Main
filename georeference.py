import os
import json
import math
import pyproj
import xml.etree.ElementTree as ET

'''
Assumptions made:
- The JGW file contains the following parameters in the following order: pixel_size_x, rotation_x, rotation_y, pixel_size_y, upper_left_x, upper_left_y.
- The XML file contains the following fields: copyright, km_reference, date_flown, coordinates, lens_focal_length, resolution.
- British national grid coordinate system by default (because srsName="osgb:BNG" in XML).
    Latitude, longitude conversion done in 1 line at the end of georeferencing using method bng_to_latlon.

NOTE:
- Defined box is lost upon georeferencing. Did not add anything currently to prevent this as it would mean having more than lat, lon coordinates as output.
- JGW and XML file names and directories need to be provided.
- Integration will probably call the method `pixel_to_geo_with_transform`.
- Kept XML data for potential copyright related reasons. It has nothing to do with the georeferencing.
'''

class Georeferencing:
    def __init__(self, jgw_file, xml_file):
        # Coordinate systems
        self.bng = pyproj.CRS("EPSG:27700")  # British National Grid (BNG)
        self.wgs84 = pyproj.CRS("EPSG:4326")  # WGS84 (latitude, longitude)

        # Create a transformer to convert between BNG and WGS84
        self.transformer = pyproj.Transformer.from_crs(self.bng, self.wgs84, always_xy=True)

        # Load JGW and XML data
        self.jgw_params = self.parse_jgw(jgw_file)
        self.metadata = self.parse_xml_metadata(xml_file)

    def bng_to_latlon(self, x_bng, y_bng):
        """
        Convert British National Grid (BNG) coordinates to latitude and longitude (WGS84).
        """
        lon, lat = self.transformer.transform(x_bng, y_bng)
        return lat, lon  # Return in (latitude, longitude)

    def parse_jgw(self, jgw_file):
        """
        Parse the JGW file and extract transformation parameters.
        """
        if not os.path.exists(jgw_file):
            raise FileNotFoundError(f"{jgw_file} not found.")

        with open(jgw_file, 'r') as f:
            jgw = [float(line.strip()) for line in f.readlines()]

        pixel_size_x = jgw[0]  # Pixel size in x-direction
        rotation_x = jgw[1]    # Rotation (x-axis)
        rotation_y = jgw[2]    # Rotation (y-axis)
        pixel_size_y = jgw[3]  # Pixel size in y-direction
        upper_left_x = jgw[4]  # Upper-left x-coordinate
        upper_left_y = jgw[5]  # Upper-left y-coordinate

        return pixel_size_x, rotation_x, rotation_y, pixel_size_y, upper_left_x, upper_left_y

    def parse_xml_metadata(self, xml_file):
        """
        Parse the XML metadata file to extract useful information.
        """
        if not os.path.exists(xml_file):
            raise FileNotFoundError(f"{xml_file} not found.")

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            metadata = {}

            namespace = {'osgb': 'http://www.ordnancesurvey.co.uk/xml/namespaces/osgb', 'gml': 'http://www.opengis.net/gml'}
            metadata['copyright'] = root.findtext('osgb:copyright', default='N/A', namespaces=namespace)
            metadata['km_reference'] = root.findtext('osgb:kmReference', default='N/A', namespaces=namespace)
            metadata['date_flown'] = root.findtext('osgb:dateFlown', default='N/A', namespaces=namespace)
            metadata['coordinates'] = root.find('osgb:kmRectangle/osgb:Rectangle/gml:coordinates', namespaces=namespace).text if root.find('osgb:kmRectangle/osgb:Rectangle/gml:coordinates', namespaces=namespace) is not None else 'N/A'
            metadata['lens_focal_length'] = root.find('osgb:lensFocalLength', namespaces=namespace).text if root.find('osgb:lensFocalLength', namespaces=namespace) is not None else 'N/A'
            metadata['resolution'] = root.find('osgb:resolution', namespaces=namespace).text if root.find('osgb:resolution', namespaces=namespace) is not None else 'N/A'

            return metadata
        except ET.ParseError:
            raise ValueError(f"Error parsing {xml_file}. Invalid XML structure.")

    def pixel_to_geo(self, pixel_x, pixel_y):
        """
        Converts pixel coordinates to georeferenced coordinates using JGW parameters.
        """
        pixel_size_x, rotation_x, rotation_y, pixel_size_y, upper_left_x, upper_left_y = self.jgw_params

        # Apply affine transformation (rotation + translation)
        x_geo = (pixel_x * pixel_size_x) + (pixel_y * rotation_x) + upper_left_x
        y_geo = (pixel_y * pixel_size_y) + (pixel_x * rotation_y) + upper_left_y

        return x_geo, y_geo

    def pixel_to_geo_with_transform(self, pixel_x, pixel_y, center, height, rotation_angle):
        """
        Converts pixel coordinates to georeferenced coordinates considering rotation, scaling, and translation.
        """
        pixel_size_x, rotation_x, rotation_y, pixel_size_y, upper_left_x, upper_left_y = self.jgw_params

        center_x, center_y = center
        width = height  # Assuming square region for simplicity

        # Translate pixel coordinates to be relative to the center
        rel_x = pixel_x - center_x
        rel_y = pixel_y - center_y

        # Apply rotation transformation
        theta = math.radians(rotation_angle)
        rotated_x = rel_x * math.cos(theta) - rel_y * math.sin(theta)
        rotated_y = rel_x * math.sin(theta) + rel_y * math.cos(theta)

        # Reapply translation
        translated_x = rotated_x + center_x
        translated_y = rotated_y + center_y

        # Convert pixel coordinates to georeferenced coordinates
        x_geo = (translated_x * pixel_size_x) + (translated_y * rotation_x) + upper_left_x
        y_geo = (translated_y * pixel_size_y) + (translated_x * rotation_y) + upper_left_y

        # Convert BNG coordinates (x_geo, y_geo) to latitude/longitude
        lat, lon = self.bng_to_latlon(x_geo, y_geo)

        return lat, lon

    def get_georeferenced_coordinates(self, initial_x, initial_y, center, height, rotation):
        """
        NOTE: Main method to call to get georeferenced coordinates.
        """
        lat, lon = self.pixel_to_geo_with_transform(initial_x, initial_y, center, height, rotation)
        return {'latitude': lat, 'longitude': lon}


# Example usage
# May find helpful to show what needs modification when integrating
if __name__ == "__main__":
    # Paths to your JGW and XML files
    jgw_file = r'C:\Users\Arif\Downloads\georeference\example.jgw'
    xml_file = r'C:\Users\Arif\Downloads\georeference\example.xml'

    # Initialize the Georeferencing object
    geo_ref = Georeferencing(jgw_file, xml_file)

    # Call the method to get georeferenced coordinates (arguments are just placeholders: the real ones to be given on integration)
    initial_x = 500
    initial_y = 500
    center = (500, 500)
    height = 100    
    rotation = 15

    result = geo_ref.get_georeferenced_coordinates(initial_x, initial_y, center, height, rotation)

    print("Georeferenced Coordinates:", result)
