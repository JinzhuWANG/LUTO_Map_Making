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
out_png = 'Rasters\lumap_2050_2024_02_14__13_34_11.png'
center, bounds = process_raster(initial_tif=init_tif,
                                reclass_dict=reclassify_dict,
                                color_dict=color_dict,
                                final_path=out_png)


m = folium.Map(center, zoom_start=3,zoom_control=False)

img = folium.raster_layers.ImageOverlay(
        name="Mercator projection SW",
        image=out_png,
        bounds=bounds,
        opacity=0.6,
        interactive=True,
        cross_origin=False,
        zindex=1,
    )

img.add_to(m)
m




