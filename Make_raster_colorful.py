import pandas as pd
import folium
import rasterio

from map_tools import (color_hex2num, 
                       convert_1band_to_4band,
                       reclassify_raster,
                       reproject_raster)

# Read the color dictionary from the csv file
color_dict = color_hex2num(csv_path='Assests/lumap_colors.csv',color_code='group_code',color_hex='group_color_HEX')

# Read the reclassify dictionary from the csv file
reclassify_dict = pd.read_csv('Assests/lumap_colors.csv', 
                              index_col='lu_code')['group_code'].to_dict()

# Reclassify the raster
reclassify_raster(lu_tif='Rasters/lumap_2050_2024_02_14__13_34_11.tiff',
                  reclass_dict=reclassify_dict,
                  band=1)



convert_1band_to_4band(lu_tif='Rasters\lumap_2050_2024_02_14__13_34_11_reclassified.tiff',
                       color_dict=color_dict,
                       band=1,
                       binary_color=False)

reproject_raster('Rasters\lumap_2050_2024_02_14__13_34_11_reclassified_colored.tiff')


import matplotlib.pyplot as plt
import rasterio
from rasterio.warp import transform_bounds
from rasterio.coords import BoundingBox

# Overlay the colored raster on the map
merc = 'Rasters\lumap_2050_2024_02_14__13_34_11_reclassified_colored_Mercator.tiff'

with rasterio.open(merc) as src:
    bounds = src.bounds
    img = src.read()
    
    # Define the source and target coordinate reference systems
    src_crs = 'EPSG:3857'  # Mercator
    dst_crs = 'EPSG:4326'  # WGS84

    # Define your Mercator bounding box (left, bottom, right, top)
    mercator_bbox = bounds

    # Transform the bounding box to WGS84
    wgs84_bbox = transform_bounds(src_crs, dst_crs, *mercator_bbox)
    wgs84_bbox = BoundingBox(*wgs84_bbox)

    # Get the center of the bounding box
    center = [(wgs84_bbox.bottom + wgs84_bbox.top) / 2, 
              (wgs84_bbox.left + wgs84_bbox.right) / 2]
    
    # Use Matplotlib to save the generated image for overlay
    plt.savefig('Rasters\lumap_2050_2024_02_14__13_34_11_reclassified_colored_Mercator.png',
                bbox_inches='tight', pad_inches=0)


m = folium.Map([37, 0], zoom_start=1)

img = folium.raster_layers.ImageOverlay(
        name="Mercator projection SW",
        image=merc,
        bounds=wgs84_bbox,
        opacity=0.6,
        interactive=True,
        cross_origin=False,
        zindex=1,
    )

img.add_to(m)
folium.LayerControl().add_to(m)




