import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import contextily as ctx
from pyproj import Transformer
import math

# Function to convert S-57 payload into plot-ready data
def s57_to_geodata(payloads):
    global data
    data = {'Description': [], 'Latitude': [], 'Longitude': [], 'Geometry': []}
    
    # Iterate over the payloads (assuming multiple operations in some cases)
    for payload in payloads:
        operations = payload.get("operations", [payload])  # If 'operations' is not present, treat it as a single operation
        
        for operation in operations:
            description = f"{operation['operation'].capitalize()} {operation['object']['type']} {operation['object'].get('subtype', '')}".strip()
            
            # Ensure 'coordinates' exists
            coords = operation['object'].get('coordinates', None)
            
            # Handle single point (dictionary with latitude and longitude)
            if isinstance(coords, dict):
                lat = coords.get('latitude')
                lon = coords.get('longitude')
                if lat is not None and lon is not None:
                    data['Description'].append(description)
                    data['Latitude'].append(lat)
                    data['Longitude'].append(lon)
                    data['Geometry'].append(Point(lon, lat))
            
            # Handle line coordinates (list of points)
            elif isinstance(coords, list):
                line_coords = [(coord['longitude'], coord['latitude']) for coord in coords if 'latitude' in coord and 'longitude' in coord]
                if line_coords:
                    data['Description'].append(description)
                    data['Latitude'].append(None)  # Not needed for lines
                    data['Longitude'].append(None)  # Not needed for lines
                    data['Geometry'].append(LineString(line_coords))
            
            # Handle leading line with start and end
            elif isinstance(coords, dict) and 'start' in coords and 'end' in coords:
                start = coords['start']
                end = coords['end']
                line_coords = [(start['longitude'], start['latitude']), (end['longitude'], end['latitude'])]
                data['Description'].append(description)
                data['Latitude'].append(None)
                data['Longitude'].append(None)
                data['Geometry'].append(LineString(line_coords))
    
    # Create a GeoDataFrame for plotting
    gdf = gpd.GeoDataFrame(
        data, 
        geometry=data['Geometry'],
        crs="EPSG:4326"  # WGS84 (Latitude/Longitude)
    )
    
    return gdf

def create_nautical_chart_image_with_latlong(gdf, output_file, zoom_level=12, use_openseamap=True):
    # Ensure the input GeoDataFrame is in WGS84 (lat/lon) to start with
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    # Reproject the GeoDataFrame to Web Mercator (EPSG:3857) for compatibility with basemaps
    gdf_mercator = gdf.to_crs(epsg=3857)

    # Get the total bounds of the data (in Web Mercator)
    bounds = gdf_mercator.total_bounds
    padding = 1000  # Define the padding to be added around the data

    # Apply padding to the bounds
    bounds_with_padding = [bounds[0] - padding, bounds[1] - padding, bounds[2] + padding, bounds[3] + padding]

    # Plot the points and lines on a basemap
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the geometries
    gdf_mercator.plot(ax=ax, color='red', marker='o', label=gdf['Description'], zorder=5)

    # Set zoom level manually for better alignment and pass the padded bounds to the basemap
    ctx.add_basemap(ax, crs=gdf_mercator.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik, zoom=zoom_level)

    # Optionally overlay OpenSeaMap for nautical features
    if use_openseamap:
        ctx.add_basemap(ax, crs=gdf_mercator.crs.to_string(), source=ctx.providers.OpenSeaMap, alpha=0.7, zoom=zoom_level)

    # Annotate points and lines with their descriptions
    for geom, label in zip(gdf_mercator.geometry, gdf['Description']):
        if isinstance(geom, Point):  # If it's a point, get the x and y directly
            ax.text(geom.x, geom.y + 50, label, fontsize=12, ha='right', color='blue')  # Added vertical space
        elif isinstance(geom, LineString):  # For lines, label at the midpoint
            x, y = geom.centroid.x, geom.centroid.y
            ax.text(x, y, label, fontsize=12, ha='center', color='blue')

    # Set plot limits based on the padded bounds
    ax.set_xlim([bounds_with_padding[0], bounds_with_padding[2]])
    ax.set_ylim([bounds_with_padding[1], bounds_with_padding[3]])

    # Reproject the axis labels to latitude and longitude (WGS84)
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

    def meter_to_latlon(x, y):
        lon, lat = transformer.transform(x, y)
        return lon, lat

    # Set ticks first to avoid the UserWarning
    xticks = ax.get_xticks()
    yticks = ax.get_yticks()

    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    # Set custom tick labels for latitude and longitude
    ax.set_xticklabels([f"{meter_to_latlon(x, yticks[0])[0]:.4f}°" for x in xticks])
    ax.set_yticklabels([f"{meter_to_latlon(xticks[0], y)[1]:.4f}°" for y in yticks])

    # Label axes in latitude and longitude
    ax.set_xlabel("Longitude (°)")
    ax.set_ylabel("Latitude (°)")

    # Save the image to a file
    plt.title('Nautical Chart with OpenSeaMap and OpenStreetMap (Lat/Long)', fontsize=15)
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()


# Example S-57 payloads
payloads = [{
        "Title": "Sea of Bothnia",
        "Description": "Light changes in the Port of Gävle, Sea of Bothnia.",
        "Notice_18176": {
          "Chart": "5342",
          "Location": "Port of Gävle",
          "Actions": [
            {
              "Action": "Delete",
              "Feature": {
                "Type": "Light",
                "Characteristic": "F3 Fl Y 3s",
                "Coordinates": {
                  "Latitude": "60-41.526N",
                  "Longitude": "017-13.816E"
                }
              }
            },
            {
              "Action": "Insert",
              "Feature": {
                "Type": "Light",
                "Characteristic": "F3 Fl G 3s",
                "Coordinates": {
                  "Latitude": "60-41.509N",
                  "Longitude": "017-13.805E"
                }
              }
            }
          ]
        }
      }]

# Convert S-57 payloads to GeoDataFrame
gdf_s57 = s57_to_geodata(payloads)

# You can now pass this GeoDataFrame (gdf_s57) to the plotting function for visualization.
print(gdf_s57)

# Run the function to generate the image
# Example GeoDataFrame with mixed Point and LineString geometries
create_nautical_chart_image_with_latlong(gdf_s57, 'nautical_chart_with_corrected_bounds.png', zoom_level=14, use_openseamap=True)