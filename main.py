import os
import pandas
import geopandas as gpd
import requests
import warnings


def read_in_file(filename, with_kml=False):
    '''customisable geopandas file reader
    
    Partial KML support is hackable in geopandas, but the fields are not read
    properly at this time.
    Additional work will be needed for KML files to be fully supported on our end.
    Alternatively, it may be wiser to drop KML support until it is fixed upstream.
    '''
    if with_kml:
        import fiona
        fiona.drvsupport.supported_drivers['KML'] = 'rw'
    return gpd.read_file(filename)


def query_scope_metadata(url='https://api.keybiodiversityareas.org:8000/v0/scope-metadata'):
    '''get the KBA scoping metadata'''
    return requests.get(url, verify=False).json()


def metadata_file_fields(x):
    '''return metadata field names to be written to the geopandas layer'''
    return [f for f in x if f != 'taxa']


def query_shape(token, wkt, url='https://api.keybiodiversityareas.org:8000/v0/scope'):
    '''query one polygon via the KBA API'''
    return requests.get(
        url,
        verify=False,
        headers={"Authorization": f"Bearer {token}", "WKT": wkt}
        ).json()


def scope(in_filename, out_filename, token, with_kml=False):
    '''fully scope a file
    
    Two outputs will be returned: an output gis file (compatible with geopandas)
    and a csv (automatically named from the gis output file name)
    '''
    # read in file
    layer = read_in_file(in_filename, with_kml=with_kml) # see details on the read_file function re KML support.
    # detach layer from file
    layer = layer.copy()
    # read in query metadata
    metadata = query_scope_metadata()
    # update whole layer with additional typed fields from the metadata query
    # this must be done at the layer level, not at the record level
    for field in metadata_file_fields(metadata):
        layer[field] = eval(f'{metadata[field][0]}()')
    # instantiate empty list of taxa results
    taxa = []
    # scope and update layer one feature (row) at a time
    for index, row in layer.iterrows():
        if row['geometry'] is None: # avoids error if some features lack geometry.
            warnings.warn(f"Feature {index} has no valid geometry: skipping")
            continue
        # scope feature
        scoping = query_shape(token=token, wkt=row['geometry'].wkt)
        # update layer with scoped data
        for f in metadata_file_fields(metadata):
            # must write to the original layer as iterrows creates a detached object
            layer.loc[index, f] = scoping[f]
        # update taxa list
        taxa.extend(scoping['taxa'])
    # write layer
    layer.to_file(out_filename)
    # compile and write csv
    df = pandas.DataFrame(taxa)
    df.to_csv(f'{os.path.splitext(out_filename)[0]}.csv', index=False)


if __name__=="__main__":
    files = {
        "data/Test_vector.kml" : "output/Test_vector_kml.kml",
        "data/Test_vector.gpkg": "output/Test_vector_gpkg.gpkg"
        }
    #files = ["data/Test_vector.gpkg"]
    # Reading, editing and writing occurs one file at a time to simplify.
    # For the portal, I would allow uploading and processing one file at a time.
    for file, output in files.items():
        scope(
            in_filename = file,
            out_filename = output,
            token = '', # your token here
            with_kml=True
            )