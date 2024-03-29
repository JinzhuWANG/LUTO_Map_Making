import os
import numpy as np
import imageio

import rasterio
from rasterio.io import MemoryFile
from rasterio.coords import BoundingBox
from rasterio.warp import (calculate_default_transform, 
                           transform_bounds, 
                           reproject, 
                           Resampling)



# function to write colormap to tif
def hex_color_to_numeric(hex_color: str, toFloat: bool = False) -> tuple:
    """
    Converts a hexadecimal color code to its numeric representation.

    Args:
        hex_color (str): The hexadecimal color code to convert.

    Returns:
        tuple: A tuple containing the red, green, blue, and (optional) alpha components of the color.
    """
    # Remove the '#' character (if present)
    hex_color = hex_color.lstrip('#')

    # Get the red, green, blue, and (optional) alpha components
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    
    # Add 1 if any of the value equals 0
    if red == 0:
        red += 1
    if green == 0:
        green += 1
    if blue == 0:
        blue += 1
    
    # If the color includes an alpha channel
    if len(hex_color) == 8:  # If the color includes an alpha channel
        alpha = int(hex_color[6:8], 16)
    else:
        alpha = 255
    
    # Convert to float if toFloat is True
    if toFloat:
        red, green, blue, alpha = red/255, green/255, blue/255, alpha/255
 
    return red, green, blue, alpha
    


def convert_1band_to_4band_in_memory(initial_tif:str,
                                     band:int=1, 
                                     color_dict: dict=None) -> MemoryFile:
    """Convert a 1-band array in a MemoryFile to 4-band (RGBA) and return a new MemoryFile.

    Args:
        initial_tif (str): 
                The path for input tif.
        color_dict (dict): 
                A dictionary of color values for each class.

    Returns:
        MemoryFile: The new MemoryFile containing the 4-band (RGBA) array.
    """
    
    with rasterio.open(initial_tif) as src:
        lu_arr = src.read(band)               # Read the 1-band array, return a 2D array (HW)
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


def save_colored_raster_as_png(src_memfile: MemoryFile, 
                               out_path: str, 
                               src_crs: str = 'EPSG:3857', 
                               dst_crs: str = 'EPSG:4326'):
    """
    Save a colored raster image as a PNG file.

    Args:
        src_memfile (MemoryFile):
            The source raster in a MemoryFile.
        out_path (str): 
            The path to save the PNG file.
        src_crs (str, optional): 
            The source coordinate reference system (CRS) of the raster image. 
            Defaults to 'EPSG:3857'.
        dst_crs (str, optional): 
            The destination CRS for transforming the bounding box. 
            Defaults to 'EPSG:4326'.

    Returns:
        Tuple[List[float], List[List[float]]]:
            A tuple containing the center coordinates and bounds of the transformed bounding box.
            The center coordinates are in the format [latitude, longitude].
            The bounds are a list of lists, where each inner list represents a point in the format [latitude, longitude].
    """
    with src_memfile.open() as src:
        bounds = src.bounds
        img = src.read()  # CHW
        img_rgba = img.transpose(1, 2, 0)  # CHW -> HWC

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
        
        imageio.imsave(out_path, img_rgba)
        
    # Return the center/bounds for folium
    return center, bounds_for_folium, mercator_bbox

# Function to reclassify -> colorfy -> reproject -> toPNG
def process_int_raster(initial_tif:str=None, 
                   band=1,
                   map_type_idx:int=None, 
                   color_dict:dict=None,
                   src_crs='EPSG:3857', 
                   dst_crs='EPSG:4326'):
    """
    Process a raster file by reclassifying, coloring, and reprojecting it entirely in memory.
    
    Args:
        initial_tif (str): 
            Path to the initial raster file.
        band (int): 
            Band number to process (default is 1).
        map_type_idx (int):
            Index of the map type (default is None).
        color_dict (dict): 
            Dictionary mapping pixel values to colors (default is None).
        src_crs (str):
            Source coordinate reference system (default is 'EPSG:3857').
        dst_crs (str):
            Destination coordinate reference system (default is 'EPSG:4326').
    
    Returns:
        tuple: A tuple containing the center, bounds for folium, and mercator bounding box.
    """
    # Process the raster entirely in memory
    f = convert_1band_to_4band_in_memory(initial_tif, band, color_dict)
    f = reproject_raster_in_memory(f)
    
    # Infer the save path (no extension) from the initial path
    save_base = os.path.splitext(initial_tif)[0]
        
    # Save the reprojected raster as a GeoTIFF file
    with f.open() as src:
        kwargs = src.meta.copy()
        kwargs.update(compress='lzw', dtype='uint8', nodata=None)
        with rasterio.open(f"{save_base}_mercator_{map_type_idx}.tif", 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i), i)
    
    # Save the reprojected raster as a PNG file
    center, bounds_for_folium, mercator_bbox = save_colored_raster_as_png(f, 
                                                    f"{save_base}_mercator_{map_type_idx}.png", 
                                                    src_crs, 
                                                    dst_crs)
    
    # Return the center and bounds for folium
    return center, bounds_for_folium, mercator_bbox




###################################################################
#                       Process float image                       #
###################################################################


def float_img_to_int(tif_path: str, 
                    band: int = 1):
    """
    Converts a floating-point image to an integer image.

    Args:
        tif_path (str): The path to the input TIFF file.
        band (int, optional): The band number to read from the TIFF file. Defaults to 1.

    Returns:
        MemoryFile: The in-memory file containing the converted integer image.
    """
    with rasterio.open(tif_path) as src:
        src_arr = src.read(band)
        src_arr = (src_arr * 100).astype(np.int16)
        
        meta = src.meta.copy()
        meta.update(compress='lzw')

        # Create an in-memory file
        memfile = MemoryFile()
        with memfile.open(**meta) as dst:
            dst.write(src_arr, band)
            
        return memfile
    

def mask_invalid_data(memfile: MemoryFile, 
                      mask_path: str):
    """
    Masks the invalid data in the input memory file using the provided mask.

    Args:
        memfile (MemoryFile): The input memory file containing the data to be masked.
        mask_path (str): The path to the mask file.

    Returns:
        MemoryFile: The memory file with the invalid data masked.
    """

    with rasterio.open(mask_path) as mask, memfile.open() as src:
        
        
        mask_arr = mask.read(1)
        mask_arr = mask_arr.astype(np.int16)
        
        # read the 4-band array
        out_arr = src.read() # CHW
        out_arr = out_arr.transpose(1, 2, 0) # CHW -> HWC
        
        # Mask the invalid data
        out_arr[mask_arr == -9999] = (0, 0, 0, 0)
        out_arr = out_arr.transpose(2, 0, 1) # HWC -> CHW
        
        meta = src.meta.copy()
        meta.update(compress='lzw', dtype=np.uint8, count=out_arr.shape[0])
        
    # Create a new in-memory file for the 4-band array
    memfile = MemoryFile()
    with memfile.open(**meta) as dst:
        dst.write(out_arr)
        
    return memfile



# Function to intify -> colorfy -> reproject -> toPNG
def process_float_raster(initial_tif:str=None, 
                   band:int=1,
                   color_dict:dict=None,
                   mask_path:str=None, 
                   src_crs='EPSG:3857', 
                   dst_crs='EPSG:4326'):
    """
    Process a float raster image by converting it to an integer, 
    converting it to a 4-band image, masking invalid data, and 
    reprojecting it. Save the reprojected raster as a GeoTIFF file 
    and a PNG file. Return the center and bounds for folium.

    Parameters:
    initial_tif (str): 
        Path to the initial float raster image.
    band (int, default=1): 
        Band number of the float raster image.
    color_dict (dict): 
        Dictionary mapping values to colors for the 4-band image.
    mask_path (str): 
        Path to the mask file for invalid data.
    src_crs (str, default='EPSG:3857'): 
        Source CRS (Coordinate Reference System) of the raster image.
    dst_crs (str, default='EPSG:4326'): 
        Destination CRS for reprojecting the raster image.

    Returns:
    tuple: A tuple containing the center coordinates, bounds for folium, and the mercator bounding box.
    """
    
    f = float_img_to_int(initial_tif,band)
    f = convert_1band_to_4band_in_memory(f,color_dict)
    f = mask_invalid_data(f, mask_path)
    f = reproject_raster_in_memory(f)
    
    # Infer the save path (no extension) from the initial path
    save_base = os.path.splitext(initial_tif)[0]

    # Save the reprojected raster as a GeoTIFF file
    with f.open() as src:
        kwargs = src.meta.copy()
        kwargs.update(compress='lzw', dtype='uint8', nodata=None)
        with rasterio.open(f"{save_base}_mercator.tif", 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i), i)

    # Save the reprojected raster as a PNG file
    center, bounds_for_folium, mercator_bbox = save_colored_raster_as_png(f, 
                                                    f"{save_base}_mercator.png", 
                                                    src_crs, 
                                                    dst_crs)

    # Return the center and bounds for folium
    return center, bounds_for_folium, mercator_bbox
