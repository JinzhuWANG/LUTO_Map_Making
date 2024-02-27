import os
import pandas as pd
import numpy as np

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.io import MemoryFile


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



def reclassify_raster_in_memory(src_path: str, 
                                reclass_dict: dict, 
                                band: int = 1) -> MemoryFile:
    """
    Reclassify a raster and return a MemoryFile.

    Parameters:
    src_path (str): 
        The path to the source raster dataset.
    reclass_dict (dict): 
        A dictionary mapping original values to reclassified values.
    band (int, optional): 
        The band index to read from the source raster. Default is 1.

    Returns:
        MemoryFile: The reclassified raster as a MemoryFile object.
    """
    with rasterio.open(src_path) as src:
        lu_arr = src.read(band)
        lu_meta = src.meta.copy()
        lu_meta.update(count=1, compress='lzw', dtype='int8', nodata=-128)
        
        for k, v in reclass_dict.items():
            lu_arr[lu_arr == k] = v

        # Create an in-memory file
        memfile = MemoryFile()
        with memfile.open(**lu_meta) as dst:
            dst.write(lu_arr, band)

    return memfile


def convert_1band_to_4band_in_memory(src_memfile: MemoryFile, 
                                     color_dict: dict, 
                                     binary_color: bool = False, 
                                     binary_dict: dict = None) -> MemoryFile:
    """Convert a 1-band array in a MemoryFile to 4-band (RGBA) and return a new MemoryFile.

    Args:
        src_memfile (MemoryFile): 
                The input MemoryFile containing the 1-band array.
        color_dict (dict): 
                A dictionary of color values for each class.
        binary_color (bool, optional): 
                If True, use the binary_dict to colorfy the raster. Defaults to False.
        binary_dict (dict, optional): 
                A dictionary of color values for binary classes. Only provided if binary_color is True.

    Returns:
        MemoryFile: The new MemoryFile containing the 4-band (RGBA) array.
    """
    if binary_color:
        color_dict = binary_dict
    
    with src_memfile.open() as src:
        lu_arr = src.read(1)    # Read the 1-band array, return a 2D array (HW)
        nodata = src.meta['nodata']
        color_dict[nodata] = (0, 0, 0, 0)  # Set the color of nodata value to transparent
        
        lu_meta = src.meta.copy()
        lu_meta.update(count=4, compress='lzw', dtype='uint8', nodata=0)

        arr_4band = np.zeros((lu_arr.shape[0], lu_arr.shape[1], 4), dtype='uint8')
        for k, v in color_dict.items():
            arr_4band[lu_arr == k] = v

        arr_4band = arr_4band.transpose(2, 0, 1)  # Convert HWC to CHW

    # Create a new in-memory file for the 4-band array
    memfile = MemoryFile()
    with memfile.open(**lu_meta) as dst:
        dst.write(arr_4band)

    return memfile


def reproject_raster_in_memory(src_memfile):
    """
    Reproject a raster in a MemoryFile to Web Mercator and return a new MemoryFile.

    Parameters:
        src_memfile (MemoryFile): The source raster in a MemoryFile.

    Returns:
        MemoryFile: The reprojected raster in a new MemoryFile.
    """
    dst_crs = 'EPSG:3857'  # Destination CRS
    
    with src_memfile.open() as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'compress': 'lzw'
        })

        memfile = MemoryFile()
        with memfile.open(**kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
    
    return memfile


# Function to reclassify -> colorfy -> reproject a raster
def process_raster(initial_tif:str=None, 
                   band=1, 
                   reclass_dict:dict=None, 
                   color_dict:dict=None,
                   binary_color:bool=False,
                   binary_dict:dict=None, 
                   final_path:str=None):
    """
    Process a raster file by reclassifying, coloring, and reprojecting it entirely in memory.
    
    Args:
        initial_tif (str): 
            Path to the initial raster file.
        band (int): 
            Band number to process (default is 1).
        reclass_dict (dict): 
            Dictionary mapping original pixel values to new values for reclassification (default is None).
        color_dict (dict): 
            Dictionary mapping pixel values to RGB color values for coloring (default is None).
        binary_color (bool):
            Flag indicating whether to use binary color mapping (default is False).
        binary_dict (dict):
            Dictionary mapping pixel values to binary values for binary color mapping (default is None).
        final_path (str): 
            Path to save the final processed raster file (default is None).
    """
    # Process the raster entirely in memory
    memfile_reclassified = reclassify_raster_in_memory(initial_tif, reclass_dict, band)
    memfile_colored = convert_1band_to_4band_in_memory(memfile_reclassified, color_dict, binary_color, binary_dict)
    memfile_reprojected = reproject_raster_in_memory(memfile_colored)

    # Optionally, save the final in-memory raster to disk
    with memfile_reprojected.open() as final_src:
        # Update the meta with compression and data type
        meta = final_src.meta.copy()
        meta.update(compress='lzw', dtype='uint8')
        with rasterio.open(final_path, 'w', **meta) as final_dst:
            final_dst.write(final_src.read())
