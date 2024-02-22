################################################################
# Tools for building a distance matrix between a set of points #
################################################################
# This functionality uses the GraphHopper API
# see documentation here: https://www.graphhopper.com/
# more specifically here: https://docs.graphhopper.com/#operation/postMatrix


# imports
import numpy as np
import pandas as pd
import requests
import plotly.express as px
# import GraphHopper API key
from api.api_key import API_KEY
# local imports
from api.requests import graphhopper_request


def get_distance_matrix(coords, session=None, profile='foot'):
    # get the distance matrix between a set of coordinates
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - session: requests.Session object (if None, a new one is created)
    # - profile: mode of transport, choose from 'car', 'bike' or 'foot'
    # returns:
    #   numpy array with distances in meter;
    #   d[i,j] gives the distances between the i'th point as source
    #   and the j'th point as destination
    if session is None: session = requests.Session()
    points = [[el['lon'], el['lat']] for el in coords]
    json = {
        'profile': profile,
        'points': points,
        'instructions': False,
        'points_encoded': False
    } 
    response = graphhopper_request(session, json, API_KEY, service='matrix')
    distances = np.array(response['weights'])
    return distances

def plot_distance_matrix(coords, distances=None, **kwargs):
    # make a visual representation of the distance matrix
    # if no distances are provided, calculate them on the fly
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - distances: distance matrix in np array format (e.g. output of get_distance_matrix)
    # - kwargs: passed down to get_distance_matrix if needed
    if distances is None: distances = get_distances_matrix(coords, **kwargs)
    # format coordinates
    lon = [float(coord['lon']) for coord in coords]
    lat = [float(coord['lat']) for coord in coords]
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
    coords = [p1,p2,p3]

    # make requests session
    session = requests.Session()

    # get distances
    distances = get_distance_matrix(coords, session=session)
    print(distances)

    # plot distances
    plot_distance_matrix(coords, distances=distances)
