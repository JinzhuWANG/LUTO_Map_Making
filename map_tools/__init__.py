import os
import pandas as pd
import numpy as np

import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject



# function to write colormap to tif
def hex_color_to_numeric(hex_color):
    # Remove the '#' character (if present)
    hex_color = hex_color.lstrip('#')

    # Get the red, green, blue, and (optional) alpha components
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    if len(hex_color) == 8:  # If the color includes an alpha channel
        alpha = int(hex_color[6:8], 16) 
        return red, green, blue, alpha
    else:
        return red, green, blue, 255
    
    
# function to convert hex color to numeric
def color_hex2num(csv_path='Assests/lumap_colors.csv',
                  color_code:str = None, 
                  color_hex:str = None):
    
    lu_colors = pd.read_csv(csv_path)
    lu_colors['color_num'] = lu_colors[color_hex].apply(lambda x: hex_color_to_numeric(x))
    lu_colors_dict = lu_colors.set_index(color_code)['color_num'].to_dict()  
    return lu_colors_dict

# function to reclasify a raster
def reclassify_raster(lu_tif:str,
                        reclass_dict:dict,
                        band:int = 1):
        """Reclassify a raster"""
    
        # get the file name without extension
        lu_base = os.path.basename(lu_tif).split('.')[0]
    
        # get the tif array and meta
        with rasterio.open(lu_tif) as src:
            lu_arr = src.read(band)
            lu_meta = src.meta
            lu_meta.update(count=1,compress='lzw',dtype='int8',nodata=-128)
            
            for k, v in reclass_dict.items():
                lu_arr[lu_arr == k] = v
 
        # write 4band array to tif
        with rasterio.open(f'Rasters/{lu_base}_reclassified.tiff', 'w', **lu_meta) as dst:
            dst.write(lu_arr, band)


# function to convert a 1-band arrary to 4-band (RGBA) array with colormap
def convert_1band_to_4band(lu_tif:str, 
                           color_dict:dict,
                           band:int = 1,
                           binary_color:bool = False):
    """Convert a 1-band array to 4-band (RGBA) array with colormap"""

    # check if the color_dict needs to be binarizd
    if binary_color:
        color_dict = {0:(19, 222, 222, 255), 1:(220, 16, 16,255)}

    # get the file name without extension
    lu_base = os.path.basename(lu_tif).split('.')[0]

    # get the tif array and meta
    with rasterio.open(lu_tif) as src:
        lu_arr = src.read(band)
        lu_meta = src.meta
        # set the color of nodata value to transparent
        color_dict[src.meta['nodata']] = (0, 0, 0, 0)

    # update meta
    lu_meta.update(count=4,compress='lzw',dtype='uint8',nodata=0)
    # convert the 1-band array to 4-band (RGBA) array
    arr_4band = np.zeros((lu_arr.shape[0], lu_arr.shape[1], 4), dtype='uint8') 
    
    # update the 4-band array with color_dict
    for k, v in color_dict.items():
        arr_4band[lu_arr == k] = v

    # convert HWC to CHW
    arr_4band = arr_4band.transpose(2, 0, 1)

    # write 4band array to tif
    with rasterio.open(f'Rasters/{lu_base}_colored.tiff', 'w', **lu_meta) as dst:
        dst.write(arr_4band)

# function to reproject a raster to Web Mercator        
def reproject_raster(in_path:str):
    
    # Get the file name without extension
    name_base = os.path.basename(in_path).split('.')[0]
    
    # Step 1: Open the original raster file
    with rasterio.open(in_path) as src:
        # Step 2: Define the target CRS - Web Mercator in this case
        dst_crs = 'EPSG:3857'

        # Step 3: Calculate the transformation and new dimensions
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)

        # Define the metadata for the new raster
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'compress':'lzw'
        })

        # Step 4: Create the new raster file for the output
        with rasterio.open(f'Rasters/{name_base}_Mercator.tiff', 'w', **kwargs) as dst:
            # Step 5: Reproject and write to the new raster
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)