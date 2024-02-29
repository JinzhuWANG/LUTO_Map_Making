import pandas as pd
import contextily as ctx
import matplotlib as mpl


from map_tools.parameters import (color_types,
                                  data_types,
                                  legend_positions)


# Function to download a basemap image
def download_basemap(bounds_mercator):
    """
    Downloads a basemap image within the specified bounds in Mercator projection.

    Args:
        bounds_mercator (mercantile.Bounds): The bounds of the area to download the basemap for.

    Returns:
        tuple: A tuple containing the downloaded basemap image and the extent of the image.

    Raises:
        None

    """
    xmin = bounds_mercator.left
    ymin = bounds_mercator.bottom
    xmax = bounds_mercator.right
    ymax = bounds_mercator.top

    base_map, extent = ctx.bounds2raster(xmin,
                                        ymin, 
                                        xmax, 
                                        ymax, 
                                        path='Assests/basemap.tif',
                                        source=ctx.providers.OpenStreetMap.Mapnik,
                                        zoom=7,
                                        n_connections=8)

   
# Function to create value-color dictionary for intergirized raster (0-100) 
def get_color_dict(color_scheme:str='YlOrRd',
                   save_path:str='Assests/float_img_colors.csv',
                   extra_color:dict={-100:(225, 225, 225, 255)}):
    """
    Create a CSV file contains the value-color(HEX) records.

    Parameters:
    - color_scheme (str): 
        The name of the color scheme to use. Default is 'YlOrRd'.
    - save_path (str): 
        The file path to save the color dictionary as a CSV file. Default is 'Assests/float_img_colors.csv'.
    - extra_color (dict): 
        Additional colors to include in the dictionary. Default is {-100:(225, 225, 225, 255)}.

    Returns:
        None
    """
    colors = mpl.colormaps[color_scheme]
    val_colors_dict = {i: colors(i/100) for i in range(101)}
    var_colors_dict = {k:tuple(int(num*255) for num in v) for k,v in val_colors_dict.items()}
    
    
    # If extra colors are specified, add them to the dictionary
    if extra_color:
        var_colors_dict.update(extra_color) 
    
    # Convert the RGBA values to HEX color codes
    var_colors_dict = {k: f"#{''.join(f'{c:02X}' for c in v)}" 
                       for k, v in var_colors_dict.items()}
    
    # Save the color dictionary to a CSV file
    color_df = pd.DataFrame(var_colors_dict.items(), columns=['lu_code', 'lu_color_HEX'])
    color_df.to_csv(save_path, index=False)
    
    
def get_map_meta():
    """
    Get the map metadata.

    Returns:
        map_meta (DataFrame): DataFrame containing map metadata with columns 'map_type', 'csv_path', 'legend_type', and 'legend_position'.
    """
    map_meta = pd.DataFrame(color_types.items(), 
                            columns=['map_type', 'csv_path'])
    map_meta = map_meta.explode('csv_path')

    map_meta['data_type'] = map_meta['map_type'].map(data_types)
    map_meta['legend_position'] = map_meta['map_type'].map(legend_positions)
    
    return map_meta.reset_index(drop=True)

