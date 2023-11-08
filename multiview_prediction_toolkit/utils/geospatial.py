import logging

import matplotlib.pyplot as plt
import numpy as np
import pyproj
import rasterio as rio
from geopandas import GeoDataFrame
from shapely import MultiPolygon, intersection, union
from tqdm import tqdm


def ensure_geometric_CRS(geodata):
    if geodata.crs == pyproj.CRS.from_epsg(4326):
        point = geodata["geometry"][0].centroid
        geometric_crs = get_projected_CRS(lon=point.x, lat=point.y)
        return geodata.to_crs(geometric_crs)
    return geodata


def get_projected_CRS(lat, lon, assume_western_hem=True):
    if assume_western_hem and lon > 0:
        lon = -lon
    # https://gis.stackexchange.com/questions/190198/how-to-get-appropriate-crs-for-a-position-specified-in-lat-lon-coordinates
    epgs_code = 32700 - round((45 + lat) / 90) * 100 + round((183 + lon) / 6)
    crs = pyproj.CRS.from_epsg(epgs_code)
    return crs


def find_union_of_intersections(list_of_multipolygons, crs, vis=False):
    all_intersections = MultiPolygon()
    for i, multipolygon_a in enumerate(list_of_multipolygons):
        for multipolygon_b in list_of_multipolygons[:i]:
            new_intersection = intersection(multipolygon_a, multipolygon_b)
            all_intersections = union(all_intersections, new_intersection)
    if vis:
        geopandas_all_intersections = GeoDataFrame(
            geometry=[all_intersections], crs=crs
        )
        geopandas_all_intersections.plot()
        plt.show()
    return all_intersections


# https://stackoverflow.com/questions/60288953/how-to-change-the-crs-of-a-raster-with-rasterio
def reproject_raster(in_path, out_path, out_crs=pyproj.CRS.from_epsg(4326)):

    """ """
    logging.warn("Starting to reproject raster")
    # reproject raster to project crs
    with rio.open(in_path) as src:
        src_crs = src.crs
        transform, width, height = rio.warp.calculate_default_transform(
            src_crs, out_crs, src.width, src.height, *src.bounds
        )
        kwargs = src.meta.copy()

        kwargs.update(
            {"crs": out_crs, "transform": transform, "width": width, "height": height}
        )

        with rio.open(out_path, "w", **kwargs) as dst:
            for i in tqdm(range(1, src.count + 1), desc="Reprojecting bands"):
                rio.warp.reproject(
                    source=rio.band(src, i),
                    destination=rio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=out_crs,
                    resampling=rio.warp.Resampling.nearest,
                )
    logging.warn("Done reprojecting raster")
