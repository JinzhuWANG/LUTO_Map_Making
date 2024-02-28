import contextily as ctx

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