# SightLink-Main

Assumptions made:
- The JGW file is in the same directory as the JPEG file.
- The XML file is in the same directory as the JPEG file.
- The JGW file contains the following parameters in the following order: pixel_size_x, rotation_x, rotation_y, pixel_size_y, upper_left_x, upper_left_y.
- The XML file contains the following fields: copyright, km_reference, date_flown, coordinates, lens_focal_length, resolution.
- From srsName="osgb:BNG" in XML, assuming that we are using british national grid coordinate system by default. 
    This script just converts it to latitude, longitude at the end. 

    If we want to georeference using lat,lon to begin with, we either convert to BNG at the start or add separate logic for lat,lon.
    Defined box is lost upon georeferencing. Did not add anything currently to prevent this as it would mean having more than lat, lon coordinates.

Current status: Needs better testing and integration.  
                JGW and XML file names and paths need to be provided. 
                Integration will probably use `pixel_to_geo_with_transform` function for one coordinate/box at a time, not provide a whole directory.  
                    Remove/simplify the directory logic as needed.  
