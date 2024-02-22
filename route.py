###################################################################
# Tools for calculating the optimal route between a set of points #
###################################################################
# This functionality uses the GraphHopper API
# see documentation here: https://www.graphhopper.com/
# more specifically here: https://docs.graphhopper.com/#operation/postRoute


# imports
import json
import numpy as np
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
# import GraphHopper API key
from api.api_key import API_KEY
# local imports
from api.requests import graphhopper_request


def get_route_coords(coords, session=None, profile='foot'):
    # get the route between a set of coordinates
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - session: requests.Session object (if None, a new one is created)
    # - profile: mode of transport, choose from 'car', 'bike' or 'foot'
    # returns:
    #   list of coordinates in same format as input
    if session is None: session = requests.Session()
    points = [[el['lon'], el['lat']] for el in coords]
    json = {
        'profile': profile,
        'points': points,
        'instructions': False,
        'points_encoded': False
    } 
    response = graphhopper_request(session, json, API_KEY, service='route')
    points = np.array(response['paths'][0]['points']['coordinates'])
    coords = [{'lon': el[0], 'lat': el[1]} for el in points]
    distance = response['paths'][0]['distance']
    info = {'distance': distance}
    return (coords, info)

def plot_route_coords(coords, route_coords=None, **kwargs):
    # make a visual representation of the route
    # if no route is provided, calculate it on the fly
    # input arguments:
    # - coords: list of coordinates, formatted as {'lon': longitude, 'lat': latitude}
    # - route_coords: route between coords, in same format as coords
    # - kwargs: passed down to get_route_coords if needed
    if route_coords is None: route_coords = get_route_coords(coords, **kwargs)[0]
    # put coordinates in a dataframe
    lon = [float(coord['lon']) for coord in coords]
    lat = [float(coord['lat']) for coord in coords]
    df_coords = pd.DataFrame({'node': np.arange(len(coords))})
    df_coords['lat'] = lat
    df_coords['lon'] = lon
    df_coords['color'] = 'red'
    df_coords['size'] = 1
    # put route in a dataframe
    lon = [float(coord['lon']) for coord in route_coords]
    lat = [float(coord['lat']) for coord in route_coords]
    df_route = pd.DataFrame({'node': np.arange(len(route_coords))})
    df_route['lat'] = lat
    df_route['lon'] = lon
    df_route['color'] = 'blue'
    # plot the coordinates on map
    fig1 = px.line_mapbox(df_route, lat="lat", lon="lon",
             color='color', color_discrete_map='identity',
             zoom=8, height=600, width=900)
    fig2 = px.scatter_mapbox(df_coords, lat="lat", lon="lon",
             hover_data={'size':False, 'lat':True, 'lon':True},
             color='color', color_discrete_map='identity',
             size='size', size_max=10,
             zoom=8, height=600, width=900)
    fig = go.Figure(data=fig1.data+fig2.data)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


if __name__=='__main__':
    # testing section

    # define points
    p1 = {'lat': 51.048903, 'lon': 3.695139}
    p2 = {'lat': 51.046213, 'lon': 3.698381}
    p3 = {'lat': 51.052116, 'lon': 3.699504}
    coords = [p2, p1, p3]

    # make requests session
    session = requests.Session()

    # get distances
    route_coords = get_route_coords(coords, session=session)[0]

    # plot distances
    plot_route_coords(coords, route_coords=route_coords)
