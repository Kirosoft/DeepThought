import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx

# Before and After data
before_data = [
    {"name": "Existing Dolphin", "lon": 17.93565, "lat": 62.63037},
    {"name": "Existing Dolphin", "lon": 17.93525, "lat": 62.63040},
    {"name": "Existing Spar Buoy", "lon": 17.93565, "lat": 62.63338},
    {"name": "Existing Spar Buoy", "lon": 17.93545, "lat": 62.63340},
    {"name": "Existing Spar Buoy", "lon": 17.93343, "lat": 62.63308},
    {"name": "Existing Spar Buoy", "lon": 17.93256, "lat": 62.63082},
]
after_data = [
    {"name": "New Dolphin (Port-hand)", "lon": 17.93565, "lat": 62.63037},
    {"name": "New Dolphin (Starboard-hand)", "lon": 17.93525, "lat": 62.63040},
    {"name": "Deleted Spar Buoy", "lon": 17.93565, "lat": 62.63338},
    {"name": "Deleted Spar Buoy", "lon": 17.93545, "lat": 62.63340},
    {"name": "New Spar Buoy (Port-hand)", "lon": 17.93808, "lat": 62.62693},
    {"name": "New Spar Buoy (Starboard-hand)", "lon": 17.93868, "lat": 62.62713},
]

# Create GeoDataFrames
before_gdf = gpd.GeoDataFrame(before_data, geometry=gpd.points_from_xy([d['lon'] for d in before_data], [d['lat'] for d in before_data]))
after_gdf = gpd.GeoDataFrame(after_data, geometry=gpd.points_from_xy([d['lon'] for d in after_data], [d['lat'] for d in after_data]))

# Set the CRS to WGS84 (EPSG:4326)
before_gdf.set_crs(epsg=4326, inplace=True)
after_gdf.set_crs(epsg=4326, inplace=True)

# Define a function to update the basemap using both OpenStreetMap and OpenSeaMap providers
def update_basemap_with_osm_and_openseamap(ax):
    """Fetch and update the basemap using OpenStreetMap and OpenSeaMap providers."""
    ctx.add_basemap(ax, crs=before_gdf.crs, source=ctx.providers.OpenStreetMap.Mapnik)
    ctx.add_basemap(ax, crs=before_gdf.crs, source=ctx.providers.OpenSeaMap, alpha=0.5)  # Adjust alpha for layer transparency

# Calculate the bounding box that includes all points (both before and after changes)
minx = min(before_gdf.total_bounds[0], after_gdf.total_bounds[0])
miny = min(before_gdf.total_bounds[1], after_gdf.total_bounds[1])
maxx = max(before_gdf.total_bounds[2], after_gdf.total_bounds[2])
maxy = max(before_gdf.total_bounds[3], after_gdf.total_bounds[3])

# Add a buffer to ensure all points are visible
buffer = 0.0005  # Adjust as needed for visibility

# Adjust the limits by adding/subtracting the buffer
minx_buffered = minx - buffer
miny_buffered = miny - buffer
maxx_buffered = maxx + buffer
maxy_buffered = maxy + buffer

# Adjusted common limits
common_xlim_buffered = (minx_buffered, maxx_buffered)
common_ylim_buffered = (miny_buffered, maxy_buffered)

# Set up the plot with the same initial view for both windows
fig, ax = plt.subplots(1, 2, figsize=(14, 7))

# Set aspect ratios to equal for both subplots
ax[0].set_aspect('equal')
ax[1].set_aspect('equal')

# Plot 'Before' on the left with buffered common limits
before_gdf.plot(ax=ax[0], color='blue', marker='o', markersize=50, label="Before Changes")
ax[0].set_title("Before Changes")
ax[0].set_xlim(common_xlim_buffered)
ax[0].set_ylim(common_ylim_buffered)
for x, y, label in zip(before_gdf.geometry.x, before_gdf.geometry.y, before_gdf['name']):
    ax[0].text(x, y, label, fontsize=8)

# Plot 'After' on the right with buffered common limits
after_gdf.plot(ax=ax[1], color='red', marker='o', markersize=50, label="After Changes")
ax[1].set_title("After Changes")
ax[1].set_xlim(common_xlim_buffered)
ax[1].set_ylim(common_ylim_buffered)
for x, y, label in zip(after_gdf.geometry.x, after_gdf.geometry.y, after_gdf['name']):
    ax[1].text(x, y, label, fontsize=8)

# Initial basemap rendering using both OpenStreetMap and OpenSeaMap
update_basemap_with_osm_and_openseamap(ax[0])
update_basemap_with_osm_and_openseamap(ax[1])

# Zoom factor for zoom in/out
zoom_factor = 0.8  # 20% zoom (reduce by factor of 0.8 for zoom-in)

# Function to zoom both axes
def zoom(zoom_in=True):
    factor = zoom_factor if zoom_in else 1 / zoom_factor
    for axis in ax:
        xlim = axis.get_xlim()
        ylim = axis.get_ylim()

        # Calculate new limits
        width = xlim[1] - xlim[0]
        height = ylim[1] - ylim[0]

        new_width = width * factor
        new_height = height * factor

        # Calculate new center
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        new_xlim = [x_center - new_width / 2, x_center + new_width / 2]
        new_ylim = [y_center - new_height / 2, y_center + new_height / 2]

        # Prevent going below certain latitude/longitude limits (i.e., latitude limits should remain within bounds)
        axis.set_xlim(new_xlim)
        axis.set_ylim(new_ylim)

    # Update the basemap after changing zoom
    update_basemap_with_osm_and_openseamap(ax[0])
    update_basemap_with_osm_and_openseamap(ax[1])
    plt.draw()

# Function to zoom in
def zoom_in(event):
    zoom(zoom_in=True)

# Function to zoom out
def zoom_out(event):
    zoom(zoom_in=False)

# Synchronize interactive zoom and pan
def sync_axes(event):
    """Sync the axes limits between the two subplots when zooming or panning."""
    if event.inaxes is None:
        return  # Ignore if the event happens outside the axes
    
    # Get the limits from the event axis
    xlim = event.inaxes.get_xlim()
    ylim = event.inaxes.get_ylim()

    # Apply the same limits to both axes
    for axis in ax:
        axis.set_xlim(xlim)
        axis.set_ylim(ylim)

    # Reapply the basemap updates for both subplots
    update_basemap_with_osm_and_openseamap(ax[0])
    update_basemap_with_osm_and_openseamap(ax[1])
    plt.draw()

# Add zoom in/out buttons
ax_zoom_in = plt.axes([0.81, 0.05, 0.08, 0.04])  # Position of the zoom in button
ax_zoom_out = plt.axes([0.71, 0.05, 0.08, 0.04])  # Position of the zoom out button

button_zoom_in = Button(ax_zoom_in, 'Zoom In')
button_zoom_out = Button(ax_zoom_out, 'Zoom Out')

# Connect the buttons to the zoom functions
button_zoom_in.on_clicked(zoom_in)
button_zoom_out.on_clicked(zoom_out)

# Connect the mouse event to sync axes on zoom and pan
fig.canvas.mpl_connect('button_release_event', sync_axes)

# Clean up the lat/lon axis labels to 5 decimal places
for axis in ax:
    axis.set_xlabel("Longitude")
    axis.set_ylabel("Latitude")
    axis.grid(True)
    axis.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.5f}'.format(val)))
    axis.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: '{:.5f}'.format(val)))

plt.tight_layout()
plt.show()
