import os
import rasterio
from rasterio.plot import show
from rasterio.merge import merge

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib_scalebar.scalebar import ScaleBar

import matplotlib.patches as mpatches



def create_png_map(tif_path: str, 
                  color_desc_dict: dict,
                  basemap_path: str, 
                  shapefile_path: str,
                  anno_text: str, 
                  save_path: str):
    """
    Creates a mosaic of a raster image with a basemap, overlays a shapefile, and adds scale bar, north arrow, and legend.

    Parameters:
    tif_path (str): 
        The file path of the raster image.
    color_desc_dict (dict):
        A dictionary mapping color values to their corresponding descriptions for the legend.
    basemap_path (str): 
        The file path of the basemap.
    shapefile_path (str): 
        The file path of the shapefile.
    anno_text (str): 
        The annotation text to be displayed on the mosaic.
    save_path (str): 
        The file path to save the resulting image.

    Returns:
    None
    """
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(20, 20)) 

    # Mosaic the raster with the basemap
    with rasterio.open(tif_path) as src, rasterio.open(basemap_path) as base:
        # Mosaic the raster with the basemap
        mosaic, out_transform = merge([src, base])
    

    # Display the mosaic raster
    show(mosaic, ax=ax, transform=out_transform)
    
    # Add annotation
    plt.annotate(anno_text, 
         xy=(0.07, 0.9), 
         xycoords='axes fraction',
         fontsize=25,
        #  fontweight = 'bold',
         ha='left', 
         va='center')
    

    # Overlay the shapefile
    # Load the shapefile with GeoPandas
    gdf = gpd.read_file(shapefile_path)
    gdf.boundary.plot(ax=ax, 
              color='grey', 
              linewidth=0.5, 
              edgecolor='grey', 
              facecolor='none')

    # Create scale bar
    ax.add_artist(ScaleBar(1, 
               "m", 
               location="lower right",
               border_pad=1,
               fixed_units="km",
               fixed_value=500,
               box_color="skyblue", 
               box_alpha=0))

    # Create north arrow
    x, y, arrow_length = 0.9, 0.9, 0.07
    ax.annotate('N', 
        xy=(x, y), 
        xytext=(x, y-arrow_length),
        arrowprops=dict(facecolor='#5f5f5e', 
                        edgecolor='#5f5f5e', 
                        width=30, 
                        headwidth=45),
        ha='center', 
        va='center', 
        fontsize=25,
        color='#2f2f2f',
        xycoords=ax.transAxes)

    # Create legend
    patches = [mpatches.Patch(color=tuple(value / 255 for value in k), label=v) 
           for k, v in color_desc_dict.items()]

    plt.legend(handles=patches, 
           bbox_to_anchor=(0.09, 0.2), 
           loc=2, 
           borderaxespad=0.,
           ncol=2, 
           fontsize=20,
           framealpha=0)

    # Optionally remove axis
    ax.set_axis_off()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    # Delete the input raster
    os.remove(tif_path)