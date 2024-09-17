import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import contextily as ctx
from pyproj import Transformer
import math
import pandas as pd

def convert_to_decimal_degrees(coordinate):
    """
    Converts a coordinate string in degrees and minutes (e.g., "022-09.57E") to decimal degrees.
    
    Parameters:
    coordinate (str): A string representing the latitude or longitude in degrees and minutes
    
    Returns:
    float: Decimal degrees representation of the input coordinate
    """
    if "N" in coordinate or "S" in coordinate:
        direction = 'N' if 'N' in coordinate else 'S'
        coordinate = coordinate.replace('N', '').replace('S', '')
    elif "E" in coordinate or "W" in coordinate:
        direction = 'E' if 'E' in coordinate else 'W'
        coordinate = coordinate.replace('E', '').replace('W', '')
    
    degrees, minutes = coordinate.split('-')
    degrees = float(degrees)
    minutes = float(minutes)
    
    decimal_degrees = degrees + minutes / 60.0
    
    if direction == 'S' or direction == 'W':
        decimal_degrees = -decimal_degrees
    
    return decimal_degrees

def process_feature(feature_data, feature_type, default_description="No Description"):
    """
    Process a feature object and return the appropriate GeoDataFrame-compatible format.
    
    Parameters:
    feature_data (dict): A dictionary representing a feature with Coordinates and Attributes.
    feature_type (str): The type of the feature (e.g., 'Point', 'LineString').
    default_description (str): A default description to use if none is provided.
    
    Returns:
    dict: A dictionary ready to be used in a GeoDataFrame, with geometry and attributes.
    """
    if feature_type == "Point":
        latitude = feature_data.get("Coordinates", {}).get("Latitude")
        longitude = feature_data.get("Coordinates", {}).get("Longitude")
        
        if latitude and longitude:
            lat_dd = convert_to_decimal_degrees(latitude)
            lon_dd = convert_to_decimal_degrees(longitude)
            geometry = Point(lon_dd, lat_dd)
            
            return {
                "featureType": feature_data.get("Type"),
                "geometry": geometry,
                "Description": feature_data.get("Type", default_description)  # Use the 'Type' field or default description
            }
    elif feature_type == "LineString":
        coordinates = feature_data.get("Coordinates")
        
        if isinstance(coordinates, list):
            line_coords = [(convert_to_decimal_degrees(coord["Longitude"]), convert_to_decimal_degrees(coord["Latitude"])) for coord in coordinates]
            geometry = LineString(line_coords)
            
            return {
                "featureType": feature_data.get("Type"),
                "geometry": geometry,
                "Description": feature_data.get("Type", default_description)  # Use the 'Type' field or default description
            }

    return None

def s57_to_geodataframe(s57_json):
    """
    Converts an S-57 JSON payload into a GeoDataFrame.
    
    Parameters:
    s57_json (dict): The S-57 JSON payload
    
    Returns:
    GeoDataFrame: A GeoDataFrame with features and spatial data
    """
    data = []
    
    for section in s57_json.get("Notices to Mariners", {}).get("Sections", []):
        for notice_key, notice_value in section.items():
            if isinstance(notice_value, dict) and "Features" in notice_value:
                for feature in notice_value["Features"]:
                    processed_feature = process_feature(feature, "Point")
                    if processed_feature:
                        data.append(processed_feature)
            if isinstance(notice_value, dict) and "Actions" in notice_value:
                for action in notice_value["Actions"]:
                    feature = action["Feature"]
                    # Determine if the feature is a point or line based on its coordinates
                    if isinstance(feature["Coordinates"], list):
                        processed_feature = process_feature(feature, "LineString")
                    else:
                        processed_feature = process_feature(feature, "Point")
                    
                    if processed_feature:
                        data.append(processed_feature)
    
    if not data:
        print("Warning: No features were extracted from the JSON.")
        return None
    
    # Convert to GeoDataFrame and add a default 'Description' column if not present
    gdf = gpd.GeoDataFrame(pd.DataFrame(data), geometry="geometry")

    # Check if 'Description' column exists, otherwise add it
    if 'Description' not in gdf.columns:
        gdf['Description'] = "No Description Available"
    
    return gdf

def s57_to_geodataframe(s57_json):
    """
    Converts an S-57 JSON payload into a GeoDataFrame.
    
    Parameters:
    s57_json (dict): The S-57 JSON payload
    
    Returns:
    GeoDataFrame: A GeoDataFrame with features and spatial data
    """
    data = []
    
    for section in s57_json.get("Notices to Mariners", {}).get("Sections", []):
        for notice_key, notice_value in section.items():
            if isinstance(notice_value, dict) and "Features" in notice_value:
                for feature in notice_value["Features"]:
                    processed_feature = process_feature(feature, "Point")
                    if processed_feature:
                        data.append(processed_feature)
            if isinstance(notice_value, dict) and "Actions" in notice_value:
                for action in notice_value["Actions"]:
                    feature = action["Feature"]
                    # Determine if the feature is a point or line based on its coordinates
                    if isinstance(feature["Coordinates"], list):
                        processed_feature = process_feature(feature, "LineString")
                    else:
                        processed_feature = process_feature(feature, "Point")
                    
                    if processed_feature:
                        data.append(processed_feature)
    
    if not data:
        print("Warning: No features were extracted from the JSON.")
        return None
    
    gdf = gpd.GeoDataFrame(pd.DataFrame(data), geometry="geometry",
                                   crs="EPSG:4326"  # WGS84 (Latitude/Longitude)
                                   )
    
    return gdf, data

def create_nautical_chart_image_with_latlong(gdf, data, output_file, zoom_level=12, use_openseamap=True):
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


# Example usage:
s57_json = {
  "Notices to Mariners": {
    "Title": "Swedish Notices to Mariners No. 1031",
    "Date": "2024-09-04",
    "Description": "This section includes all updates and corrections for the relevant nautical charts in Swedish waters. These changes are provided by the Swedish Maritime Administration and are essential for safe navigation.",
    "Sections": [
    #   {
    #     "Title": "The Quark",
    #     "Description": "Chart correction for light and depth changes in the Quark region.",
    #     "Notice_18701": {
    #       "Chart": "42",
    #       "Location": "Nykarleby",
    #       "Action": "Delete",
    #       "Features": [
    #         {
    #           "Type": "Depth",
    #           "Depth": 3.5,
    #           "Coordinates": {
    #             "Latitude": "63-30.28N",
    #             "Longitude": "022-09.57E"
    #           }
    #         }
    #       ]
    #     }
    #   },
      {
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
    #   },
    #   {
    #     "Title": "Northern Baltic",
    #     "Description": "Various updates on buoyage, lights, and rock features in the Northern Baltic area.",
    #     "Notice_18231": {
    #       "Chart": "621",
    #       "Location": "Bråviken, Marviken",
    #       "Actions": [
    #         {
    #           "Action": "Delete",
    #           "Feature": {
    #             "Type": "Special Purpose Spar Buoy",
    #             "Coordinates": {
    #               "Latitude": "58-33.376N",
    #               "Longitude": "016-50.163E"
    #             }
    #           }
    #         },
    #         {
    #           "Action": "Delete",
    #           "Feature": {
    #             "Type": "Maritime Limit Line",
    #             "Coordinates": [
    #               { "Latitude": "58-33.385N", "Longitude": "016-49.860E" },
    #               { "Latitude": "58-33.370N", "Longitude": "016-50.160E" },
    #               { "Latitude": "58-33.260N", "Longitude": "016-50.110E" }
    #             ]
    #           }
    #         },
    #         {
    #           "Action": "Delete",
    #           "Feature": {
    #             "Type": "Leading Light F R (occas)",
    #             "Coordinates": [
    #               { "Latitude": "58-32.952N", "Longitude": "016-50.479E" },
    #               { "Latitude": "58-33.047N", "Longitude": "016-50.515E" }
    #             ]
    #           }
    #         }
    #       ]
    #     },
    #     "Notice_18504": {
    #       "Chart": "621",
    #       "Location": "Arkösund, Lindöja",
    #       "Action": "Insert",
    #       "Features": [
    #         {
    #           "Type": "Underwater Rock",
    #           "Coordinates": {
    #             "Latitude": "58-31.874N",
    #             "Longitude": "016-56.055E"
    #           },
    #           "DepthContour": "3m"
    #         }
    #       ]
    #     }
    #   },
    #   {
    #     "Title": "Lake Mälaren and Södertälje Canal",
    #     "Description": "Updates regarding underwater rocks, bridges, and restrictions for Lake Mälaren and the Södertälje Canal.",
    #     "Notice_18596": {
    #       "Chart": "113",
    #       "Location": "Stora Askholmen",
    #       "Action": "Insert",
    #       "Feature": {
    #         "Type": "Rock Awash",
    #         "Coordinates": {
    #           "Latitude": "59-28.742N",
    #           "Longitude": "016-41.756E"
    #         }
    #       }
    #     },
    #     "Notice_18698": {
    #       "Chart": "6141",
    #       "Location": "Liljeholmsbron Bridge",
    #       "Action": "Bridge Survey",
    #       "Dates": {
    #         "Start": "2024-09-09",
    #         "End": "2024-09-11"
    #       },
    #       "Contact": {
    #         "VHFChannel": "16/68",
    #         "CallSign": "SFE2577"
    #       }
    #     },
    #     "Notice_18706": {
    #       "Chart": "111",
    #       "Location": "Kärsön, Nockebybron Bridge",
    #       "Action": "Bridge closed for pleasure craft due to technical problems",
    #       "End": "2024-09-30",
    #       "Details": "Bridge will still open for cargo ships."
    #     }
       }
    ]
  }
}


gdf, data = s57_to_geodataframe(s57_json)
print(gdf)


create_nautical_chart_image_with_latlong(gdf, data, 'nautical_chart_with_corrected_bounds.png', zoom_level=14, use_openseamap=True)