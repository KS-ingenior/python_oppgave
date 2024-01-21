# -*- coding: utf-8 -*-
import requests

import geopandas as gpd
from shapely.geometry import Point
from prcoords import wgs_gcj

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Beijing city centre
BBOX = "(39.823303697329386,116.29852294921876,39.970805680527725,116.50812149047853)"

OUT_FILE = "data/beijing_bakerier.geojson"


def get_bakeries(url: str, bbox: str, tags_to_include: list) -> list:
    """
    Returns a dictionary holding all OSM bakeries within a bounding box with specified tags.
    All locations are converted to the GCJ-02 datum using PRCoords.
    """
    query = f"""
[out:json][timeout:25];
nwr["shop"="bakery"]{bbox};
out geom;
"""
    response = requests.get(url, params={"data": query})

    data = response.json()

    result_dicts = []
    for element in data["elements"]:
        dict_elem = {}
        # Parse id, always present
        dict_elem["id"] = element["id"]
        # Parse optional tags, most bakeries have these in particular:
        for tag in tags_to_include:
            dict_elem[tag] = (
                element["tags"][tag] if tag in element["tags"] else ""
            )
        # Parse geometry and obfuscate using GCJ-02
        gcj_latlon = wgs_gcj((element["lat"], element["lon"]))
        dict_elem["geometry"] = Point(gcj_latlon[1], gcj_latlon[0])
        result_dicts.append(dict_elem)

    return result_dicts


if __name__ == "__main__":
    results = get_bakeries(
        url=OVERPASS_URL,
        bbox=BBOX,
        tags_to_include=["name", "name:en", "shop", "opening_hours"],
    )
    results_gdf = gpd.GeoDataFrame(results)

    results_gdf.to_file(OUT_FILE)
