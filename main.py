import json
import sys

import fiona
import pandas as pd
import seaborn as sns
import numpy as np
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

# def test_convert():
#     filename = "data/Test_vector.json"
#     gdf = read_in_files(filename)
#     gdf.to_file('data/new_file.gpkg', driver='GPKG')
#     sys.exit()

if __name__=="__main__":
    files = ["data/Test_vector.geojson", "data/Test_vector.json", "data/Test_vector.kml", "data/Test_vector.zip"]
    url = "https://api.keybiodiversityareas.org:8000/v0/scope"
    auth = "Authorization"
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--token', type=str, help="Authorization token")
    args = parser.parse_args()

    # Read in geometries from "uploaded" files
    gdf = read_in_files(files[0])
    for f in range(1, len(files)):
        cur_gdf = read_in_files(files[f])
        gdf = gdf.merge(cur_gdf, on="geometry", how='outer')

    # Get geometries in WKT format for querying API
    geo_list = gdf["geometry"].to_wkt().tolist()

    # Get responses for uploaded (multi-)polygons
    responses = []
    for g in geo_list:
        r = query_shapes(url, auth, args.token, g)
        responses.append(r)

    # Generate files for export for each uploaded (multi-)polygon
    for i in range(len(responses)):
        # (1) Adding response fields as columns of GeoDataFrame
        cur_row = gdf.iloc[i].copy() # get first row, i.e., first inputted (multi-)polygon

        #  adding responses as new columns
        for col in responses[i].keys():
            if col != 'taxa':
                cur_row[col] = responses[i][col]

        #  manipulating back into a GeoDataFrame
        cur_row = cur_row.to_frame().T
        cur_row = gpd.GeoDataFrame(cur_row, geometry = 'geometry')

        #  exporting new info to gpkg using the original filename
        gpkg_filename = 'test_outputs/' + files[i].split('/')[-1]
        cur_row = cur_row.drop(columns=["fid"])
        print(cur_row.columns)
        cur_row.to_file(gpkg_filename, driver = 'GPKG')

        # (2) Build dataframe w/all of the taxa info and export as CSV
        #   - `from_dict` works even when fields aren't all the same... fills w/NaN!
        taxa_df = pd.DataFrame.from_dict(responses[i]['taxa'])

        taxa_filename = 'test_outputs/' + files[i].split('/')[-1].removesuffix('.gpkg') + '.csv'
        taxa_df.to_csv(taxa_filename, index = False)
