import pandas as pd
import folium
import rasterio
from rasterio.merge import merge

from map_tools import color_hex2num, process_raster



# Read the color dictionary from the csv file
color_dict = color_hex2num(csv_path='Assests/lumap_colors.csv',
                           color_code='group_code',
                           color_hex='group_color_HEX')

# Read the reclassify dictionary from the csv file
reclassify_dict = pd.read_csv('Assests/lumap_colors.csv', 
                              index_col='lu_code')['group_code'].to_dict()

init_tif = 'Rasters\lumap_2050_2024_02_14__13_34_11.tiff'
out_base = 'Rasters\lumap_2050_2024_02_14__13_34_11'
center,  bounds_wgs, bounds_mercator = process_raster(initial_tif=init_tif,
                                reclass_dict=reclassify_dict,
                                color_dict=color_dict,
                                final_path=out_base)


def Hex2RGB(hex):
    hex = hex.lstrip('#')
    color_rgb = tuple(int(hex[i:i+2], 16)/255 for i in (0, 2, 4))
    return color_rgb



import matplotlib.pyplot as plt
import geopandas as gpd

import rasterio
from rasterio.plot import show
from rasterio.merge import merge
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.patches as mpatches



# Mosaic raster with basemap
tif_path = f"{out_base}_mercator.tif"
basemap_path = 'Assests/basemap.tif'
shapefile_path = 'Assests\AUS_adm\STE11aAust_mercator_simplified.shp'
save_path = f"{out_base}_mosaic.png"

color_dict = pd.read_csv('Assests/lumap_colors.csv',
            index_col='group_color_HEX')['group_desc'].to_dict()

patches = [ mpatches.Patch(color=Hex2RGB(k), label=v ) 
            for k, v in color_dict.items()]


with rasterio.open(tif_path) as src, rasterio.open(basemap_path) as base:
    # Mosaic the raster with the basemap
    mosaic, out_transform = merge([src, base])
    crs = src.crs

# Load the shapefile with GeoPandas
gdf = gpd.read_file(shapefile_path)


# Plotting
fig, ax = plt.subplots(figsize=(20, 20))  

x, y, arrow_length = 0.9, 0.9, 0.07

ax.add_artist(ScaleBar(1, 
                       "m", 
                       location="lower right",
                       border_pad=1,
                       fixed_units="km",
                       fixed_value=500,
                       box_color="skyblue", 
                       box_alpha=0))


# Display the mosaic raster
show(mosaic, ax=ax, transform=out_transform) 

# Plot the GeoDataFrame on top of the raster
# Note: You may need to adjust the 'edgecolor' and 'facecolor' as needed
gdf.boundary.plot(ax=ax, 
                  color='grey', 
                  linewidth=0.5, 
                  edgecolor='grey', 
                  facecolor='none')

ax.annotate('N', 
            xy=(x, y), 
            xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='black', width=30, headwidth=45),
            ha='center', 
            va='center', 
            fontsize=25,
            xycoords=ax.transAxes)


plt.legend(handles=patches, 
           bbox_to_anchor=(0.1, 0.2), 
           loc=2, 
           borderaxespad=0.,
           ncol=2, 
           fontsize=18,
           framealpha=0)


# Optionally remove axis
ax.set_axis_off()
plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0)








# m = folium.Map(center, zoom_start=3,zoom_control=False)

# img = folium.raster_layers.ImageOverlay(
#         name="Mercator projection SW",
#         image=out_png,
#         bounds=bounds,
#         opacity=0.6,
#         interactive=True,
#         cross_origin=False,
#         zindex=1,
#     )

# img.add_to(m)
# m









