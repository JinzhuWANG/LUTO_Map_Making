import pandas as pd
import folium
import rasterio
from rasterio.merge import merge

from map_tools import (get_color_dict, 
                       hex_color_to_numeric, 
                       process_float_raster, 
                       process_int_raster)

from map_tools.map_making import create_png_map


###################################################################
#           Get reclassification and color dictionary             #
###################################################################

# Read the lu_code|lu_color|lu_desc records from the csv file
csv_path = 'Assests/lumap_colors.csv'
color_df = pd.read_csv(csv_path)

# Convert the HEX color codes to numeric
color_df['lu_color_numeric'] = color_df['group_color_HEX'].apply(hex_color_to_numeric)
color_df['group_color_numeric'] = color_df['group_color_HEX'].apply(hex_color_to_numeric)  

# Get the val-color dictionary
val_color_dict = color_df.set_index('group_code')['group_color_numeric'].to_dict()
reclassify_dict = color_df.set_index('lu_code')['group_code'].to_dict()
color_desc_dict = color_df.set_index('group_color_numeric')['group_desc'].to_dict()


###################################################################
#    Reclassify -> 1-band to 4-bands -> Reproject to Mercator     #
###################################################################
init_tif = 'Rasters\lumap_2050_2024_02_14__13_34_11.tiff'
out_base = 'Rasters\lumap_2050_2024_02_14__13_34_11'

# center -> the center of the raster, can be used for folium map
# bounds_wgs -> the bounds of the raster in WGS84, can be used for folium map
# bounds_mercator -> the bounds of the raster in Mercator, can be to download the basemap
center,  bounds_wgs, bounds_mercator = process_int_raster(initial_tif=init_tif,
                                reclass_dict=reclassify_dict,
                                color_dict=val_color_dict,
                                final_path=out_base)


###################################################################
#       Merge processed map with basemap, create png map          #
###################################################################
in_map_path = f"{out_base}_mercator.tif"
Au_shp = 'Assests\AUS_adm\STE11aAust_mercator_simplified.shp'
inmap_text = '''Precision Agriculture\nScenario: 1.5℃ (50%)\nYear: 2050'''
basemap_path = 'Assests/basemap.tif'
png_out_path = f"{out_base}_mosaic.png"

create_png_map(tif_path = in_map_path,
                color_desc_dict = color_desc_dict,
                basemap_path = basemap_path,
                shapefile_path = Au_shp,
                anno_text = inmap_text,
                save_path = png_out_path)


###################################################################
#       Merge processed map with basemap, create png map          #
###################################################################
tif_path = 'Rasters/Non-Ag_LU_00_Environmental Plantings_2050.tiff'
NLUM_mask = 'Assests/NLUM_2010-11_mask.tif'
save_base = 'Rasters/Non-Ag_LU_00_Environmental Plantings_2050'
var_colors_dict = get_color_dict(color_scheme ='YlOrRd')

center, bounds_for_folium, mercator_bbox = process_float_raster(
                    initial_tif=tif_path,
                     band=1, 
                     color_dict=var_colors_dict,
                     mask_path=NLUM_mask,
                     final_path=save_base)

    




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









