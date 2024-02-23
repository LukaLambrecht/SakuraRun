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
import plotly.graph_objects as go
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
        'points_encoded': False,
        'out_arrays': ['distances']
    } 
    response = graphhopper_request(session, json, API_KEY, service='matrix')
    distances = np.array(response['distances'])
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
    df_coords['color'] = 'red'
    df_coords['size'] = 1
    # put connecting lines in a list of dataframes
    # note: differences between i,j and j,i are ignored for now
    dfs = []
    for i in range(distances.shape[0]):
        for j in range(i+1,distances.shape[1]):
            df = pd.DataFrame({'note': np.arange(2)})
            df['lat'] = [lat[i], lat[j]]
            df['lon'] = [lon[i], lon[j]]
            dfs.append(df)
    # make a dataframe with transparent points along the edges for displaying text
    df_text = pd.DataFrame({'node': np.arange(len(dfs))})
    mid_lat = []
    mid_lon = []
    mid_dist = []
    for i in range(distances.shape[0]):
        for j in range(i+1,distances.shape[1]):
            mid_lat.append( (lat[i]+lat[j])/2. )
            mid_lon.append( (lon[i]+lon[j])/2. )
            mid_dist.append(distances[i,j])
    df_text['lat'] = mid_lat
    df_text['lon'] = mid_lon
    df_text['size'] = 1
    df_text['distance'] = mid_dist
    # plot the coordinates on map
    tempfig = px.scatter_mapbox(df_text, lat="lat", lon="lon",
                hover_data={'distance': True, 'size':False, 'lat':False, 'lon':False},
                size='size', size_max=10)
    figdata = tempfig.data
    for df in dfs:
        tempfig = px.line_mapbox(df, lat="lat", lon="lon")
        figdata += tempfig.data
    tempfig = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
                hover_data={'size':False, 'color':False, 'lat':True, 'lon':True},
                color='color', color_discrete_map='identity',
                size='size', size_max=10,
                zoom=8, height=600, width=900)
    figdata += tempfig.data
    fig = go.Figure(figdata)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
