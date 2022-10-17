import json

import fiona
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import requests
import argparse

def read_in_files(filename):
    if(filename.split('.')[1] == "kml"):
        fiona.drvsupport.supported_drivers['KML'] = 'rw'
        return gpd.read_file(filename, driver="KML")
    else:
        return gpd.read_file(filename)

def query_shapes(url, auth, token, wkt):
    r = requests.get(url, verify=False, headers={auth: f"Bearer {token}", "WKT": wkt})
    response_dict = json.loads(r.text)
    return response_dict

if __name__=="__main__":
    files = ["data/Test_vector.kml", "data/Test_vector.gpkg"]
    url = "https://api.keybiodiversityareas.org:8000/v0/scope"
    auth = "Authorization"
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--token', type=str, help="Authorization token")
    args = parser.parse_args()

    gdf = read_in_files(files[0])

    for f in range(1, len(files)):
        cur_gdf = read_in_files(files[f])
        gdf = gdf.merge(cur_gdf, on="geometry", how='outer')

    geo_list = gdf["geometry"].to_wkt().tolist()
    print(type(geo_list[0]))

    responses = []
    for g in geo_list:
        r = query_shapes(url, auth, args.token, g)
        responses.append(r)

    print(responses)



