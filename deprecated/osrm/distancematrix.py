################################################################
# Tools for building a distance matrix between a set of points #
################################################################
# This functionality uses the OSRM API
# see documentation here: https://project-osrm.org/
# more specifically here: https://project-osrm.org/docs/v5.24.0/api/#table-service


# imports
import numpy as np
import pandas as pd
import requests
import plotly.express as px


def make_osrm_table_url(coords, profile='foot'):
    # prepare the correct OSRM request URL
    # input arguments:
    # - coords: list of coordinates, formatted as strings of the form "lon,lat"
    # - profile: choose from "car", "bike" or "foot"
    url = 'http://router.project-osrm.org/table/v1/{}/'.format(profile)
    url += '{}?'.format(';'.join(coords))
    url += 'annotations=duration,distance'
    return url

def get_distance_matrix(coords, **kwargs):
    # get the distance matrix between a set of coordinates
    # input arguments:
    # - coords: list of coordinates, formatted as strings of the form "lon,lat"
    # - kwargs: passed down to make_osrm_table_url
    # returns:
    #   numpy array with distances in meter;
    #   d[i,j] gives the distances between the i'th point as source
    #   and the j'th point as destination
    url = make_osrm_table_url(coords, **kwargs)
    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers=headers)
    rjson = r.json()
    if rjson['code']!='Ok':
        msg = 'WARNING: request returned status code {}'.format(rjson['code'])
        print(msg)
    distances = np.array(rjson['distances'])
    return distances

def plot_distance_matrix(coords, distances=None, **kwargs):
    # make a visual representation of the distance matrix
    # if no distances are provided, calculate them on the fly
    if distances is None: distances = get_distances_matrix(coords, **kwargs)
    # format coordinates
    lon = [float(coord.split(',')[0]) for coord in coords]
    lat = [float(coord.split(',')[1]) for coord in coords]
    # put coordinates in a dataframe
    df_coords = pd.DataFrame({'node': np.arange(len(coords))})
    df_coords['lat'] = lat
    df_coords['lon'] = lon
    # put connecting lines in a dataframe
    # to do...
    # plot the coordinates on map
    fig = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
            zoom=8, height=600, width=900)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


if __name__=='__main__':
    # testing section

    # define points
    p1 = {'lat': 51.048903, 'lon': 3.695139}
    p2 = {'lat': 51.046213, 'lon': 3.698381}
    p3 = {'lat': 51.052116, 'lon': 3.699504}

    # format points
    coords = ["{},{}".format(p['lon'], p['lat']) for p in [p1,p2,p3]]

    # get distances
    distances = get_distance_matrix(coords)
    print(distances)

    # plot distances
    plot_distance_matrix(coords, distances=distances)
