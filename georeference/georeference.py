from pyproj import Transformer
from osgeo import gdal, osr

def georefereceJGW(x1,y1,x2,y2,x3,y3,x4,y4,pixelSizeX,pixelSizeY,topLeftXGeo,topLeftYGeo):
    x1 = topLeftXGeo + pixelSizeX * x1
    y1 = topLeftYGeo + pixelSizeY * y1
    x2 = topLeftXGeo + pixelSizeX * x2
    y2 = topLeftYGeo + pixelSizeY * y2
    x3 = topLeftXGeo + pixelSizeX * x3
    y3 = topLeftYGeo + pixelSizeY * y3
    x4 = topLeftXGeo + pixelSizeX * x4
    y4 = topLeftYGeo + pixelSizeY * y4
    return([(x1,y1),(x2,y2),(x3,y3),(x4,y4)])


def BNGtoLatLong(listOfPoints):
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    longLatList = []
    for xBNG, yBNG in listOfPoints:
        long, lat = transformer.transform(xBNG, yBNG)
        longLatList.append((long, lat))
    return longLatList



def georeferenceTIF(croppedTifImage, x1,y1,x2,y2,x3,y3,x4,y4):
    geotransform = croppedTifImage.GetGeoTransform()
    if not geotransform:
        raise ValueError(f"No geotransform found in the file: {croppedTifImage}")
    projection = croppedTifImage.GetProjection()

    # Convert pixel coordinates to real-world coordinates in the file's CRS
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    x1 = origin_x + x1 * pixel_width + y1 * geotransform[2]
    y1 = origin_y + x1 * geotransform[4] + y1 * pixel_height
    x2 = origin_x + x2 * pixel_width + y2 * geotransform[2]
    y2 = origin_y + x2 * geotransform[4] + y2 * pixel_height
    x3 = origin_x + x3 * pixel_width + y3 * geotransform[2]
    y3 = origin_y + x3 * geotransform[4] + y3 * pixel_height
    x4 = origin_x + x4 * pixel_width + y4 * geotransform[2]
    y4 = origin_y + x4 * geotransform[4] + y4 * pixel_height

    # Set up transformation to WGS84 (latitude/longitude)
    source_crs = osr.SpatialReference()
    source_crs.ImportFromWkt(projection)

    target_crs = osr.SpatialReference()
    target_crs.ImportFromEPSG(4326)  # WGS84 EPSG code

    transform = osr.CoordinateTransformation(source_crs, target_crs)

    outputList = []
    lat1, lon1, _ = transform.TransformPoint(x1, y1)
    lat2, lon2, _ = transform.TransformPoint(x2, y2)
    lat3, lon3, _ = transform.TransformPoint(x3, y3)
    lat4, lon4, _ = transform.TransformPoint(x4, y4)
    outputList.append((lat1, lon1))
    outputList.append((lat2, lon2))
    outputList.append((lat3, lon3))
    outputList.append((lat4, lon4))

    return outputList