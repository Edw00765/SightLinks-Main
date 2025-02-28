import folium
import json
import os

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "../input")
json_file = os.path.join(input_dir, "inRowColNotNSquared.json")

# Load JSON data
with open(json_file, "r") as f:
    data = json.load(f)

# Define the map center based on the first coordinate
map_center = [40.80891562675996, -73.93823464989758]

m = folium.Map(location=map_center, zoom_start=16)

# Extract coordinates and confidence values
coordinates = data[0]["coordinates"]
confidence_values = data[0]["confidence"]

# Add polygons for the squares and confidence markers
for i, (square, conf) in enumerate(zip(coordinates, confidence_values)):
    folium.Polygon(
        locations=square,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.4,
        popup=f"Confidence: {conf}",
    ).add_to(m)
    
    # Add a marker at the center of each square
    center_lat = sum(point[0] for point in square) / len(square)
    center_lon = sum(point[1] for point in square) / len(square)
    folium.Marker(
        location=[center_lat, center_lon],
        popup=f"Confidence: {conf}",
        icon=folium.Icon(color="blue"),
    ).add_to(m)

# Save the map to an HTML file
m.save("map_visualization.html")
print("Map saved as map_visualization.html")
