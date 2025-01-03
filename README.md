# Georeferencing

Assumptions made:
- The JGW file contains the following parameters in the following order: pixel_size_x, rotation_x, rotation_y, pixel_size_y, upper_left_x, upper_left_y.
- The XML file contains the following fields: copyright, km_reference, date_flown, coordinates, lens_focal_length, resolution.
- British national grid coordinate system by default (because srsName="osgb:BNG" in XML data used).
  - Latitude, longitude conversion done in 1 line at the end of georeferencing using method bng_to_latlon.

NOTE:
- Defined box is lost upon georeferencing. Did not add anything currently to prevent this as it would mean having more than lat, lon coordinates as output.
- JGW and XML file names (and possibly directories) need to be provided.
- Kept XML data for potential copyright related reasons. It has nothing to do with the georeferencing.

# Integration
- Call method `pixel_to_geo_with_transform`
- jgw and xml file paths need to be provided as is. This will likely need changing depending on how we plan to use it. 
- Modify logic requiring access to jgw file if it is not going to be given.
  - Instead of parsing a jgw simply saving relevant values in variables should do.
- See initialisation for an example call case (line 137)
