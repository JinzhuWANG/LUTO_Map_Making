import pandas as pd
import folium
import rasterio

from map_tools import color_hex2num, process_raster



# Read the color dictionary from the csv file
color_dict = color_hex2num(csv_path='Assests/lumap_colors.csv',
                           color_code='group_code',
                           color_hex='group_color_HEX')

# Read the reclassify dictionary from the csv file
reclassify_dict = pd.read_csv('Assests/lumap_colors.csv', 
                              index_col='lu_code')['group_code'].to_dict()

init_tif = 'Rasters\lumap_2050_2024_02_14__13_34_11.tiff'
out_tif = 'Rasters\lumap_2050_2024_02_14__13_34_11_reclassified_colored_Mercator.tiff'
process_raster(initial_tif=init_tif,
               reclass_dict=reclassify_dict,
               color_dict=color_dict,
               final_path=out_tif)



import imageio
import rasterio
from rasterio.warp import transform_bounds
from rasterio.coords import BoundingBox

# Overlay the colored raster on the map
merc = 'Rasters\lumap_2050_2024_02_14__13_34_11_reclassified_colored_Mercator.tiff'

with rasterio.open(merc) as src:
    bounds = src.bounds
    img = src.read()  # HWC
    img_rgba = img.transpose(1, 2, 0)  # CHW -> HWC
    
    # Define the source and target coordinate reference systems
    src_crs = 'EPSG:3857'  # Mercator
    dst_crs = 'EPSG:4326'  # WGS84

    # Define your Mercator bounding box (left, bottom, right, top)
    mercator_bbox = bounds

    # Transform the bounding box to WGS84
    wgs84_bbox = transform_bounds(src_crs, dst_crs, *mercator_bbox)
    wgs84_bbox = BoundingBox(*wgs84_bbox)
    bounds_for_folium = [[wgs84_bbox.bottom, wgs84_bbox.left], 
                         [wgs84_bbox.top, wgs84_bbox.right]]

    # Get the center of the bounding box
    center = [(wgs84_bbox.bottom + wgs84_bbox.top) / 2, 
              (wgs84_bbox.left + wgs84_bbox.right) / 2]
    
    # Save the image to a file
    imageio.imsave('Rasters\lumap_2050_2024_02_14__13_34_11_reclassified_colored_Mercator.png', img_rgba)



merc_png = 'Rasters\lumap_2050_2024_02_14__13_34_11_reclassified_colored_Mercator.png'
m = folium.Map(center, zoom_start=3,zoom_control=False)

img = folium.raster_layers.ImageOverlay(
        name="Mercator projection SW",
        image=merc_png,
        bounds=bounds_for_folium,
        opacity=0.6,
        interactive=True,
        cross_origin=False,
        zindex=1,
    )

img.add_to(m)
m




