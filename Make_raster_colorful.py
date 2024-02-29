import pandas as pd
import folium
from rasterio.merge import merge

from map_tools import hex_color_to_numeric, process_raster
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
# Read the reclassify dictionary 
reclassify_dict = color_df.set_index('lu_code')['group_code'].to_dict()
# Get the color-desc dictionary
color_desc_dict = color_df.set_index('group_color_numeric')['group_desc'].to_dict()


###################################################################
#    Reclassify -> 1-band to 4-bands -> Reproject (Mercator)      #
###################################################################
init_tif = 'Rasters\lumap_2050_2024_02_14__13_34_11.tiff'
out_base = 'Rasters\lumap_2050_2024_02_14__13_34_11'
center,  bounds_wgs, bounds_mercator = process_raster(initial_tif=init_tif,
                                reclass_dict=reclassify_dict,
                                color_dict=val_color_dict,
                                final_path=out_base)


###################################################################
#       Merge processed map with basemap, create png map          #
###################################################################
create_png_map(tif_path=f"{out_base}_mercator.tif",
                color_desc_dict=color_desc_dict,
                basemap_path='Assests/basemap.tif',
                shapefile_path='Assests\AUS_adm\STE11aAust_mercator_simplified.shp',
                anno_text='''Precision Agriculture\nScenario: 1.5℃ (50%)\nYear: 2050''',
                save_path=f"{out_base}_mosaic.png")











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









