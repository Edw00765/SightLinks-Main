import unittest
import sys
import os
from osgeo import gdal, osr
from pyproj import Transformer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from georeference.georeference import georeferenceTIF, georefereceJGW, BNGtoLatLong

class TestGeoreferencingFunctions(unittest.TestCase):

    def test_georefereceJGW(self):
        # Test with simple inputs
        x1, y1, x2, y2, x3, y3, x4, y4 = 0, 0, 1, 0, 1, 1, 0, 1
        pixelSizeX, pixelSizeY = 10, -10
        topLeftXGeo, topLeftYGeo = 100, 200

        result = georefereceJGW(x1, y1, x2, y2, x3, y3, x4, y4, pixelSizeX, pixelSizeY, topLeftXGeo, topLeftYGeo)
        expected = [(100.0, 200.0), (110.0, 200.0), (110.0, 190.0), (100.0, 190.0)]
        self.assertEqual(result, expected)

        # Additional test cases
        result2 = georefereceJGW(2, 2, 3, 2, 3, 3, 2, 3, pixelSizeX, pixelSizeY, topLeftXGeo, topLeftYGeo)
        expected2 = [(120.0, 180.0), (130.0, 180.0), (130.0, 170.0), (120.0, 170.0)]
        self.assertEqual(result2, expected2)

        result3 = georefereceJGW(4, 4, 5, 4, 5, 5, 4, 5, pixelSizeX, pixelSizeY, topLeftXGeo, topLeftYGeo)
        expected3 = [(140.0, 160.0), (150.0, 160.0), (150.0, 150.0), (140.0, 150.0)]
        self.assertEqual(result3, expected3)

    def test_BNGtoLatLong(self):
        # Test with known BNG coordinates
        listOfPoints = [(530000, 180000), (540000, 181000), (550000, 182000)]
        result = BNGtoLatLong(listOfPoints)

        # Calculate expected values using the same transformer as the function
        transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
        expected = []
        for xBNG, yBNG in listOfPoints:
            long, lat = transformer.transform(xBNG, yBNG)
            expected.append((lat, long))

        self.assertEqual(result, expected)

    def test_georeferenceTIF(self):
        # Create a dummy GeoTIFF file for testing
        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create('dummy.tif', 10, 10, 1, gdal.GDT_Byte)
        geotransform = (530000, 10, 0, 180000, 0, -10)  # Adjusted to match BNG coordinates
        dataset.SetGeoTransform(geotransform)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(27700)  # BNG CRS
        dataset.SetProjection(srs.ExportToWkt())
        dataset = None  # Close the dataset

        # Open the dummy GeoTIFF file
        croppedTifImage = gdal.Open('dummy.tif')

        # Test with pixel coordinates
        x1, y1, x2, y2, x3, y3, x4, y4 = 0, 0, 1, 0, 1, 1, 0, 1
        result = georeferenceTIF(croppedTifImage, x1, y1, x2, y2, x3, y3, x4, y4)

        # Calculate expected values using the same logic as the function
        geotransform = croppedTifImage.GetGeoTransform()
        origin_x = geotransform[0]
        origin_y = geotransform[3]
        pixel_width = geotransform[1]
        pixel_height = geotransform[5]

        x1_geo = origin_x + x1 * pixel_width + y1 * geotransform[2]
        y1_geo = origin_y + x1 * geotransform[4] + y1 * pixel_height
        x2_geo = origin_x + x2 * pixel_width + y2 * geotransform[2]
        y2_geo = origin_y + x2 * geotransform[4] + y2 * pixel_height
        x3_geo = origin_x + x3 * pixel_width + y3 * geotransform[2]
        y3_geo = origin_y + x3 * geotransform[4] + y3 * pixel_height
        x4_geo = origin_x + x4 * pixel_width + y4 * geotransform[2]
        y4_geo = origin_y + x4 * geotransform[4] + y4 * pixel_height

        source_crs = osr.SpatialReference()
        source_crs.ImportFromWkt(croppedTifImage.GetProjection())
        target_crs = osr.SpatialReference()
        target_crs.ImportFromEPSG(4326)  # WGS84 EPSG code
        transform = osr.CoordinateTransformation(source_crs, target_crs)

        expected = []
        for x, y in [(x1_geo, y1_geo), (x2_geo, y2_geo), (x3_geo, y3_geo), (x4_geo, y4_geo)]:
            lat, lon, _ = transform.TransformPoint(x, y)
            expected.append((lat, lon))

        self.assertEqual(result, expected)

        # Additional test cases
        x1, y1, x2, y2, x3, y3, x4, y4 = 2, 2, 3, 2, 3, 3, 2, 3
        result2 = georeferenceTIF(croppedTifImage, x1, y1, x2, y2, x3, y3, x4, y4)

        x1_geo = origin_x + x1 * pixel_width + y1 * geotransform[2]
        y1_geo = origin_y + x1 * geotransform[4] + y1 * pixel_height
        x2_geo = origin_x + x2 * pixel_width + y2 * geotransform[2]
        y2_geo = origin_y + x2 * geotransform[4] + y2 * pixel_height
        x3_geo = origin_x + x3 * pixel_width + y3 * geotransform[2]
        y3_geo = origin_y + x3 * geotransform[4] + y3 * pixel_height
        x4_geo = origin_x + x4 * pixel_width + y4 * geotransform[2]
        y4_geo = origin_y + x4 * geotransform[4] + y4 * pixel_height

        expected2 = []
        for x, y in [(x1_geo, y1_geo), (x2_geo, y2_geo), (x3_geo, y3_geo), (x4_geo, y4_geo)]:
            lat, lon, _ = transform.TransformPoint(x, y)
            expected2.append((lat, lon))

        self.assertEqual(result2, expected2)

        # Clean up the dummy file
        os.remove('dummy.tif')

if __name__ == '__main__':
    unittest.main()