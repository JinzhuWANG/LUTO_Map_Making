import os
import pandas as pd
import folium
import rasterio
from rasterio.merge import merge

from map_tools import (hex_color_to_numeric, 
                       process_float_raster, 
                       process_int_raster)


from map_tools.map_making import create_png_map
from map_tools.helper import get_map_meta



###################################################################
#           Get reclassification and color dictionary             #
###################################################################

init_tif = 'Rasters/lumap_2050_2024_02_17__21_20_52.tiff'

# Get the metadata for map making
map_meta = get_map_meta()

csv_path = map_meta['csv_path']
data_type = map_meta['data_type']
legend_position = map_meta['legend_position']



###################################################################
#           Get reclassification and color dictionary             #
###################################################################


for idx, row in map_meta.iterrows():
    
    # Get the metadata for map making if map_type in init_tif
    if row['map_type'] in init_tif:
        
        csv_path = row['csv_path']
        data_type = row['data_type']
        legend_position = row['legend_position']
        
        color_df = pd.read_csv(csv_path)
        # Convert the HEX color codes to numeric
        color_df['lu_color_numeric'] = color_df['lu_color_HEX'].apply(hex_color_to_numeric)

        # Get the val-color dictionary
        val_color_dict = color_df.set_index('lu_code')['lu_color_numeric'].to_dict()
        
        # Get the color-description dictionary, if the data type is integer
        if data_type == 'integer':
            color_desc_dict = color_df.set_index('lu_color_numeric')['lu_desc'].to_dict()
        else:
            color_desc_dict = None


        ###################################################################
        #           1-band to 4-bands ----> Reproject to Mercator         #
        ###################################################################


        # center -> the center of the raster, can be used for folium map
        # bounds_wgs -> the bounds of the raster in WGS84, can be used for folium map
        # bounds_mercator -> the bounds of the raster in Mercator, can be to download the basemap
        center,  bounds_wgs, bounds_mercator = process_int_raster(initial_tif=init_tif, 
                                                                color_dict=val_color_dict,
                                                                map_type_idx=idx)







tif_path = 'Rasters/lucc_separate/Non-Ag_LU_00_Environmental Plantings_2050.tiff'
NLUM_mask = 'Assests/NLUM_2010-11_mask.tif'


center, bounds_for_folium, mercator_bbox = process_float_raster(
                                                initial_tif=tif_path,
                                                color_dict=var_colors_dict,
                                                mask_path=NLUM_mask)



###################################################################
#       Merge processed map with basemap, create png map          #
###################################################################
out_base = os.path.splitext(tif_path)[0]
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









